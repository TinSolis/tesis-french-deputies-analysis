"""
Analisis a nivel partido de las LEYES (projets/propositions de loi) segun como
votan los diputados. Texto = predicciones MARPOR del scrutin; voto = scrutin final.
Resultados en results/.
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
         / "lois" / "results" / "predictions.csv")
VOTES = (REPO / "french_deputies" / "lois_votes" / "votes_rd" / "processed"
         / "votos_por_diputado.csv")
DEP = (REPO / "french_deputies" / "datos_diputados" / "data"
       / "deputes_an_rd.csv")
OUT = THIS / "results"


def main() -> None:
    votes.run("lois", PREDS, VOTES, DEP, OUT)
    print(f"\nResultados en {OUT}/")


if __name__ == "__main__":
    main()
