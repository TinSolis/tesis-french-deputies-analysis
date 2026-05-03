#!/usr/bin/env python3
"""
Lee los ndjson exportados por Zeeschuimer (Twitter/X) en zeeschuimer/captures/,
extrae ítems (tweets) y los cruza con deputes_2017_2022.csv por twitter_handle.
Escribe:
  - processed/tweets_with_deputies.csv (todas las columnas)
  - processed/tweets_text_only.csv (solo diputado + texto, para análisis)

Estructura del ndjson (Zeeschuimer reciente): cada línea tiene "data" con
data.core.user_results.result.core.screen_name, data.legacy.full_text,
data.note_tweet.note_tweet_results.result.text (texto largo).

Ejecutar desde francia_deputies: python3 zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ZEESCHUIMER_DIR = SCRIPT_DIR.parent
FRANCIA_DEPUTIES = ZEESCHUIMER_DIR.parent
CAPTURES_DIR = ZEESCHUIMER_DIR / "captures"
PROCESSED_DIR = ZEESCHUIMER_DIR / "processed"
DEPUTIES_CSV = FRANCIA_DEPUTIES / "datos_diputados" / "processed" / "deputes_2017_2022.csv"
OUT_CSV = PROCESSED_DIR / "tweets_with_deputies.csv"
OUT_TEXT_ONLY = PROCESSED_DIR / "tweets_text_only.csv"
OUT_SUMMARY = PROCESSED_DIR / "deputies_capture_summary.csv"

# Menciones: extraer del JSON (entities) y del texto (@handle)
RE_MENTION = re.compile(r"@([A-Za-z0-9_]{1,20})\b")


def _normalize_handle(handle):
    if not handle:
        return ""
    s = str(handle).strip().lower()
    if s.startswith("@"):
        s = s[1:]
    return s


def load_deputies_by_handle():
    """Carga deputes_2017_2022.csv indexado por twitter_handle (normalizado)."""
    by_handle = {}
    with open(DEPUTIES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            h = _normalize_handle(r.get("twitter_handle", ""))
            if h:
                by_handle[h] = dict(r)
    return by_handle


def extract_mentions_from_obj(obj, text):
    """
    Extrae handles mencionados: primero de data.legacy.entities.user_mentions (screen_name),
    luego del texto con regex @handle. Devuelve lista única normalizada (sin @).
    """
    mentions = set()
    data = obj.get("data") or {}
    legacy = data.get("legacy") or {}
    entities = legacy.get("entities") or {}
    for u in entities.get("user_mentions") or []:
        if isinstance(u, dict):
            sn = (u.get("screen_name") or "").strip()
            if sn:
                mentions.add(_normalize_handle(sn))
    for m in RE_MENTION.finditer(text or ""):
        mentions.add(_normalize_handle(m.group(1)))
    return sorted(mentions)


def extract_tweet_fields(obj):
    """
    Extrae autor y texto del ndjson de Zeeschuimer (formato con "data" anidado).
    Autor: data.core.user_results.result.core.screen_name o source_platform_url.
    Texto: data.legacy.full_text; si hay note_tweet, usar note_tweet_results.result.text (texto largo).
    """
    author = ""
    text = ""
    ts = ""
    tid = str(obj.get("item_id") or obj.get("id") or "")

    data = obj.get("data") or {}
    if data:
        core = data.get("core") or {}
        user_results = core.get("user_results") or {}
        result = user_results.get("result") or {}
        inner_core = result.get("core") or {}
        author = (inner_core.get("screen_name") or "").strip()
        legacy = data.get("legacy") or {}
        text = (legacy.get("full_text") or "").strip()
        ts = (legacy.get("created_at") or "").strip()
        note = data.get("note_tweet") or {}
        note_result = (note.get("note_tweet_results") or {}).get("result") or {}
        if isinstance(note_result, dict) and note_result.get("text"):
            text = (note_result.get("text") or "").strip() or text
    if not author and obj.get("source_platform_url"):
        m = re.search(r"(?:twitter\.com|x\.com)/([^/?]+)", str(obj["source_platform_url"]), re.I)
        if m:
            author = m.group(1)
    if not author:
        author = (
            obj.get("author_handle") or obj.get("author") or obj.get("username")
            or (obj.get("author_data", {}) or {}).get("username")
            or ""
        )
    if isinstance(author, dict):
        author = author.get("username") or author.get("handle") or ""
    if not text:
        text = obj.get("body") or obj.get("text") or obj.get("full_text") or ""
    if not ts:
        ts = obj.get("timestamp") or obj.get("created_at") or ""
    text = str(text)[:5000]
    mentions = extract_mentions_from_obj(obj, text)
    return {
        "author_handle": _normalize_handle(author) or author,
        "tweet_id": tid,
        "timestamp": str(ts),
        "text": text,
        "mentioned_handles": "; ".join(mentions) if mentions else "",
    }


def main():
    if not DEPUTIES_CSV.exists():
        print(f"No se encuentra {DEPUTIES_CSV}")
        return
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    deputies = load_deputies_by_handle()
    print(f"Cargados {len(deputies)} diputados con twitter_handle.")

    ndjson_files = list(CAPTURES_DIR.glob("*.ndjson"))
    if not ndjson_files:
        print(f"No hay archivos .ndjson en {CAPTURES_DIR}")
        print("Exporta primero datos desde Zeeschuimer a captures/.")
        return

    rows = []
    for path in sorted(ndjson_files):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                tw = extract_tweet_fields(obj)
                handle = tw.get("author_handle") or ""
                dep = deputies.get(_normalize_handle(handle)) if handle else None
                row = {
                    "tweet_id": tw.get("tweet_id", ""),
                    "timestamp": tw.get("timestamp", ""),
                    "text": tw.get("text", ""),
                    "author_handle": handle,
                    "mentioned_handles": tw.get("mentioned_handles", ""),
                }
                if dep:
                    row["deputy_id"] = dep.get("id", "")
                    row["full_name"] = dep.get("full_name", "")
                    row["twitter_name"] = dep.get("twitter_handle", "")
                    row["twitter_web_urls"] = dep.get("twitter_web_urls", "")
                    row["political_group_abbrev"] = dep.get("political_group_abbrev", "")
                    row["political_group"] = dep.get("political_group", "")
                else:
                    row["deputy_id"] = row["full_name"] = row["twitter_name"] = row["twitter_web_urls"] = ""
                    row["political_group_abbrev"] = row["political_group"] = ""
                rows.append(row)

    fieldnames = [
        "tweet_id", "timestamp", "text", "author_handle", "mentioned_handles",
        "deputy_id", "full_name", "twitter_name", "twitter_web_urls",
        "political_group_abbrev", "political_group",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # Solo texto + menciones para análisis
    text_only_fieldnames = [
        "deputy_id", "full_name", "twitter_name", "twitter_web_urls",
        "political_group_abbrev", "political_group",
        "mentioned_handles", "text",
    ]
    with open(OUT_TEXT_ONLY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=text_only_fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in text_only_fieldnames})

    # Resumen por diputado: id, full_name, twitter_name, twitter_web_urls, tweets_en_captura, top_mentions
    deputy_tweets = [r for r in rows if r.get("deputy_id")]
    dep_meta = {}
    dep_count = Counter()
    dep_mentions_per_dep = {}  # deputy_id -> Counter(handle -> count)
    for r in deputy_tweets:
        did = r.get("deputy_id", "")
        dep_count[did] += 1
        if did not in dep_meta:
            dep_meta[did] = {
                "full_name": r.get("full_name", ""),
                "twitter_name": r.get("twitter_name", ""),
                "twitter_web_urls": r.get("twitter_web_urls", ""),
            }
        if did not in dep_mentions_per_dep:
            dep_mentions_per_dep[did] = Counter()
        for h in (r.get("mentioned_handles") or "").split(";"):
            h = h.strip().lower()
            if h:
                dep_mentions_per_dep[did][h] += 1
    summary_rows = []
    for did in sorted(dep_meta.keys(), key=lambda x: -dep_count[x]):
        meta = dep_meta[did]
        top = [f"{h}:{c}" for h, c in dep_mentions_per_dep.get(did, {}).most_common(30)]
        top_str = "; ".join(top)
        summary_rows.append({
            "id": did,
            "full_name": meta["full_name"],
            "twitter_name": meta["twitter_name"],
            "twitter_web_urls": meta["twitter_web_urls"],
            "tweets_en_captura": dep_count[did],
            "top_mentions": top_str,
        })
    summary_fieldnames = ["id", "full_name", "twitter_name", "twitter_web_urls", "tweets_en_captura", "top_mentions"]
    with open(OUT_SUMMARY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fieldnames)
        w.writeheader()
        w.writerows(summary_rows)

    matched = len(deputy_tweets)
    print(f"Procesados {len(rows)} ítems de {len(ndjson_files)} archivo(s).")
    print(f"Con diputado asignado: {matched}.")
    print(f"  Completo (con menciones): {OUT_CSV}")
    print(f"  Texto + menciones: {OUT_TEXT_ONLY}")
    print(f"  Resumen por diputado (tweets en captura, top menciones): {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
