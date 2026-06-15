"""
Analisis de enfasis tematico a nivel partido sobre los MANIFIESTOS (Francia 2017).
Partido = `party_abbrev` (10 partidos, ya limpio). Resultados en results/.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
MODULE = THIS.parent
sys.path.insert(0, str(MODULE))
from common import analysis  # noqa: E402

REPO = MODULE.parent.parent
PREDS = (REPO / "french_deputies" / "manifestoberta_analysis"
         / "manifestos" / "results" / "predictions.csv")
OUT = THIS / "results"


def main() -> None:
    analysis.run("manifestos", PREDS, party_col="party_abbrev", out_dir=OUT,
                 min_docs=30)
    print(f"\nResultados en {OUT}/")


if __name__ == "__main__":
    main()
