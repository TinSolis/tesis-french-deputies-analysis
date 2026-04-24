#!/usr/bin/env python3
"""
Construye tablas de TODAS las votaciones de adopción de loi (projet / proposition)
de la XVe législature (2017-2022) y TODOS los votos individuales por diputado.

Fuentes en lois_votes/votes_rd/ (tras download + unzip):
  - Scrutins_XV.json (o dentro de Scrutins_XV.json.zip)
  - Opcional: Dossiers_Legislatifs_XV.json (enriquece metadatos del dossier)

Salida en lois_votes/votes_rd/processed/:
  - leyes_votadas_2017_2022.csv   — un scrutin de adopción de ley por fila
  - votos_por_diputado.csv        — todos los votos (todos los acteurs PA* del scrutin)
  - votos_por_diputado_cohorte.csv — mismo contenido filtrado a ids en deputes_2017_2022.csv

Uso (desde francia_deputies):
  python3 lois_votes/scripts/build_laws_and_votes.py
  python3 lois_votes/scripts/build_laws_and_votes.py --sin-filtro-fechas   # incluye scrutins sin fecha parseable
"""

import argparse
import csv
import json
import re
import zipfile
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
VOTES_RD_DIR = LOIS_VOTES_DIR / "votes_rd"
DATA_DIR = VOTES_RD_DIR
PROCESSED_DIR = VOTES_RD_DIR / "processed"
# Carpeta francia_deputies (padre de lois_votes)
FRANCIA_DEPUTIES_DIR = LOIS_VOTES_DIR.parent
DEPUTIES_CSV = FRANCIA_DEPUTIES_DIR / "datos_diputados" / "processed" / "deputes_2017_2022.csv"

# XVe législature (dates officielles approx.)
LEGISLATURE_START = date(2017, 6, 27)
LEGISLATURE_END = date(2022, 6, 21)

OUT_LAWS = "leyes_votadas_2017_2022.csv"
OUT_VOTES_ALL = "votos_por_diputado.csv"
OUT_VOTES_COHORT = "votos_por_diputado_cohorte.csv"


def extract_pa_id(uid):
    """Extrae id numérico del acteur AN (PA720916 -> 720916)."""
    if not uid:
        return ""
    s = str(uid).strip()
    m = re.search(r"PA(\d+)", s, re.I)
    return m.group(1) if m else s


def load_deputy_ids():
    """Set de deputy_id que existen en deputes_2017_2022.csv."""
    ids = set()
    if not DEPUTIES_CSV.exists():
        print(f"Aviso: no se encuentra {DEPUTIES_CSV} (cohorte vacía).")
        return ids
    with open(DEPUTIES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            i = (row.get("id") or "").strip()
            if i:
                ids.add(i)
    return ids


def _as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return [x]
    return []


def load_scrutins_monolithic():
    """Carga un único JSON agregado (formato antiguo AN)."""
    zip_path = DATA_DIR / "Scrutins_XV.json.zip"
    json_path = DATA_DIR / "Scrutins_XV.json"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            names = [n for n in z.namelist() if n.endswith(".json")]
            if not names:
                raise FileNotFoundError(f"No hay .json dentro de {zip_path}")
            # Formato actual: solo json/VTANR5L15V*.json → descomprimir y leer la carpeta
            if names and all("VTAN" in n.upper() for n in names):
                return None
            pick = next(
                (n for n in names if "Scrutins" in n and "VTAN" not in n.upper()),
                names[0],
            )
            with z.open(pick) as f:
                return json.load(f)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def iter_all_scrutins():
    """
    Itera todos los scrutins: JSON monolítico, o uno por archivo json/VTAN*.json
    (formato actual open data AN, tras descomprimir Scrutins_XV.json.zip).
    """
    data = load_scrutins_monolithic()
    if data is not None:
        yield from iter_scrutins(data)
        return

    per_dir = DATA_DIR / "json"
    if per_dir.is_dir():
        paths = sorted(per_dir.glob("VTAN*.json"))
        if paths:
            for p in paths:
                try:
                    with open(p, encoding="utf-8") as f:
                        obj = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    print(f"Aviso: omito {p.name}: {e}")
                    continue
                s = obj.get("scrutin", obj)
                if isinstance(s, dict):
                    yield s
            return

    raise FileNotFoundError(
        f"No hay scrutins en {DATA_DIR}.\n"
        "Descarga y descomprime Scrutins_XV.json.zip en votes_rd/ "
        "(debe existir votes_rd/json/VTAN*.json) o coloca Scrutins_XV.json.\n"
        "Ejecuta: python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py"
    )


def iter_scrutins(data):
    """Itera sobre cada scrutin. Acepta varias estructuras posibles del JSON."""
    if isinstance(data, dict):
        lst = data.get("scrutins", data)
        if isinstance(lst, dict):
            lst = lst.get("scrutin", lst)
        if isinstance(lst, list):
            for s in lst:
                yield s
            return
        if isinstance(lst, dict):
            yield lst
            return
    if isinstance(data, list):
        for s in data:
            yield s


def get_scrutin_id(s):
    return str(s.get("numero") or s.get("uid") or s.get("scrutinId") or s.get("id") or "")


def get_scrutin_titre(s):
    t = s.get("titre")
    if t and not isinstance(t, dict):
        return str(t).strip()
    obj = s.get("objet")
    if isinstance(obj, dict):
        lib = obj.get("libelle") or obj.get("#text") or ""
        if lib:
            return str(lib).strip()
    t = s.get("titre") or s.get("libelle") or s.get("titulaire") or ""
    if isinstance(t, dict):
        t = t.get("#text", t.get("libelle", ""))
    return (t or "").strip()


def get_scrutin_date_raw(s):
    d = s.get("dateScrutin") or s.get("date") or ""
    if isinstance(d, dict):
        d = d.get("#text", "")
    return (d or "").strip()


def parse_scrutin_date(raw: str):
    """
    Devuelve date o None. Formatos habituales AN: YYYY-MM-DD, DD/MM/YYYY.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw[:19] if "T" in raw else raw[:10], fmt[: len(fmt)]).date()
        except ValueError:
            continue
    # Solo parte fecha si viene con hora
    if len(raw) >= 10 and raw[4] == "-":
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    return None


def get_dossier_ref(s):
    """Referencia dossier législatif si existe en el scrutin."""
    for key in ("dossierLegislatif", "dossier", "titreDossier", "uidDossier"):
        v = s.get(key)
        if v is None:
            continue
        if isinstance(v, dict):
            v = v.get("uid") or v.get("#text") or v.get("ref") or ""
        if v:
            return str(v).strip()
    return ""
           

def is_law_adoption_scrutin(titre: str) -> bool:
    """
    Votación sobre el texto legislativo global (no enmiendas sueltas).
    Incluye «l'ensemble du projet / de la proposition de loi» y frases d'adoption explicites.
    """
    t = titre.lower().replace("’", "'")
    # Excluir scrutin sobre amendements / articles aislados
    if t.startswith("l'amendement ") or t.startswith("le sous-amendement "):
        return False
    if t.startswith("l'article ") or t.startswith("les articles "):
        return False

    has_texte = (
        "projet de loi" in t
        or "proposition de loi" in t
        or ("loi organique" in t and "projet" in t)
    )
    if not has_texte and "ratification" in t and "projet de loi" in t:
        has_texte = True
    if not has_texte:
        return False

    # Vote sur l'intégralité du texte (lecture) — criterio principal
    if "l'ensemble" in t:
        return True
    # Adoption explicite du texte (éviter «réformer l'adoption» dans un amendement)
    if "adoption du projet de loi" in t or "adoption de la proposition de loi" in t:
        return True
    if "adoption d'un projet de loi" in t or "adoption d'une proposition de loi" in t:
        return True
    return False


def _is_xml_style_ventilation(vent) -> bool:
    return isinstance(vent, dict) and "organe" in vent


def collect_votes_xml_style(s):
    """Formato open data AN: ventilationVotes.organe.groupes.groupe[].vote.decompteNominatif."""
    by_dep = {}
    vent = s.get("ventilationVotes") or {}
    if not _is_xml_style_ventilation(vent):
        return list(by_dep.items())
    organe = vent.get("organe") or {}
    groupes = organe.get("groupes") or {}
    groupe_list = _as_list(groupes.get("groupe"))
    mapping = (
        ("nonVotants", "NonVotant"),
        ("pours", "Pour"),
        ("contres", "Contre"),
        ("abstentions", "Abstention"),
    )
    for g in groupe_list:
        if not isinstance(g, dict):
            continue
        vote = g.get("vote") or {}
        deco = vote.get("decompteNominatif") or {}
        for key, label in mapping:
            bucket = deco.get(key)
            if not bucket or not isinstance(bucket, dict):
                continue
            votant = bucket.get("votant")
            for a in _as_list(votant):
                if not isinstance(a, dict):
                    continue
                uid = a.get("acteurRef") or a.get("uid") or ""
                if isinstance(uid, dict):
                    uid = uid.get("#text", "")
                pid = extract_pa_id(str(uid))
                if pid:
                    by_dep[pid] = label
    return list(by_dep.items())


def collect_votes_from_scrutin(s):
    """Extrae (acteur_id_num, vote) por diputado. vote = Pour|Contre|Abstention|NonVotant.
    Prioridad: ventilationVotes; voteIndividuel solo rellena actores ausentes."""
    vent = s.get("ventilationVotes", s.get("ventilation", {}))
    if _is_xml_style_ventilation(vent):
        return collect_votes_xml_style(s)

    by_dep = {}

    if isinstance(vent, dict):
        for vote_type in ("pour", "contre", "abstention", "nonVotant", "nonInscrit"):
            group = vent.get(vote_type, vent.get(vote_type.capitalize(), {}))
            if not isinstance(group, dict):
                continue
            acteurs = group.get("acteur", group.get("acteurs", []))
            if not isinstance(acteurs, list):
                acteurs = [acteurs] if acteurs else []
            for a in acteurs:
                if not isinstance(a, dict):
                    continue
                uid = a.get("uid", a.get("acteurRef", a.get("id", "")))
                if isinstance(uid, dict):
                    uid = uid.get("#text", "")
                pid = extract_pa_id(uid)
                if pid:
                    v = {"nonInscrit": "NonVotant", "nonVotant": "NonVotant"}.get(
                        vote_type, vote_type.capitalize()
                    )
                    by_dep[pid] = v

    ind = s.get("voteIndividuel", s.get("votes", {}))
    if isinstance(ind, dict):
        ind = ind.get("vote", [])
    if isinstance(ind, list):
        for v in ind:
            if not isinstance(v, dict):
                continue
            uid = v.get("acteurRef", v.get("uid", v.get("acteur", "")))
            if isinstance(uid, dict):
                uid = uid.get("#text", "")
            vote_lib = (v.get("vote", v.get("position", "")) or "").strip()
            if isinstance(vote_lib, dict):
                vote_lib = (vote_lib.get("#text") or "").strip()
            if not vote_lib:
                continue
            pid = extract_pa_id(uid)
            if not pid:
                continue
            if pid in by_dep:
                continue
            vote_lib = str(vote_lib).replace(" ", "").lower()
            if "pour" in vote_lib:
                by_dep[pid] = "Pour"
            elif "contre" in vote_lib:
                by_dep[pid] = "Contre"
            elif "abstention" in vote_lib:
                by_dep[pid] = "Abstention"
            else:
                by_dep[pid] = "NonVotant"

    return list(by_dep.items())


def main():
    parser = argparse.ArgumentParser(description="Exporta leyes + votos XVe législature.")
    parser.add_argument(
        "--sin-filtro-fechas",
        action="store_true",
        help="Incluir scrutins de adopción aunque la fecha no esté en 2017-06-27 … 2022-06-21.",
    )
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deputy_ids = load_deputy_ids()
    print(f"Diputados en deputes_2017_2022.csv: {len(deputy_ids)}")

    try:
        scrutin_iter = iter_all_scrutins()
    except FileNotFoundError as e:
        print(e)
        return

    adoption_scrutins = []
    for s in scrutin_iter:
        titre = get_scrutin_titre(s)
        if not is_law_adoption_scrutin(titre):
            continue
        d_raw = get_scrutin_date_raw(s)
        d_parsed = parse_scrutin_date(d_raw)
        if not args.sin_filtro_fechas and d_parsed is not None:
            if d_parsed < LEGISLATURE_START or d_parsed > LEGISLATURE_END:
                continue
        adoption_scrutins.append((d_parsed or date.min, get_scrutin_id(s), s))

    # Un solo registro por scrutin_id (el JSON no debería duplicar; por si acaso)
    by_id = {}
    for d_parsed, sid, s in adoption_scrutins:
        sid = sid or get_scrutin_id(s)
        if not sid:
            continue
        if sid not in by_id or d_parsed >= by_id[sid][0]:
            by_id[sid] = (d_parsed, s)

    ordered = sorted(by_id.values(), key=lambda x: (x[0], x[1].get("numero", "")))

    laws_rows = []
    votes_all = []
    votes_cohort = []

    for d_parsed, s in ordered:
        scrut_id = str(get_scrutin_id(s))
        titre = get_scrutin_titre(s)
        d_raw = get_scrutin_date_raw(s)
        dossier = get_dossier_ref(s)
        laws_rows.append(
            {
                "scrutin_id": scrut_id,
                "titulo": titre,
                "fecha": d_raw,
                "fecha_iso": d_parsed.isoformat() if d_parsed and d_parsed != date.min else "",
                "dossier_ref": dossier,
            }
        )
        for dep_id, vote in collect_votes_from_scrutin(s):
            row = {"deputy_id": dep_id, "scrutin_id": scrut_id, "vote": vote}
            votes_all.append(row)
            if dep_id in deputy_ids:
                votes_cohort.append(row)

    law_fields = ["scrutin_id", "titulo", "fecha", "fecha_iso", "dossier_ref"]
    vote_fields = ["deputy_id", "scrutin_id", "vote"]

    with open(PROCESSED_DIR / OUT_LAWS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=law_fields)
        w.writeheader()
        w.writerows(laws_rows)

    with open(PROCESSED_DIR / OUT_VOTES_ALL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vote_fields)
        w.writeheader()
        w.writerows(votes_all)

    with open(PROCESSED_DIR / OUT_VOTES_COHORT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vote_fields)
        w.writeheader()
        w.writerows(votes_cohort)

    print(f"Leyes (scrutins d'adoption, période {LEGISLATURE_START} – {LEGISLATURE_END}): {len(laws_rows)}")
    print(f"  → {PROCESSED_DIR / OUT_LAWS}")
    print(f"Votos (tous les députés dans les scrutins): {len(votes_all)}")
    print(f"  → {PROCESSED_DIR / OUT_VOTES_ALL}")
    print(f"Votos (cohorte deputes_2017_2022): {len(votes_cohort)}")
    print(f"  → {PROCESSED_DIR / OUT_VOTES_COHORT}")


if __name__ == "__main__":
    main()
