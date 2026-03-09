#!/usr/bin/env python3
"""
Genera la lista de URLs de Twitter a partir de deputes_2017_2022.csv
para usar con Zeeschuimer (abrir perfiles y capturar).

Salida:
  - url_list.csv: id, full_name, political_group_abbrev, political_group, twitter_handle, url
  - url_list.txt: una URL por línea (para abrir en lote o copiar/pegar)

Ejecutar desde francia_deputies: python3 zeeschuimer/scripts/generate_twitter_url_list.py
"""

import csv
from pathlib import Path

# Rutas: script en zeeschuimer/scripts/ → francia_deputies es el padre del padre
SCRIPT_DIR = Path(__file__).resolve().parent
ZEESCHUIMER_DIR = SCRIPT_DIR.parent
FRANCIA_DEPUTIES = ZEESCHUIMER_DIR.parent

DEPUTIES_CSV = FRANCIA_DEPUTIES / "datos_diputados" / "processed" / "deputes_2017_2022.csv"
OUT_CSV = ZEESCHUIMER_DIR / "url_list.csv"
OUT_TXT = ZEESCHUIMER_DIR / "url_list.txt"
BASE_URL = "https://twitter.com"  # o https://x.com


def main():
    if not DEPUTIES_CSV.exists():
        print(f"No se encuentra {DEPUTIES_CSV}")
        print("Ejecuta desde la carpeta Tesis o francia_deputies.")
        return

    rows = []
    with open(DEPUTIES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            handle = (r.get("twitter_handle") or "").strip()
            if not handle:
                continue
            url = f"{BASE_URL}/{handle}"
            rows.append({
                "id": r.get("id", ""),
                "full_name": r.get("full_name", ""),
                "political_group_abbrev": r.get("political_group_abbrev", ""),
                "political_group": r.get("political_group", ""),
                "twitter_handle": handle,
                "url": url,
            })

    ZEESCHUIMER_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "full_name", "political_group_abbrev", "political_group", "twitter_handle", "url"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(row["url"] + "\n")

    print(f"Generadas {len(rows)} URLs con twitter_handle.")
    print(f"  CSV: {OUT_CSV}")
    print(f"  TXT (una URL por línea): {OUT_TXT}")


if __name__ == "__main__":
    main()
