"""
Clasifica intervenciones del hemiciclo (XVe legislatura) con manifestoberta.

NOTA: ~140k intervenciones sustantivas. En Apple Silicon (MPS) toma
~1-2 horas. Para una primera pasada usar MAX_DOCS para muestrear.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd

THIS = Path(__file__).resolve().parent
ROOT = THIS.parent
sys.path.insert(0, str(ROOT))
from common.classifier_runner import classify_dataframe  # noqa: E402

DATA = (
    ROOT.parents[0] / "hemicycle" / "processed" / "interventions_xv_2017_2022_with_deputies.csv.gz"
)
OUT = THIS / "results"

MIN_WORDS = 10
MAX_DOCS = int(os.environ.get("MAX_DOCS", "0"))


PROCEDURAL = [
    r"^la séance est ouverte",
    r"^la séance est suspendue",
    r"^la séance est reprise",
    r"^l'ordre du jour appelle",
    r"^je mets aux voix",
    r"^le scrutin est ouvert",
    r"^le scrutin est clos",
    r"^la parole est à",
]


def is_procedural(t: str) -> bool:
    if not isinstance(t, str):
        return True
    t = t.strip().lower()
    return any(re.match(p, t) for p in PROCEDURAL)


def main():
    df = pd.read_csv(DATA, compression="gzip", low_memory=False)
    print(f"intervenciones: {len(df):,}")
    df = df[df["deputy_id"].notna()].copy()
    if "nb_mots" not in df.columns:
        df["nb_mots"] = df["intervention_plain"].fillna("").str.split().str.len()
    df = df[df["nb_mots"] >= MIN_WORDS].copy()
    df = df[~df["intervention_plain"].apply(is_procedural)].reset_index(drop=True)
    print(f"  sustantivas: {len(df):,}")

    if MAX_DOCS and len(df) > MAX_DOCS:
        df = df.sample(MAX_DOCS, random_state=42).reset_index(drop=True)
        print(f"  muestreado a MAX_DOCS={MAX_DOCS:,}")

    extras = [c for c in ["deputy_id", "deputy_full_name", "political_group_abbrev", "date"] if c in df.columns]

    classify_dataframe(
        df=df,
        text_col="intervention_plain",
        out_dir=OUT,
        extra_cols=extras,
        batch_size=16,
    )


if __name__ == "__main__":
    main()
