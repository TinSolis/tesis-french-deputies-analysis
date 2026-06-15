"""
Análisis 2 — La agenda REVELADA: leyes y enmiendas no miden lo mismo.

Pregunta: ¿el voto parlamentario revela preferencias temáticas, o solo disciplina
gobierno/oposición?

Argumento: el voto final de una ley mide sobre todo **posición institucional**
(mayoría vs oposición). El voto sobre enmiendas debilita esa lógica de bloque y
deja ver clivajes temáticos modestos, sobre todo culturales.

Este módulo no recalcula soporte/cohesión/heatmaps (ya están en lois/ y
amendements/). Agrega lo que cruza ambos corpus y blinda el argumento:

  1. Descomposición de poder explicativo (R² ponderado), por separado en leyes y
     enmiendas, de cuatro modelos anidados:
        bloque          : mayoría vs oposición
        partido         : diferencias estables entre partidos
        partido+dominio : añade el tema MARPOR dominante (aditivo)
        partido×dominio : el tema modula el apoyo de cada partido (interacción)
     Compara bloque vs partido: ¿basta saber el bloque, o importa el partido fino?
  2. Comparación cross-corpus: soporte global en leyes vs enmiendas por partido.
  3. Bootstrap por scrutin (clúster) del soporte relativo en enmiendas: IC95 y
     estabilidad de signo del clivaje cultural (Fabric of Society, Freedom & Dem.).
  4. Leverage por ley: cada dominio, ¿en cuántas leyes distintas se reparte, o se
     concentra en un solo gran debate legislativo?

Salidas en agenda_revelada/results/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS = Path(__file__).resolve().parent
PA = THIS.parent
sys.path.insert(0, str(PA))
from common import votes  # noqa: E402

REPO = PA.parent.parent
MB = REPO / "french_deputies" / "manifestoberta_analysis"
VOTES_DIR = REPO / "french_deputies" / "lois_votes" / "votes_rd" / "processed"
DEP = REPO / "french_deputies" / "datos_diputados" / "data" / "deputes_an_rd.csv"
OUT = THIS / "results"

CORPORA = {
    "leyes": (MB / "lois" / "results" / "predictions.csv",
              VOTES_DIR / "votos_por_diputado.csv"),
    "enmiendas": (MB / "amendements" / "results" / "predictions.csv",
                  VOTES_DIR / "votos_amendements_por_diputado.csv"),
}
AMEND_PREDS = MB / "amendements" / "results" / "predictions.csv"
GOV = {"LREM", "MoDem"}  # bloque gubernamental (mayoría presidencial 2017-2022)
N_BOOT = 1000
RNG = np.random.default_rng(11)


def load_corpus(preds_path: Path, votes_path: Path, dep2party: dict):
    """Devuelve (stance, dom_long) restringidos a scrutins con texto y votos."""
    preds = pd.read_csv(preds_path, usecols=["scrutin_id", "domain"])
    vts = pd.read_csv(votes_path)
    stance = votes.party_stance(vts, dep2party)
    dom_long = votes.scrutin_domain_counts(preds)
    sset = set(dom_long["scrutin_id"]) & set(stance["scrutin_id"])
    stance = stance[stance["scrutin_id"].isin(sset)].copy()
    dom_long = dom_long[dom_long["scrutin_id"].isin(sset)].copy()
    return stance, dom_long


def build_units(stance: pd.DataFrame, dom_long: pd.DataFrame) -> pd.DataFrame:
    """Unidad (partido, scrutin): support_rate, expressed, dominio dominante, bloque."""
    dom = (dom_long.sort_values("n", ascending=False)
           .drop_duplicates("scrutin_id")[["scrutin_id", "domain_name"]])
    units = stance.merge(dom, on="scrutin_id", how="inner")
    units["bloque"] = np.where(units["party"].isin(GOV), "gobierno", "oposicion")
    return units[["party", "bloque", "scrutin_id", "support_rate", "expressed",
                  "domain_name"]]


def group_pred(df: pd.DataFrame, cols: list) -> np.ndarray:
    g = df.assign(wy=df["support_rate"] * df["expressed"])
    gm = g.groupby(cols).agg(wy=("wy", "sum"), w=("expressed", "sum"))
    gm["pred"] = gm["wy"] / gm["w"]
    return df.merge(gm["pred"].reset_index(), on=cols, how="left")["pred"].values


def wls_pred(df: pd.DataFrame, factors: list) -> np.ndarray:
    X = pd.get_dummies(df[factors].astype(str), drop_first=True, dtype=float)
    X.insert(0, "const", 1.0)
    Xv, yv, wv = X.values, df["support_rate"].values, df["expressed"].values
    sw = np.sqrt(wv)
    beta, *_ = np.linalg.lstsq(Xv * sw[:, None], yv * sw, rcond=None)
    return Xv @ beta


def weighted_r2(y: np.ndarray, pred: np.ndarray, w: np.ndarray) -> float:
    ybar = np.average(y, weights=w)
    ss_tot = float(np.sum(w * (y - ybar) ** 2))
    ss_res = float(np.sum(w * (y - pred) ** 2))
    return 1 - ss_res / ss_tot if ss_tot else np.nan


def decompose(units: pd.DataFrame) -> dict:
    y, w = units["support_rate"].values, units["expressed"].values
    r2_bloc = weighted_r2(y, group_pred(units, ["bloque"]), w)
    r2_a = weighted_r2(y, group_pred(units, ["party"]), w)
    r2_b = weighted_r2(y, wls_pred(units, ["party", "domain_name"]), w)
    r2_c = weighted_r2(y, group_pred(units, ["party", "domain_name"]), w)
    return {
        "n_units": int(len(units)),
        "n_scrutins": int(units["scrutin_id"].nunique()),
        "r2_bloque": round(r2_bloc, 3),
        "r2_party": round(r2_a, 3),
        "r2_party_domain": round(r2_b, 3),
        "r2_party_x_domain": round(r2_c, 3),
        "delta_party_vs_bloque": round(r2_a - r2_bloc, 3),
        "delta_domain": round(r2_c - r2_a, 3),
    }


def overall_support(units: pd.DataFrame) -> pd.DataFrame:
    g = units.assign(pour=units["support_rate"] * units["expressed"])
    agg = g.groupby("party").agg(pour=("pour", "sum"),
                                 expr=("expressed", "sum")).reset_index()
    agg["support_pct"] = (agg["pour"] / agg["expr"] * 100).round(1)
    return agg[["party", "support_pct"]]


def domain_leverage(units: pd.DataFrame) -> pd.DataFrame:
    g = (units.drop_duplicates("scrutin_id")
         .groupby("domain_name").size().rename("n_scrutins").reset_index())
    g["share_pct"] = (g["n_scrutins"] / g["n_scrutins"].sum() * 100).round(1)
    return g.sort_values("n_scrutins", ascending=False)


def leverage_by_law(dom_long: pd.DataFrame) -> pd.DataFrame:
    """Por dominio dominante: nº enmiendas, nº leyes distintas, máx % en una ley."""
    preds = pd.read_csv(AMEND_PREDS, usecols=["scrutin_id", "ley_titulo_corto"])
    ley = preds.drop_duplicates("scrutin_id")
    dom = (dom_long.sort_values("n", ascending=False)
           .drop_duplicates("scrutin_id")[["scrutin_id", "domain_name"]])
    d = dom.merge(ley, on="scrutin_id", how="left")
    rows = []
    for dname, sub in d.groupby("domain_name"):
        per_law = sub["ley_titulo_corto"].value_counts()
        n = len(sub)
        rows.append({
            "domain_name": dname,
            "n_amendments": n,
            "n_laws": int(per_law.shape[0]),
            "max_share_one_law_pct": round(float(per_law.iloc[0] / n * 100), 1),
            "top_law": str(per_law.index[0])[:45],
        })
    return pd.DataFrame(rows).sort_values("n_amendments", ascending=False)


def bootstrap_relative_support(stance: pd.DataFrame, dom_long: pd.DataFrame,
                               b: int = N_BOOT) -> pd.DataFrame:
    """
    Soporte relativo[p,d] = soporte_ponderado[p,d] - soporte_global[p], con IC95 y
    estabilidad de signo por bootstrap de clúster (remuestreo de SCRUTINS).
    """
    m = dom_long.merge(stance[["party", "scrutin_id", "support_rate"]],
                       on="scrutin_id", how="inner")
    scrutins = np.array(sorted(set(stance["scrutin_id"]) & set(dom_long["scrutin_id"])))
    idx = {s: i for i, s in enumerate(scrutins)}
    n_scr = len(scrutins)

    # tabla soporte ponderado por (party,domain)
    m = m[m["scrutin_id"].isin(scrutins)]
    m_scr = m["scrutin_id"].map(idx).to_numpy()
    pd_code, pd_uniq = pd.factorize(m["party"] + " || " + m["domain_name"])
    mn = m["n"].to_numpy(float)
    msup = m["support_rate"].to_numpy()
    n_pd = len(pd_uniq)

    # tabla soporte global por party (una fila por party-scrutin)
    st = stance[stance["scrutin_id"].isin(scrutins)]
    st_scr = st["scrutin_id"].map(idx).to_numpy()
    p_code, p_uniq = pd.factorize(st["party"])
    pour = st["Pour"].to_numpy(float)
    expr = st["expressed"].to_numpy(float)
    n_p = len(p_uniq)
    p_of_pd = np.array([list(p_uniq).index(u.split(" || ")[0]) for u in pd_uniq])

    def rel_vector(cm, cst):
        ws = (np.bincount(pd_code, weights=cm * mn * msup, minlength=n_pd) /
              np.bincount(pd_code, weights=cm * mn, minlength=n_pd)) * 100
        ov = (np.bincount(p_code, weights=cst * pour, minlength=n_p) /
              np.bincount(p_code, weights=cst * expr, minlength=n_p)) * 100
        return ws - ov[p_of_pd]

    point = rel_vector(np.ones(len(m)), np.ones(len(st)))
    boot = np.empty((b, n_pd))
    with np.errstate(invalid="ignore", divide="ignore"):
        for i in range(b):
            c = RNG.multinomial(n_scr, np.full(n_scr, 1 / n_scr)).astype(float)
            boot[i] = rel_vector(c[m_scr], c[st_scr])
    lo = np.nanpercentile(boot, 2.5, axis=0)
    hi = np.nanpercentile(boot, 97.5, axis=0)
    same_sign = np.nanmean(np.sign(boot) == np.sign(point), axis=0)

    rows = []
    for k, u in enumerate(pd_uniq):
        party, dname = u.split(" || ")
        rows.append({"party": party, "domain_name": dname,
                     "rel_pp": round(float(point[k]), 1),
                     "ci_low": round(float(lo[k]), 1),
                     "ci_high": round(float(hi[k]), 1),
                     "sign_stability": round(float(same_sign[k]), 3)})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dep2party = votes.load_deputy_party(DEP)
    corp = {c: load_corpus(p, v, dep2party) for c, (p, v) in CORPORA.items()}
    units = {c: build_units(*corp[c]) for c in corp}

    # 1) descomposición de R² (con bloque)
    decomp = {c: decompose(u) for c, u in units.items()}
    dec_df = pd.DataFrame(decomp).T.reset_index().rename(columns={"index": "corpus"})
    dec_df.to_csv(OUT / "variance_decomposition.csv", index=False)

    # 2) cross-corpus
    sup = (overall_support(units["leyes"]).rename(columns={"support_pct": "leyes"})
           .merge(overall_support(units["enmiendas"])
                  .rename(columns={"support_pct": "enmiendas"}), on="party"))
    sup.to_csv(OUT / "support_lois_vs_amend.csv", index=False)

    # 3) bootstrap por scrutin del soporte relativo (enmiendas)
    boot = bootstrap_relative_support(*corp["enmiendas"])
    boot.to_csv(OUT / "enmiendas_relative_support_ci.csv", index=False)

    # 4) leverage por dominio (conteo) y por ley
    lev = pd.concat([domain_leverage(u).assign(corpus=c)
                     for c, u in units.items()], ignore_index=True)
    lev[["corpus", "domain_name", "n_scrutins", "share_pct"]].to_csv(
        OUT / "domain_leverage.csv", index=False)
    lev_law = leverage_by_law(corp["enmiendas"][1])
    lev_law.to_csv(OUT / "domain_leverage_by_law.csv", index=False)

    # figuras
    plot_r2(decomp, OUT / "r2_decomposition.png")
    plot_support_scatter(sup, OUT / "scatter_lois_vs_amend.png")

    summary = {
        "decomposition": decomp,
        "support_lois_vs_amend": sup.set_index("party").round(1).to_dict("index"),
        "cleavage_sign_stability": boot[boot["domain_name"].isin(
            ["Fabric of Society", "Freedom & Democracy"])][
            ["party", "domain_name", "rel_pp", "ci_low", "ci_high",
             "sign_stability"]].to_dict("records"),
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    pd.set_option("display.width", 170)
    print("=== Descomposición de R² (ponderado; con modelo bloque) ===")
    print(dec_df.to_string(index=False))
    print("\n=== Soporte global por partido: leyes vs enmiendas ===")
    print(sup.sort_values("leyes", ascending=False).to_string(index=False))
    print("\n=== Bootstrap por scrutin — clivaje cultural en enmiendas (IC95, estab. signo) ===")
    key = boot[boot["domain_name"].isin(["Fabric of Society", "Freedom & Democracy"])]
    print(key.sort_values(["domain_name", "rel_pp"]).to_string(index=False))
    print("\n=== Leverage por ley (enmiendas) ===")
    print(lev_law.to_string(index=False))


def plot_r2(decomp: dict, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models = ["r2_bloque", "r2_party", "r2_party_domain", "r2_party_x_domain"]
    labels = ["bloque\n(mayoría/opo)", "partido", "partido +\ndominio",
              "partido ×\ndominio"]
    x = np.arange(len(models))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = {"leyes": "#90a4ae", "enmiendas": "#c62828"}
    for i, c in enumerate(["leyes", "enmiendas"]):
        vals = [decomp[c][m] for m in models]
        ax.bar(x + (i - 0.5) * w, vals, w, label=c, color=colors[c])
        for xi, vv in zip(x + (i - 0.5) * w, vals):
            ax.text(xi, vv + 0.01, f"{vv:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("R² ponderado (varianza del % Pour explicada)")
    ax.set_ylim(0, 1.05)
    ax.set_title("¿Qué explica el voto? Bloque, partido y tema, en leyes y enmiendas\n"
                 "en leyes el bloque ya explica casi todo; el dominio temático suma poco",
                 fontsize=10.5)
    ax.legend(title="corpus")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_support_scatter(sup: pd.DataFrame, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.scatter(sup["leyes"], sup["enmiendas"], s=80, color="#1565c0", zorder=3)
    for _, r in sup.iterrows():
        ax.annotate(r["party"], (r["leyes"], r["enmiendas"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.plot([0, 100], [100, 0], ls="--", color="#bbb", lw=1)
    ax.set_xlabel("Soporte en LEYES finales (% Pour)")
    ax.set_ylabel("Soporte en ENMIENDAS (% Pour)")
    ax.set_title("El eje se invierte: quien aprueba leyes rechaza enmiendas\n"
                 "(mayoría arriba-izq, oposición abajo-der)", fontsize=11)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
