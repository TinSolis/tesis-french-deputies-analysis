"""
Clasifica las quasi-oraciones MARPOR 2017 (FR) con manifestoberta.

Este es el caso especial: la entrada YA TIENE etiqueta MARPOR (`cmp_code`)
asignada manualmente por los codificadores del Manifesto Project. Por eso,
ademas de clasificar, **validamos** el modelo midiendo su acuerdo con la
etiqueta humana en `validation/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

THIS = Path(__file__).resolve().parent
ROOT = THIS.parent
sys.path.insert(0, str(ROOT))
from common.classifier_runner import classify_dataframe  # noqa: E402

DATA = ROOT.parents[0] / "manifestos" / "processed" / "manifesto_texts.csv"
FULL = ROOT.parents[0] / "manifestos" / "processed" / "manifesto_full_texts.csv"
OUT = THIS / "results"


def main():
    df = pd.read_csv(DATA)
    print(f"manifestos: {len(df):,} quasi-oraciones")
    # Sin filtro de largo: las quasi-oraciones MARPOR ya estan pre-segmentadas
    # por anotadores expertos. Filtrar por largo descartaria texto codificable
    # y sub-representaria al PCF (estilo telegrafico, 39 quasi-frases).
    df = df[df["text"].notna()].reset_index(drop=True)
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0].reset_index(drop=True)
    print(f"  no vacias: {len(df):,}")

    if FULL.exists():
        mp = pd.read_csv(FULL)
        if {"manifesto_id", "party_abbrev"}.issubset(mp.columns):
            df = df.merge(mp[["manifesto_id", "party_abbrev"]], on="manifesto_id", how="left")

    classify_dataframe(
        df=df,
        text_col="text",
        out_dir=OUT,
        extra_cols=["manifesto_id", "cmp_code", "party_abbrev"],
        batch_size=16,
    )


if __name__ == "__main__":
    main()
