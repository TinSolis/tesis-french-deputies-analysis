"""
Análisis 3 — Declarar y revelar: ¿los partidos votan lo que dicen?

Conecta la agenda DECLARADA (Análisis 1: de qué habla cada partido en manifiesto,
Twitter y hemiciclo) con la agenda REVELADA por el voto (Análisis 2: qué apoya
relativamente en enmiendas).

Problema central: las dos agendas NO son comparables en niveles. La declarada es
*salience* (cuánto habla de un dominio: positiva, sin dirección); la revelada es
*soporte relativo* (signada, orientada). Por eso no se restan: se comparan como
**firmas relativas entre partidos** (distintividad), y la correlación —invariante a
escala— absorbe el desajuste de unidades.

  - Firma declarada:  s_decl[p,d,c] = emphasis[p,d,c] − promedio_partidos(·,d,c)
  - Firma revelada:   s_rev[p,d]    = soporte_relativo[p,d]   (centrado por la base
                      del partido). Variante re-centrada por dominio (s_rev*) para
                      que sea distintividad entre-partidos, igual que la declarada.

Métrica: coherencia_p = corr(firma declarada, firma revelada) sobre los dominios.
OJO: con 6 dominios la correlación por partido es RUIDOSA → se reporta con IC y
junto a Spearman y a la variante re-centrada; el resultado de fondo es la
**tipología de cuadrantes** por celda (bandera real / de ataque / apoyo silencioso),
que no depende del coeficiente frágil.

Cobertura de partidos:
  - manifiesto vs voto: 7 partidos (el manifiesto se indexa por partido electoral y
    el voto por grupo parlamentario; coinciden LFI, PS, PCF, MoDem, LREM, LR, FN).
  - tweets/hemiciclo vs voto: hasta 11 (misma consolidación de grupos, FN separado
    de NI por deputy_id en ambos lados; NI queda como residuo heterogéneo).

External Relations se excluye del análisis principal (bajo leverage en el voto:
5 leyes / 16 enmiendas, ver Análisis 2).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

THIS = Path(__file__).resolve().parent
PA = THIS.parent
OUT = THIS / "results"

DECL = {
    "manifiesto": PA / "manifestos" / "results" / "party_domain_distribution.csv",
    "tweets": PA / "tweets" / "results" / "party_domain_distribution.csv",
    "hemiciclo": PA / "interventions" / "results" / "party_domain_distribution.csv",
}
REV = PA / "amendements" / "results" / "party_domain_support_relative.csv"
REV_ABS = PA / "amendements" / "results" / "party_domain_support.csv"

BAND = 1.0  # zona neutra en pp para clasificar una celda como +/- (robustez de signo)
ALIGN = {"GDR-PCF": "PCF"}  # un solo rótulo consistente en todo el análisis
DOMS7 = ["External Relations", "Freedom & Democracy", "Political System", "Economy",
         "Welfare & QoL", "Fabric of Society", "Social Groups"]
DROP = "External Relations"
DOMS = [d for d in DOMS7 if d != DROP]
SHORT = {"Freedom & Democracy": "Libertades", "Political System": "Sist.Político",
         "Economy": "Economía", "Welfare & QoL": "Bienestar",
         "Fabric of Society": "Soc/Seguridad", "Social Groups": "Grupos Soc.",
         "External Relations": "Ext.Rel"}
IDEO = ["LFI", "PCF", "PS", "EDS", "LT", "MoDem", "LREM", "UDI-Agir", "LR", "FN", "NI"]
SMALL_MANIF = {"PCF", "PS"}  # manifiestos de muestra chica
RNG = np.random.default_rng(13)


def load_wide(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["party"] = df["party"].map(lambda x: ALIGN.get(x, x))
    return df.groupby("party")[DOMS7].mean()  # por si una alineación junta filas


def coherence(a: np.ndarray, b: np.ndarray) -> tuple:
    if np.std(a) == 0 or np.std(b) == 0:
        return np.nan, np.nan
    return pearsonr(a, b)[0], spearmanr(a, b)[0]


def boot_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 2000) -> tuple:
    n = len(a)
    rs = []
    for _ in range(n_boot):
        j = RNG.integers(0, n, n)
        if np.std(a[j]) == 0 or np.std(b[j]) == 0:
            continue
        rs.append(pearsonr(a[j], b[j])[0])
    if not rs:
        return np.nan, np.nan
    return round(float(np.percentile(rs, 2.5)), 2), round(float(np.percentile(rs, 97.5)), 2)


def _sign(x: float, band: float = 0.0) -> int:
    if x > band:
        return 1
    if x < -band:
        return -1
    return 0


# Nombres metodológicos (descriptivos, no normativos). La lectura sustantiva
# (bandera real / de ataque / apoyo silencioso) va en la prosa, no acá.
TIPO = {(1, 1): "énfasis respaldado", (1, -1): "énfasis no respaldado",
        (-1, 1): "apoyo no enfatizado", (-1, -1): "baja prioridad y menor apoyo relativo"}


def tipo_celda(decl: float, rev: float, band: float = 0.0) -> str:
    sd, sr = _sign(decl, band), _sign(rev, band)
    if sd == 0 or sr == 0:
        return "neutro/intermedio"
    return TIPO[(sd, sr)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rev = load_wide(REV)             # soporte relativo (signado, vs base del partido)
    rev_abs = load_wide(REV_ABS)     # soporte absoluto (% Pour sobre votos expresados)
    # soporte global del partido = absoluto − relativo (constante por dominio salvo redondeo)
    glob = (rev_abs - rev).mean(axis=1)
    decl = {c: load_wide(p) for c, p in DECL.items()}
    common6 = sorted(set(decl["manifiesto"].index) & set(rev.index))

    coh_rows, aligned_rows, pooled_rows = [], [], []
    sig_decl_by_channel = {}  # para figuras

    for c, E in decl.items():
        parties = sorted(set(E.index) & set(rev.index))
        # firma declarada: centrar por promedio de los partidos comparables, por dominio
        Ec = E.loc[parties, DOMS7]
        s_decl = Ec.sub(Ec.mean(axis=0), axis=1)
        R = rev.loc[parties, DOMS7]
        s_rev = R                                   # centrado por base del partido
        s_rev_dc = R.sub(R.mean(axis=0), axis=1)    # re-centrado por dominio
        sig_decl_by_channel[c] = (s_decl, s_rev, parties)

        for p in parties:
            a = s_decl.loc[p, DOMS].to_numpy(float)
            b = s_rev.loc[p, DOMS].to_numpy(float)
            b2 = s_rev_dc.loc[p, DOMS].to_numpy(float)
            pe, sp = coherence(a, b)
            pe_dc, _ = coherence(a, b2)
            row = {"party": p, "channel": c,
                   "pearson": round(pe, 2) if pe == pe else np.nan,
                   "spearman": round(sp, 2) if sp == sp else np.nan,
                   "pearson_recentrado": round(pe_dc, 2) if pe_dc == pe_dc else np.nan,
                   "small_manifesto": (c == "manifiesto" and p in SMALL_MANIF)}
            if c == "manifiesto":
                lo, hi = boot_ci(a, b)
                row["ci_low"], row["ci_high"] = lo, hi
            coh_rows.append(row)

            for d in DOMS:
                sd, sr = float(s_decl.loc[p, d]), float(s_rev.loc[p, d])
                aligned_rows.append({
                    "channel": c, "party": p, "domain": d,
                    "s_decl": round(sd, 1),
                    "s_rev": round(sr, 1),
                    "soporte_abs": round(float(rev_abs.loc[p, d]), 1),
                    "soporte_global": round(float(glob.loc[p]), 1),
                    "tipo": tipo_celda(sd, sr),                 # por signo
                    "tipo_band1pp": tipo_celda(sd, sr, BAND)})  # con zona neutra ±1pp

        # pooled por canal. "todos" = todos los partidos del canal (7 en manifiesto,
        # 11 en tweets/hemiciclo); "6p" = restringido a los partidos comunes (hoy 7,
        # incluida FN) y RE-CENTRADO sobre ese set (comparación justa entre canales,
        # misma base de partidos en ambos lados). El tag "6p" es histórico; la columna
        # n_parties (=7) es la fuente de verdad del tamaño del set comparable.
        for label, dd in [("sin_ExtRel", DOMS), ("con_ExtRel", DOMS7)]:
            for pset, ptag in [(parties, "todos"), (common6, "6p")]:
                Es = E.loc[pset, dd]
                Rs = rev.loc[pset, dd]
                A = Es.sub(Es.mean(axis=0), axis=1).to_numpy(float).ravel()
                B = Rs.to_numpy(float).ravel()
                ok = ~(np.isnan(A) | np.isnan(B))
                pooled_rows.append({"channel": c, "domains": label, "partidos": ptag,
                                    "n_parties": len(pset),
                                    "pooled_pearson": round(float(pearsonr(A[ok], B[ok])[0]), 2)})

    coh = pd.DataFrame(coh_rows)
    coh.to_csv(OUT / "coherence_by_party_channel.csv", index=False)
    aligned = pd.DataFrame(aligned_rows)
    aligned.to_csv(OUT / "declared_revealed_aligned.csv", index=False)
    aligned[aligned.channel == "manifiesto"].to_csv(
        OUT / "quadrant_typology_manifesto.csv", index=False)
    pooled = pd.DataFrame(pooled_rows)
    pooled.to_csv(OUT / "pooled_coherence.csv", index=False)

    # estabilidad de signo declarado entre canales (por celda partido×dominio).
    # CAVEAT: manifiesto es otra unidad y otro período; el acuerdo de signo es
    # convergencia entre actos comunicativos distintos, no robustez muestral pura.
    stab = (aligned.assign(dpos=lambda x: x.s_decl > BAND, dneg=lambda x: x.s_decl < -BAND)
            .groupby(["party", "domain"])
            .agg(n_canales=("channel", "nunique"), decl_pos=("dpos", "sum"),
                 decl_neg=("dneg", "sum"), s_rev=("s_rev", "first"))
            .reset_index())
    stab["rev_signo"] = stab.s_rev.apply(
        lambda v: "+" if v > BAND else ("-" if v < -BAND else "0"))
    stab.to_csv(OUT / "cross_channel_sign_stability.csv", index=False)

    # figuras
    plot_quadrants(sig_decl_by_channel["manifiesto"], coh,
                   OUT / "fig_quadrants_manifiesto.png")
    plot_ranking(coh[coh.channel == "manifiesto"], OUT / "fig_coherence_ranking.png")
    plot_channel_matrix(coh, OUT / "fig_coherence_by_channel.png")

    summary = {
        "pooled_coherence": pooled.to_dict("records"),
        "manifiesto_coherence": coh[coh.channel == "manifiesto"][
            ["party", "pearson", "spearman", "pearson_recentrado",
             "ci_low", "ci_high"]].to_dict("records"),
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    pd.set_option("display.width", 170)
    print("=== Coherencia declarado–revelado (corr sobre 6 dominios, vs enmiendas) ===")
    print(coh.to_string(index=False))
    print("\n=== Coherencia pooled por canal ===")
    print(pooled.to_string(index=False))
    print("\n=== Tipología por celda — manifiesto (conteo, clasificación por signo) ===")
    print(aligned[aligned.channel == "manifiesto"]
          .groupby(["party", "tipo"]).size().rename("n").reset_index()
          .to_string(index=False))

    # robustez del umbral: ¿cuántas celdas mantienen su cuadrante con zona neutra ±1pp?
    print(f"\n=== Robustez de la tipología a umbral ±{BAND:g}pp ===")
    for scope, df in [("manifiesto", aligned[aligned.channel == "manifiesto"]),
                      ("todos los canales", aligned)]:
        same = (df.tipo == df.tipo_band1pp).mean()
        neutro = (df.tipo_band1pp == "neutro/intermedio").mean()
        flip = ((df.tipo != df.tipo_band1pp) &
                (df.tipo_band1pp != "neutro/intermedio")).mean()
        print(f"  {scope}: {same:.0%} mantienen cuadrante · "
              f"{neutro:.0%} pasan a neutro · {flip:.0%} cambian de cuadrante")


def plot_quadrants(sig, coh, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s_decl, s_rev, parties = sig
    cm = coh[coh.channel == "manifiesto"].set_index("party")
    ncols = 3
    nrows = -(-len(parties) // ncols)  # ceil: acomoda 7 partidos (FN incluida)
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 4.5 * nrows))
    axes = np.atleast_1d(axes).ravel()
    for ax in axes[len(parties):]:
        ax.axis("off")
    for ax, p in zip(axes, parties):
        x = s_decl.loc[p, DOMS].to_numpy(float)
        y = s_rev.loc[p, DOMS].to_numpy(float)
        ax.axhline(0, color="#999", lw=0.8)
        ax.axvline(0, color="#999", lw=0.8)
        ax.scatter(x, y, s=55, color="#1565c0", zorder=3)
        for xi, yi, d in zip(x, y, DOMS):
            ax.annotate(SHORT[d], (xi, yi), textcoords="offset points",
                        xytext=(4, 3), fontsize=7.5)
        r = cm.loc[p, "pearson"]
        flag = " *muestra chica" if p in SMALL_MANIF else ""
        ax.set_title(f"{p} — r={r:.2f}{flag}", fontsize=10)
        ax.set_xlabel("declarado (firma manifiesto, pp)", fontsize=8)
        ax.set_ylabel("revelado (soporte rel. enmiendas, pp)", fontsize=8)
        ax.grid(True, alpha=0.2)
    fig.suptitle("¿Votan lo que dicen? Firma declarada (manifiesto) vs revelada "
                 "(enmiendas), por dominio\narriba-der = bandera real · abajo-der = "
                 "bandera de ataque · arriba-izq = apoyo silencioso", fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_ranking(cm: pd.DataFrame, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = cm.sort_values("pearson", ascending=True)
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#b0bec5" if s else "#1565c0" for s in d["small_manifesto"]]
    err_lo = d["pearson"] - d["ci_low"]
    err_hi = d["ci_high"] - d["pearson"]
    ax.barh(y, d["pearson"], color=colors, zorder=3)
    ax.errorbar(d["pearson"], y, xerr=[err_lo, err_hi], fmt="none",
                ecolor="#37474f", capsize=3, zorder=4)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{p}{' *' if s else ''}"
                        for p, s in zip(d["party"], d["small_manifesto"])])
    ax.axvline(0, color="#999", lw=0.8)
    ax.set_xlabel("coherencia (Pearson manifiesto vs enmiendas, 6 dominios)")
    ax.set_title("Coherencia declarado–revelado por partido\n"
                 "IC95 por bootstrap de dominios (anchos: n=6) · gris = manifiesto chico",
                 fontsize=10.5)
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_channel_matrix(coh: pd.DataFrame, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    piv = coh.pivot(index="party", columns="channel", values="pearson")
    piv = piv.reindex([p for p in IDEO if p in piv.index])
    piv = piv[["manifiesto", "tweets", "hemiciclo"]]
    fig, ax = plt.subplots(figsize=(7, 0.5 * len(piv) + 2))
    im = ax.imshow(piv.values, cmap="RdBu", vmin=-0.7, vmax=0.7, aspect="auto")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["manifiesto\n(7 part.)", "tweets\n(11)", "hemiciclo\n(11)"])
    ax.set_yticks(range(len(piv)))
    ax.set_yticklabels(piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if v == v:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("¿Qué canal declarado se alinea con el voto?\ncoherencia con el "
                 "soporte relativo en enmiendas (Pearson)", fontsize=10.5)
    fig.colorbar(im, ax=ax, fraction=0.04, label="coherencia")
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
