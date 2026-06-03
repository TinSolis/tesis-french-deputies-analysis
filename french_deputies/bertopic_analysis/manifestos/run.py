"""
BERTopic sobre las quasi-frases de los manifiestos electorales 2017 (MARPOR).

POLITICA DE FILTRADO (consistente con la tesis):
  - Sin filtro de largo: los manifiestos ya estan pre-segmentados en
    quasi-sentences por los anotadores del Manifesto Project, que es la unidad
    nativa de codificacion del esquema MARPOR. Filtrar aqui equivaldria a
    descartar texto ya validado por expertos como codificable, y ademas
    sub-representaria al PCF (39 quasi-frases en total, estilo telegrafico).

Entrada:
  french_deputies/manifestos/processed/manifesto_texts.csv       (texto)
  french_deputies/manifestos/processed/manifesto_full_texts.csv  (mapping partido)
Salida : ./results/
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent
sys.path.insert(0, str(ROOT))
from common.bertopic_runner import run_bertopic  # noqa: E402

MANIFESTOS = ROOT.parents[0] / "manifestos" / "processed"
DATA_TEXTS = MANIFESTOS / "manifesto_texts.csv"
DATA_FULL = MANIFESTOS / "manifesto_full_texts.csv"
OUT = THIS_DIR / "results"


def main():
    if not DATA_TEXTS.exists():
        print(f"ERROR: no encuentro {DATA_TEXTS}")
        sys.exit(1)

    df = pd.read_csv(DATA_TEXTS)
    print(f"Quasi-frases totales: {len(df):,}")

    df = df[df["text"].notna()].reset_index(drop=True)
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0].reset_index(drop=True)
    print(f"  no vacias: {len(df):,}")

    party_col = "manifesto_id"
    if DATA_FULL.exists():
        mp = pd.read_csv(DATA_FULL)
        if "manifesto_id" in mp.columns and "party_abbrev" in mp.columns:
            df = df.merge(mp[["manifesto_id", "party_abbrev"]], on="manifesto_id", how="left")
            party_col = "party_abbrev"

    classes = df[party_col].fillna("Inconnu").astype(str).tolist()
    docs = df["text"].tolist()

    run_bertopic(
        docs=docs,
        out_dir=OUT,
        classes=classes,
        class_label="party",
        min_topic_size=15,
        nr_topics="auto",
        target_nr_topics=25,
        ngram_range=(1, 2),
        min_df=3,
    )


if __name__ == "__main__":
    main()
