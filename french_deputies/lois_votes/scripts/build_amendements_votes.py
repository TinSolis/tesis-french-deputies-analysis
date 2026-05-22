#!/usr/bin/env python3
"""
Construye las tablas de votos sobre ENMIENDAS (amendements) de la XVe legislature.

Mientras que build_laws_and_votes.py extrae solo los votos globales sobre la
adopcion de cada ley (373 scrutins), este script saca los votos sobre cada
amendement individual (>3000 scrutins), util para detectar posturas
granulares (Manifesto / valores) y posibles cambios de voto durante la
tramitacion de un mismo proyecto.

Salida en lois_votes/votes_rd/processed/:
  - amendements_votados.csv               — un scrutin de amendement por fila
  - votos_amendements_por_diputado.csv    — todos los votos (todos los acteurs PA*)
  - votos_amendements_por_diputado_cohorte.csv — filtrado a deputes_2017_2022.csv

Uso (desde francia_deputies):
  python3 lois_votes/scripts/build_amendements_votes.py
"""

import csv
import re
from datetime import date
from pathlib import Path

# Reutilizamos toda la logica de carga / parseo de votos de build_laws_and_votes
from build_laws_and_votes import (
    LEGISLATURE_START,
    LEGISLATURE_END,
    PROCESSED_DIR,
    collect_votes_from_scrutin,
    get_dossier_ref,
    get_scrutin_date_raw,
    get_scrutin_id,
    get_scrutin_titre,
    iter_all_scrutins,
    load_deputy_ids,
    parse_scrutin_date,
)

OUT_AMEND = "amendements_votados.csv"
OUT_VOTES_ALL = "votos_amendements_por_diputado.csv"
OUT_VOTES_COHORT = "votos_amendements_por_diputado_cohorte.csv"

# ------------------------------ Regex de parseo ------------------------------
# Aceptamos varias variantes: "amendement n° 307", "sous-amendement n°4",
# "amendement de suppression n° 81", "amendement de redaction globale n° 1249".
PAT_AMEND = re.compile(
    r"\bamendement(?:\s+de\s+(?:suppression|redaction\s+globale|substitution))?\s*n[°o]?\s*(\d+)",
    re.IGNORECASE,
)
PAT_SOUSAMEND = re.compile(
    r"\bsous-?amendement\s*n[°o]?\s*(\d+)", re.IGNORECASE
)
PAT_IDENTIQUES = re.compile(r"amendements?\s+identiques?", re.IGNORECASE)
PAT_SUPPRESSION = re.compile(r"amendement\s+de\s+suppression", re.IGNORECASE)
PAT_REDACTION = re.compile(r"amendement\s+de\s+r[eé]daction\s+globale", re.IGNORECASE)

# Captura el demandeur (autor del amendement) entre "de" y "a/à l'article"
# Ejemplos: "de M. Roussel à l'article", "du Gouvernement à l'article",
# "de la commission des affaires sociales à l'article"
PAT_DEMANDEUR = re.compile(
    r"\bamendement(?:\s+de\s+(?:suppression|r[eé]daction\s+globale|substitution))?"
    r"\s*n[°o]?\s*\d+\s+(?:de|du|de\s+la|des)\s+(.+?)\s+(?:à|a)\s+l[''\u2019]article",
    re.IGNORECASE,
)

# Captura el numero de articulo ("article premier", "article 3", "article 4 bis")
PAT_ARTICLE = re.compile(
    r"[àa]\s+l[''\u2019]article\s+([^,()]+?)\s+(?:du|de\s+la|de)\s+(?:projet|proposition)\s+de\s+loi",
    re.IGNORECASE,
)

# Captura el titulo del proyecto/proposicion de ley
PAT_BILL_TITLE = re.compile(
    r"(projet\s+de\s+loi|proposition\s+de\s+loi)(?:\s+organique)?\s+(.+?)\s*(?:\([^)]+\))?\s*\.?\s*$",
    re.IGNORECASE,
)


def normalize_title_for_re(titre: str) -> str:
    return titre.replace("\u2019", "'").replace("\u2018", "'")


def is_amendement_scrutin(titre: str) -> bool:
    """
    True si el scrutin trata sobre un amendement (no sobre el voto global).
    """
    t = normalize_title_for_re(titre).lower()
    if "amendement" not in t and "sous-amendement" not in t:
        return False
    return True


def parse_amendement_fields(titre: str) -> dict:
    """
    Extrae campos estructurados del titulo del scrutin.
    """
    t = normalize_title_for_re(titre)

    sous_match = PAT_SOUSAMEND.search(t)
    amend_match = PAT_AMEND.search(t)
    art_match = PAT_ARTICLE.search(t)
    bill_match = PAT_BILL_TITLE.search(t)
    dem_match = PAT_DEMANDEUR.search(t)

    return {
        "amendement_num": amend_match.group(1) if amend_match else "",
        "sous_amendement_num": sous_match.group(1) if sous_match else "",
        "es_sous_amendement": bool(sous_match),
        "es_suppression": bool(PAT_SUPPRESSION.search(t)),
        "es_redaction_globale": bool(PAT_REDACTION.search(t)),
        "es_identiques": bool(PAT_IDENTIQUES.search(t)),
        "demandeur": dem_match.group(1).strip() if dem_match else "",
        "article_ref": art_match.group(1).strip() if art_match else "",
        "ley_tipo": (bill_match.group(1).lower() if bill_match else ""),
        "ley_titulo_corto": (bill_match.group(2).strip() if bill_match else ""),
    }


def get_scrutin_sort(s) -> str:
    """Sort del scrutin (adopté / rejeté)."""
    sort = s.get("sort")
    if isinstance(sort, dict):
        return (sort.get("code") or sort.get("libelle") or "").strip()
    return (sort or "").strip() if isinstance(sort, str) else ""


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deputy_ids = load_deputy_ids()
    print(f"Diputados en deputes_2017_2022.csv: {len(deputy_ids)}")

    try:
        scrutin_iter = iter_all_scrutins()
    except FileNotFoundError as e:
        print(e)
        return

    amend_scrutins = []
    n_skipped_unparsed = 0
    n_outside_dates = 0
    n_total_seen = 0

    for s in scrutin_iter:
        n_total_seen += 1
        titre = get_scrutin_titre(s)
        if not is_amendement_scrutin(titre):
            continue
        d_raw = get_scrutin_date_raw(s)
        d_parsed = parse_scrutin_date(d_raw)
        if d_parsed is not None and (
            d_parsed < LEGISLATURE_START or d_parsed > LEGISLATURE_END
        ):
            n_outside_dates += 1
            continue
        fields = parse_amendement_fields(titre)
        if not fields["amendement_num"] and not fields["sous_amendement_num"]:
            n_skipped_unparsed += 1
        amend_scrutins.append((d_parsed or date.min, s, fields))

    amend_rows = []
    votes_all = []
    votes_cohort = []
    n_amend_no_num = 0

    for d_parsed, s, fields in amend_scrutins:
        scrut_id = str(get_scrutin_id(s))
        titre = get_scrutin_titre(s)
        d_raw = get_scrutin_date_raw(s)
        dossier_ref = get_dossier_ref(s)
        sort = get_scrutin_sort(s)
        if not fields["amendement_num"] and not fields["sous_amendement_num"]:
            n_amend_no_num += 1

        amend_rows.append(
            {
                "scrutin_id": scrut_id,
                "fecha": d_raw,
                "fecha_iso": d_parsed.isoformat() if d_parsed and d_parsed != date.min else "",
                "sort": sort,
                "amendement_num": fields["amendement_num"],
                "sous_amendement_num": fields["sous_amendement_num"],
                "es_sous_amendement": int(fields["es_sous_amendement"]),
                "es_suppression": int(fields["es_suppression"]),
                "es_redaction_globale": int(fields["es_redaction_globale"]),
                "es_identiques": int(fields["es_identiques"]),
                "demandeur": fields["demandeur"],
                "article_ref": fields["article_ref"],
                "ley_tipo": fields["ley_tipo"],
                "ley_titulo_corto": fields["ley_titulo_corto"],
                "dossier_ref": dossier_ref,
                "titulo_scrutin": titre,
            }
        )

        for dep_id, vote in collect_votes_from_scrutin(s):
            row = {"deputy_id": dep_id, "scrutin_id": scrut_id, "vote": vote}
            votes_all.append(row)
            if dep_id in deputy_ids:
                votes_cohort.append(row)

    amend_fields = [
        "scrutin_id",
        "fecha",
        "fecha_iso",
        "sort",
        "amendement_num",
        "sous_amendement_num",
        "es_sous_amendement",
        "es_suppression",
        "es_redaction_globale",
        "es_identiques",
        "demandeur",
        "article_ref",
        "ley_tipo",
        "ley_titulo_corto",
        "dossier_ref",
        "titulo_scrutin",
    ]
    vote_fields = ["deputy_id", "scrutin_id", "vote"]

    with open(PROCESSED_DIR / OUT_AMEND, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=amend_fields)
        w.writeheader()
        w.writerows(amend_rows)

    with open(PROCESSED_DIR / OUT_VOTES_ALL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vote_fields)
        w.writeheader()
        w.writerows(votes_all)

    with open(PROCESSED_DIR / OUT_VOTES_COHORT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=vote_fields)
        w.writeheader()
        w.writerows(votes_cohort)

    print()
    print(f"Total scrutins recorridos        : {n_total_seen}")
    print(f"Scrutins sobre amendement        : {len(amend_rows)}")
    print(f"  - sin numero detectable (regex): {n_amend_no_num}  "
          f"({100*n_amend_no_num/max(1,len(amend_rows)):.0f}%)")
    print(f"  - fuera del rango de fechas    : {n_outside_dates}")
    print(f"Votos individuales totales       : {len(votes_all)}")
    print(f"Votos en la cohorte de la tesis  : {len(votes_cohort)}")
    print()
    print(f"  -> {PROCESSED_DIR / OUT_AMEND}")
    print(f"  -> {PROCESSED_DIR / OUT_VOTES_ALL}")
    print(f"  -> {PROCESSED_DIR / OUT_VOTES_COHORT}")


if __name__ == "__main__":
    main()
