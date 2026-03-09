#!/usr/bin/env python3
"""
Descarga los ZIP de Scrutins XV y Dossiers législatifs XV desde data.assemblee-nationale.fr
y los guarda en lois_votes/data/ (para usarlos con build_laws_and_votes.py).

Uso (desde francia_deputies):
  python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py

Si la descarga falla, descarga a mano desde:
  - https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins
  - https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs
y coloca los .zip en francia_deputies/lois_votes/data/
"""

import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
DATA_DIR = LOIS_VOTES_DIR / "data"

URLS = {
    "Scrutins_XV.json.zip": "https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip",
    "Dossiers_Legislatifs_XV.json.zip": "https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip",
}


def download(url: str, path: Path) -> bool:
    if not requests:
        print("Instala 'requests' para descarga automática: pip install requests")
        return False
    print(f"Descargando {url} ...")
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        path.write_bytes(r.content)
        print(f"  Guardado: {path}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        path = DATA_DIR / name
        if path.exists():
            print(f"Ya existe: {path}")
            continue
        if not download(url, path):
            print(f"Descarga manual: {url}")
            print(f"  Luego coloca {name} en {DATA_DIR}")
    print("Listo. Ejecuta build_laws_and_votes.py después de descomprimir los ZIP si es necesario.")


if __name__ == "__main__":
    main()
