#!/usr/bin/env python3
"""
FASE 1 del enriquecimiento DOLE/PISTE:
Recupera textos de leyes para los 'dossier_uid' que quedaron SIN texto_oficial,
buscando en Légifrance por TÍTULO del scrutin (no por NOR, porque no lo tienen).

Estrategia:
  1) Tomar leyes_texto_oficial.csv y agrupar por dossier_uid.
  2) Para cada dossier_uid sin texto_oficial:
       - Limpiar titulo_scrutin (sacar "l'ensemble du", "(première lecture)", etc.)
       - Hacer POST /search a PISTE con fond=JORF + typeChamp=TITLE + TOUS_LES_MOTS
       - Filtrar resultados por nature (LOI / ORDONNANCE / LOI_ORGANIQUE),
         fecha >= fecha_scrutin (la promulgación es posterior al voto), y por
         coincidencia razonable del kernel del título.
       - Si hay match, POST /consult/jorf con el JORFTEXT → texto plano.
       - Guardar en votes_rd/textes_lois/<dossier_uid>.txt y <dossier_uid>.json.
  3) Actualizar votes_rd/textes_lois/_index_titles.csv con qué se resolvió.

Uso (desde francia_deputies):
  python3 lois_votes/scripts/fetch_missing_by_title.py
  python3 lois_votes/scripts/fetch_missing_by_title.py --limit 5     # piloto
  python3 lois_votes/scripts/fetch_missing_by_title.py --only DLR5L15N40790,DLR5L15N35927
  python3 lois_votes/scripts/fetch_missing_by_title.py --debug       # verboso

Requiere lois_votes/.env (mismo client_id/secret PISTE que el otro script).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
INDEX_CSV = TEXTES_DIR / "_index_titles.csv"

# Importamos del script principal reutilizando código (mismo directorio).
sys.path.insert(0, str(SCRIPT_DIR))
from fetch_legifrance_texts_piste import (  # noqa: E402
    PisteClient,
    extract_text_from_jorf,
    load_env_file,
    resolve_credentials,
)

# Tipos de scrutin que no son "loi promulgable" (sirven para filtrarlos).
NON_PROMULGABLE_HINTS = (
    "motion de censure",
    "résolution",
    "resolution",
    "déclaration de politique générale",
    "déclaration du gouvernement",
)


def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clean_scrutin_title(titulo: str) -> str:
    """Limpia un título de scrutin para usarlo como query en Légifrance.

    Importante: las leyes promulgadas se llaman 'LOI n°...' en JORF, NO
    'Projet de loi'. Si dejamos 'projet de' en el query, /search devuelve 0
    resultados. Sacamos 'projet de' y 'proposition de' pero conservamos 'loi'
    y 'loi organique'.

    'l'ensemble du projet de loi pour la confiance dans la vie publique (première lecture).'
    → 'loi pour la confiance dans la vie publique'
    """
    t = (titulo or "").lower().replace("’", "'").strip()
    for p in (
        "l'ensemble du ",
        "l'ensemble de la ",
        "l'ensemble des ",
        "ensemble du ",
        "ensemble de la ",
    ):
        if t.startswith(p):
            t = t[len(p):]
    # Sufijos entre paréntesis: (première lecture), (texte de la cmp), etc.
    t = re.sub(r"\s*\([^)]*\)\.?\s*$", "", t)
    t = t.rstrip(". ")
    t = re.sub(r",?\s*adopt[ée]+s?\s+par\s+(?:le\s+s[ée]nat|l'assembl[ée]e\s+nationale)\s*,?",
               " ", t)
    # Aquí está la corrección clave: sacar 'projet de' / 'proposition de'
    # antes de 'loi' (y antes de 'loi organique').
    t = re.sub(r"\bprojet\s+de\s+loi\s+organique\b", "loi organique", t)
    t = re.sub(r"\bproposition\s+de\s+loi\s+organique\b", "loi organique", t)
    t = re.sub(r"\bprojet\s+de\s+loi\b", "loi", t)
    t = re.sub(r"\bproposition\s+de\s+loi\b", "loi", t)
    return re.sub(r"\s+", " ", t).strip()


def is_promulgable(titulo: str) -> bool:
    low = (titulo or "").lower()
    for hint in NON_PROMULGABLE_HINTS:
        if hint in low:
            return False
    return True


def kernel_for_match(s: str) -> str:
    """Versión más estricta para comparar matches: sin prefijos, sin 'projet'/'proposition'."""
    s = clean_scrutin_title(s)
    s = re.sub(r"^projet\s+de\s+loi(\s+organique)?\s*", "", s)
    s = re.sub(r"^proposition\s+de\s+loi(\s+organique)?\s*", "", s)
    return norm_txt(s)


def parse_date(d: str) -> Optional[date]:
    if not d:
        return None
    try:
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_publi(s: str) -> Optional[date]:
    """Parsea fechas devueltas por PISTE: ISO 'YYYY-MM-DDT...' o timestamp ms."""
    if not s:
        return None
    if isinstance(s, (int, float)):
        try:
            return datetime.fromtimestamp(s / 1000).date()
        except (OSError, ValueError):
            return None
    s = str(s)
    if s.isdigit():
        try:
            return datetime.fromtimestamp(int(s) / 1000).date()
        except (OSError, ValueError):
            return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _build_search_payload(query: str, type_champ: str = "TITLE") -> Dict:
    return {
        "fond": "JORF",
        "recherche": {
            "champs": [
                {
                    "typeChamp": type_champ,
                    "operateur": "ET",
                    "criteres": [
                        {
                            "typeRecherche": "TOUS_LES_MOTS_DANS_UN_CHAMP",
                            "valeur": query,
                            "operateur": "ET",
                        }
                    ],
                }
            ],
            # Solo filtramos por NATURE (DATE_SIGNATURE no es facette válida en JORF
            # y rompe la búsqueda devolviendo 0). Bonus por fecha en pick_best_result.
            "filtres": [
                {"facette": "NATURE", "valeurs": ["LOI", "ORDONNANCE", "LOI_ORGANIQUE"]},
            ],
            "pageNumber": 1,
            "pageSize": 15,
            "sort": "PERTINENCE",
            "operateur": "ET",
            "typePagination": "DEFAUT",
        },
    }


def search_by_title(
    client: PisteClient,
    titulo_clean: str,
    fecha_min: Optional[date] = None,
    fecha_max: Optional[date] = None,
    nature_hint: Optional[str] = None,
) -> List[Dict]:
    """POST /search en JORF. Hace 3 intentos en cascada:
       1) Por TITLE con título limpio.
       2) Por ALL (cualquier campo) con título limpio — más permisivo, rescata
          casos donde el título del scrutin tiene typos (ej. 'vie publique' vs
          'vie politique') porque busca también en el cuerpo del texto.
       3) Por TITLE con los 4 sustantivos más largos del título (last resort).
    """
    data = client.post("/search", _build_search_payload(titulo_clean, "TITLE"))
    results = data.get("results") or []
    if results:
        return results

    data = client.post("/search", _build_search_payload(titulo_clean, "ALL"))
    results = data.get("results") or []
    if results:
        return results

    tokens = [w for w in titulo_clean.split() if len(w) > 4]
    tokens.sort(key=len, reverse=True)
    if len(tokens) >= 3:
        short_query = " ".join(tokens[:4])
        data = client.post("/search", _build_search_payload(short_query, "ALL"))
        return data.get("results") or []
    return []


def pick_best_result(
    results: List[Dict],
    titulo_clean: str,
    fecha_scrutin: Optional[date],
    debug: bool = False,
) -> Tuple[Optional[Dict], str, float]:
    """Elige el mejor JORFTEXT entre los resultados. Devuelve (resultado, jorftext, score)."""
    if not results:
        return None, "", 0.0

    kernel = kernel_for_match(titulo_clean)
    kernel_tokens = {w for w in kernel.split() if len(w) > 3}

    best = None
    best_score = 0.0
    best_jorftext = ""

    for r in results:
        # Extraer JORFTEXT
        jorftext = ""
        title_str = ""
        for t in (r.get("titles") or []):
            cid = (t.get("cid") or "").strip()
            if cid.startswith("JORFTEXT"):
                jorftext = cid
                title_str = (t.get("title") or "").strip()
                break
        if not jorftext:
            continue

        title_n = norm_txt(title_str)
        title_tokens = {w for w in title_n.split() if len(w) > 3}
        overlap = len(kernel_tokens & title_tokens) / max(1, len(kernel_tokens))

        # Bonus si la fecha es posterior al scrutin y razonablemente cercana
        date_score = 0.0
        for d_field in ("datePublication", "dateSignature", "dateDiffusion"):
            d = parse_publi(r.get(d_field))
            if d and fecha_scrutin:
                gap = (d - fecha_scrutin).days
                if 0 <= gap <= 365:
                    date_score = 0.2 * (1 - gap / 365)
                    break
                elif gap >= -30:
                    date_score = 0.05
                    break

        # Bonus/penalty por concordancia de "organique": si el query pide una
        # loi organique, el resultado tiene que ser organique también; y viceversa.
        organique_query = "organique" in kernel
        organique_result = "organique" in title_n
        organique_score = 0.0
        if organique_query and organique_result:
            organique_score = 0.3
        elif organique_query and not organique_result:
            organique_score = -0.5
        elif not organique_query and organique_result:
            organique_score = -0.15

        score = overlap + date_score + organique_score

        if debug:
            print(f"     · score={score:.2f}  overlap={overlap:.2f}  date={date_score:.2f}  "
                  f"{jorftext} :: {title_str[:80]}")

        if score > best_score:
            best_score = score
            best = r
            best_jorftext = jorftext

    return best, best_jorftext, best_score


def load_targets(args: argparse.Namespace) -> List[Dict[str, str]]:
    if not LEYES_CSV.is_file():
        raise SystemExit(f"Falta {LEYES_CSV}. Ejecuta build_leyes_texte_oficial.py primero.")

    csv.field_size_limit(sys.maxsize)
    with open(LEYES_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Agrupar por dossier_uid; quedarse con los SIN texto
    por_dossier: Dict[str, List[Dict[str, str]]] = {}
    for r in rows:
        d = (r.get("dossier_uid") or "").strip() or f"__sin_{r.get('scrutin_id')}"
        por_dossier.setdefault(d, []).append(r)

    targets = []
    for d, rs in por_dossier.items():
        if any((r.get("texto_oficial") or "").strip() for r in rs):
            continue
        # Tomar la fila con título más representativo (suele ser cualquiera, pero el primero)
        first = rs[0]
        targets.append(
            {
                "dossier_uid": d if d.startswith("DLR") else "",
                "scrutin_id": first.get("scrutin_id", ""),
                "fecha": first.get("fecha", ""),
                "titulo_scrutin": first.get("titulo_scrutin", ""),
                "n_scrutins": str(len(rs)),
                "_storage_key": d if d.startswith("DLR") else f"S{first.get('scrutin_id','')}",
            }
        )

    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        targets = [t for t in targets if t["dossier_uid"] in wanted or t["scrutin_id"] in wanted]
    if args.limit and args.limit > 0:
        targets = targets[: args.limit]
    return targets


def load_index() -> Dict[str, Dict[str, str]]:
    if not INDEX_CSV.is_file():
        return {}
    out = {}
    with open(INDEX_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            k = row.get("storage_key", "")
            if k:
                out[k] = row
    return out


def write_index(rows: List[Dict[str, str]]) -> None:
    fields = [
        "storage_key", "dossier_uid", "scrutin_id", "fecha_scrutin",
        "titulo_scrutin", "jorf_text_id", "title_matched", "match_score",
        "bytes", "status",
    ]
    INDEX_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> None:
    ap = argparse.ArgumentParser(description="Recupera textos faltantes vía PISTE buscando por título.")
    ap.add_argument("--client-id", default=None)
    ap.add_argument("--client-secret", default=None)
    ap.add_argument("--sandbox", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="", help="dossier_uid o scrutin_id, separados por coma")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.4)
    ap.add_argument("--min-score", type=float, default=0.35,
                    help="Score mínimo (overlap+date_bonus) para aceptar match")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    client_id, client_secret = resolve_credentials(args)
    targets = load_targets(args)
    if not targets:
        print("No hay dossiers faltantes (todos tienen texto_oficial).")
        return

    TEXTES_DIR.mkdir(parents=True, exist_ok=True)
    client = PisteClient(client_id, client_secret, sandbox=args.sandbox)
    index = load_index()
    rows_by_key: Dict[str, Dict[str, str]] = {r["storage_key"]: r for r in index.values()}

    print(f"Procesando {len(targets)} dossiers sin texto ({'SANDBOX' if args.sandbox else 'PROD'}).")
    n_ok = n_skip = n_nofound = n_skipped_non_prom = n_err = 0

    for i, t in enumerate(targets, 1):
        key = t["_storage_key"]
        titulo = t["titulo_scrutin"]
        fecha = parse_date(t["fecha"])
        txt_path = TEXTES_DIR / f"{key}.txt"
        json_path = TEXTES_DIR / f"{key}.json"

        if txt_path.is_file() and not args.force:
            n_skip += 1
            print(f"  [{i}/{len(targets)}] {key}: existe (skip)")
            continue

        if not is_promulgable(titulo):
            print(f"  [{i}/{len(targets)}] {key}: SKIP no-promulgable ({titulo[:60]!r})")
            n_skipped_non_prom += 1
            rows_by_key[key] = {
                "storage_key": key, "dossier_uid": t["dossier_uid"],
                "scrutin_id": t["scrutin_id"], "fecha_scrutin": t["fecha"],
                "titulo_scrutin": titulo, "jorf_text_id": "",
                "title_matched": "", "match_score": "0", "bytes": "0",
                "status": "non_promulgable",
            }
            continue

        titulo_clean = clean_scrutin_title(titulo)
        print(f"  [{i}/{len(targets)}] {key}: {titulo_clean[:80]!r}")

        try:
            results = search_by_title(client, titulo_clean, fecha_min=fecha)
        except Exception as e:
            print(f"     ERROR search: {e}")
            n_err += 1
            rows_by_key[key] = {
                "storage_key": key, "dossier_uid": t["dossier_uid"],
                "scrutin_id": t["scrutin_id"], "fecha_scrutin": t["fecha"],
                "titulo_scrutin": titulo, "jorf_text_id": "",
                "title_matched": "", "match_score": "0", "bytes": "0",
                "status": f"search_error: {e}",
            }
            continue

        best, jorftext, score = pick_best_result(results, titulo_clean, fecha, debug=args.debug)

        if not best or not jorftext or score < args.min_score:
            print(f"     NO match (mejor score: {score:.2f}, {len(results)} resultados)")
            n_nofound += 1
            rows_by_key[key] = {
                "storage_key": key, "dossier_uid": t["dossier_uid"],
                "scrutin_id": t["scrutin_id"], "fecha_scrutin": t["fecha"],
                "titulo_scrutin": titulo, "jorf_text_id": jorftext,
                "title_matched": "", "match_score": f"{score:.2f}", "bytes": "0",
                "status": "low_score_or_no_match",
            }
            time.sleep(args.sleep)
            continue

        title_str = ""
        for tt in (best.get("titles") or []):
            if (tt.get("cid") or "") == jorftext:
                title_str = tt.get("title", "")
                break

        try:
            payload = client.consult_jorf(jorftext)
        except Exception as e:
            print(f"     ERROR consult: {e}")
            n_err += 1
            rows_by_key[key] = {
                "storage_key": key, "dossier_uid": t["dossier_uid"],
                "scrutin_id": t["scrutin_id"], "fecha_scrutin": t["fecha"],
                "titulo_scrutin": titulo, "jorf_text_id": jorftext,
                "title_matched": title_str, "match_score": f"{score:.2f}", "bytes": "0",
                "status": f"consult_error: {e}",
            }
            continue

        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        txt = extract_text_from_jorf(payload)
        txt_path.write_text(txt, encoding="utf-8")
        n_ok += 1
        print(f"     OK score={score:.2f} → {jorftext} ({len(txt)} bytes)")
        rows_by_key[key] = {
            "storage_key": key, "dossier_uid": t["dossier_uid"],
            "scrutin_id": t["scrutin_id"], "fecha_scrutin": t["fecha"],
            "titulo_scrutin": titulo, "jorf_text_id": jorftext,
            "title_matched": title_str, "match_score": f"{score:.2f}",
            "bytes": str(len(txt)), "status": "ok",
        }
        time.sleep(args.sleep)

    write_index(list(rows_by_key.values()))
    print("\n" + "=" * 60)
    print("Resumen Fase 1:")
    print(f"  OK:                       {n_ok}")
    print(f"  Saltados (ya existían):   {n_skip}")
    print(f"  No-promulgables:          {n_skipped_non_prom}")
    print(f"  Sin match aceptable:      {n_nofound}")
    print(f"  Errores:                  {n_err}")
    print(f"  Total:                    {len(targets)}")
    print(f"  Índice:                   {INDEX_CSV}")
    print("=" * 60)
    print("\nSiguiente paso: parchear build_leyes_texte_oficial.py para que también")
    print("cargue <dossier_uid>.txt, y luego re-correrlo.")


if __name__ == "__main__":
    main()
