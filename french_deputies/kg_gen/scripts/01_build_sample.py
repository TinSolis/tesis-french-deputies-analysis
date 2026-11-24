"""
Construcción del subset acotado para el demo de KG-Gen.

Criterio:
  - Debate emblemático: "renforcement du dialogue social"
    (Ordonnances Macron sobre el Code du travail, julio-agosto 2017)
  - Filtro: 60 <= nb_mots <= 400  (ni muy corto ni muy largo)
  - Estratificación: ~6 intervenciones por grupo político principal
  - Output: ~24 intervenciones representativas de 4-5 grupos
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "hemicycle" / "processed" / "interventions_xv_sample5000.csv"
DST = ROOT / "data" / "sample_interventions.csv"

DEBATE_PREFIX = "renforcement du dialogue social"
GROUPS = ["LAREM", "FI", "GDR", "LR", "NG"]
PER_GROUP = 6
MIN_WORDS, MAX_WORDS = 60, 400

df = pd.read_csv(SRC)
df = df.dropna(subset=["intervention_plain", "political_group_abbrev",
                       "deputy_full_name", "section"])
df = df[df["section"].str.startswith(DEBATE_PREFIX, na=False)]
df = df[(df["nb_mots"] >= MIN_WORDS) & (df["nb_mots"] <= MAX_WORDS)]

parts = []
for g in GROUPS:
    sub = df[df["political_group_abbrev"] == g].copy()
    sub = sub.sort_values("nb_mots").reset_index(drop=True)
    if len(sub) == 0:
        continue
    idxs = [int(i) for i in [
        0, len(sub) // 4, len(sub) // 2,
        3 * len(sub) // 4, len(sub) - 1
    ]]
    pick = sub.iloc[idxs[:PER_GROUP]].head(PER_GROUP)
    parts.append(pick)

sample = pd.concat(parts, ignore_index=True)
sample = sample[["intervention_id", "date", "section",
                 "deputy_full_name", "political_group_abbrev",
                 "nb_mots", "intervention_plain"]]
sample.to_csv(DST, index=False)

print(f"Sample construido: {len(sample)} intervenciones -> {DST.relative_to(ROOT.parent)}")
print(f"Palabras totales: {int(sample['nb_mots'].sum())}")
print(f"Palabras promedio: {sample['nb_mots'].mean():.0f}")
print(f"Grupos: {sample['political_group_abbrev'].value_counts().to_dict()}")
