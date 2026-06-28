"""
Analisis de ENFASIS TEMATICO a nivel partido sobre las predicciones MARPOR de
manifestoberta. No mide POSICION (izquierda-derecha) sino AGENDA: de que habla
cada partido en cada corpus.

A diferencia de RILE (1-D, fragil, ciego a la direccion), trabajar con la
distribucion completa sobre los 7 dominios y las 56 categorias MARPOR es robusto:
describe el enfasis tematico observado, sin colapsarlo a un eje.

Metricas por partido:
  - distribucion sobre dominios (que grandes areas prioriza),
  - distribucion sobre categorias (top temas),
  - DISTINTIVIDAD: cuanto sobre/sub-enfatiza cada categoria respecto del promedio
    del corpus (en puntos porcentuales) -> "la firma" de cada partido,
  - CONCENTRACION de agenda: entropia normalizada de su distribucion de categorias
    (baja = monotematico; alta = agenda diversificada).

Salidas (CSV + JSON + figuras) por corpus.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .families import apply_fn_override

DOMAIN_NAMES = {
    1: "External Relations",
    2: "Freedom & Democracy",
    3: "Political System",
    4: "Economy",
    5: "Welfare & QoL",
    6: "Fabric of Society",
    7: "Social Groups",
}

# Consolidacion de GRUPOS parlamentarios (XV legislatura) -> familia politica
# legible, para tweets e interventions (que traen `political_group_abbrev`).
# Mas amplio que el mapeo CHES: conserva todas las familias con presencia real.
GROUP_LABEL = {
    "LAREM": "LREM", "LREM": "LREM",
    "DEM": "MoDem", "MODEM": "MoDem",
    "LR": "LR", "LC": "LR",
    "FI": "LFI",
    "GDR": "GDR-PCF",
    "SOC": "PS", "NG": "PS",
    "UDI_I": "UDI-Agir", "UDI-I": "UDI-Agir", "UDI-AGIR": "UDI-Agir",
    "UDI-A-I": "UDI-Agir", "AGIR-E": "UDI-Agir",
    "LT": "LT",
    "EDS": "EDS",
    "NI": "NI",
}


def load_preds(preds_path: Path, party_col: str,
               party_map: dict | None = None, min_docs: int = 0) -> pd.DataFrame:
    """Carga predicciones, normaliza el partido y filtra partidos chicos.

    Si el corpus trae `deputy_id` (tweets, intervenciones), se aplica el override
    FN por diputado DESPUES del mapeo de grupo y ANTES del filtro `min_docs`, de
    modo que `FN` se evalua con su volumen propio. En manifiestos no hay
    `deputy_id`: el override es no-op y `party_abbrev=FN` queda como `FN`.
    """
    header = pd.read_csv(preds_path, nrows=0).columns
    cols = [party_col, "top1_code", "top1_label", "domain"]
    has_dep = "deputy_id" in header
    if has_dep:
        cols.append("deputy_id")
    df = pd.read_csv(preds_path, usecols=cols)
    df = df.rename(columns={party_col: "party"})
    if party_map is not None:
        df["party"] = df["party"].map(lambda x: party_map.get(x, None))
    if has_dep:
        df = apply_fn_override(df, party_col="party", id_col="deputy_id")
    df = df[df["party"].notna()]
    df = df[df["domain"].notna()]
    df["domain"] = df["domain"].astype(int)
    df = df[df["domain"].between(1, 7)]
    if min_docs > 0:
        keep = df["party"].value_counts()
        keep = keep[keep >= min_docs].index
        df = df[df["party"].isin(keep)]
    return df


def domain_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """party x domain en % (filas suman 100)."""
    ct = pd.crosstab(df["party"], df["domain"], normalize="index") * 100
    ct = ct.rename(columns=DOMAIN_NAMES)
    for name in DOMAIN_NAMES.values():
        if name not in ct.columns:
            ct[name] = 0.0
    return ct[list(DOMAIN_NAMES.values())].round(2)


def category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """party x categoria (top1_label) en %."""
    ct = pd.crosstab(df["party"], df["top1_label"], normalize="index") * 100
    return ct.round(3)


def distinctiveness(cat_dist: pd.DataFrame, top_n: int = 6) -> pd.DataFrame:
    """
    Para cada partido, las categorias mas sobre/sub-enfatizadas respecto del
    promedio del corpus (diferencia en puntos porcentuales).
    """
    baseline = cat_dist.mean(axis=0)
    diff = cat_dist.sub(baseline, axis=1)
    rows = []
    for party in diff.index:
        s = diff.loc[party].sort_values(ascending=False)
        for cat in list(s.index[:top_n]):
            rows.append({"party": party, "category": cat, "direction": "over",
                         "party_pct": round(cat_dist.loc[party, cat], 2),
                         "corpus_pct": round(baseline[cat], 2),
                         "diff_pp": round(s[cat], 2)})
        for cat in list(s.index[-top_n:][::-1]):
            rows.append({"party": party, "category": cat, "direction": "under",
                         "party_pct": round(cat_dist.loc[party, cat], 2),
                         "corpus_pct": round(baseline[cat], 2),
                         "diff_pp": round(s[cat], 2)})
    return pd.DataFrame(rows)


def concentration(df: pd.DataFrame, cat_dist: pd.DataFrame) -> pd.DataFrame:
    """Entropia normalizada (evenness) de la agenda de categorias por partido."""
    k = cat_dist.shape[1]
    rows = []
    counts = df["party"].value_counts()
    for party in cat_dist.index:
        p = cat_dist.loc[party].values / 100.0
        p = p[p > 0]
        ent = -(p * np.log2(p)).sum()
        evenness = ent / np.log2(k) if k > 1 else 0.0
        top_dom = df[df["party"] == party]["domain"].map(DOMAIN_NAMES).mode()
        rows.append({
            "party": party,
            "n_docs": int(counts.get(party, 0)),
            "agenda_evenness": round(float(evenness), 3),
            "top_domain": top_dom.iloc[0] if len(top_dom) else None,
        })
    return pd.DataFrame(rows).sort_values("agenda_evenness").reset_index(drop=True)


def plot_domain_heatmap(dom: pd.DataFrame, title: str, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = dom.copy()
    fig, ax = plt.subplots(figsize=(9, 0.6 * len(d) + 2.5))
    im = ax.imshow(d.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(d.shape[1]))
    ax.set_xticklabels(d.columns, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(d.shape[0]))
    ax.set_yticklabels(d.index, fontsize=9)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    color="black" if v < d.values.max() * 0.6 else "white",
                    fontsize=8)
    ax.set_title(title, fontsize=11)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025)
    cbar.set_label("% de quasi-frases", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_signature_heatmap(cat_dist: pd.DataFrame, title: str, out_png: Path,
                           n_cats: int = 16) -> None:
    """Heatmap de las categorias mas DISCRIMINANTES (mayor varianza entre partidos)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    var = cat_dist.var(axis=0).sort_values(ascending=False)
    cats = list(var.index[:n_cats])
    d = cat_dist[cats]
    # z-score por categoria (columna) para resaltar quien sobresale
    z = (d - d.mean(axis=0)) / d.std(axis=0).replace(0, 1)
    fig, ax = plt.subplots(figsize=(0.55 * len(cats) + 4, 0.55 * len(d) + 3))
    im = ax.imshow(z.values, cmap="RdBu_r", aspect="auto", vmin=-2, vmax=2)
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([c[:28] for c in cats], rotation=55, ha="right", fontsize=8)
    ax.set_yticks(range(len(d.index)))
    ax.set_yticklabels(d.index, fontsize=9)
    ax.set_title(title + "\n(z-score por categoria; rojo = sobre-enfatiza)",
                 fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.025)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def run(corpus: str, preds_path: Path, party_col: str, out_dir: Path,
        party_map: dict | None = None, min_docs: int = 0) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load_preds(preds_path, party_col, party_map, min_docs)

    dom = domain_distribution(df)
    cat = category_distribution(df)
    dist = distinctiveness(cat)
    conc = concentration(df, cat)

    dom.to_csv(out_dir / "party_domain_distribution.csv")
    cat.round(3).to_csv(out_dir / "party_category_distribution.csv")
    dist.to_csv(out_dir / "distinctive_categories.csv", index=False)
    conc.to_csv(out_dir / "agenda_concentration.csv", index=False)

    plot_domain_heatmap(
        dom, f"Enfasis por dominio MARPOR a nivel partido — {corpus}",
        out_dir / "heatmap_party_domain.png")
    plot_signature_heatmap(
        cat, f"Firma tematica por partido — {corpus}",
        out_dir / "heatmap_party_signature.png")

    # headline por partido: su categoria mas distintiva (over)
    over = dist[dist["direction"] == "over"].sort_values(
        "diff_pp", ascending=False).drop_duplicates("party")
    headline = {r["party"]: {"top_distinctive": r["category"],
                             "diff_pp": r["diff_pp"]}
                for _, r in over.iterrows()}
    summary = {
        "corpus": corpus,
        "n_docs": int(len(df)),
        "n_parties": int(df["party"].nunique()),
        "parties": sorted(df["party"].unique().tolist()),
        "most_monothematic": conc.iloc[0]["party"],
        "most_diversified": conc.iloc[-1]["party"],
        "party_signature": headline,
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # consola
    print(f"\n=== {corpus}: {len(df):,} quasi-frases, "
          f"{df['party'].nunique()} partidos ===")
    print("\nEnfasis por dominio (%):")
    print(dom.to_string())
    print("\nConcentracion de agenda (evenness; bajo=monotematico):")
    print(conc.to_string(index=False))
    print("\nCategoria mas distintiva por partido:")
    for p, h in sorted(headline.items(), key=lambda kv: -kv[1]["diff_pp"]):
        print(f"  {p:10s} {h['top_distinctive'][:40]:40s} (+{h['diff_pp']} pp)")
    return summary
