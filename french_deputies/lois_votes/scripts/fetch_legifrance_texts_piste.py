#!/usr/bin/env python3
"""
Descarga el texto oficial de las leyes (JORF) desde Légifrance vía la API PISTE.

Lee NORs desde votes_rd/processed/leyes_texto_oficial.csv y guarda un .txt por NOR
en votes_rd/textes_lois/<NOR>.txt. Después, al volver a ejecutar
build_leyes_texte_oficial.py, esos textos se incorporan en la columna texto_oficial.

Requisitos previos (manual, una sola vez):
  1) Crear cuenta en https://piste.gouv.fr/registration
  2) En "API > Consentement CGU API" aceptar las CGU de Légifrance
  3) En "Applications" crear una app y vincularla a la API "Légifrance"
     (selecciona el entorno PROD; SANDBOX devuelve datos limitados)
  4) Copiar client_id y client_secret de esa aplicación

Credenciales: el script las lee en este orden
  - variables de entorno PISTE_CLIENT_ID y PISTE_CLIENT_SECRET
  - archivo lois_votes/.env con líneas KEY=VALUE
  - flags --client-id / --client-secret

Uso (desde francia_deputies):
  python3 lois_votes/scripts/fetch_legifrance_texts_piste.py
  python3 lois_votes/scripts/fetch_legifrance_texts_piste.py --limit 10        # prueba rápida
  python3 lois_votes/scripts/fetch_legifrance_texts_piste.py --sandbox         # apunta al entorno SANDBOX
  python3 lois_votes/scripts/fetch_legifrance_texts_piste.py --force           # re-descarga aunque exista

Salidas:
  - votes_rd/textes_lois/<NOR>.txt    (texto plano, UTF-8)
  - votes_rd/textes_lois/<NOR>.json   (JSON crudo devuelto por /consult/jorf)
  - votes_rd/textes_lois/_index.csv   (índice: nor,scrutin_id,jorf_text_id,bytes,status)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Falta el paquete 'requests'. Instala con: pip install requests")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
VOTES_RD = LOIS_VOTES_DIR / "votes_rd"
PROCESSED = VOTES_RD / "processed"
TEXTES_DIR = VOTES_RD / "textes_lois"
LEYES_CSV = PROCESSED / "leyes_texto_oficial.csv"
ENV_FILE = LOIS_VOTES_DIR / ".env"
INDEX_CSV = TEXTES_DIR / "_index.csv"

OAUTH_URL_PROD = "https://oauth.piste.gouv.fr/api/oauth/token"
OAUTH_URL_SBX = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
API_URL_PROD = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"
API_URL_SBX = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"


def load_env_file(path: Path) -> Dict[str, str]:
    """Carga un archivo .env simple (KEY=VALUE por línea). Ignora comentarios."""
    env: Dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        env[k.strip()] = v
    return env


def resolve_credentials(args: argparse.Namespace) -> Tuple[str, str]:
    file_env = load_env_file(ENV_FILE)
    cid = (
        args.client_id
        or os.environ.get("PISTE_CLIENT_ID")
        or file_env.get("PISTE_CLIENT_ID", "")
    ).strip()
    csec = (
        args.client_secret
        or os.environ.get("PISTE_CLIENT_SECRET")
        or file_env.get("PISTE_CLIENT_SECRET", "")
    ).strip()
    if not cid or not csec:
        print("ERROR: faltan credenciales PISTE.")
        print(f"  Define PISTE_CLIENT_ID y PISTE_CLIENT_SECRET (env o {ENV_FILE}),")
        print("  o pásalas con --client-id / --client-secret.")
        sys.exit(2)
    return cid, csec


def get_token(client_id: str, client_secret: str, sandbox: bool) -> Tuple[str, float]:
    url = OAUTH_URL_SBX if sandbox else OAUTH_URL_PROD
    r = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "openid",
        },
        timeout=30,
    )
    r.raise_for_status()
    j = r.json()
    return j["access_token"], time.time() + float(j.get("expires_in", 3600)) - 60


class PisteClient:
    def __init__(self, client_id: str, client_secret: str, sandbox: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.api_base = API_URL_SBX if sandbox else API_URL_PROD
        self._token: Optional[str] = None
        self._token_expires: float = 0.0
        self.session = requests.Session()

    def _ensure_token(self) -> str:
        if self._token is None or time.time() >= self._token_expires:
            self._token, self._token_expires = get_token(
                self.client_id, self.client_secret, self.sandbox
            )
        return self._token

    def post(self, endpoint: str, payload: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        last_exc: Optional[Exception] = None
        for attempt in range(retries):
            token = self._ensure_token()
            try:
                r = self.session.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )
                if r.status_code == 401:
                    self._token = None
                    continue
                if r.status_code == 429:
                    wait = 2 ** attempt
                    print(f"  429 rate-limit; espero {wait}s...")
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                if not r.text.strip():
                    return {}
                return r.json()
            except requests.RequestException as e:
                last_exc = e
                time.sleep(1 + attempt)
        raise RuntimeError(f"POST {endpoint} falló tras {retries} intentos: {last_exc}")

    def search_by_nor(self, nor: str) -> List[Dict[str, Any]]:
        """Busca en el fondo JORF por número NOR. Devuelve la lista de resultados."""
        payload = {
            "fond": "JORF",
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "NOR",
                        "operateur": "ET",
                        "criteres": [
                            {
                                "typeRecherche": "EXACTE",
                                "valeur": nor,
                                "operateur": "ET",
                            }
                        ],
                    }
                ],
                "filtres": [],
                "pageNumber": 1,
                "pageSize": 10,
                "sort": "SIGNATURE_DATE_DESC",
                "operateur": "ET",
                "typePagination": "DEFAUT",
            },
        }
        data = self.post("/search", payload)
        return data.get("results") or []

    def consult_jorf(self, text_cid: str) -> Dict[str, Any]:
        return self.post("/consult/jorf", {"textCid": text_cid})


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t]+\n")
_MULTI_NL = re.compile(r"\n{3,}")


def html_to_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    s = s.replace("</p>", "\n\n").replace("</P>", "\n\n")
    s = _TAG_RE.sub("", s)
    s = unescape(s)
    s = _WS_RE.sub("\n", s)
    s = _MULTI_NL.sub("\n\n", s)
    return s.strip()


def extract_text_from_jorf(payload: Dict[str, Any]) -> str:
    """Convierte la respuesta de /consult/jorf en un texto plano legible."""
    text_obj = payload.get("text") or payload.get("jorf") or payload
    parts: List[str] = []

    titre = (text_obj.get("titreLong") or text_obj.get("titre") or "").strip()
    if titre:
        parts.append(titre)
    nor = (text_obj.get("nor") or "").strip()
    nature = (text_obj.get("nature") or "").strip()
    date_sig = (text_obj.get("dateSignature") or "").strip()
    date_pub = (text_obj.get("datePublication") or text_obj.get("datePubli") or "").strip()
    meta = " | ".join([x for x in [nature, date_sig, date_pub, f"NOR: {nor}" if nor else ""] if x])
    if meta:
        parts.append(meta)

    visa = text_obj.get("visa") or ""
    if visa:
        parts.append("--- VISA ---")
        parts.append(html_to_text(visa))
    notice = text_obj.get("notice") or ""
    if notice:
        parts.append("--- NOTICE ---")
        parts.append(html_to_text(notice))

    def walk(node: Any, depth: int = 1) -> None:
        if isinstance(node, dict):
            section_title = node.get("title") or node.get("titre") or ""
            if section_title:
                parts.append("\n" + ("#" * min(depth, 6)) + " " + section_title.strip())
            for key in ("content", "contenu", "texte", "texteHtml"):
                v = node.get(key)
                if isinstance(v, str) and v.strip():
                    parts.append(html_to_text(v))
            for key in ("articles", "sections", "structure", "children", "elements"):
                v = node.get(key)
                if isinstance(v, list):
                    for child in v:
                        walk(child, depth + 1)
                elif isinstance(v, dict):
                    walk(v, depth + 1)
        elif isinstance(node, list):
            for child in node:
                walk(child, depth)

    walk(text_obj, 1)

    signataires = text_obj.get("signataires") or ""
    if signataires:
        parts.append("--- SIGNATAIRES ---")
        parts.append(html_to_text(signataires))

    txt = "\n".join(p for p in parts if p and p.strip())
    return _MULTI_NL.sub("\n\n", txt).strip()


def load_targets(args: argparse.Namespace) -> List[Dict[str, str]]:
    """Devuelve la lista de (nor, scrutin_id, titulo) a descargar."""
    if not LEYES_CSV.is_file():
        raise SystemExit(f"Falta {LEYES_CSV}. Ejecuta build_leyes_texte_oficial.py primero.")
    targets: List[Dict[str, str]] = []
    seen: set = set()
    with open(LEYES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nor = (row.get("nor_jo") or "").strip()
            if not nor or nor in seen:
                continue
            seen.add(nor)
            targets.append(
                {
                    "nor": nor,
                    "scrutin_id": (row.get("scrutin_id") or "").strip(),
                    "titulo": (row.get("titulo_scrutin") or "").strip(),
                }
            )
    if args.only_nor:
        wanted = {n.strip() for n in args.only_nor.split(",") if n.strip()}
        targets = [t for t in targets if t["nor"] in wanted]
    if args.limit and args.limit > 0:
        targets = targets[: args.limit]
    return targets


def load_existing_index() -> Dict[str, Dict[str, str]]:
    if not INDEX_CSV.is_file():
        return {}
    out: Dict[str, Dict[str, str]] = {}
    with open(INDEX_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nor = row.get("nor", "")
            if nor:
                out[nor] = row
    return out


def write_index(rows: List[Dict[str, str]]) -> None:
    fields = ["nor", "scrutin_id", "jorf_text_id", "bytes", "status", "titulo"]
    INDEX_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    ap = argparse.ArgumentParser(description="Descarga textos JORF desde Légifrance vía PISTE.")
    ap.add_argument("--client-id", default=None, help="PISTE client_id (alternativa a env/.env)")
    ap.add_argument("--client-secret", default=None, help="PISTE client_secret")
    ap.add_argument("--sandbox", action="store_true", help="Usa el entorno SANDBOX de PISTE")
    ap.add_argument("--limit", type=int, default=0, help="Máximo de NORs a procesar (0 = todos)")
    ap.add_argument("--only-nor", default="", help="Lista de NORs separados por coma a procesar")
    ap.add_argument("--force", action="store_true", help="Re-descarga aunque exista el .txt")
    ap.add_argument("--sleep", type=float, default=0.3, help="Segundos de pausa entre llamadas")
    args = ap.parse_args()

    client_id, client_secret = resolve_credentials(args)
    targets = load_targets(args)
    if not targets:
        print("No hay NORs para descargar. Verifica leyes_texto_oficial.csv.")
        return

    TEXTES_DIR.mkdir(parents=True, exist_ok=True)
    client = PisteClient(client_id, client_secret, sandbox=args.sandbox)
    index = load_existing_index()

    n_ok = n_skip = n_fail = 0
    rows: List[Dict[str, str]] = list(index.values())
    rows_by_nor: Dict[str, Dict[str, str]] = {r["nor"]: r for r in rows}

    print(f"Procesando {len(targets)} NORs ({'SANDBOX' if args.sandbox else 'PROD'}).")
    for i, t in enumerate(targets, 1):
        nor = t["nor"]
        txt_path = TEXTES_DIR / f"{nor}.txt"
        json_path = TEXTES_DIR / f"{nor}.json"

        if txt_path.is_file() and not args.force:
            n_skip += 1
            print(f"  [{i}/{len(targets)}] {nor}: existe (skip)")
            continue

        print(f"  [{i}/{len(targets)}] {nor}: buscando...", end="", flush=True)
        try:
            results = client.search_by_nor(nor)
        except Exception as e:
            print(f" ERROR search: {e}")
            n_fail += 1
            rows_by_nor[nor] = {
                "nor": nor,
                "scrutin_id": t["scrutin_id"],
                "jorf_text_id": "",
                "bytes": "0",
                "status": f"search_error: {e}",
                "titulo": t["titulo"],
            }
            continue

        text_cid = ""
        for r in results:
            for title in (r.get("titles") or []):
                cid = (title.get("cid") or "").strip()
                if cid.startswith("JORFTEXT"):
                    text_cid = cid
                    break
                tid = (title.get("id") or "").strip()
                if tid.startswith("JORFTEXT"):
                    text_cid = tid.split("_", 1)[0]
                    break
            if text_cid:
                break
            tid = (r.get("id") or "").strip()
            if tid.startswith("JORFTEXT"):
                text_cid = tid
                break

        if not text_cid:
            print(" no encontrado")
            n_fail += 1
            rows_by_nor[nor] = {
                "nor": nor,
                "scrutin_id": t["scrutin_id"],
                "jorf_text_id": "",
                "bytes": "0",
                "status": "not_found",
                "titulo": t["titulo"],
            }
            time.sleep(args.sleep)
            continue

        try:
            payload = client.consult_jorf(text_cid)
        except Exception as e:
            print(f" ERROR consult: {e}")
            n_fail += 1
            rows_by_nor[nor] = {
                "nor": nor,
                "scrutin_id": t["scrutin_id"],
                "jorf_text_id": text_cid,
                "bytes": "0",
                "status": f"consult_error: {e}",
                "titulo": t["titulo"],
            }
            continue

        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        txt = extract_text_from_jorf(payload)
        txt_path.write_text(txt, encoding="utf-8")
        n_ok += 1
        print(f" OK ({text_cid}, {len(txt)} bytes)")
        rows_by_nor[nor] = {
            "nor": nor,
            "scrutin_id": t["scrutin_id"],
            "jorf_text_id": text_cid,
            "bytes": str(len(txt)),
            "status": "ok",
            "titulo": t["titulo"],
        }
        time.sleep(args.sleep)

    write_index(list(rows_by_nor.values()))
    print("\nResumen:")
    print(f"  OK:        {n_ok}")
    print(f"  Saltados:  {n_skip}")
    print(f"  Fallidos:  {n_fail}")
    print(f"  Índice:    {INDEX_CSV}")
    print(f"  Textos:    {TEXTES_DIR}/")
    print("\nSiguiente paso (para inyectar 'texto_oficial' en el CSV final):")
    print("  python3 lois_votes/scripts/build_leyes_texte_oficial.py")


if __name__ == "__main__":
    main()
