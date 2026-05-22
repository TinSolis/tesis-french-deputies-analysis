"""
Descarga robusta del ZIP de enmiendas XV de la AN.

El servidor de la AN corta conexiones a la mitad. Este script:
  - descarga por chunks con stream
  - reanuda desde donde quedó usando Range header
  - VALIDA que el servidor respete el rango pedido (status 206)
  - si el servidor devuelve 200 sobre un Range request, descarta lo recibido
    y vuelve a empezar de cero (evita corrupción)
  - se detiene cuando llega al tamaño exacto reportado por el servidor

Uso:
    python3 lois_votes/scripts/download_amendements.py
"""

import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

URL = "https://data.assemblee-nationale.fr/static/openData/repository/15/loi/amendements_legis/Amendements_XV.xml.zip"
DEST = Path(__file__).resolve().parent.parent / "votes_rd" / "Amendements" / "Amendements_XV.xml.zip"

CHUNK = 64 * 1024
MAX_RETRIES = 100000
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 thesis-script"


def get_remote_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return int(resp.headers.get("Content-Length", 0))


def download_with_resume(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        total = get_remote_size(url)
        print(f"Tamano remoto: {total} bytes ({total / (1024*1024):.1f} MB)")
    except Exception as e:
        print(f"No pude obtener Content-Length: {e}.")
        sys.exit(1)

    # Si el archivo local ya pasa del tamano correcto, esta corrupto -> borrar
    if dest.exists():
        size = dest.stat().st_size
        if size > total:
            print(f"Archivo local pesa {size} > {total}: esta corrupto, lo borro.")
            dest.unlink()
        elif size == total:
            print("Ya esta completo.")
            return

    for attempt in range(1, MAX_RETRIES + 1):
        have = dest.stat().st_size if dest.exists() else 0
        if have >= total:
            print(f"Listo: {have} bytes.")
            return

        headers = {"User-Agent": USER_AGENT}
        if have:
            headers["Range"] = f"bytes={have}-{total - 1}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                status = resp.status
                # Si pedi Range pero me devuelve 200, el servidor no respeta el rango.
                # Hay que descartar lo local y empezar de cero.
                if have and status != 206:
                    print(f"  [{attempt}] el servidor devolvio {status} en vez de 206. "
                          f"Borro local y reinicio.")
                    dest.unlink(missing_ok=True)
                    time.sleep(2)
                    continue

                mode = "ab" if have else "wb"
                start_ts = time.time()
                last_print = start_ts
                with open(dest, mode) as f:
                    while True:
                        chunk = resp.read(CHUNK)
                        if not chunk:
                            break
                        # No permitir crecer mas alla del total esperado
                        if have + len(chunk) > total:
                            chunk = chunk[: total - have]
                        f.write(chunk)
                        have += len(chunk)
                        if have >= total:
                            break
                        now = time.time()
                        if now - last_print > 2:
                            pct = 100 * have / total
                            mbs = have / (1024 * 1024)
                            sp = (have - (have - (now - start_ts) * 100000)) / 1024  # approx
                            print(f"  [{attempt}] {mbs:6.1f} MB  {pct:5.1f}%")
                            last_print = now
            if have >= total:
                print(f"Descarga completa: {have} bytes en intento {attempt}.")
                return
            print(f"  [{attempt}] cierre limpio pero faltan {total - have} bytes. Reintento.")
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            print(f"  [{attempt}] error: {e} -- reintento en 5s ({have}/{total} bytes)")
            time.sleep(5)
        except Exception as e:
            print(f"  [{attempt}] error inesperado: {e} -- reintento en 10s")
            time.sleep(10)

    raise SystemExit(f"No pude completar la descarga tras {MAX_RETRIES} intentos.")


if __name__ == "__main__":
    print(f"Destino: {DEST}")
    print(f"URL    : {URL}")
    download_with_resume(URL, DEST)
    print(f"OK -- archivo final: {DEST.stat().st_size / (1024*1024):.1f} MB")
