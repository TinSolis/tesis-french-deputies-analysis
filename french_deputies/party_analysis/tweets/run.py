"""
Analisis de enfasis tematico a nivel partido sobre los TWEETS de los diputados.
Partido = grupo parlamentario consolidado (GROUP_LABEL). Resultados en results/.
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
         / "tweets" / "results" / "predictions.csv")
OUT = THIS / "results"


def main() -> None:
    analysis.run("tweets", PREDS, party_col="political_group_abbrev", out_dir=OUT,
                 party_map=analysis.GROUP_LABEL, min_docs=1000)
    print(f"\nResultados en {OUT}/")


if __name__ == "__main__":
    main()
