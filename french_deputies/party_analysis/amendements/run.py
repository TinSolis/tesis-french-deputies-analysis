"""
Analisis a nivel partido de las ENMIENDAS segun como votan los diputados.
Texto = prediccion MARPOR de la enmienda (1 por scrutin); voto = scrutin de la
enmienda. Resultados en results/.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
MODULE = THIS.parent
sys.path.insert(0, str(MODULE))
from common import votes  # noqa: E402

REPO = MODULE.parent.parent
PREDS = (REPO / "french_deputies" / "manifestoberta_analysis"
         / "amendements" / "results" / "predictions.csv")
VOTES = (REPO / "french_deputies" / "lois_votes" / "votes_rd" / "processed"
         / "votos_amendements_por_diputado.csv")
DEP = (REPO / "french_deputies" / "datos_diputados" / "data"
       / "deputes_an_rd.csv")
OUT = THIS / "results"


def main() -> None:
    votes.run("amendements", PREDS, VOTES, DEP, OUT)
    print(f"\nResultados en {OUT}/")


if __name__ == "__main__":
    main()
