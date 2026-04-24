#!/usr/bin/env python3
"""Limpieza de deputes_twitter_rd: deja columnas en inglés y solo URLs twitter.com."""

import csv
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
INPUT_CSV = DATA_DIR / "deputes_twitter_rd.csv"
OUTPUT_CSV = DATA_DIR / "deputes_twitter.csv"


def extract_twitter_urls(sites_web: str) -> str:
    if not sites_web or not isinstance(sites_web, str):
        return ""
    urls = [u.strip() for u in sites_web.split("|")]
    twitter_urls = []
    for u in urls:
        m = re.search(r"https?://(?:www\.)?(twitter\.com/[^\s/?#]+)", u, re.I)
        if m:
            twitter_urls.append(m.group(1))
    return "|".join(twitter_urls) if twitter_urls else ""


def main():
    if not INPUT_CSV.exists():
        print(f"No existe {INPUT_CSV}. Coloca allí el CSV de twitter-parlementaires.")
        return
    with open(INPUT_CSV, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    fieldnames = [
        "family_name", "first_name", "gender",
        "twitter_handle", "twitter_verified", "twitter_id", "twitter_name",
        "twitter_created_at", "twitter_web_urls",
    ]
    out_rows = []
    for r in rows:
        out_rows.append({
            "family_name": r.get("nom_de_famille", ""),
            "first_name": r.get("prenom", ""),
            "gender": r.get("sexe", ""),
            "twitter_handle": r.get("twitter", ""),
            "twitter_verified": r.get("twitter_verified", ""),
            "twitter_id": r.get("twitter_id", ""),
            "twitter_name": r.get("twitter_name", ""),
            "twitter_created_at": r.get("twitter_created_at", ""),
            "twitter_web_urls": extract_twitter_urls(r.get("sites_web", "")),
        })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Escrito {len(out_rows)} filas → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
