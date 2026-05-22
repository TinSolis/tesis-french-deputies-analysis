#!/usr/bin/env python3
"""
Parsea los 311k archivos XML de enmiendas y produce una sola tabla.

Cada archivo XML tiene una enmienda con:
  - identificador unico (uid)
  - texto del proyecto/proposicion de ley al que se aplica (texteLegislatifRef)
  - dossier legislativo (extraido del path del archivo)
  - numero de la enmienda (numeroLong) <-- clave para linkear con votos
  - autor principal y cosignatarios
  - articulo afectado
  - texto del cambio propuesto (dispositif)
  - exposicion de motivos (exposeSommaire)
  - resultado final (sort: Adopte / Rejete / Retire / ...)

Salida: lois_votes/votes_rd/processed/amendements_textos.csv

Tiempo estimado: 5-10 min con ~5000 archivos/segundo.
"""

import csv
import html
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
AMEND_XML_DIR = LOIS_VOTES_DIR / "votes_rd" / "Amendements" / "xml"
PROCESSED_DIR = LOIS_VOTES_DIR / "votes_rd" / "processed"
OUT_CSV = PROCESSED_DIR / "amendements_textos.csv"

NS = {"a": "http://schemas.assemblee-nationale.fr/referentiel"}
TAG_PREFIX = "{http://schemas.assemblee-nationale.fr/referentiel}"

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def strip_html(s: str) -> str:
    """Quita tags HTML y normaliza entidades / espacios."""
    if not s:
        return ""
    s = html.unescape(s)
    s = html.unescape(s)
    s = HTML_TAG_RE.sub(" ", s)
    s = s.replace("\u00a0", " ").replace("\u2019", "'")
    s = WHITESPACE_RE.sub(" ", s).strip()
    return s


def find_text(el, path: str) -> str:
    """Busca un elemento con namespace y devuelve su texto."""
    if el is None:
        return ""
    parts = path.split("/")
    cur = el
    for p in parts:
        if cur is None:
            return ""
        cur = cur.find(TAG_PREFIX + p)
    if cur is None:
        return ""
    return (cur.text or "").strip()


def find_all_text(el, path: str) -> list:
    """Devuelve todos los textos en un path (para listas como cosignataires)."""
    if el is None:
        return []
    parts = path.split("/")
    cur_list = [el]
    for p in parts:
        new = []
        for c in cur_list:
            new.extend(c.findall(TAG_PREFIX + p))
        cur_list = new
    return [(c.text or "").strip() for c in cur_list]


def parse_amend(xml_path: Path, dossier_uid: str, texte_leg_uid: str):
    """Parsea un archivo XML de enmienda."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        return None

    root = tree.getroot()

    uid = find_text(root, "uid")
    numero = find_text(root, "identification/numeroLong")
    numero_depot = find_text(root, "identification/numeroOrdreDepot")
    numero_rect = find_text(root, "identification/numeroRect")
    auteur_type = find_text(root, "signataires/auteur/typeAuteur")
    auteur_ref = find_text(root, "signataires/auteur/acteurRef")
    gouvernement_ref = find_text(root, "signataires/auteur/gouvernementRef")
    signataires_libelle = strip_html(find_text(root, "signataires/libelle"))
    cosignataires = find_all_text(root, "signataires/cosignataires/acteurRef")
    cosignataires_str = ";".join(cosignataires)

    article_titre = find_text(root, "pointeurFragmentTexte/division/titre")
    article_type = find_text(root, "pointeurFragmentTexte/division/type")
    avant_apres = find_text(root, "pointeurFragmentTexte/division/avant_A_Apres")

    dispositif = strip_html(find_text(root, "corps/contenuAuteur/dispositif"))
    expose = strip_html(find_text(root, "corps/contenuAuteur/exposeSommaire"))

    date_depot = find_text(root, "cycleDeVie/dateDepot")
    date_pub = find_text(root, "cycleDeVie/datePublication")
    date_sort = find_text(root, "cycleDeVie/dateSort")
    sort = find_text(root, "cycleDeVie/sort")
    etat = find_text(root, "cycleDeVie/etatDesTraitements/etat/libelle")
    sous_etat = find_text(root, "cycleDeVie/etatDesTraitements/sousEtat/libelle")

    return {
        "amendement_uid": uid,
        "dossier_uid": dossier_uid,
        "texte_legislatif_ref": texte_leg_uid,
        "numero": numero,
        "numero_depot": numero_depot,
        "numero_rect": numero_rect,
        "auteur_type": auteur_type,
        "auteur_ref": auteur_ref,
        "gouvernement_ref": gouvernement_ref,
        "signataires_libelle": signataires_libelle,
        "cosignataires_refs": cosignataires_str,
        "n_cosignataires": str(len(cosignataires)),
        "article_titre": article_titre,
        "article_type": article_type,
        "avant_apres": avant_apres,
        "sort": sort,
        "etat": etat,
        "sous_etat": sous_etat,
        "date_depot": date_depot,
        "date_publication": date_pub,
        "date_sort": date_sort,
        "dispositif_len": str(len(dispositif)),
        "expose_len": str(len(expose)),
        "dispositif": dispositif,
        "expose_sommaire": expose,
    }


def main():
    if not AMEND_XML_DIR.exists():
        print(f"No existe: {AMEND_XML_DIR}")
        print("Descomprime Amendements_XV.xml.zip en esa carpeta primero.")
        sys.exit(1)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "amendement_uid",
        "dossier_uid",
        "texte_legislatif_ref",
        "numero",
        "numero_depot",
        "numero_rect",
        "auteur_type",
        "auteur_ref",
        "gouvernement_ref",
        "signataires_libelle",
        "cosignataires_refs",
        "n_cosignataires",
        "article_titre",
        "article_type",
        "avant_apres",
        "sort",
        "etat",
        "sous_etat",
        "date_depot",
        "date_publication",
        "date_sort",
        "dispositif_len",
        "expose_len",
        "dispositif",
        "expose_sommaire",
    ]

    n_ok = 0
    n_err = 0
    n_xv = 0
    t0 = time.time()
    last_print = t0

    print(f"Recorriendo {AMEND_XML_DIR} ...")
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for dossier_dir in AMEND_XML_DIR.iterdir():
            if not dossier_dir.is_dir():
                continue
            dossier_uid = dossier_dir.name
            for texte_dir in dossier_dir.iterdir():
                if not texte_dir.is_dir():
                    continue
                texte_leg_uid = texte_dir.name
                # Filtramos solo la XVe legislature: las carpetas DLR5L14*
                # contienen tambien dossiers que arrancaron en la 14e pero
                # se discutieron en la 15e; igual los procesamos porque sus
                # texte_legislatif comienza con PIONANR5L15 o similar.
                if "5L15" not in texte_leg_uid:
                    continue

                for xml_path in texte_dir.glob("*.xml"):
                    try:
                        row = parse_amend(xml_path, dossier_uid, texte_leg_uid)
                    except Exception as e:
                        n_err += 1
                        continue
                    if row is None:
                        n_err += 1
                        continue
                    n_xv += 1
                    w.writerow(row)
                    n_ok += 1

                    now = time.time()
                    if now - last_print > 3:
                        rate = n_ok / (now - t0)
                        print(f"  {n_ok:7d} ok, {n_err:5d} err  ({rate:.0f}/s)")
                        last_print = now

    elapsed = time.time() - t0
    print()
    print(f"Procesados : {n_ok}")
    print(f"Errores XML: {n_err}")
    print(f"Tiempo     : {elapsed:.0f}s ({n_ok / max(1, elapsed):.0f} archivos/s)")
    print(f"Salida     : {OUT_CSV}")
    print(f"Tamano CSV : {OUT_CSV.stat().st_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    main()
