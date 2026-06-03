"""
Análisis exploratorio de los 102 triples extraídos sobre el subset.
Produce:
  - Estadísticas básicas (entidades únicas, predicados únicos)
  - Top entidades y predicados
  - Distribución por grupo político
  - Visualización del grafo (PNG)
"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
TRIPLES = ROOT / "results" / "triples.csv"
STATS_OUT = ROOT / "results" / "stats.json"
GRAPH_PNG = ROOT / "results" / "graph.png"

GROUP_COLORS = {
    "LAREM": "#FFD700",  # amarillo
    "FI": "#B5152F",     # rojo
    "GDR": "#900000",    # rojo oscuro
    "LR": "#0066CC",     # azul
    "NG": "#FF8000",     # naranja
}


def main() -> None:
    df = pd.read_csv(TRIPLES)
    print(f"Triples cargados: {len(df)}")

    def norm(x: str) -> str:
        return str(x).strip().lower()

    df["s_n"] = df["s"].apply(norm)
    df["p_n"] = df["p"].apply(norm)
    df["o_n"] = df["o"].apply(norm)

    entities = Counter()
    for s in df["s_n"]:
        entities[s] += 1
    for o in df["o_n"]:
        entities[o] += 1
    predicates = Counter(df["p_n"])

    by_group = df.groupby("group").size().to_dict()

    triples_per_doc = (df.groupby("intervention_id").size().describe()
                       .round(2).to_dict())

    stats = {
        "n_triples": len(df),
        "n_intervenciones_con_triples": df["intervention_id"].nunique(),
        "n_entidades_unicas": len(entities),
        "n_predicados_unicos": len(predicates),
        "triples_por_doc": triples_per_doc,
        "top_20_entidades": entities.most_common(20),
        "top_20_predicados": predicates.most_common(20),
        "triples_por_grupo": by_group,
    }
    with open(STATS_OUT, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print("ESTADÍSTICAS")
    print("=" * 60)
    print(f"Triples:                {len(df)}")
    print(f"Intervenciones con triples: {df['intervention_id'].nunique()}/25")
    print(f"Entidades únicas:       {len(entities)}")
    print(f"Predicados únicos:      {len(predicates)}")
    print()
    print("TOP 10 ENTIDADES (por frecuencia):")
    for ent, n in entities.most_common(10):
        print(f"   {n:>3}  {ent}")
    print()
    print("TOP 10 PREDICADOS:")
    for pred, n in predicates.most_common(10):
        print(f"   {n:>3}  {pred}")
    print()
    print("TRIPLES POR GRUPO POLÍTICO:")
    for g, n in sorted(by_group.items(), key=lambda x: -x[1]):
        print(f"   {g:<6} {n}")

    G = nx.MultiDiGraph()
    top_entities = {e for e, _ in entities.most_common(40)}
    for _, r in df.iterrows():
        s, p, o = r["s_n"], r["p_n"], r["o_n"]
        if s in top_entities and o in top_entities:
            G.add_edge(s, o, label=p, group=r["group"])

    if len(G) == 0:
        print("\n(Grafo demasiado disperso: no hay ejes entre top-40 entidades)")
        for _, r in df.head(60).iterrows():
            G.add_edge(r["s_n"], r["o_n"], label=r["p_n"], group=r["group"])

    print(f"\nGrafo: {G.number_of_nodes()} nodos, {G.number_of_edges()} ejes")

    fig, ax = plt.subplots(figsize=(14, 10))
    pos = nx.spring_layout(G, k=1.2, iterations=70, seed=42)
    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_size=400, node_color="#cfd8dc",
        edgecolors="#37474f", linewidths=0.5,
    )
    for group, color in GROUP_COLORS.items():
        edges = [(u, v) for u, v, d in G.edges(data=True)
                 if d.get("group") == group]
        if edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=edges, ax=ax,
                edge_color=color, alpha=0.55, width=1.0,
                arrows=True, arrowsize=8,
            )
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7)
    handles = [plt.Line2D([0], [0], color=c, lw=2, label=g)
               for g, c in GROUP_COLORS.items()]
    ax.legend(handles=handles, loc="lower left", fontsize=9,
              title="Color del eje = grupo del orador")
    ax.set_title(
        "Grafo de conocimiento exploratorio: 25 intervenciones del debate\n"
        "« renforcement du dialogue social » (Ordonnances Macron, 2017)\n"
        f"qwen2.5:3b local | 102 triples | 5 grupos políticos",
        fontsize=11,
    )
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(GRAPH_PNG, dpi=140, bbox_inches="tight")
    print(f"\nGrafo guardado: {GRAPH_PNG.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
