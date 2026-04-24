#!/usr/bin/env python3
"""
Descarga manifiestos de partidos franceses (elección legislativa 2017)
desde el Manifesto Project (MARPOR) vía su API REST.

Requisitos previos:
  1. Cuenta en https://manifesto-project.wzb.eu/ (gratis, email académico)
  2. API key generado desde tu perfil
  3. pip install requests

Uso (desde french_deputies/):
  export MARPOR_API_KEY="tu_api_key_aqui"
  python3 manifestos/scripts/download_manifestos.py

  # O pasando la key directamente:
  python3 manifestos/scripts/download_manifestos.py --api-key TU_KEY

Salidas en manifestos/:
  data/marpor_core_france_2017.csv        Dataset principal filtrado
  data/marpor_corpus_metadata.json        Metadatos del corpus
  processed/manifesto_texts.csv           Textos quasi-sentence por partido
  processed/party_positions.csv           Posiciones (rile, per_*) por partido
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Instala requests: pip install requests")

SCRIPT_DIR = Path(__file__).resolve().parent
MANIFESTO_DIR = SCRIPT_DIR.parent
DATA_DIR = MANIFESTO_DIR / "data"
PROCESSED_DIR = MANIFESTO_DIR / "processed"

API_BASE = "https://manifesto-project.wzb.eu/api/v1"
DATASET_VERSION = "MPDS2025a"

FRANCE_COUNTRY_CODE = 31
FRANCE_2017_EDATE = "200706"


def api_get(endpoint: str, api_key: str, params: dict | None = None) -> dict:
    p = {"api_key": api_key}
    if params:
        p.update(params)
    r = requests.get(f"{API_BASE}/{endpoint}", params=p, timeout=120)
    r.raise_for_status()
    return r.json()


def api_post(endpoint: str, api_key: str, data: dict) -> dict:
    data["api_key"] = api_key
    r = requests.post(f"{API_BASE}/{endpoint}", data=data, timeout=120)
    r.raise_for_status()
    return r.json()


# ── Step 1: download core dataset, filter France 2017 ───────────────

def download_core(api_key: str) -> list[dict]:
    print("[1/4] Descargando dataset principal (MARPOR)...")
    r = requests.get(
        f"{API_BASE}/get_core",
        params={"api_key": api_key, "key": DATASET_VERSION, "kind": "csv", "raw": "true"},
        timeout=300,
    )
    r.raise_for_status()

    text = r.text
    reader = csv.DictReader(io.StringIO(text))
    all_rows = list(reader)
    print(f"   Dataset completo: {len(all_rows)} filas")

    france_2017 = [
        row for row in all_rows
        if row.get("countryname", "").strip().lower() == "france"
        and "2017" in row.get("edate", "")
    ]
    print(f"   Francia 2017: {len(france_2017)} partidos")

    out = DATA_DIR / "marpor_core_france_2017.csv"
    if france_2017:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=france_2017[0].keys())
            w.writeheader()
            w.writerows(france_2017)
        print(f"   → {out.relative_to(MANIFESTO_DIR)}")
    else:
        print("   ⚠ No encontré filas para Francia 2017. Revisá el dataset.")

    return france_2017


# ── Step 2: build party keys for corpus query ───────────────────────

def build_keys(france_rows: list[dict]) -> list[tuple[str, str, str]]:
    """Returns list of (key, party_code, party_name)."""
    keys = []
    for row in france_rows:
        party = row.get("party", "").strip()
        date_col = row.get("date", "").strip()
        name = row.get("partyname", row.get("partyabbrev", party))
        if party and date_col:
            key = f"{party}_{date_col}"
            keys.append((key, party, name))
    print(f"\n[2/4] Keys para consultar el corpus: {len(keys)}")
    for k, _, n in keys:
        print(f"   {k}  ({n})")
    return keys


# ── Step 3: get metadata and texts ──────────────────────────────────

def get_corpus_version(api_key: str) -> str:
    resp = api_get("list_metadata_versions", api_key, {"tag": "true"})
    versions = resp.get("versions", resp) if isinstance(resp, dict) else resp
    tagged = [v for v in versions if v.get("tag")]
    latest = tagged[-1] if tagged else versions[-1]
    tag = latest.get("tag", latest.get("name", ""))
    print(f"   Versión corpus más reciente: {tag}")
    return tag


def get_metadata(api_key: str, keys: list[str], version: str) -> dict:
    print(f"\n[3/4] Consultando metadatos del corpus...")
    form_data = [("api_key", api_key), ("version", version)]
    for k in keys:
        form_data.append(("keys[]", k))

    r = requests.post(f"{API_BASE}/metadata", data=form_data, timeout=120)
    r.raise_for_status()
    result = r.json()

    items = result.get("items", [])
    missing = result.get("missing_items", [])
    print(f"   Metadatos encontrados: {len(items)}")
    if missing:
        print(f"   Sin metadatos: {missing}")

    out = DATA_DIR / "marpor_corpus_metadata.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"   → {out.relative_to(MANIFESTO_DIR)}")

    return result


def download_texts(api_key: str, metadata: dict, version: str) -> list[dict]:
    print(f"\n[4/4] Descargando textos del corpus...")
    items = metadata.get("items", [])

    manifesto_ids = []
    for item in items:
        mid = item.get("manifesto_id", "")
        has_text = item.get("annotations", False)
        name = item.get("party_name", item.get("manifesto_id", ""))
        status = "✓ texto" if has_text else "✗ sin texto digitalizado"
        print(f"   {mid:20s}  {name:40s}  [{status}]")
        if has_text and mid:
            manifesto_ids.append(mid)

    if not manifesto_ids:
        print("   ⚠ Ningún manifiesto tiene texto digitalizado disponible.")
        print("   Podés descargar los PDFs manualmente desde la web del Manifesto Project.")
        return []

    form_data = [("api_key", api_key), ("version", version)]
    for k in manifesto_ids:
        form_data.append(("keys[]", k))
    r = requests.post(
        f"{API_BASE}/texts_and_annotations",
        data=form_data,
        timeout=300,
    )
    r.raise_for_status()
    result = r.json()

    all_sentences = []
    for item in result.get("items", []):
        mid = item.get("key", item.get("manifesto_id", "unknown"))
        texts = item.get("items", [])
        for sent in texts:
            all_sentences.append({
                "manifesto_id": mid,
                "text": sent.get("text", ""),
                "cmp_code": sent.get("cmp_code", ""),
                "eu_code": sent.get("eu_code", ""),
            })
        print(f"   {mid}: {len(texts)} quasi-sentences")

    if all_sentences:
        out = PROCESSED_DIR / "manifesto_texts.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["manifesto_id", "text", "cmp_code", "eu_code"])
            w.writeheader()
            w.writerows(all_sentences)
        print(f"   → {out.relative_to(MANIFESTO_DIR)}")

    return all_sentences


# ── Step 5: extract party positions summary ─────────────────────────

POSITION_COLS = [
    "party", "partyname", "partyabbrev", "edate",
    "rile", "planeco", "markeco", "welfare", "intpeace",
]


def save_positions(france_rows: list[dict]):
    out = PROCESSED_DIR / "party_positions.csv"
    cols = []
    if france_rows:
        available = set(france_rows[0].keys())
        cols = [c for c in POSITION_COLS if c in available]
        if not cols:
            cols = list(france_rows[0].keys())

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in france_rows:
            w.writerow({c: row.get(c, "") for c in cols})
    print(f"\n   Posiciones → {out.relative_to(MANIFESTO_DIR)}")


# ── main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Descarga manifiestos Francia 2017 desde MARPOR")
    parser.add_argument("--api-key", default=None, help="API key (o usa MARPOR_API_KEY env var)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("MARPOR_API_KEY")
    if not api_key:
        sys.exit(
            "Necesito un API key del Manifesto Project.\n"
            "  export MARPOR_API_KEY='tu_key'\n"
            "  o: python3 download_manifestos.py --api-key TU_KEY\n\n"
            "Registrate gratis en https://manifesto-project.wzb.eu/"
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    france_rows = download_core(api_key)
    if not france_rows:
        return

    keys_info = build_keys(france_rows)
    keys = [k for k, _, _ in keys_info]

    corpus_version = get_corpus_version(api_key)
    metadata = get_metadata(api_key, keys, corpus_version)
    download_texts(api_key, metadata, corpus_version)
    save_positions(france_rows)

    print("\n── Listo ──")
    print(f"Archivos en {MANIFESTO_DIR.relative_to(MANIFESTO_DIR.parent)}/:")
    for p in sorted(DATA_DIR.glob("*")):
        print(f"  data/{p.name}")
    for p in sorted(PROCESSED_DIR.glob("*")):
        print(f"  processed/{p.name}")


if __name__ == "__main__":
    main()
