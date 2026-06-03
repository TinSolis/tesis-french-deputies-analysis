"""
BERTopic sobre los tweets de los diputados (XVe legislature).

POLITICA DE FILTRADO:
  - Threshold = 10 palabras (sobre el texto limpio). Descarta tweets puro-link,
    emoji-only o reactivos cortos ("merci!", "+1") sin sacrificar contenido
    sustantivo. Retencion esperada ~93%.
  - Stop-words: TWITTER_STOPWORDS para sacar ruido web (urls, "rt", "via",
    nombres de plataformas) que sobrevive al regex de limpieza.
  - Reduccion a 25 topicos finales.

Entrada: french_deputies/twitter_zeeschuimer/processed/tweets_text_only.csv
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
from common.bertopic_runner import run_bertopic, TWITTER_STOPWORDS  # noqa: E402

DATA = ROOT.parents[0] / "twitter_zeeschuimer" / "processed" / "tweets_text_only.csv"
OUT = THIS_DIR / "results"

MIN_WORDS = 10


def clean_tweet(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^\w\sàâäéèêëïîôùûüÿçœæ-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    if not DATA.exists():
        print(f"ERROR: no encuentro {DATA}")
        sys.exit(1)

    print(f"Cargando tweets desde {DATA.name} ...")
    df = pd.read_csv(DATA)
    print(f"  total: {len(df):,}")

    df["clean_text"] = df["text"].apply(clean_tweet)
    df["nw"] = df["clean_text"].str.split().str.len()
    df = df[df["nw"] >= MIN_WORDS].reset_index(drop=True)
    print(f"  >= {MIN_WORDS} palabras: {len(df):,}")

    classes = df["political_group_abbrev"].fillna("Inconnu").tolist()
    docs = df["clean_text"].tolist()

    run_bertopic(
        docs=docs,
        out_dir=OUT,
        classes=classes,
        class_label="political_group",
        min_topic_size=100,
        nr_topics="auto",
        target_nr_topics=25,
        ngram_range=(1, 2),
        min_df=30,
        extra_stopwords=TWITTER_STOPWORDS,
    )


if __name__ == "__main__":
    main()
