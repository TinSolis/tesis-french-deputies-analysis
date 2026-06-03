"""
BERTopic sobre las intervenciones en el hemiciclo (XVe legislature).

CORPUS COMPLETO: 949.718 intervenciones del periodo 2017-2022. Tras los
filtros descritos abajo quedan ~508.000 documentos.

POLITICA DE FILTRADO:
  - Threshold = 10 palabras. Descarta interjecciones procedurales del
    hemiciclo ("Tres bien!", "Mme la Presidente.", "La parole est a...",
    "Je mets aux voix.") sin perder discursos sustantivos cortos.
    Retencion esperada ~54% del corpus completo (la cola corta es enorme).
  - Solo intervenciones enlazadas a un diputado de la cohorte (deputy_id no
    nulo).
  - Patrones procedurales adicionales (apertura/cierre de sesion, anuncios
    de scrutin) se filtran con regex.
  - Stop-words: HEMICYCLE_STOPWORDS para sacar vocabulario procedural
    ("monsieur le president", "madame la ministre", "applaudissements",
    "chers collegues") que el threshold de palabras no elimina.
  - Reduccion a 25 topicos finales.

ADVERTENCIA DE TIEMPO: con ~500k docs y el embedder multilingue, el
fit_transform puede tomar 2-6 horas en CPU (Mac M1/M2). En GPU es mucho
mas rapido.

Entrada: french_deputies/hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz
Salida : ./results/
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent
sys.path.insert(0, str(ROOT))
from common.bertopic_runner import run_bertopic, HEMICYCLE_STOPWORDS  # noqa: E402

DATA = (
    ROOT.parents[0]
    / "hemicycle"
    / "processed"
    / "interventions_xv_2017_2022_with_deputies.csv.gz"
)
OUT = THIS_DIR / "results"

MIN_WORDS = 10

PROCEDURAL_PATTERNS = [
    r"^la séance est ouverte",
    r"^la séance est suspendue",
    r"^la séance est reprise",
    r"^l'ordre du jour appelle",
    r"^je mets aux voix",
    r"^le scrutin est ouvert",
    r"^le scrutin est clos",
    r"^la parole est à",
]


def is_procedural(text: str) -> bool:
    if not isinstance(text, str):
        return True
    t = text.strip().lower()
    return any(re.match(p, t) for p in PROCEDURAL_PATTERNS)


def main():
    if not DATA.exists():
        print(f"ERROR: no encuentro {DATA}")
        sys.exit(1)

    print(f"Cargando intervenciones desde {DATA.name} ...")
    df = pd.read_csv(DATA, compression="gzip")
    print(f"  total: {len(df):,}")

    df = df[df["deputy_id"].notna()].copy()
    print(f"  con deputy_id: {len(df):,}")

    if "nb_mots" in df.columns:
        df = df[df["nb_mots"] >= MIN_WORDS].copy()
    else:
        df["nb_mots"] = df["intervention_plain"].fillna("").str.split().str.len()
        df = df[df["nb_mots"] >= MIN_WORDS].copy()
    print(f"  >= {MIN_WORDS} palabras: {len(df):,}")

    df = df[~df["intervention_plain"].apply(is_procedural)].reset_index(drop=True)
    print(f"  no procedurales (post-regex): {len(df):,}")

    docs = df["intervention_plain"].astype(str).tolist()
    classes = df.get("political_group_abbrev", pd.Series(["Inconnu"] * len(df))).fillna("Inconnu").tolist()

    run_bertopic(
        docs=docs,
        out_dir=OUT,
        classes=classes,
        class_label="political_group",
        min_topic_size=150,
        nr_topics="auto",
        target_nr_topics=25,
        ngram_range=(1, 2),
        min_df=50,
        extra_stopwords=HEMICYCLE_STOPWORDS,
    )


if __name__ == "__main__":
    main()
