"""
Clasifica tweets de la cohorte de diputados (XVe legislatura) con manifestoberta.

NOTA: ~232k tweets. En Apple Silicon (MPS) toma ~1-3 horas.
Para una primera pasada se puede setear MAX_DOCS para muestrear.
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

DATA = ROOT.parents[0] / "twitter_zeeschuimer" / "processed" / "tweets_text_only.csv"
OUT = THIS / "results"

MIN_WORDS = 10
MAX_DOCS = int(os.environ.get("MAX_DOCS", "0"))  # 0 = todos


def clean_tweet(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    df = pd.read_csv(DATA)
    print(f"tweets: {len(df):,}")
    df["clean_text"] = df["text"].apply(clean_tweet)
    df["nw"] = df["clean_text"].str.split().str.len()
    df = df[df["nw"] >= MIN_WORDS].reset_index(drop=True)
    print(f"  clean >= {MIN_WORDS} palabras: {len(df):,}")

    if MAX_DOCS and len(df) > MAX_DOCS:
        df = df.sample(MAX_DOCS, random_state=42).reset_index(drop=True)
        print(f"  muestreado a MAX_DOCS={MAX_DOCS:,}")

    classify_dataframe(
        df=df,
        text_col="clean_text",
        out_dir=OUT,
        extra_cols=["deputy_id", "full_name", "political_group_abbrev"],
        batch_size=32,  # tweets cortos: podemos batch mas grande
    )


if __name__ == "__main__":
    main()
