"""
BERTopic sobre el texto promulgado de las leyes (XVe legislature).

Cada ley es un texto largo (cientos o miles de palabras); para que BERTopic
descubra topicos significativos los partimos en parrafos. Cada parrafo
preserva el dossier y el scrutin de origen para poder agregar despues.

POLITICA DE FILTRADO:
  - Threshold = 10 palabras por parrafo (no por caracteres). Descarta
    encabezados, referencias y fragmentos de tabla sin contenido.
  - Solo se usan leyes con `texto_confianza == "alta"` (filtro pre-existente).
  - Stop-words legales: aplica el conjunto LEGAL_STOPWORDS para evitar el
    cluster gigantesco dominado por vocabulario procedural (`decret`,
    `modalites`, `ainsi redige`, `alinea`, `insere`, etc.). En la corrida
    anterior, sin estos stop-words, un solo topico procedural absorbia el
    56% del corpus.
  - Reduccion a 25 topicos finales (de los ~60 que BERTopic propone) para
    una version mas limpia e interpretable.

Entrada: french_deputies/lois_votes/votes_rd/processed/leyes_texto_oficial.csv
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
from common.bertopic_runner import run_bertopic, LEGAL_STOPWORDS  # noqa: E402

DATA = (
    ROOT.parents[0]
    / "lois_votes"
    / "votes_rd"
    / "processed"
    / "leyes_texto_oficial.csv"
)
OUT = THIS_DIR / "results"

MIN_WORDS = 10
ONLY_HIGH_CONFIDENCE = True


def split_paragraphs(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    parts = re.split(r"\n{2,}|\r\n{2,}", text)
    if len(parts) == 1:
        parts = re.split(r"\n", text)
    return [p.strip() for p in parts if p.strip()]


def main():
    if not DATA.exists():
        print(f"ERROR: no encuentro {DATA}")
        sys.exit(1)

    print(f"Cargando {DATA.name} ...")
    df = pd.read_csv(DATA)
    print(f"  scrutins (filas): {len(df):,}")

    if ONLY_HIGH_CONFIDENCE and "texto_confianza" in df.columns:
        df = df[df["texto_confianza"] == "alta"].copy()
        print(f"  confianza alta: {len(df):,}")

    df = df[df["texto_oficial"].notna() & (df["texto_oficial"].astype(str).str.len() > 0)].copy()
    print(f"  con texto: {len(df):,}")

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
    print(f"  parrafos retenidos (>= {MIN_WORDS} palabras): {len(paragraphs):,}")

    classes = paragraphs["dossier_uid"].fillna("desconocido").astype(str).tolist()
    docs = paragraphs["paragraph"].tolist()

    run_bertopic(
        docs=docs,
        out_dir=OUT,
        classes=classes,
        class_label="dossier",
        min_topic_size=50,
        nr_topics="auto",
        target_nr_topics=25,
        ngram_range=(1, 2),
        min_df=10,
        extra_stopwords=LEGAL_STOPWORDS,
    )


if __name__ == "__main__":
    main()
