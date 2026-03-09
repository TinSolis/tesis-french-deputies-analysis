#!/usr/bin/env python3
"""
Construye leyes_50.csv y votos_por_diputado.csv a partir de Scrutins_XV (y opcionalmente
Dossiers_Legislatifs_XV). Cruza con deputes_2017_2022.csv para quedarnos solo con
nuestros diputados.

Espera en lois_votes/data/:
  - Scrutins_XV.json (o Scrutins_XV.json.zip)
  - Opcional: Dossiers_Legislatifs_XV.json

Salida en lois_votes/processed/:
  - leyes_50.csv: scrutin_id, titulo, fecha
  - votos_por_diputado.csv: deputy_id, scrutin_id, vote (Pour/Contre/Abstention/NonVotant)

Uso (desde francia_deputies):
  python3 lois_votes/scripts/build_laws_and_votes.py
"""

import csv
import json
import re
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOIS_VOTES_DIR = SCRIPT_DIR.parent
DATA_DIR = LOIS_VOTES_DIR / "data"
PROCESSED_DIR = LOIS_VOTES_DIR / "processed"
FRANCIA_DIR = LOIS_VOTES_DIR.parent.parent
DEPUTIES_CSV = FRANCIA_DIR / "datos_diputados" / "processed" / "deputes_2017_2022.csv"
NUM_LAWS = 50


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
        return ids
    with open(DEPUTIES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            i = (row.get("id") or "").strip()
            if i:
                ids.add(i)
    return ids


def load_scrutins_json():
    """Carga el JSON de scrutins desde data/ (zip o json)."""
    # Buscar zip o json
    zip_path = DATA_DIR / "Scrutins_XV.json.zip"
    json_path = DATA_DIR / "Scrutins_XV.json"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            names = [n for n in z.namelist() if n.endswith(".json")]
            if not names:
                raise FileNotFoundError(f"No hay .json dentro de {zip_path}")
            with z.open(names[0]) as f:
                return json.load(f)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(
        f"Coloca Scrutins_XV.json o Scrutins_XV.json.zip en {DATA_DIR}"
    )


def iter_scrutins(data):
    """Itera sobre cada scrutin. Acepta varias estructuras posibles del JSON."""
    if isinstance(data, dict):
        # Puede ser { "scrutins": { "scrutin": [ ... ] } } o { "scrutin": [ ... ] }
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
    """Obtiene identificador del scrutin."""
    return (
        s.get("numero") or s.get("uid") or s.get("scrutinId") or s.get("id") or ""
    )


def get_scrutin_titre(s):
    """Obtiene título/objet del scrutin."""
    t = s.get("titre") or s.get("objet") or s.get("libelle") or s.get("titulaire") or ""
    if isinstance(t, dict):
        t = t.get("#text", t.get("libelle", ""))
    return (t or "").strip()


def get_scrutin_date(s):
    """Obtiene fecha del scrutin."""
    d = s.get("dateScrutin") or s.get("date") or ""
    if isinstance(d, dict):
        d = d.get("#text", "")
    return (d or "").strip()


def collect_votes_from_scrutin(s):
    """Extrae (acteur_id_num, vote) para cada voto. vote = Pour|Contre|Abstention|NonVotant."""
    out = []
    # Estructura típica: ventilationVotes con pour, contre, abstention, nonVotant, cada uno con acteurs
    vent = s.get("ventilationVotes", s.get("ventilation", {}))
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
                    out.append((pid, v))
    # Alternativa: voteIndividuel con lista de { acteurRef, vote }
    ind = s.get("voteIndividuel", s.get("votes", {}))
    if isinstance(ind, dict):
        ind = ind.get("vote", [])
    if isinstance(ind, list) and not out:
        for v in ind:
            if not isinstance(v, dict):
                continue
            uid = v.get("acteurRef", v.get("uid", v.get("acteur", "")))
            if isinstance(uid, dict):
                uid = uid.get("#text", "")
            vote_lib = (v.get("vote", v.get("position", "")) or "").strip()
            if not vote_lib:
                continue
            pid = extract_pa_id(uid)
            if pid:
                # Normalizar valor
                vote_lib = vote_lib.replace(" ", "").lower()
                if "pour" in vote_lib:
                    out.append((pid, "Pour"))
                elif "contre" in vote_lib:
                    out.append((pid, "Contre"))
                elif "abstention" in vote_lib:
                    out.append((pid, "Abstention"))
                else:
                    out.append((pid, "NonVotant"))
    return out


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deputy_ids = load_deputy_ids()
    print(f"Diputados en deputes_2017_2022: {len(deputy_ids)}")

    try:
        data = load_scrutins_json()
    except FileNotFoundError as e:
        print(e)
        print("Ejecuta antes: python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py")
        print("y descomprime Scrutins_XV.json.zip en data/ si hace falta.")
        return

    # Seleccionar scrutins de "Adoption" (leyes)
    adoption_scrutins = []
    for s in iter_scrutins(data):
        titre = get_scrutin_titre(s)
        if titre and "adoption" in titre.lower() and ("loi" in titre.lower() or "projet" in titre.lower() or "proposition" in titre.lower()):
            adoption_scrutins.append(s)
            if len(adoption_scrutins) >= NUM_LAWS * 2:
                break

    # Quedarnos con NUM_LAWS (por ejemplo los primeros 50 por fecha o orden)
    adoption_scrutins = adoption_scrutins[:NUM_LAWS]
    if len(adoption_scrutins) < NUM_LAWS:
        print(f"Aviso: solo se encontraron {len(adoption_scrutins)} scrutins de adopción (objetivo {NUM_LAWS}).")

    # Escribir leyes_50.csv
    laws_rows = []
    votes_rows = []
    for s in adoption_scrutins:
        scrut_id = str(get_scrutin_id(s))
        titre = get_scrutin_titre(s)
        date = get_scrutin_date(s)
        laws_rows.append({"scrutin_id": scrut_id, "titulo": titre, "fecha": date})
        for dep_id, vote in collect_votes_from_scrutin(s):
            if dep_id in deputy_ids:
                votes_rows.append({"deputy_id": dep_id, "scrutin_id": scrut_id, "vote": vote})

    with open(PROCESSED_DIR / "leyes_50.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["scrutin_id", "titulo", "fecha"])
        w.writeheader()
        w.writerows(laws_rows)

    with open(PROCESSED_DIR / "votos_por_diputado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["deputy_id", "scrutin_id", "vote"])
        w.writeheader()
        w.writerows(votes_rows)

    print(f"Leyes (scrutins de adopción): {len(laws_rows)} → {PROCESSED_DIR / 'leyes_50.csv'}")
    print(f"Votos (solo diputados en tu CSV): {len(votes_rows)} → {PROCESSED_DIR / 'votos_por_diputado.csv'}")


if __name__ == "__main__":
    main()
