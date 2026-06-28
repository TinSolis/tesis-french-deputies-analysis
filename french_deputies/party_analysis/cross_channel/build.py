"""
Compara la AGENDA DECLARADA de cada partido entre los 3 canales que el partido
*produce*: manifiestos, tweets y hemiciclo. Responde: ¿un partido habla igual en
un programa, en Twitter y en el Parlamento?

Trabaja sobre los 7 partidos presentes en los tres canales:
  LFI, PS, PCF (=GDR-PCF en hemiciclo/tweets), MoDem, LREM, LR, FN.
  (FN entra como familia analitica via override por deputy_id en tweets/hemiciclo
  y via party_abbrev en el manifiesto; ver common/families.py.)

Mide dos cosas distintas:
  - SHIFT BRUTO: cuánto cambia la mezcla temática total del partido entre canales.
    Confunde la estrategia del partido con el efecto estructural del canal (todos
    van a Political System en tweets/hemiciclo).
  - SHIFT ESPECÍFICO: cuánto cambia la *firma relativa* del partido (su desviación
    respecto del promedio del canal). Descuenta el efecto canal -> aísla estrategia.
  Ambos como distancia euclídea media (en pp) entre canales, con IC bootstrap.

Y formaliza la "firma persistente":
  - PERSISTENCIA (Opción A): correlación de los vectores-firma (categorías centradas
    por el promedio del canal) entre pares de canales. Alta = sobre-enfatiza temas
    parecidos en distintos canales.
  - OVERLAP (Opción B): categorías que reaparecen en el top-firma de >=2 canales.

Salidas en cross_channel/results/.
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

THIS = Path(__file__).resolve().parent
PA = THIS.parent
sys.path.insert(0, str(PA))
from common.analysis import DOMAIN_NAMES, GROUP_LABEL  # noqa: E402
from common.families import apply_fn_override  # noqa: E402

REPO = PA.parent.parent
OUT = THIS / "results"
MB = REPO / "french_deputies" / "manifestoberta_analysis"

CHANNELS = {  # canal -> (predictions, columna de partido)
    "manifiesto": (MB / "manifestos" / "results" / "predictions.csv", "party_abbrev"),
    "tweets": (MB / "tweets" / "results" / "predictions.csv", "political_group_abbrev"),
    "hemiciclo": (MB / "interventions" / "results" / "predictions.csv",
                  "political_group_abbrev"),
}
ALIGN = {"GDR-PCF": "PCF"}  # alinear etiquetas entre corpus
# Partidos presentes en los TRES canales que el partido produce (manifiesto,
# tweets, hemiciclo). FN entra como familia normal: manifiesto via party_abbrev,
# tweets/hemiciclo via override por deputy_id.
COMMON = ["LFI", "PS", "PCF", "MoDem", "LREM", "LR", "FN"]
DOMAINS = list(DOMAIN_NAMES.values())
TOP_K = 6           # categorias por canal para el overlap
N_BOOT = 2000
RNG = np.random.default_rng(7)


def load_channel(path: Path, party_col: str) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0).columns
    cols = [party_col, "top1_label", "domain"]
    has_dep = "deputy_id" in header
    if has_dep:
        cols.append("deputy_id")
    df = pd.read_csv(path, usecols=cols)
    df = df.rename(columns={party_col: "party"})
    if party_col != "party_abbrev":
        df["party"] = df["party"].map(GROUP_LABEL)
    if has_dep:
        df = apply_fn_override(df, party_col="party", id_col="deputy_id")
    df["party"] = df["party"].map(lambda x: ALIGN.get(x, x))
    df = df[df["party"].isin(COMMON)]
    df = df[df["domain"].notna()]
    df["domain"] = df["domain"].astype(int)
    df = df[df["domain"].between(1, 7)]
    df["domain_name"] = df["domain"].map(DOMAIN_NAMES)
    return df


def euclid_mean_pairwise(vectors: dict) -> float:
    keys = list(vectors)
    ds = [float(np.linalg.norm(vectors[a] - vectors[b]))
          for a, b in combinations(keys, 2)]
    return float(np.mean(ds))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {ch: load_channel(p, col) for ch, (p, col) in CHANNELS.items()}

    # === distribucion de DOMINIOS por (partido, canal) ===
    dom_counts = {}   # (party,channel) -> np.array(7) de conteos
    dom_n = {}        # (party,channel) -> n
    dom_pct = {}      # (party,channel) -> np.array(7) en %
    for ch, df in data.items():
        for party in COMMON:
            sub = df[df["party"] == party]
            counts = np.array([(sub["domain_name"] == d).sum() for d in DOMAINS],
                              dtype=float)
            dom_counts[(party, ch)] = counts
            dom_n[(party, ch)] = counts.sum()
            dom_pct[(party, ch)] = counts / counts.sum() * 100 if counts.sum() else counts

    # tabla larga para heatmap / csv
    long_rows = []
    for (party, ch), v in dom_pct.items():
        for d, val in zip(DOMAINS, v):
            long_rows.append({"party": party, "channel": ch, "domain": d,
                              "pct": round(float(val), 2)})
    long = pd.DataFrame(long_rows)
    long.to_csv(OUT / "domain_by_party_channel.csv", index=False)
    wide = long.pivot_table(index=["party", "channel"], columns="domain",
                            values="pct")[DOMAINS]

    # === shift BRUTO y ESPECIFICO (euclidiano, pp) + bootstrap ===
    def shifts_from_pct(pct: dict) -> tuple[dict, dict]:
        chans = list(CHANNELS)
        chan_mean = {ch: np.mean([pct[(p, ch)] for p in COMMON], axis=0)
                     for ch in chans}
        gross, spec = {}, {}
        for p in COMMON:
            raw = {ch: pct[(p, ch)] for ch in chans}
            cen = {ch: pct[(p, ch)] - chan_mean[ch] for ch in chans}
            gross[p] = euclid_mean_pairwise(raw)
            spec[p] = euclid_mean_pairwise(cen)
        return gross, spec

    gross, spec = shifts_from_pct(dom_pct)

    # bootstrap: remuestreo multinomial de los conteos por (partido,canal)
    boot_gross = {p: [] for p in COMMON}
    boot_spec = {p: [] for p in COMMON}
    for _ in range(N_BOOT):
        pct_b = {}
        for (party, ch), counts in dom_counts.items():
            n = int(dom_n[(party, ch)])
            phat = counts / counts.sum()
            draw = RNG.multinomial(n, phat).astype(float)
            pct_b[(party, ch)] = draw / n * 100
        g_b, s_b = shifts_from_pct(pct_b)
        for p in COMMON:
            boot_gross[p].append(g_b[p])
            boot_spec[p].append(s_b[p])

    def ci(vals):
        lo, hi = np.percentile(vals, [2.5, 97.5])
        return round(float(lo), 1), round(float(hi), 1)

    shift_rows = []
    for p in COMMON:
        doms = {ch: DOMAINS[int(np.argmax(dom_pct[(p, ch)]))] for ch in CHANNELS}
        g_lo, g_hi = ci(boot_gross[p])
        s_lo, s_hi = ci(boot_spec[p])
        shift_rows.append({
            "party": p,
            "gross_shift": round(gross[p], 1),
            "gross_ci": f"[{g_lo}, {g_hi}]",
            "party_specific_shift": round(spec[p], 1),
            "specific_ci": f"[{s_lo}, {s_hi}]",
            "channel_effect": round(gross[p] - spec[p], 1),
            "dom_manifiesto": doms["manifiesto"],
            "dom_tweets": doms["tweets"],
            "dom_hemiciclo": doms["hemiciclo"],
        })
    shift = pd.DataFrame(shift_rows).sort_values("party_specific_shift",
                                                 ascending=False)
    shift.to_csv(OUT / "agenda_shift.csv", index=False)

    # === firma a nivel CATEGORIA (centrada por promedio de canal, 7 partidos) ===
    cats = sorted(set().union(*[set(df["top1_label"].unique())
                                for df in data.values()]))
    cat_pct = {}  # (party,channel) -> Series sobre `cats`
    for ch, df in data.items():
        for party in COMMON:
            sub = df[df["party"] == party]
            vc = sub["top1_label"].value_counts(normalize=True) * 100
            cat_pct[(party, ch)] = vc.reindex(cats).fillna(0.0)
    # firma = pct - promedio del canal (sobre los 7 partidos)
    chan_cat_mean = {ch: pd.concat([cat_pct[(p, ch)] for p in COMMON], axis=1)
                     .mean(axis=1) for ch in CHANNELS}
    sig = {(p, ch): cat_pct[(p, ch)] - chan_cat_mean[ch]
           for p in COMMON for ch in CHANNELS}

    # === PERSISTENCIA (Opción A): correlacion de firmas entre canales ===
    pers_rows = []
    pairs = list(combinations(CHANNELS, 2))
    for p in COMMON:
        corrs = {}
        for a, b in pairs:
            corrs[f"corr_{a[:3]}_{b[:3]}"] = round(
                float(np.corrcoef(sig[(p, a)], sig[(p, b)])[0, 1]), 3)
        mean_corr = round(float(np.mean(list(corrs.values()))), 3)
        pers_rows.append({"party": p, **corrs, "mean_corr": mean_corr})
    persistence = pd.DataFrame(pers_rows).sort_values("mean_corr", ascending=False)
    persistence.to_csv(OUT / "signature_persistence.csv", index=False)

    # === OVERLAP (Opción B): top categorias-firma que reaparecen entre canales ===
    top_by = {(p, ch): set(sig[(p, ch)].sort_values(ascending=False).head(TOP_K).index)
              for p in COMMON for ch in CHANNELS}
    ov_rows = []
    for p in COMMON:
        from collections import Counter
        cnt = Counter()
        for ch in CHANNELS:
            for c in top_by[(p, ch)]:
                cnt[c] += 1
        repeated = sorted([c for c, k in cnt.items() if k >= 2],
                          key=lambda c: -cnt[c])
        ov_rows.append({"party": p, "n_repeated": len(repeated),
                        "categories_repeated": "; ".join(
                            f"{c.split(' - ')[0]} ({cnt[c]}x)" for c in repeated)})
    pd.DataFrame(ov_rows).to_csv(OUT / "signature_overlap.csv", index=False)

    # top distintivas por canal (para el texto), desde la firma centrada
    dist_rows = []
    for p in COMMON:
        for ch in CHANNELS:
            for c in sig[(p, ch)].sort_values(ascending=False).head(4).index:
                dist_rows.append({"party": p, "channel": ch, "category": c,
                                  "signature_pp": round(float(sig[(p, ch)][c]), 2)})
    pd.DataFrame(dist_rows).to_csv(OUT / "top_distinctive_by_channel.csv",
                                   index=False)

    # === figuras ===
    plot_heatmap(wide, OUT / "heatmap_party_channel_domain.png")
    plot_shift_bars(shift, OUT / "shift_gross_vs_specific.png")

    # === consola ===
    pd.set_option("display.width", 170)
    print("=== Shift BRUTO vs ESPECÍFICO (euclídeo, pp; IC bootstrap 95%) ===")
    print(shift[["party", "gross_shift", "gross_ci", "party_specific_shift",
                 "specific_ci", "channel_effect"]].to_string(index=False))
    print("\n=== Persistencia de firma (correlación entre canales) ===")
    print(persistence.to_string(index=False))
    print("\n=== Overlap de categorías-firma (reaparecen en >=2 canales) ===")
    print(pd.read_csv(OUT / "signature_overlap.csv").to_string(index=False))


def plot_heatmap(wide: pd.DataFrame, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = [(p, ch) for p in COMMON for ch in ["manifiesto", "tweets", "hemiciclo"]
             if (p, ch) in wide.index]
    d = wide.loc[order]
    labels = [f"{p} · {c}" for p, c in d.index]
    fig, ax = plt.subplots(figsize=(10, 0.42 * len(d) + 2))
    im = ax.imshow(d.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=45)
    ax.set_xticks(range(len(DOMAINS)))
    ax.set_xticklabels(DOMAINS, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    color="black" if v < 27 else "white", fontsize=7)
    for k in range(3, len(d), 3):
        ax.axhline(k - 0.5, color="#37474f", lw=1.2)
    ax.set_title("¿Habla igual cada partido en su programa, en Twitter y en el "
                 "hemiciclo?\nÉnfasis por dominio MARPOR (% de quasi-frases)",
                 fontsize=11)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025)
    cbar.set_label("%", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_shift_bars(shift: pd.DataFrame, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = shift.sort_values("gross_shift", ascending=False)
    x = np.arange(len(d))
    w = 0.38
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - w / 2, d["gross_shift"], w, label="bruto (incluye efecto canal)",
           color="#b0bec5")
    ax.bar(x + w / 2, d["party_specific_shift"], w,
           label="específico del partido (firma centrada)", color="#1565c0")
    ax.set_xticks(x)
    ax.set_xticklabels(d["party"])
    ax.set_ylabel("distancia entre canales (pp, euclídea)")
    ax.set_title("Cuánto cambia la agenda de cada partido entre canales\n"
                 "bruto vs. neto del efecto estructural del canal", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
