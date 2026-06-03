"""
BERTopic sobre las enmiendas votadas en hemiciclo (XVe legislature).

Cada enmienda tiene dos campos de texto:
  - dispositif      : el cambio concreto propuesto al articulado
  - expose_sommaire : la justificacion del autor (rica para topicos)

Concatenamos ambos para captar tanto la materia juridica como la motivacion
politica.

POLITICA DE FILTRADO:
  - Match con la ley de confianza alta/media (asegura que el texto este
    correctamente vinculado a su contexto legal).
  - >=10 palabras tras concatenar dispositif+expose_sommaire. Aunque la
    mediana del corpus es ~206 palabras, hay una cola corta de ~5% formada
    por filas donde ambos campos vienen NaN (la concatenacion queda en
    "nan nan" y BERTopic las agrupa en un topico espureo); el threshold
    de 10 palabras las descarta junto con un punado de enmiendas reales
    extremadamente breves.

Entrada: french_deputies/lois_votes/votes_rd/processed/amendements_votos_con_texto.csv
Salida : ./results/
"""

from __future__ import annotations

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
    / "amendements_votos_con_texto.csv"
)
OUT = THIS_DIR / "results"

MIN_WORDS = 10


def _clean(v) -> str:
    """Devuelve string limpia, tratando NaN/None como vacio."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    s = str(v).strip()
    return "" if s.lower() == "nan" else s


def build_text(row: pd.Series) -> str:
    d = _clean(row.get("dispositif"))
    e = _clean(row.get("expose_sommaire"))
    if d and e:
        return f"{d}\n{e}"
    return d or e


def main():
    if not DATA.exists():
        print(f"ERROR: no encuentro {DATA}")
        sys.exit(1)

    print(f"Cargando {DATA.name} ...")
    df = pd.read_csv(DATA)
    print(f"  scrutins de enmienda: {len(df):,}")

    df["texto"] = df.apply(build_text, axis=1)
    df = df[df["texto"].str.split().str.len() > 0].reset_index(drop=True)
    print(f"  con texto no vacio (disp+expose): {len(df):,}")

    if "match_confianza" in df.columns:
        n0 = len(df)
        df = df[df["match_confianza"].isin(["alta", "media"])].reset_index(drop=True)
        print(f"  match alta/media (de {n0}): {len(df):,}")

    n0 = len(df)
    df = df[df["texto"].str.split().str.len() >= MIN_WORDS].reset_index(drop=True)
    print(f"  >= {MIN_WORDS} palabras (de {n0}): {len(df):,}")

    classes = df.get("ley_titulo_corto", pd.Series(["desconocido"] * len(df))).fillna("desconocido").astype(str).tolist()
    docs = df["texto"].tolist()

    run_bertopic(
        docs=docs,
        out_dir=OUT,
        classes=classes,
        class_label="ley",
        min_topic_size=20,
        nr_topics="auto",
        target_nr_topics=25,
        ngram_range=(1, 2),
        min_df=5,
        extra_stopwords=LEGAL_STOPWORDS,
    )


if __name__ == "__main__":
    main()
