"""
Extracción de triples (sujeto, predicado, objeto) al estilo KG-Gen
(Mo et al., 2025, arxiv:2502.09956) sobre el subset acotado.

Implementación minimal: en lugar de instalar el paquete kg-gen (que
requiere Python 3.10+ y DSPy), replicamos su pipeline esencial
mediante llamadas directas a un LLM local (Ollama + qwen2.5:3b).
Esto mantiene el demo 100% gratis, offline y reproducible.

Métricas reportadas:
  - tiempo por intervención
  - tiempo total
  - extrapolación al corpus completo de intervenciones (n=205.940)
  - extrapolación al corpus completo de las 5 fuentes (n≈466.000)
"""
import json
import re
import time
from pathlib import Path

import pandas as pd
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "sample_interventions.csv"
OUT_TRIPLES = ROOT / "results" / "triples.csv"
OUT_TIMING = ROOT / "results" / "timing.json"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"
TEMPERATURE = 0.0

CORPUS_INTERVENCIONES = 205_940
CORPUS_5_FUENTES = 466_000

SYSTEM_PROMPT = (
    "Tu es un extracteur de triplets (sujet, prédicat, objet) à partir "
    "de textes politiques en français. Pour chaque intervention "
    "parlementaire, identifie les acteurs (personnes, partis, institutions), "
    "les concepts/sujets (lois, politiques publiques, valeurs) et les "
    "relations entre eux. Réponds UNIQUEMENT par un JSON valide de la forme:\n"
    '{"triples":[{"s":"...","p":"...","o":"..."}, ...]}\n'
    "Maximum 12 triplets par intervention. Pas de texte hors JSON."
)


def call_ollama(text: str, timeout: int = 300, retries: int = 2) -> tuple[str, float]:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_predict": 600},
        "format": "json",
        "keep_alive": "10m",
    }
    data = json.dumps(payload).encode()
    last_err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(
            OLLAMA_URL, data=data,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = json.loads(r.read())
            dt = time.perf_counter() - t0
            content = body.get("message", {}).get("content", "")
            return content, dt
        except Exception as e:
            last_err = e
            print(f"      ! intento {attempt + 1} falló ({e}); reintento...")
    raise RuntimeError(f"Ollama falló tras {retries + 1} intentos: {last_err}")


def parse_triples(raw: str) -> list[dict]:
    try:
        obj = json.loads(raw)
        tr = obj.get("triples", [])
        out = []
        for t in tr:
            if not isinstance(t, dict):
                continue
            s = str(t.get("s", "")).strip()
            p = str(t.get("p", "")).strip()
            o = str(t.get("o", "")).strip()
            if s and p and o:
                out.append({"s": s, "p": p, "o": o})
        return out
    except json.JSONDecodeError:
        # fallback: try to find a JSON block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return []
        try:
            return parse_triples(m.group(0))
        except Exception:
            return []


def main() -> None:
    df = pd.read_csv(INPUT)
    print(f"Procesando {len(df)} intervenciones...")
    print(f"Modelo: {MODEL} (Ollama local, 100% gratis)\n")

    rows = []
    times = []
    t_start = time.perf_counter()
    for i, row in df.iterrows():
        text = str(row["intervention_plain"])
        try:
            raw, dt = call_ollama(text)
        except Exception as e:
            print(f"  [{i + 1:>2}/{len(df)}] SKIP por error: {e}")
            continue
        triples = parse_triples(raw)
        times.append(dt)
        for tr in triples:
            rows.append({
                "intervention_id": row["intervention_id"],
                "deputy": row["deputy_full_name"],
                "group": row["political_group_abbrev"],
                "date": row["date"],
                "nb_mots": row["nb_mots"],
                "s": tr["s"], "p": tr["p"], "o": tr["o"],
            })
        print(
            f"  [{i + 1:>2}/{len(df)}] {row['political_group_abbrev']:<6} "
            f"{row['deputy_full_name']:<30} "
            f"{int(row['nb_mots']):>3}w  "
            f"{dt:>5.1f}s  -> {len(triples)} triples"
        )
        pd.DataFrame(rows).to_csv(OUT_TRIPLES, index=False)

    t_total = time.perf_counter() - t_start

    triples_df = pd.DataFrame(rows)
    triples_df.to_csv(OUT_TRIPLES, index=False)

    avg = sum(times) / len(times)
    total_words = int(df["nb_mots"].sum())
    triples_n = len(triples_df)

    timing = {
        "modelo": MODEL,
        "backend": "Ollama local (qwen2.5:3b)",
        "costo_USD": 0.0,
        "n_intervenciones_demo": len(df),
        "palabras_totales_demo": total_words,
        "triples_extraidos": triples_n,
        "triples_promedio_por_doc": round(triples_n / len(df), 1),
        "tiempo_total_segundos": round(t_total, 1),
        "tiempo_promedio_por_doc_segundos": round(avg, 2),
        "tiempo_min": round(min(times), 2),
        "tiempo_max": round(max(times), 2),
        "throughput_docs_por_segundo": round(len(df) / t_total, 3),
        "extrapolacion_corpus_intervenciones_n": CORPUS_INTERVENCIONES,
        "extrapolacion_corpus_intervenciones_horas": round(
            CORPUS_INTERVENCIONES * avg / 3600, 1),
        "extrapolacion_corpus_intervenciones_dias": round(
            CORPUS_INTERVENCIONES * avg / 86400, 1),
        "extrapolacion_5_fuentes_n": CORPUS_5_FUENTES,
        "extrapolacion_5_fuentes_dias": round(
            CORPUS_5_FUENTES * avg / 86400, 1),
    }

    with open(OUT_TIMING, "w") as f:
        json.dump(timing, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    print(f"Triples totales:           {triples_n}")
    print(f"Triples promedio/doc:      {triples_n / len(df):.1f}")
    print(f"Tiempo total demo:         {t_total:.1f}s "
          f"({t_total / 60:.1f} min)")
    print(f"Tiempo promedio/doc:       {avg:.2f}s")
    print(f"Throughput:                {len(df) / t_total:.2f} docs/s")
    print()
    print(f"EXTRAPOLACIÓN al corpus completo de intervenciones "
          f"(n={CORPUS_INTERVENCIONES:,}):")
    print(f"   -> {CORPUS_INTERVENCIONES * avg / 3600:,.1f} horas "
          f"= {CORPUS_INTERVENCIONES * avg / 86400:.1f} días non-stop")
    print()
    print(f"EXTRAPOLACIÓN a las 5 fuentes (n≈{CORPUS_5_FUENTES:,}):")
    print(f"   -> {CORPUS_5_FUENTES * avg / 86400:.1f} días non-stop")
    print()
    print(f"Triples guardados en:  {OUT_TRIPLES.relative_to(ROOT.parent)}")
    print(f"Métricas guardadas en: {OUT_TIMING.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
