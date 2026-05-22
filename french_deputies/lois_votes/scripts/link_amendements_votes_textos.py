#!/usr/bin/env python3
"""
Une los 3.126 votos de enmiendas con sus textos completos.

Insumos:
  - votes_rd/processed/amendements_votados.csv   (un scrutin x fila + titulo)
  - votes_rd/processed/amendements_textos.csv    (311k enmiendas con texto)
  - votes_rd/Dossiers_Legislatifs_XV.json.zip    (catalogo de dossiers)

Estrategia:
  1. Indexar todos los dossiers por su titulo normalizado.
  2. Para cada scrutin de enmienda, hacer fuzzy match titulo del scrutin
     contra titulos de dossier -> elegir dossier_uid mas probable.
  3. Dentro de ese dossier, buscar la(s) enmienda(s) con el mismo
     amendement_num.
  4. Si hay varias (lecturas distintas), preferir la mas cercana a la fecha
     del scrutin (date_sort vs fecha del vote).

Salida:
  - votes_rd/processed/amendements_votos_con_texto.csv
        un scrutin x fila, con texto de la enmienda + metadata + confianza
"""

import csv
import json
import re
import sys
import unicodedata
import zipfile
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

csv.field_size_limit(sys.maxsize)

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
VOTES_RD = LOIS_VOTES_DIR / "votes_rd"
PROCESSED = VOTES_RD / "processed"
DOSSIERS_ZIP = VOTES_RD / "Dossiers_Legislatifs_XV.json.zip"

IN_VOTES = PROCESSED / "amendements_votados.csv"
IN_TEXTOS = PROCESSED / "amendements_textos.csv"
OUT_CSV = PROCESSED / "amendements_votos_con_texto.csv"

STOPWORDS = {
    "de", "du", "des", "le", "la", "les", "l", "d", "et", "a", "au", "aux",
    "pour", "par", "sur", "en", "ou", "sans", "dans", "ce", "cette", "ces",
    "un", "une", "qui", "que",
    # palabras genericas que no aportan al matching
    "projet", "proposition", "loi", "organique",
    "premiere", "deuxieme", "nouvelle", "lecture",
}


def normalize(s: str) -> str:
    if not s:
        return ""
    s = s.lower().replace("\u2019", "'").replace("\u2018", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokens(s: str) -> set:
    return {t for t in normalize(s).split() if t and t not in STOPWORDS}


def parse_date(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S+%f"):
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
    return None


# ---------------------------- Cargar dossiers ----------------------------
def load_dossiers(zip_path: Path) -> dict:
    """Devuelve dict dossier_uid -> {titulo, tokens_set, procedure}."""
    if not zip_path.exists():
        print(f"No existe {zip_path}")
        sys.exit(1)
    out = {}
    with zipfile.ZipFile(zip_path, "r") as z:
        names = [n for n in z.namelist() if n.endswith(".json")]
        for name in names:
            with z.open(name) as f:
                obj = json.load(f)
            d = obj.get("dossierParlementaire", obj)
            uid = d.get("uid")
            tit = d.get("titreDossier", {})
            if isinstance(tit, dict):
                titulo = tit.get("titre", "") or ""
            else:
                titulo = str(tit or "")
            procedure = ""
            proc = d.get("procedureParlementaire")
            if isinstance(proc, dict):
                procedure = proc.get("libelle", "")
            if uid:
                out[uid] = {
                    "titulo": titulo.strip(),
                    "tokens": tokens(titulo),
                    "procedure": procedure,
                }
    print(f"Dossiers cargados: {len(out)}")
    return out


# ---------------------------- Cargar enmiendas ---------------------------
NUM_RECT_RE = re.compile(r"^(\d+)\s*\(\s*rect[^)]*\)$", re.IGNORECASE)


def normalize_amend_num(num: str) -> list:
    """
    Devuelve todas las representaciones bajo las que conviene indexar el
    numero. Ej.: '199 (Rect)' -> ['199 (Rect)', '199'].
    """
    num = (num or "").strip()
    if not num:
        return []
    keys = {num, num.lstrip("0") or num}
    m = NUM_RECT_RE.match(num)
    if m:
        base = m.group(1).lstrip("0") or m.group(1)
        keys.add(base)
    return list(keys)


def load_amendments_index(textos_csv: Path) -> dict:
    """
    Devuelve indice:
        (dossier_uid, numero_str) -> list[dict de amendement_textos]

    Indexamos cada enmienda bajo varias claves:
      - su numeroLong tal cual
      - su numeroLong sin sufijo "(Rect)"
      - su numeroOrdreDepot (clave que usan los scrutins para leyes de
        finanzas, donde numeroLong es 'I-2076' pero el voto dice '2076')
    Asi cubrimos los diferentes esquemas de numeracion.
    """
    idx = defaultdict(list)
    n = 0
    with open(textos_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n += 1
            dossier = row.get("dossier_uid", "")
            if not dossier:
                continue
            keys = set()
            for raw in (row.get("numero", ""), row.get("numero_depot", "")):
                for k in normalize_amend_num(raw):
                    keys.add(k)
            for k in keys:
                idx[(dossier, k)].append(row)
    print(f"Enmiendas en CSV : {n}")
    print(f"Claves (dossier, numero): {len(idx)}")
    return idx


# ---------------- Matching scrutin -> dossier_uid ------------------------
def best_dossier_match(scrutin_tokens: set, dossiers: dict, min_overlap: int = 2):
    """
    Devuelve (dossier_uid, score 0..1) o (None, 0).
    Score = |interseccion| / |union| (Jaccard).
    """
    if not scrutin_tokens:
        return None, 0.0
    best = (None, 0.0)
    for uid, d in dossiers.items():
        dtoks = d["tokens"]
        if not dtoks:
            continue
        inter = scrutin_tokens & dtoks
        if len(inter) < min_overlap:
            continue
        union = scrutin_tokens | dtoks
        score = len(inter) / len(union)
        if score > best[1]:
            best = (uid, score)
    return best


def pick_amendment(candidates: list, target_date) -> dict:
    """De varios candidatos por (dossier, numero), elige el mas cercano a la fecha."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    if not target_date:
        return candidates[0]
    best = None
    best_diff = None
    for c in candidates:
        d = parse_date(c.get("date_sort") or c.get("date_publication") or c.get("date_depot"))
        if d is None:
            continue
        diff = abs((d - target_date).days)
        if best_diff is None or diff < best_diff:
            best_diff = diff
            best = c
    return best or candidates[0]


def main():
    dossiers = load_dossiers(DOSSIERS_ZIP)
    amend_idx = load_amendments_index(IN_TEXTOS)

    # IMPORTANTE: muchos dossiers del catalogo no tienen amendments asociados
    # (4980 en el catalogo vs 437 con carpeta de enmiendas). Restringimos el
    # universo de matching a los que SI tienen enmiendas, para no matchear
    # con un dossier "homologo" sin texto.
    dossiers_con_amend = {k[0] for k in amend_idx.keys()}
    dossiers = {uid: d for uid, d in dossiers.items() if uid in dossiers_con_amend}
    print(f"Dossiers con enmiendas en XML    : {len(dossiers)}")

    title_cache: dict = {}

    n_total = 0
    n_dossier_ok = 0
    n_amend_ok = 0
    confidence_buckets = defaultdict(int)

    out_fields = [
        "scrutin_id",
        "fecha",
        "sort_voto",
        "amendement_num",
        "es_sous_amendement",
        "es_identiques",
        "demandeur",
        "article_ref",
        "ley_tipo",
        "ley_titulo_corto",
        "titulo_scrutin",
        # del XML de la enmienda:
        "dossier_uid_matched",
        "dossier_titulo",
        "match_score",
        "match_confianza",
        "amendement_uid",
        "texte_legislatif_ref",
        "auteur_type",
        "auteur_ref",
        "signataires_libelle",
        "n_cosignataires",
        "article_titre",
        "sort_amend",
        "etat_amend",
        "date_depot",
        "date_publication",
        "dispositif",
        "expose_sommaire",
    ]

    with open(IN_VOTES, encoding="utf-8") as fi, \
         open(OUT_CSV, "w", newline="", encoding="utf-8") as fo:
        reader = csv.DictReader(fi)
        writer = csv.DictWriter(fo, fieldnames=out_fields)
        writer.writeheader()

        for r in reader:
            n_total += 1
            titulo_corto = r.get("ley_titulo_corto", "")
            cache_key = titulo_corto
            if cache_key in title_cache:
                dossier_uid, score = title_cache[cache_key]
            else:
                stoks = tokens(titulo_corto)
                dossier_uid, score = best_dossier_match(stoks, dossiers)
                title_cache[cache_key] = (dossier_uid, score)

            if dossier_uid:
                n_dossier_ok += 1

            # nivel de confianza segun score
            if score >= 0.6:
                confianza = "alta"
            elif score >= 0.4:
                confianza = "media"
            elif score >= 0.2:
                confianza = "baja"
            else:
                confianza = "ninguna"
            confidence_buckets[confianza] += 1

            num = (r.get("amendement_num") or "").strip().lstrip("0") or r.get("amendement_num")
            amend = None
            if dossier_uid and num:
                key = (dossier_uid, num)
                candidates = amend_idx.get(key, [])
                target = parse_date(r.get("fecha_iso") or r.get("fecha"))
                amend = pick_amendment(candidates, target)
                if amend:
                    n_amend_ok += 1

            row_out = {
                "scrutin_id": r.get("scrutin_id", ""),
                "fecha": r.get("fecha", ""),
                "sort_voto": r.get("sort", ""),
                "amendement_num": r.get("amendement_num", ""),
                "es_sous_amendement": r.get("es_sous_amendement", ""),
                "es_identiques": r.get("es_identiques", ""),
                "demandeur": r.get("demandeur", ""),
                "article_ref": r.get("article_ref", ""),
                "ley_tipo": r.get("ley_tipo", ""),
                "ley_titulo_corto": titulo_corto,
                "titulo_scrutin": r.get("titulo_scrutin", ""),
                "dossier_uid_matched": dossier_uid or "",
                "dossier_titulo": dossiers.get(dossier_uid, {}).get("titulo", "") if dossier_uid else "",
                "match_score": f"{score:.3f}",
                "match_confianza": confianza,
                "amendement_uid": amend.get("amendement_uid", "") if amend else "",
                "texte_legislatif_ref": amend.get("texte_legislatif_ref", "") if amend else "",
                "auteur_type": amend.get("auteur_type", "") if amend else "",
                "auteur_ref": amend.get("auteur_ref", "") if amend else "",
                "signataires_libelle": amend.get("signataires_libelle", "") if amend else "",
                "n_cosignataires": amend.get("n_cosignataires", "") if amend else "",
                "article_titre": amend.get("article_titre", "") if amend else "",
                "sort_amend": amend.get("sort", "") if amend else "",
                "etat_amend": amend.get("sous_etat", "") if amend else "",
                "date_depot": amend.get("date_depot", "") if amend else "",
                "date_publication": amend.get("date_publication", "") if amend else "",
                "dispositif": amend.get("dispositif", "") if amend else "",
                "expose_sommaire": amend.get("expose_sommaire", "") if amend else "",
            }
            writer.writerow(row_out)

    print()
    print(f"Scrutins de enmienda procesados : {n_total}")
    print(f"Con dossier matcheado            : {n_dossier_ok} ({100*n_dossier_ok/max(1,n_total):.0f}%)")
    print(f"Con texto de enmienda encontrado : {n_amend_ok} ({100*n_amend_ok/max(1,n_total):.0f}%)")
    print()
    print("Confianza del match titulo->dossier:")
    for k in ("alta", "media", "baja", "ninguna"):
        v = confidence_buckets.get(k, 0)
        print(f"  {k:8s}: {v:5d} ({100*v/max(1,n_total):.0f}%)")
    print()
    print(f"Salida: {OUT_CSV}")
    print(f"        {OUT_CSV.stat().st_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    main()
