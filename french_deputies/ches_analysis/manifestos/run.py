"""
Validacion RILE vs CHES sobre los manifiestos electorales (Francia 2017).

Pipeline:
  1. Carga las predicciones MARPOR de manifestoberta sobre los manifiestos
     (un top1_code por quasi-frase) + el cmp_code humano de MARPOR.
  2. Calcula RILE por partido de TRES formas:
       - rile_model    : desde top1_code (lo que predice manifestoberta)
       - rile_human    : desde cmp_code  (codificacion humana, mismas frases)
       - rile_official : del party_positions.csv publicado por MARPOR (sanity check)
  3. Empareja cada partido con su posicion lrgen en CHES 2019 (benchmark externo).
  4. Calcula correlaciones (Pearson + Spearman) en tres capas:
       A) rile_model    vs rile_human   -> el modelo reproduce al humano?  (n=10)
       B) rile_model    vs ches_lrgen   -> validacion EXTERNA               (n=8)
       Techo) rile_human vs ches_lrgen  -> cuanto coinciden dos gold std.   (n=8)
  5. Guarda CSVs, JSON de correlaciones y un scatter.

Resultados en ches_analysis/manifestos/results/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

THIS = Path(__file__).resolve().parent
MODULE = THIS.parent
sys.path.insert(0, str(MODULE))
from common.rile import compute_rile  # noqa: E402
from common import ches  # noqa: E402

REPO = MODULE.parent.parent  # .../Tesis
PREDS = (REPO / "french_deputies" / "manifestoberta_analysis"
         / "manifestos" / "results" / "predictions.csv")
CHES_CSV = MODULE / "data" / "CHES2019V3.csv"
OFFICIAL = (REPO / "french_deputies" / "manifestos" / "processed"
            / "party_positions.csv")
OUT = THIS / "results"


def rile_per_party(df: pd.DataFrame, code_col: str) -> pd.DataFrame:
    rows = []
    for party, sub in df.groupby("party_abbrev"):
        rile, n = compute_rile(sub[code_col])
        rows.append({"party_abbrev": party, "rile": round(rile, 3), "n_coded": n})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Cargando predicciones: {PREDS}")
    df = pd.read_csv(PREDS)
    print(f"  {len(df):,} quasi-frases, {df['party_abbrev'].nunique()} partidos")

    # === 1-2. RILE por partido (modelo y humano) ===
    rile_model = rile_per_party(df, "top1_code").rename(
        columns={"rile": "rile_model", "n_coded": "n_model"})
    rile_human = rile_per_party(df, "cmp_code").rename(
        columns={"rile": "rile_human", "n_coded": "n_human"})
    party = rile_model.merge(rile_human, on="party_abbrev")

    # RILE oficial publicado por MARPOR (sanity check del calculo)
    off = pd.read_csv(OFFICIAL)[["partyabbrev", "rile"]].rename(
        columns={"partyabbrev": "party_abbrev", "rile": "rile_official"})
    # el CSV oficial tiene algunos abbrev vacios (LFI, LR); los completamos por nombre
    official_by_name = pd.read_csv(OFFICIAL)[["partyname", "rile"]]
    name_to_abbrev = {"Indomitable France": "LFI", "The Republicans": "LR"}
    extra = official_by_name.assign(
        party_abbrev=official_by_name["partyname"].map(name_to_abbrev)).dropna(
        subset=["party_abbrev"])[["party_abbrev", "rile"]].rename(
        columns={"rile": "rile_official"})
    off = pd.concat([off.dropna(subset=["party_abbrev"]), extra], ignore_index=True)
    off = off.drop_duplicates("party_abbrev")
    party = party.merge(off, on="party_abbrev", how="left")

    # === 3. Emparejar con CHES 2019 ===
    ches_fr = ches.load_ches_france(CHES_CSV)
    party["ches_party"] = party["party_abbrev"].map(ches.ABBREV_TO_CHES)
    party = party.merge(ches_fr, on="ches_party", how="left")

    party = party.sort_values("rile_model").reset_index(drop=True)
    party.to_csv(OUT / "party_rile.csv", index=False)
    print("\nRILE por partido:")
    print(party[["party_abbrev", "rile_model", "rile_human",
                 "rile_official", "ches_party", "lrgen"]].to_string(index=False))

    # === 4. Correlaciones (tres capas) ===
    corr_layer_a = ches.correlate(party["rile_model"], party["rile_human"])
    corr_layer_b = ches.correlate(party["rile_model"], party["lrgen"])
    corr_ceiling = ches.correlate(party["rile_human"], party["lrgen"])
    corr_official = ches.correlate(party["rile_official"], party["lrgen"])

    # Diagnosticos:
    #  - contra lrecon (eje economico): RILE tiene fuerte carga economica
    #  - excluyendo RN: RILE subestima sistematicamente a la derecha radical
    #    (enfatiza welfare/504, una categoria "de izquierda"); es una limitacion
    #    documentada del indice, no un error del modelo.
    corr_b_econ = ches.correlate(party["rile_model"], party["lrecon"])
    no_rn = party[party["ches_party"] != "RN"]
    corr_b_no_rn = ches.correlate(no_rn["rile_model"], no_rn["lrgen"])
    corr_ceiling_no_rn = ches.correlate(no_rn["rile_human"], no_rn["lrgen"])
    # umbral de fiabilidad: RILE es ruidoso con pocas quasi-frases (MARPOR
    # recomienda cautela); exigimos >=100 frases clasificadas.
    MIN_N = 100
    reliable = party[party["n_model"] >= MIN_N]
    corr_b_reliable = ches.correlate(reliable["rile_model"], reliable["lrgen"])

    correlations = {
        "source": "manifestos",
        "ches_wave": 2019,
        "ches_scale": "lrgen 0-10",
        "layer_A_model_vs_human": corr_layer_a,
        "layer_B_model_vs_ches": corr_layer_b,
        "ceiling_human_vs_ches": corr_ceiling,
        "ref_official_rile_vs_ches": corr_official,
        "diagnostics": {
            "model_vs_ches_lrecon": corr_b_econ,
            "model_vs_ches_excl_RN": corr_b_no_rn,
            "human_vs_ches_excl_RN": corr_ceiling_no_rn,
            "model_vs_ches_reliable_nmin100": corr_b_reliable,
        },
        "parties_total": int(len(party)),
        "parties_matched_ches": int(party["lrgen"].notna().sum()),
        "parties_not_in_ches": party.loc[party["lrgen"].isna(),
                                         "party_abbrev"].tolist(),
    }
    ches.dump_json(correlations, OUT / "correlations.json")

    print("\n=== Correlaciones ===")
    print(f"  A) modelo vs humano (RILE):   "
          f"rho={corr_layer_a['spearman_rho']}  r={corr_layer_a['pearson_r']}  "
          f"n={corr_layer_a['n']}")
    print(f"  B) modelo vs CHES (externo):  "
          f"rho={corr_layer_b['spearman_rho']}  r={corr_layer_b['pearson_r']}  "
          f"n={corr_layer_b['n']}")
    print(f"  Techo) humano vs CHES:        "
          f"rho={corr_ceiling['spearman_rho']}  r={corr_ceiling['pearson_r']}  "
          f"n={corr_ceiling['n']}")
    print("  --- diagnosticos ---")
    print(f"  modelo vs CHES lrecon:        "
          f"rho={corr_b_econ['spearman_rho']}  r={corr_b_econ['pearson_r']}  "
          f"n={corr_b_econ['n']}")
    print(f"  modelo vs CHES (sin RN):      "
          f"rho={corr_b_no_rn['spearman_rho']}  r={corr_b_no_rn['pearson_r']}  "
          f"n={corr_b_no_rn['n']}")
    print(f"  humano vs CHES (sin RN):      "
          f"rho={corr_ceiling_no_rn['spearman_rho']}  "
          f"r={corr_ceiling_no_rn['pearson_r']}  n={corr_ceiling_no_rn['n']}")
    print(f"  modelo vs CHES (n>=100):      "
          f"rho={corr_b_reliable['spearman_rho']}  "
          f"r={corr_b_reliable['pearson_r']}  n={corr_b_reliable['n']}")

    # tabla de comparacion final (solo emparejados con CHES)
    matched = party.dropna(subset=["lrgen"]).copy()
    matched[["party_abbrev", "ches_party", "rile_model", "rile_human",
             "lrgen", "lrecon", "galtan"]].to_csv(
        OUT / "rile_vs_ches.csv", index=False)

    # === 5. Scatter modelo vs CHES ===
    ches.scatter_rile_vs_ches(
        matched, x_col="rile_model", y_col="lrgen", label_col="party_abbrev",
        title="RILE estimado (manifestoberta) vs CHES 2019 lrgen — manifiestos",
        out_png=OUT / "scatter_rile_vs_ches.png", corr=corr_layer_b)

    print(f"\nResultados en {OUT}/")


if __name__ == "__main__":
    main()
