#!/usr/bin/env python3
"""
Merge AN + Twitter → deputes_rd.csv (data/) y deputes_2017_2022.csv (processed/).

Requisito: data/deputes_an_rd.csv y data/deputes_twitter.csv.

Uso (desde francia_deputies): python3 datos_diputados/scripts/merge_deputes_2017_2022.py
"""

import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
PROCESSED_DIR = SCRIPT_DIR.parent / "processed"

AN_CSV = DATA_DIR / "deputes_an_rd.csv"
TWITTER_CSV = DATA_DIR / "deputes_twitter.csv"
OUT_RD = DATA_DIR / "deputes_rd.csv"
OUT_CONSOLIDATED = PROCESSED_DIR / "deputes_2017_2022.csv"

AN_COLS = [
    "id", "full_name", "family_name", "first_name", "gender", "birth_date", "birth_place",
    "dept_num", "district_name", "district_num", "mandate_start", "mandate_end",
    "former_deputy", "political_group_abbrev", "political_group",
]
TWITTER_COLS = [
    "twitter_handle", "twitter_verified", "twitter_id", "twitter_name",
    "twitter_created_at", "twitter_web_urls",
]


def main():
    if not AN_CSV.exists():
        print(f"No existe {AN_CSV}. Ejecuta antes: python3 datos_diputados/scripts/fetch_an_15e_deputes.py")
        return
    if not TWITTER_CSV.exists():
        print(f"No existe {TWITTER_CSV}. Ejecuta antes: python3 datos_diputados/scripts/build_deputes_twitter_csv.py")
        return

    with open(AN_CSV, newline="", encoding="utf-8") as f:
        an_rows = list(csv.DictReader(f))
    with open(TWITTER_CSV, newline="", encoding="utf-8") as f:
        twitter_rows = list(csv.DictReader(f))

    twitter_by_name = {}
    for r in twitter_rows:
        k = (r.get("family_name", "").strip(), r.get("first_name", "").strip())
        twitter_by_name[k] = r

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_RD, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=AN_COLS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in an_rows:
            w.writerow({c: r.get(c, "") for c in AN_COLS})
    print(f"1) Escrito {len(an_rows)} filas → {OUT_RD.name}")

    consolidated = []
    for r in an_rows:
        k = (r.get("family_name", "").strip(), r.get("first_name", "").strip())
        tw = twitter_by_name.get(k, {})
        row = {c: r.get(c, "") for c in AN_COLS}
        row["twitter_handle"] = tw.get("twitter_handle", "")
        row["twitter_verified"] = tw.get("twitter_verified", "")
        row["twitter_id"] = tw.get("twitter_id", "")
        row["twitter_name"] = tw.get("twitter_name", "")
        row["twitter_created_at"] = tw.get("twitter_created_at", "")
        row["twitter_web_urls"] = tw.get("twitter_web_urls", "")
        consolidated.append(row)

    with open(OUT_CONSOLIDATED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=AN_COLS + TWITTER_COLS, delimiter=";")
        w.writeheader()
        w.writerows(consolidated)
    print(f"2) Escrito {len(consolidated)} filas → {OUT_CONSOLIDATED}")
    matched = sum(1 for r in consolidated if r.get("twitter_handle"))
    print(f"   (Twitter encontrado para {matched} diputados)")


if __name__ == "__main__":
    main()
