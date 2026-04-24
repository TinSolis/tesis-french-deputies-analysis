#!/usr/bin/env python3
"""
Lee salidas en hemicycle/processed/ y escribe RESUMEN_CUANTITATIVO.md
(narrativa + tablas breves). Ejecutar desde francia_deputies:

  python3 hemicycle/scripts/report_hemicycle_stats.py
"""

from __future__ import annotations

import csv
import gzip
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HEMICYCLE_DIR = SCRIPT_DIR.parent
FRANCIA_DEPUTIES = HEMICYCLE_DIR.parent
PROCESSED = HEMICYCLE_DIR / "processed"
META_XV = PROCESSED / "interventions_xv_2017_2022_meta.csv.gz"
OTHER = PROCESSED / "interventions_xiii_xiv_xvi_speaker_text.csv.gz"
LEYSES = (
    FRANCIA_DEPUTIES
    / "lois_votes"
    / "votes_rd"
    / "processed"
    / "leyes_votadas_2017_2022.csv"
)
OUT_MD = HEMICYCLE_DIR / "RESUMEN_CUANTITATIVO.md"


def count_rows_gz(path: Path) -> int:
    if not path.is_file():
        return 0
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def main() -> None:
    lines_out: list[str] = []
    if not META_XV.is_file():
        OUT_MD.write_text(
            "# Resumen cuantitativo\n\n"
            "Todavía no generé `processed/interventions_xv_2017_2022_meta.csv.gz`. "
            "Primero corro `python3 hemicycle/scripts/build_interventions_with_deputies.py`.\n",
            encoding="utf-8",
        )
        print(OUT_MD.read_text())
        return

    n_total = 0
    n_with_words = 0
    n_with_deputy = 0
    seances: set[str] = set()
    dates: set[str] = set()
    deputies_speaking: set[str] = set()
    types_c: Counter[str] = Counter()
    sections_nonempty: set[str] = set()
    sections_loi_hint: set[str] = set()

    with gzip.open(META_XV, "rt", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            n_total += 1
            try:
                nw = int(row.get("nb_mots") or 0)
            except ValueError:
                nw = 0
            if nw > 0:
                n_with_words += 1
            did = (row.get("deputy_id") or "").strip()
            if did:
                n_with_deputy += 1
                deputies_speaking.add(did)
            sid = (row.get("seance_id") or "").strip()
            if sid:
                seances.add(sid)
            d = (row.get("date") or "").strip()
            if d:
                dates.add(d)
            t = (row.get("type") or "").strip() or "(vacío)"
            types_c[t] += 1
            sec = (row.get("section") or "").strip()
            if sec and sec.upper() != "NULL":
                sections_nonempty.add(sec)
                low = sec.lower()
                if any(
                    k in low
                    for k in (
                        "loi",
                        "projet",
                        "budget",
                        "finances",
                        "réforme",
                        "europ",
                    )
                ):
                    sections_loi_hint.add(sec)

    n_other = count_rows_gz(OTHER)
    n_leyes_an = 0
    if LEYSES.is_file():
        with open(LEYSES, newline="", encoding="utf-8") as f:
            n_leyes_an = sum(1 for _ in csv.DictReader(f))

    top_types = types_c.most_common(12)
    lines_out.append("# Resumen cuantitativo (hemiciclo)\n\n")
    lines_out.append(
        "Yo calculé estas cifras a partir de **`interventions_xv_2017_2022_meta.csv.gz`** "
        "(XVe / ND15), más el conteo de otras legislaturas y de filas en mis leyes votadas cuando existía el archivo.\n\n"
    )
    lines_out.append("\n## Narrativa breve\n\n")
    lines_out.append(
        f"Tengo **{n_total:,}** intervenciones en el hemiciclo para la **XVe legislatura (2017–2022)** "
        f"en esta exportación. En **{n_with_words:,}** el acta marca al menos una palabra "
        f"(`nb_mots` > 0), que es lo que uso como señal de que hay texto analizable. "
        f"En **{n_with_deputy:,}** filas pude enlazar el orador con mi `deputes_2017_2022.csv` "
        f"(columna `deputy_id`); eso son **{len(deputies_speaking):,}** diputados distintos con al menos una intervención "
        f"en este corpus. Vi **{len(seances):,}** `seance_id` distintos y **{len(dates):,}** días "
        f"(`date`) distintos con actividad en el acta.\n\n"
    )
    lines_out.append(
        f"Los **tipos** de tramo más frecuentes en `type` los dejé en la tabla de abajo; "
        f"a mí me sirve ver cuánto cae bajo `loi` vs. `question`, pero eso **no reemplaza** leer el texto ni la sección.\n\n"
    )
    lines_out.append(
        f"En **`section`** conté **{len(sections_nonempty):,}** títulos distintos no vacíos. "
        f"**{len(sections_loi_hint):,}** de esos títulos contienen palabras que yo asocié a legislación "
        f"(«loi», «projet», «budget», etc.): es una **heurística mía** para ver cuánto del debate va explícitamente "
        f"etiquetado en esa lógica, no un conteo oficial de leyes del AN.\n\n"
    )
    if n_leyes_an:
        lines_out.append(
            f"Para comparar con mis votos: en `lois_votes/.../leyes_votadas_2017_2022.csv` tengo **{n_leyes_an:,}** filas "
            f"(scrutins de adopción en mi filtro). El vínculo hemiciclo ↔ ley concreta no viene como ID en esta tabla: "
            f"lo tengo que pensar yo con fechas, dossiers o lectura manual.\n\n"
        )
    if n_other:
        lines_out.append(
            f"También generé el agregado de **otras legislaturas** (XIIIe, XIVe, XVIe en un solo `.csv.gz`): "
            f"**{n_other:,}** intervenciones con texto y metadatos básicos, **sin** cruce a mi `deputes_2017_2022.csv`.\n\n"
        )

    lines_out.append("## Tipos (`type`) más frecuentes (XV)\n\n")
    lines_out.append("| Tipo | Intervenciones |\n")
    lines_out.append("|------|----------------:|\n")
    for t, c in top_types:
        tt = t.replace("|", "\\|")
        lines_out.append(f"| {tt} | {c:,} |\n")
    lines_out.append("\n---\n*Generado con `hemicycle/scripts/report_hemicycle_stats.py`.*\n")

    OUT_MD.write_text("".join(lines_out), encoding="utf-8")
    print(f"Escrito {OUT_MD.relative_to(FRANCIA_DEPUTIES)}")


if __name__ == "__main__":
    main()
