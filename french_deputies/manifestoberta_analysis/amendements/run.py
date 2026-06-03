"""
Clasifica enmiendas votadas (dispositif + expose_sommaire) con manifestoberta.

Filtros (alineados con bertopic_analysis/amendements/run.py):
  - match_confianza alta/media (vinculo correcto con la ley).
  - >=10 palabras tras concatenar dispositif+expose_sommaire (descarta filas
    "nan nan" por NaN en ambos campos y enmiendas ultracortas tipo
    "Supprimer cet article").
"""

from __future__ import annotations

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
    / "amendements_votos_con_texto.csv"
)
OUT = THIS / "results"

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
    df = pd.read_csv(DATA)
    print(f"enmiendas: {len(df):,}")
    df["texto"] = df.apply(build_text, axis=1)
    df = df[df["texto"].str.split().str.len() > 0].reset_index(drop=True)
    print(f"  con texto no vacio: {len(df):,}")

    if "match_confianza" in df.columns:
        n0 = len(df)
        df = df[df["match_confianza"].isin(["alta", "media"])].reset_index(drop=True)
        print(f"  match alta/media (de {n0}): {len(df):,}")

    n0 = len(df)
    df = df[df["texto"].str.split().str.len() >= MIN_WORDS].reset_index(drop=True)
    print(f"  >= {MIN_WORDS} palabras (de {n0}): {len(df):,}")

    extras = [c for c in ["scrutin_id", "ley_titulo_corto", "autor_nombre", "resultado"] if c in df.columns]

    classify_dataframe(
        df=df,
        text_col="texto",
        out_dir=OUT,
        extra_cols=extras,
        batch_size=16,
    )


if __name__ == "__main__":
    main()
