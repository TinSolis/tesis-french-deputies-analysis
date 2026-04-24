#!/usr/bin/env python3
"""
Lee los TSV.gz Regards Citoyens en hemicycle/fuente/, detecta la legislatura
(_ND13_, _ND15_, etc.), texto plano de la intervención y —solo ND15 (XVe 2017-2022)—
cruce con datos_diputados/processed/deputes_2017_2022.csv.

Para análisis de tesis (ND15), además del CSV completo genera:
  - meta sin texto largo (uniones, NLP aparte)
  - tabla id → texto
  - muestra .csv sin comprimir para abrir en editor / Excel

Ejecutar desde francia_deputies:
  python3 hemicycle/scripts/build_interventions_with_deputies.py
"""

from __future__ import annotations

import csv
import gzip
import re
from contextlib import ExitStack
import unicodedata
from html import unescape
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HEMICYCLE_DIR = SCRIPT_DIR.parent
FRANCIA_DEPUTIES = HEMICYCLE_DIR.parent
FUENTE_DIR = HEMICYCLE_DIR / "fuente"
DEPUTIES_CSV = FRANCIA_DEPUTIES / "datos_diputados" / "processed" / "deputes_2017_2022.csv"
PROCESSED_DIR = HEMICYCLE_DIR / "processed"
RE_ND = re.compile(r"_ND(\d+)_", re.IGNORECASE)
RE_HTML_TAGS = re.compile(r"<[^>]+>")
# Ex.: .../15/cri/2016-2017/20170124.asp#P980120
RE_AN_CRI = re.compile(
    r"assemblee-nationale\.fr/(\d+)/cri/([^/]+)/([^#?\s]+)(?:#([^\s]*))?",
    re.IGNORECASE,
)

LEGISLATURE_LABELS: dict[int, str] = {
    13: "XIIIe législature (2007-2012)",
    14: "XIVe législature (2012-2017)",
    15: "XVe législature (2017-2022)",
    16: "XVIe législature (2022-2027)",
}

OUT_XV = PROCESSED_DIR / "interventions_xv_2017_2022_with_deputies.csv.gz"
OUT_XV_META = PROCESSED_DIR / "interventions_xv_2017_2022_meta.csv.gz"
OUT_XV_TEXTS = PROCESSED_DIR / "interventions_xv_2017_2022_texts.csv.gz"
OUT_XV_SAMPLE = PROCESSED_DIR / "interventions_xv_sample5000.csv"
OUT_OTHER = PROCESSED_DIR / "interventions_xiii_xiv_xvi_speaker_text.csv.gz"

SAMPLE_MAX = 5000

XV_FIELDNAMES = [
    "legislature_num",
    "legislature_label",
    "source_filename",
    "intervention_id",
    "seance_id",
    "date",
    "moment",
    "type",
    "section",
    "sous_section",
    "timestamp",
    "intervention_plain",
    "nb_mots",
    "personnalite",
    "parlementaire",
    "parlementaire_sexe",
    "parlementaire_groupe",
    "fonction",
    "source_url",
    "cri_url_legislature_num",
    "cri_session_period",
    "cri_page_file",
    "cri_anchor_id",
    "deputy_id",
    "deputy_full_name",
    "deputy_family_name",
    "deputy_first_name",
    "deputy_gender",
    "birth_date",
    "birth_place",
    "political_group_abbrev",
    "political_group",
    "dept_num",
    "district_name",
    "district_num",
    "mandate_start",
    "mandate_end",
    "former_deputy",
    "twitter_handle",
    "twitter_id",
    "twitter_verified",
]

META_FIELDNAMES = [c for c in XV_FIELDNAMES if c != "intervention_plain"]

OTHER_FIELDNAMES = [
    "legislature_num",
    "legislature_label",
    "source_filename",
    "intervention_id",
    "seance_id",
    "date",
    "moment",
    "type",
    "section",
    "sous_section",
    "timestamp",
    "intervention_plain",
    "nb_mots",
    "personnalite",
    "parlementaire",
    "parlementaire_sexe",
    "parlementaire_groupe",
    "fonction",
    "source_url",
]


def normalize_name(s: str) -> str:
    if not s or str(s).strip().upper() == "NULL":
        return ""
    s = unicodedata.normalize("NFKD", str(s).strip())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s).lower()
    return s


def strip_html(html: str) -> str:
    if not html or str(html).strip().upper() == "NULL":
        return ""
    t = RE_HTML_TAGS.sub(" ", str(html))
    t = unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def parse_cri_url(url: str) -> dict[str, str]:
    """Fragmentos útiles del URL Compte rendu intégral (AN)."""
    out = {
        "cri_url_legislature_num": "",
        "cri_session_period": "",
        "cri_page_file": "",
        "cri_anchor_id": "",
    }
    if not url:
        return out
    m = RE_AN_CRI.search(url.replace("http://", "https://"))
    if not m:
        return out
    out["cri_url_legislature_num"] = m.group(1) or ""
    out["cri_session_period"] = m.group(2) or ""
    out["cri_page_file"] = m.group(3) or ""
    frag = (m.group(4) or "").strip()
    if frag.startswith("#"):
        frag = frag[1:]
    out["cri_anchor_id"] = frag
    return out


def load_deputies_by_full_name() -> dict[str, dict[str, str]]:
    by_full: dict[str, dict[str, str]] = {}
    with open(DEPUTIES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            key = normalize_name(row.get("full_name", ""))
            if key and key not in by_full:
                by_full[key] = row
    return by_full


def null_cell(v: str | None) -> str:
    if v is None or str(v).strip().upper() == "NULL":
        return ""
    return str(v).strip()


def empty_deputy_block() -> dict[str, str]:
    return {
        "deputy_id": "",
        "deputy_full_name": "",
        "deputy_family_name": "",
        "deputy_first_name": "",
        "deputy_gender": "",
        "birth_date": "",
        "birth_place": "",
        "political_group_abbrev": "",
        "political_group": "",
        "dept_num": "",
        "district_name": "",
        "district_num": "",
        "mandate_start": "",
        "mandate_end": "",
        "former_deputy": "",
        "twitter_handle": "",
        "twitter_id": "",
        "twitter_verified": "",
    }


def deputy_fields_from_csv(dep: dict[str, str]) -> dict[str, str]:
    return {
        "deputy_id": dep.get("id", ""),
        "deputy_full_name": dep.get("full_name", ""),
        "deputy_family_name": dep.get("family_name", ""),
        "deputy_first_name": dep.get("first_name", ""),
        "deputy_gender": dep.get("gender", ""),
        "birth_date": dep.get("birth_date", ""),
        "birth_place": dep.get("birth_place", ""),
        "political_group_abbrev": dep.get("political_group_abbrev", ""),
        "political_group": dep.get("political_group", ""),
        "dept_num": dep.get("dept_num", ""),
        "district_name": dep.get("district_name", ""),
        "district_num": dep.get("district_num", ""),
        "mandate_start": dep.get("mandate_start", ""),
        "mandate_end": dep.get("mandate_end", ""),
        "former_deputy": dep.get("former_deputy", ""),
        "twitter_handle": dep.get("twitter_handle", ""),
        "twitter_id": dep.get("twitter_id", ""),
        "twitter_verified": dep.get("twitter_verified", ""),
    }


def _legislature_num_from_filename(path: Path) -> int | None:
    m = RE_ND.search(path.name)
    return int(m.group(1)) if m else None


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    by_full = load_deputies_by_full_name()
    files = sorted(FUENTE_DIR.glob("*_ND*_interventions_hemicycle_rich.tsv.gz"))
    if not files:
        raise SystemExit(
            f"No se encontraron *_ND*_interventions_hemicycle_rich.tsv.gz en {FUENTE_DIR}"
        )

    write_other_legs = False
    for p in files:
        n = _legislature_num_from_filename(p)
        if n is not None and n != 15:
            write_other_legs = True
            break

    n_xv = 0
    n_other = 0
    n_xv_unmatched = 0
    n_sample = 0

    with ExitStack() as stack:
        fxv = stack.enter_context(
            gzip.open(OUT_XV, "wt", encoding="utf-8", newline="")
        )
        fmeta = stack.enter_context(
            gzip.open(OUT_XV_META, "wt", encoding="utf-8", newline="")
        )
        ftext = stack.enter_context(
            gzip.open(OUT_XV_TEXTS, "wt", encoding="utf-8", newline="")
        )
        fsample = stack.enter_context(
            open(OUT_XV_SAMPLE, "w", encoding="utf-8", newline="")
        )
        wxv = csv.DictWriter(fxv, fieldnames=XV_FIELDNAMES, extrasaction="ignore")
        wmeta = csv.DictWriter(fmeta, fieldnames=META_FIELDNAMES, extrasaction="ignore")
        wtext = csv.DictWriter(
            ftext, fieldnames=["intervention_id", "intervention_plain"]
        )
        wsample = csv.DictWriter(
            fsample, fieldnames=XV_FIELDNAMES, extrasaction="ignore"
        )
        wxv.writeheader()
        wmeta.writeheader()
        wtext.writeheader()
        wsample.writeheader()

        woth = None
        if write_other_legs:
            foth = stack.enter_context(
                gzip.open(OUT_OTHER, "wt", encoding="utf-8", newline="")
            )
            woth = csv.DictWriter(foth, fieldnames=OTHER_FIELDNAMES, extrasaction="ignore")
            woth.writeheader()

        for path in files:
            m = RE_ND.search(path.name)
            if not m:
                print(f"Omitido (sin _NDn_ en nombre): {path.name}")
                continue
            leg_num = int(m.group(1))
            label = LEGISLATURE_LABELS.get(
                leg_num, f"{leg_num}e législature (ND{leg_num})"
            )
            print(f"Procesando {path.name} → législature {leg_num}: {label}")

            with gzip.open(path, "rt", encoding="utf-8", newline="") as raw:
                reader = csv.DictReader(raw, delimiter="\t")
                for row in reader:
                    parl = null_cell(row.get("parlementaire"))
                    plain = strip_html(row.get("intervention") or "")
                    source_url = null_cell(row.get("source"))
                    base_other = {
                        "legislature_num": str(leg_num),
                        "legislature_label": label,
                        "source_filename": path.name,
                        "intervention_id": null_cell(row.get("id")),
                        "seance_id": null_cell(row.get("seance_id")),
                        "date": null_cell(row.get("date")),
                        "moment": null_cell(row.get("moment")),
                        "type": null_cell(row.get("type")),
                        "section": null_cell(row.get("section")),
                        "sous_section": null_cell(row.get("sous_section")),
                        "timestamp": null_cell(row.get("timestamp")),
                        "intervention_plain": plain,
                        "nb_mots": null_cell(row.get("nb_mots")),
                        "personnalite": null_cell(row.get("personnalite")),
                        "parlementaire": parl,
                        "parlementaire_sexe": null_cell(row.get("parlementaire_sexe")),
                        "parlementaire_groupe": null_cell(
                            row.get("parlementaire_groupe")
                        ),
                        "fonction": null_cell(row.get("fonction")),
                        "source_url": source_url,
                    }

                    if leg_num != 15:
                        if woth is None:
                            raise SystemExit(
                                f"Archivo {path.name} es legislatura != 15 pero en fuente/ "
                                "no había ningún ND13/14/16 al inicio; revisá los nombres o añadí esos TSV."
                            )
                        woth.writerow(base_other)
                        n_other += 1
                        continue

                    cri = parse_cri_url(source_url)
                    dep = by_full.get(normalize_name(parl)) if parl else None
                    out_xv = {**base_other, **cri}
                    if dep:
                        out_xv.update(deputy_fields_from_csv(dep))
                    else:
                        out_xv.update(empty_deputy_block())
                        if parl:
                            n_xv_unmatched += 1

                    wxv.writerow(out_xv)
                    wmeta.writerow({k: out_xv[k] for k in META_FIELDNAMES})
                    wtext.writerow(
                        {
                            "intervention_id": out_xv["intervention_id"],
                            "intervention_plain": plain,
                        }
                    )
                    if n_sample < SAMPLE_MAX:
                        wsample.writerow(out_xv)
                        n_sample += 1
                    n_xv += 1

    print()
    print(f"XV (ND15) filas: {n_xv}")
    print(f"  → {OUT_XV.relative_to(FRANCIA_DEPUTIES)}")
    print(f"  → {OUT_XV_META.relative_to(FRANCIA_DEPUTIES)} (sin columna texto)")
    print(f"  → {OUT_XV_TEXTS.relative_to(FRANCIA_DEPUTIES)} (id + texto)")
    print(
        f"  → {OUT_XV_SAMPLE.relative_to(FRANCIA_DEPUTIES)} (muestra {SAMPLE_MAX} filas, sin comprimir)"
    )
    if n_xv_unmatched:
        print(
            f"  Aviso: {n_xv_unmatched} filas con parlementaire sin match en deputes_2017_2022.csv"
        )
    if write_other_legs:
        print(
            f"Otras legislaturas filas: {n_other} → {OUT_OTHER.relative_to(FRANCIA_DEPUTIES)}"
        )
    elif OUT_OTHER.is_file():
        print(
            f"Otras legislaturas: no se regeneró {OUT_OTHER.name} "
            "(solo hay ND15 en fuente/; el archivo anterior se conserva)."
        )
    else:
        print(
            "Otras legislaturas: no hay salida agregada (añadí ND13/14/16 en fuente/ y volvé a ejecutar)."
        )


if __name__ == "__main__":
    main()
