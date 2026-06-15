"""
Analisis a nivel partido de LEYES y ENMIENDAS basado en COMO VOTAN los diputados.

A diferencia de manifiestos/tweets/hemiciclo (texto que el partido *produce*), una
ley o enmienda no tiene autor partidario: el partido revela su preferencia
*votando*. Este modulo cruza:

  - el TEXTO del scrutin (su composicion tematica MARPOR, de manifestoberta),
  - el VOTO de cada diputado (Pour/Contre/Abstention) en ese scrutin,
  - el PARTIDO de cada diputado,

para responder la pregunta central de la tesis: *¿que tipo de politicas (por tema
MARPOR) apoya o rechaza cada partido?* Es la agenda REVELADA por el voto, que puede
diferir de la agenda DECLARADA en el discurso.

Metricas por partido:
  - soporte global  : % de Pour sobre votos expresados (Pour+Contre). Gobierno vs
                      oposicion.
  - cohesion (Rice) : |Pour-Contre|/(Pour+Contre) promedio. Disciplina de voto.
  - soporte por tema: para cada dominio MARPOR, cuanto apoya el partido los textos
                      que cargan ese tema, ponderado por el contenido del texto.
  - soporte RELATIVO: soporte por tema - soporte global del partido. Revela el
                      perfil tematico neto del efecto gobierno/oposicion (que apoya
                      un partido *mas* de lo que le toca por su posicion general).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .analysis import DOMAIN_NAMES, GROUP_LABEL

MIN_EXPRESSED = 3  # min diputados del partido que expresan voto para contar el scrutin


def load_deputy_party(dep_csv: Path) -> dict:
    """deputy_id -> familia politica consolidada (GROUP_LABEL)."""
    dep = pd.read_csv(dep_csv, usecols=["id", "political_group_abbrev"])
    dep["party"] = dep["political_group_abbrev"].map(GROUP_LABEL)
    dep = dep.dropna(subset=["party"])
    return dict(zip(dep["id"], dep["party"]))


def party_stance(votes: pd.DataFrame, dep2party: dict) -> pd.DataFrame:
    """
    Por (party, scrutin): conteo de Pour/Contre y tasa de soporte entre expresados.
    Devuelve filas con expressed>=MIN_EXPRESSED.
    """
    v = votes.copy()
    v["party"] = v["deputy_id"].map(dep2party)
    v = v.dropna(subset=["party"])
    v = v[v["vote"].isin(["Pour", "Contre"])]  # solo votos expresados
    g = v.groupby(["party", "scrutin_id", "vote"]).size().unstack(fill_value=0)
    for col in ("Pour", "Contre"):
        if col not in g.columns:
            g[col] = 0
    g = g.reset_index()
    g["expressed"] = g["Pour"] + g["Contre"]
    g = g[g["expressed"] >= MIN_EXPRESSED].copy()
    g["support_rate"] = g["Pour"] / g["expressed"]
    g["rice"] = (g["Pour"] - g["Contre"]).abs() / g["expressed"]
    return g


def scrutin_domain_counts(preds: pd.DataFrame) -> pd.DataFrame:
    """Long: scrutin_id, domain(name), n (cantidad de quasi-frases en ese dominio)."""
    p = preds.dropna(subset=["domain"]).copy()
    p["domain"] = p["domain"].astype(int)
    p = p[p["domain"].between(1, 7)]
    p["domain_name"] = p["domain"].map(DOMAIN_NAMES)
    long = (p.groupby(["scrutin_id", "domain_name"]).size()
            .rename("n").reset_index())
    return long


def weighted_domain_support(stance: pd.DataFrame,
                            dom_long: pd.DataFrame) -> pd.DataFrame:
    """
    party x domain: soporte ponderado por contenido del texto.
    weighted_support[p,d] = sum_s(n_{s,d} * support_rate_{p,s}) / sum_s(n_{s,d}).
    """
    m = dom_long.merge(stance[["party", "scrutin_id", "support_rate"]],
                       on="scrutin_id", how="inner")
    m["num"] = m["n"] * m["support_rate"]
    agg = m.groupby(["party", "domain_name"]).agg(
        num=("num", "sum"), den=("n", "sum")).reset_index()
    agg["support"] = (agg["num"] / agg["den"] * 100)
    mat = agg.pivot(index="party", columns="domain_name",
                    values="support")
    for name in DOMAIN_NAMES.values():
        if name not in mat.columns:
            mat[name] = np.nan
    return mat[list(DOMAIN_NAMES.values())].round(1)


def overall_support_and_cohesion(stance: pd.DataFrame) -> pd.DataFrame:
    """Por partido: soporte global (% Pour pooled), cohesion (Rice ponderado), n."""
    rows = []
    for party, sub in stance.groupby("party"):
        pour = sub["Pour"].sum()
        contre = sub["Contre"].sum()
        overall = pour / (pour + contre) * 100 if (pour + contre) else np.nan
        rice = np.average(sub["rice"], weights=sub["expressed"])
        rows.append({"party": party,
                     "overall_support_pct": round(overall, 1),
                     "cohesion_rice": round(float(rice), 3),
                     "n_scrutins": int(sub["scrutin_id"].nunique())})
    return pd.DataFrame(rows).sort_values("overall_support_pct",
                                          ascending=False).reset_index(drop=True)


def supported_vs_opposed_agenda(stance: pd.DataFrame,
                                dom_long: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada partido, distribucion de dominios de los textos que APOYA (support>0.5)
    vs los que RECHAZA, ponderada por longitud del texto.
    """
    st = stance.copy()
    st["stance"] = np.where(st["support_rate"] > 0.5, "supported", "opposed")
    m = dom_long.merge(st[["party", "scrutin_id", "stance"]],
                       on="scrutin_id", how="inner")
    out = []
    for (party, stnc), sub in m.groupby(["party", "stance"]):
        tot = sub["n"].sum()
        dist = sub.groupby("domain_name")["n"].sum() / tot * 100
        row = {"party": party, "stance": stnc, "n_sentences": int(tot)}
        for name in DOMAIN_NAMES.values():
            row[name] = round(float(dist.get(name, 0.0)), 1)
        out.append(row)
    return pd.DataFrame(out)


def relative_support(dom_support: pd.DataFrame,
                     cohesion: pd.DataFrame) -> pd.DataFrame:
    """weighted_support[p,d] - soporte global del partido (centra el efecto gob/opo)."""
    base = cohesion.set_index("party")["overall_support_pct"]
    rel = dom_support.sub(base, axis=0)
    return rel.round(1)


def plot_domain_support_heatmap(rel: pd.DataFrame, title: str,
                                out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = rel.dropna(how="all")
    order = d.mean(axis=1).sort_values().index  # de oposicion a gobierno aprox
    d = d.loc[order]
    fig, ax = plt.subplots(figsize=(9, 0.6 * len(d) + 2.5))
    vmax = float(np.nanmax(np.abs(d.values)))
    im = ax.imshow(d.values, cmap="RdBu", aspect="auto", vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(d.shape[1]))
    ax.set_xticklabels(d.columns, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(d.shape[0]))
    ax.set_yticklabels(d.index, fontsize=9)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.0f}", ha="center", va="center", fontsize=8)
    ax.set_title(title + "\n(soporte por tema − soporte global; azul = apoya de mas)",
                 fontsize=11)
    cbar = fig.colorbar(im, ax=ax, fraction=0.025)
    cbar.set_label("pp vs soporte global del partido", fontsize=9)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_support_cohesion(cohesion: pd.DataFrame, title: str,
                          out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(cohesion["overall_support_pct"], cohesion["cohesion_rice"],
               s=80, color="#5e35b1", zorder=3)
    for _, r in cohesion.iterrows():
        ax.annotate(r["party"], (r["overall_support_pct"], r["cohesion_rice"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set_xlabel("Soporte global (% Pour sobre expresados) — oposición ◄──► gobierno")
    ax.set_ylabel("Cohesión (índice Rice) — disciplina de voto")
    ax.set_title(title, fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def run(corpus: str, preds_path: Path, votes_path: Path, dep_csv: Path,
        out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    dep2party = load_deputy_party(dep_csv)
    preds = pd.read_csv(preds_path, usecols=["scrutin_id", "domain"])
    votes = pd.read_csv(votes_path)

    stance = party_stance(votes, dep2party)
    dom_long = scrutin_domain_counts(preds)
    # solo scrutins que ademas tienen texto clasificado
    dom_long = dom_long[dom_long["scrutin_id"].isin(preds["scrutin_id"])]

    dom_support = weighted_domain_support(stance, dom_long)
    coh = overall_support_and_cohesion(
        stance[stance["scrutin_id"].isin(dom_long["scrutin_id"])])
    rel = relative_support(dom_support, coh)
    agenda = supported_vs_opposed_agenda(stance, dom_long)

    dom_support.to_csv(out_dir / "party_domain_support.csv")
    rel.to_csv(out_dir / "party_domain_support_relative.csv")
    coh.to_csv(out_dir / "party_cohesion.csv", index=False)
    agenda.to_csv(out_dir / "supported_vs_opposed_agenda.csv", index=False)

    plot_domain_support_heatmap(
        rel, f"Soporte por tema a nivel partido — {corpus}",
        out_dir / "heatmap_domain_support.png")
    plot_support_cohesion(
        coh, f"Soporte global vs cohesión de voto — {corpus}",
        out_dir / "scatter_support_cohesion.png")

    # headline: para cada partido, el tema que MAS apoya por encima de su base
    signature = {}
    for party in rel.index:
        s = rel.loc[party].dropna().sort_values(ascending=False)
        if len(s):
            signature[party] = {"most_supported_theme": s.index[0],
                                "rel_pp": round(float(s.iloc[0]), 1)}
    summary = {
        "corpus": corpus,
        "n_scrutins_with_text_and_votes": int(dom_long["scrutin_id"].nunique()),
        "n_parties": int(len(coh)),
        "most_governmental": coh.iloc[0]["party"],
        "most_oppositional": coh.iloc[-1]["party"],
        "most_cohesive": coh.sort_values("cohesion_rice").iloc[-1]["party"],
        "least_cohesive": coh.sort_values("cohesion_rice").iloc[0]["party"],
        "party_revealed_signature": signature,
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n=== {corpus}: {dom_long['scrutin_id'].nunique()} scrutins con texto+votos, "
          f"{len(coh)} partidos ===")
    print("\nSoporte global y cohesión:")
    print(coh.to_string(index=False))
    print("\nSoporte RELATIVO por tema (pp vs soporte global; >0 = apoya de más):")
    print(rel.to_string())
    print("\nTema que cada partido más apoya (relativo a su base):")
    for p, h in sorted(signature.items(), key=lambda kv: -kv[1]["rel_pp"]):
        print(f"  {p:10s} {h['most_supported_theme']:22s} (+{h['rel_pp']} pp)")
    return summary
