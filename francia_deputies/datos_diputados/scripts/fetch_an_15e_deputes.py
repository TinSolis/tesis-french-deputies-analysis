#!/usr/bin/env python3
"""
Descarga los datos oficiales de diputados de la 15ª legislatura (2017-2022)
desde data.assemblee-nationale.fr y genera data/deputes_an_rd.csv.

Uso (desde francia_deputies): python3 datos_diputados/scripts/fetch_an_15e_deputes.py
ZIP se busca/guarda en datos_diputados/data/.
"""

import csv
import json
import re
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ZIP_URL = "https://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip"
ZIP_NAME = "AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip"
OUTPUT_CSV = DATA_DIR / "deputes_an_rd.csv"


def download_zip():
    zip_path = DATA_DIR / ZIP_NAME
    if zip_path.exists():
        print(f"Usando ZIP existente: {zip_path}")
        return zip_path
    if not requests:
        print("Instala 'requests' para descarga automática: pip install requests")
        return None
    print(f"Descargando {ZIP_URL} ...")
    r = requests.get(ZIP_URL, timeout=60)
    r.raise_for_status()
    zip_path.write_bytes(r.content)
    print(f"Guardado: {zip_path}")
    return zip_path


def extract_id_an(uid):
    if not uid:
        return ""
    if isinstance(uid, dict) and "#text" in uid:
        uid = uid["#text"]
    m = re.search(r"PA(\d+)", str(uid), re.I)
    return m.group(1) if m else ""


def _text_or_empty(val):
    if val is None:
        return ""
    if isinstance(val, dict):
        if "#text" in val:
            return str(val["#text"] or "")
        if "@xsi:nil" in val:
            return ""
    return str(val)


def load_organes_gp(z):
    gp = {}
    for name in z.namelist():
        if "organe/" not in name or not name.endswith(".json"):
            continue
        try:
            with z.open(name) as f:
                o = json.load(f)
            org = o.get("organe", o)
            ct = org.get("codeType")
            if isinstance(ct, dict) and "#text" in ct:
                ct = ct["#text"]
            if ct != "GP":
                continue
            uid = org.get("uid")
            if isinstance(uid, dict) and "#text" in uid:
                uid = uid["#text"]
            lib = org.get("libelle") or ""
            lib_ab = org.get("libelleAbrev") or org.get("libelleAbrege") or ""
            if isinstance(lib, dict):
                lib = lib.get("#text", "")
            if isinstance(lib_ab, dict):
                lib_ab = lib_ab.get("#text", "")
            if uid:
                gp[str(uid)] = {"abbrev": _text_or_empty(lib_ab), "name": _text_or_empty(lib)}
        except (json.JSONDecodeError, KeyError):
            continue
    return gp


def parse_acteur_an(act, organes_gp=None):
    if not isinstance(act, dict):
        return None
    organes_gp = organes_gp or {}
    ec = act.get("etatCivil", {}) or {}
    ident = ec.get("ident", {}) or {}
    info_naiss = ec.get("infoNaissance", {}) or {}
    nom = _text_or_empty(ident.get("nom", ""))
    prenom = _text_or_empty(ident.get("prenom", ""))
    nom_complet = f"{prenom} {nom}".strip()
    date_naiss = _text_or_empty(info_naiss.get("dateNais", ""))
    ville = info_naiss.get("villeNais") or info_naiss.get("depNais") or {}
    lieu_naiss = _text_or_empty(ville.get("#text")) if isinstance(ville, dict) else str(ville)
    if not lieu_naiss and isinstance(info_naiss.get("paysNais"), dict):
        lieu_naiss = _text_or_empty(info_naiss["paysNais"].get("#text"))
    civ = ident.get("civ", "")
    sexe = "F" if civ and "Mme" in str(civ) else ("H" if civ else "")
    mandats = act.get("mandats", {}) or {}
    mandat_list = mandats.get("mandat", [])
    if not isinstance(mandat_list, list):
        mandat_list = [mandat_list] if mandat_list else []
    mandat_debut = mandat_fin = num_circo = num_dept = nom_circo = ""
    for m in mandat_list:
        if not isinstance(m, dict) or m.get("typeOrgane") != "ASSEMBLEE":
            continue
        mandat_debut = _text_or_empty(m.get("dateDebut", "")) or mandat_debut
        mandat_fin = _text_or_empty(m.get("dateFin", "")) or mandat_fin
        elec = m.get("election", {}) or {}
        lieu = elec.get("lieu", {}) or {}
        if isinstance(lieu, dict):
            num_dept = _text_or_empty(lieu.get("numDepartement", "")) or num_dept
            num_circo = _text_or_empty(lieu.get("numCirco", "")) or num_circo
            nom_circo = _text_or_empty(lieu.get("departement", "")) or nom_circo
        break
    political_group_abbrev = ""
    political_group = ""
    for m in mandat_list:
        if not isinstance(m, dict) or m.get("typeOrgane") != "GP":
            continue
        deb = _text_or_empty(m.get("dateDebut", ""))
        fin = _text_or_empty(m.get("dateFin", ""))
        if not deb or deb > "2022-06-21" or (fin and fin < "2017-06-18"):
            continue
        ref = (m.get("organes") or {})
        if isinstance(ref, dict):
            ref = ref.get("organeRef", "")
        if ref and ref in organes_gp:
            g = organes_gp[ref]
            political_group_abbrev = g.get("abbrev", "")
            political_group = g.get("name", "")
            break
    uid = act.get("uid", "")
    id_an = extract_id_an(uid)
    if not id_an and not (nom or prenom):
        return None
    return {
        "id": id_an or "",
        "full_name": nom_complet,
        "family_name": nom,
        "first_name": prenom,
        "gender": sexe,
        "birth_date": date_naiss,
        "birth_place": lieu_naiss,
        "dept_num": num_dept,
        "district_name": nom_circo,
        "district_num": num_circo,
        "mandate_start": mandat_debut,
        "mandate_end": mandat_fin,
        "former_deputy": "1" if mandat_fin else "0",
        "political_group_abbrev": political_group_abbrev,
        "political_group": political_group,
    }


def run():
    zip_path = download_zip()
    if not zip_path or not zip_path.exists():
        print(f"Coloca {ZIP_NAME} en {DATA_DIR} y vuelve a ejecutar.")
        return

    rows = []
    with zipfile.ZipFile(zip_path, "r") as z:
        organes_gp = load_organes_gp(z)
        names = [n for n in z.namelist() if n.endswith(".json") and "acteur" in n]
        if names:
            for json_name in names:
                try:
                    with z.open(json_name) as f:
                        data = json.load(f)
                    act = data.get("acteur", data) if isinstance(data, dict) else None
                    if not act:
                        continue
                    row = parse_acteur_an(act, organes_gp)
                    if row and (row.get("mandate_start") or row.get("district_num")) and (row.get("full_name") or row.get("family_name") or row.get("first_name")):
                        rows.append(row)
                except (json.JSONDecodeError, KeyError):
                    continue
        else:
            json_name = next((n for n in z.namelist() if n.endswith(".json")), z.namelist()[0] if z.namelist() else None)
            if not json_name:
                print("No se encontró JSON en el ZIP")
                return
            with z.open(json_name) as f:
                data = json.load(f)
            exp = data.get("export", data)
            acteurs_data = exp.get("acteurs", exp.get("acteur", {}))
            acteurs = acteurs_data.get("acteur", acteurs_data.get("acteurs", [])) if isinstance(acteurs_data, dict) else (acteurs_data if isinstance(acteurs_data, list) else [])
            if not isinstance(acteurs, list):
                acteurs = [acteurs] if acteurs else []
            for a in acteurs:
                row = parse_acteur_an(a, organes_gp)
                if row and (row.get("full_name") or row.get("family_name") or row.get("first_name")):
                    rows.append(row)

    if not rows:
        print("No se encontraron acteurs.")
        return

    fieldnames = [
        "id", "full_name", "family_name", "first_name", "gender", "birth_date", "birth_place",
        "dept_num", "district_name", "district_num", "mandate_start", "mandate_end",
        "former_deputy", "political_group_abbrev", "political_group",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"Escritos {len(rows)} diputados en {OUTPUT_CSV}")


if __name__ == "__main__":
    run()
