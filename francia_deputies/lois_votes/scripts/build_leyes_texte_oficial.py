#!/usr/bin/env python3
"""
Enlaza cada fila de leyes_votadas_2017_2022.csv con un dossier parlamentario
(votes_rd/json/dossierParlementaire/*.json) y extrae la promulgación → NOR + URL Légifrance.

Genera:
  - votes_rd/processed/leyes_texto_oficial.csv
    (scrutin_id, metadatos, nor, urls; columna texto_oficial si existe archivo local)

Texto oficial (JORF / Légifrance):
  - El HTML de legifrance.gouv.fr suele estar protegido (Cloudflare): no se descarga
    bien con requests/curl sin navegador o API.
  - Coloca el texto en: votes_rd/textes_lois/<scrutin_id>.txt  o  <NOR>.txt
    (UTF-8). El script los incrustará en texto_oficial al regenerar el CSV.

  - Alternativa robusta: API Légifrance vía PISTE (inscripción gratuita en piste.gouv.fr).

Uso (desde francia_deputies):
  python3 lois_votes/scripts/build_leyes_texte_oficial.py
"""

from __future__ import annotations

import csv
import json
import pickle
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
VOTES_RD = LOIS_VOTES_DIR / "votes_rd"
PROCESSED = VOTES_RD / "processed"
DOSSIERS_DIR = VOTES_RD / "json" / "dossierParlementaire"
TEXTES_DIR = VOTES_RD / "textes_lois"
LEYES_CSV = PROCESSED / "leyes_votadas_2017_2022.csv"
OUT_CSV = PROCESSED / "leyes_texto_oficial.csv"
INDEX_CACHE = VOTES_RD / ".dossier_index_cache.pkl"

try:
    from rapidfuzz import fuzz

    def match_score(a: str, b: str) -> float:
        return fuzz.token_set_ratio(a, b) / 100.0

except ImportError:

    def match_score(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()


def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def kernel_scrutin_titre(titre: str) -> str:
    t = titre.lower().replace("’", "'").replace("?", " ")
    for p in ("l'ensemble du ", "l'ensemble de la "):
        if t.startswith(p):
            t = t[len(p) :]
    t = re.sub(r"\s*\([^)]*lecture[^)]*\)\.?\s*$", "", t)
    return norm_txt(t)


def type_consistent(scrutin_norm: str, dossier_raw: str) -> bool:
    """Evita emparejar projet con proposition."""
    dr = dossier_raw.lower()
    s_prop = "proposition de loi" in scrutin_norm
    s_proj = "projet de loi" in scrutin_norm
    d_prop = dr.startswith("proposition de loi") or dr.startswith("proposition ")
    d_proj = dr.startswith("projet de loi") or (
        dr.startswith("projet ") and "proposition" not in dr[:40]
    )
    if s_prop and d_proj and not d_prop:
        return False
    if s_proj and d_prop and not d_proj:
        return False
    return True


def organique_consistent(scrutin_norm: str, dossier_raw: str) -> bool:
    s_org = "organique" in scrutin_norm
    d_org = "organique" in dossier_raw.lower()
    if s_org != d_org:
        return False
    return True


def extract_promulgation_from_raw(text: str) -> list[dict]:
    """
    Los dossiers PLF tienen actesLegislatifs gigantes; recorrer el JSON es muy lento.
    Buscamos el primer bloque PROM-PUB y leemos urlLegifrance / NOR por regex.
    """
    markers = ('"codeActe": "PROM-PUB"', '"codeActe":"PROM-PUB"')
    pos = -1
    for m in markers:
        pos = text.find(m)
        if pos != -1:
            break
    if pos == -1:
        return []
    chunk = text[pos : pos + 25000]
    url_m = re.search(r'"urlLegifrance"\s*:\s*"(https?://[^"]+)"', chunk)
    if not url_m:
        return []
    nor_m = re.search(r'"referenceNOR"\s*:\s*"([^"]+)"', chunk)
    date_m = re.search(r'"dateJO"\s*:\s*"([^"]+)"', chunk)
    code_m = re.search(r'"codeLoi"\s*:\s*"([^"]+)"', chunk)
    titre_m = re.search(r'"titreLoi"\s*:\s*"([^"]*)"', chunk)
    nor_rect_m = re.search(r'"infoJORect"\s*:\s*\{[^}]{0,4000}?"referenceNOR"\s*:\s*"([^"]+)"', chunk, re.DOTALL)
    url_rect_m = re.search(r'"infoJORect"\s*:\s*\{[^}]{0,4000}?"urlLegifrance"\s*:\s*"(https?://[^"]+)"', chunk, re.DOTALL)
    return [
        {
            "nor": (nor_m.group(1) if nor_m else "").strip(),
            "url_legifrance": url_m.group(1).strip(),
            "date_jo": (date_m.group(1) if date_m else "").strip(),
            "nor_rect": (nor_rect_m.group(1) if nor_rect_m else "").strip(),
            "url_rect": (url_rect_m.group(1) if url_rect_m else "").strip(),
            "code_loi": (code_m.group(1) if code_m else "").strip(),
            "titre_loi": (titre_m.group(1) if titre_m else "").strip(),
        }
    ]


def _dossier_dir_latest_mtime() -> float:
    m = 0.0
    for p in DOSSIERS_DIR.glob("DLR*.json"):
        try:
            m = max(m, p.stat().st_mtime)
        except OSError:
            pass
    return m


def load_dossier_index():
    """Lista de (uid, titre brut, titre normalizado, promulgaciones)."""
    if not DOSSIERS_DIR.is_dir():
        raise FileNotFoundError(f"No existe {DOSSIERS_DIR} (descomprime Dossiers_Legislatifs_XV.json.zip).")

    lm = _dossier_dir_latest_mtime()
    if INDEX_CACHE.is_file():
        try:
            with open(INDEX_CACHE, "rb") as cf:
                cached_lm, rows = pickle.load(cf)
            if cached_lm >= lm:
                return rows
        except (pickle.PickleError, OSError, EOFError):
            pass

    rows = []
    for p in DOSSIERS_DIR.glob("DLR*.json"):
        try:
            raw = p.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        root = data.get("dossierParlementaire") or data
        if not isinstance(root, dict):
            continue
        uid = (root.get("uid") or p.stem).strip()
        td = root.get("titreDossier") or {}
        titre = (td.get("titre") or "").strip()
        if not titre:
            continue
        prom = extract_promulgation_from_raw(raw)
        tn = norm_txt(titre)
        rows.append(
            {
                "uid": uid,
                "titre": titre,
                "titre_n": tn,
                "_tok": frozenset(_significant_tokens(tn)),
                "prom": prom,
            }
        )
    try:
        with open(INDEX_CACHE, "wb") as cf:
            pickle.dump((lm, rows), cf, protocol=pickle.HIGHEST_PROTOCOL)
    except OSError:
        pass
    return rows


def _significant_tokens(s: str) -> set[str]:
    return {w for w in s.split() if len(w) > 3}


def best_dossier_for_scrutin(titre_scrutin: str, index: list[dict]) -> tuple[dict | None, float]:
    k = kernel_scrutin_titre(titre_scrutin)
    kt = _significant_tokens(k)
    # Reducir candidatos: al menos una palabra significativa en común
    candidates = [d for d in index if kt & d.get("_tok", frozenset())]
    if not candidates:
        candidates = index
    best = None
    best_s = 0.0
    for d in candidates:
        if not type_consistent(k, d["titre"]):
            continue
        if not organique_consistent(k, d["titre"]):
            continue
        s = match_score(k, d["titre_n"])
        if k in d["titre_n"] or d["titre_n"] in k:
            s = max(s, 0.82)
        if s > best_s:
            best_s = s
            best = d
    return best, best_s


def load_text_for_row(scrutin_id: str, nor: str) -> str:
    TEXTES_DIR.mkdir(parents=True, exist_ok=True)
    for name in (f"{scrutin_id}.txt", f"{nor}.txt" if nor else ""):
        if not name:
            continue
        path = TEXTES_DIR / name
        if path.is_file():
            try:
                return path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass
    return ""


def main():
    if not LEYES_CSV.is_file():
        raise SystemExit(f"Falta {LEYES_CSV}. Ejecuta antes build_laws_and_votes.py")

    print("Cargando índice de dossiers (puede tardar un minuto)...")
    index = load_dossier_index()
    print(f"  {len(index)} dossiers con título.")

    out_rows = []
    with open(LEYES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        laws = list(reader)

    n_matched = 0
    n_prom = 0
    n_text = 0

    for row in laws:
        sid = (row.get("scrutin_id") or "").strip()
        tit = (row.get("titulo") or "").strip()
        fecha = (row.get("fecha") or "").strip()
        dossier_uid = (row.get("dossier_ref") or "").strip()

        match = None
        score = 0.0
        if dossier_uid:
            match = next((d for d in index if d["uid"] == dossier_uid), None)
            if match:
                score = 1.0
        if match is None:
            match, score = best_dossier_for_scrutin(tit, index)

        if match:
            n_matched += 1

        prom = (match or {}).get("prom") or []
        p0 = prom[0] if prom else {}
        nor = p0.get("nor", "")
        if prom:
            n_prom += 1

        texto = load_text_for_row(sid, nor)
        if texto.strip():
            n_text += 1

        out_rows.append(
            {
                "scrutin_id": sid,
                "titulo_scrutin": tit,
                "fecha": fecha,
                "dossier_uid": (match or {}).get("uid", ""),
                "dossier_titre": (match or {}).get("titre", ""),
                "match_score": f"{score:.3f}",
                "code_loi": p0.get("code_loi", ""),
                "titre_loi_promulgation": p0.get("titre_loi", ""),
                "nor_jo": nor,
                "url_legifrance": p0.get("url_legifrance", ""),
                "nor_jo_rectificatif": p0.get("nor_rect", ""),
                "url_legifrance_rectificatif": p0.get("url_rect", ""),
                "texto_oficial": texto,
            }
        )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scrutin_id",
        "titulo_scrutin",
        "fecha",
        "dossier_uid",
        "dossier_titre",
        "match_score",
        "code_loi",
        "titre_loi_promulgation",
        "nor_jo",
        "url_legifrance",
        "nor_jo_rectificatif",
        "url_legifrance_rectificatif",
        "texto_oficial",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Escrito {OUT_CSV}")
    print(f"  Leyes (filas): {len(out_rows)}")
    print(f"  Con dossier emparejado: {n_matched}")
    print(f"  Con acto de promulgación (NOR/URL): {n_prom}")
    print(f"  Con texto local en textes_lois/: {n_text}")
    print("\nPara rellenar texto_oficial:")
    print(f"  - Añade archivos .txt en {TEXTES_DIR}")
    print("  - O usa la API Légifrance (PISTE). Véase README_LOIS_VOTES.md")


if __name__ == "__main__":
    main()
