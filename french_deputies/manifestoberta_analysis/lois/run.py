"""
Clasifica leyes promulgadas (texto JORF) partidas en parrafos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

THIS = Path(__file__).resolve().parent
ROOT = THIS.parent
sys.path.insert(0, str(ROOT))
from common.classifier_runner import classify_dataframe  # noqa: E402

DATA = (
    ROOT.parents[0]
    / "lois_votes"
    / "votes_rd"
    / "processed"
    / "leyes_texto_oficial.csv"
)
OUT = THIS / "results"

MIN_WORDS = 10


def split_paragraphs(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    parts = re.split(r"\n{2,}|\r\n{2,}", text)
    if len(parts) == 1:
        parts = re.split(r"\n", text)
    return [p.strip() for p in parts if p.strip()]


def main():
    df = pd.read_csv(DATA)
    print(f"leyes: {len(df):,}")
    if "texto_confianza" in df.columns:
        df = df[df["texto_confianza"] == "alta"].copy()
    df = df[df["texto_oficial"].notna() & (df["texto_oficial"].astype(str).str.len() > 0)].copy()
    print(f"  con texto alta: {len(df):,}")

    rows = []
    for _, r in df.iterrows():
        for p in split_paragraphs(str(r["texto_oficial"])):
            if len(p.split()) >= MIN_WORDS:
                rows.append({
                    "scrutin_id": r.get("scrutin_id", ""),
                    "dossier_uid": r.get("dossier_uid", ""),
                    "nor_jo": r.get("nor_jo", ""),
                    "paragraph": p,
                })
    paragraphs = pd.DataFrame(rows)
    print(f"  parrafos >= {MIN_WORDS} palabras: {len(paragraphs):,}")

    classify_dataframe(
        df=paragraphs,
        text_col="paragraph",
        out_dir=OUT,
        extra_cols=["scrutin_id", "dossier_uid", "nor_jo"],
        batch_size=16,
    )


if __name__ == "__main__":
    main()
