#!/usr/bin/env python3
"""
Descarga los ZIP de Scrutins XV y Dossiers législatifs XV (législature 2017-2022)
desde data.assemblee-nationale.fr y los descomprime en lois_votes/votes_rd/.

Uso (desde francia_deputies):
  python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py
  python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py --no-unzip   # solo descarga

Si la descarga falla, descarga a mano desde:
  - https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins
  - https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs
y coloca los .zip en francia_deputies/lois_votes/votes_rd/ y descomprime.
"""

import argparse
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
# Datos brutos AN (zip + json) y salida procesada bajo votes_rd/
VOTES_RD_DIR = LOIS_VOTES_DIR / "votes_rd"
DATA_DIR = VOTES_RD_DIR

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
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
        print(f"  Guardado: {path} ({path.stat().st_size / 1e6:.1f} MB)")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def unzip_to_data(zip_path: Path) -> None:
    """Extrae el contenido del zip en votes_rd/ (mismo directorio que el zip)."""
    print(f"Descomprimiendo {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DATA_DIR)
    print(f"  → {DATA_DIR}")


def main():
    parser = argparse.ArgumentParser(description="Descarga open data AN XV (scrutins + dossiers).")
    parser.add_argument("--force", action="store_true", help="Volver a descargar aunque exista el zip.")
    parser.add_argument("--no-unzip", action="store_true", help="No descomprimir tras descargar.")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in URLS.items():
        path = DATA_DIR / name
        if path.exists() and not args.force:
            print(f"Ya existe: {path}")
        else:
            if not download(url, path):
                print(f"Descarga manual: {url}")
                print(f"  Luego coloca {name} en {DATA_DIR}")
                continue
        if not args.no_unzip and path.exists():
            unzip_to_data(path)

    print("\nSiguiente paso:")
    print("  python3 lois_votes/scripts/build_laws_and_votes.py")


if __name__ == "__main__":
    main()
