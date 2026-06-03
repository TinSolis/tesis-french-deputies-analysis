"""
Runner compartido para clasificar textos politicos con
manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1.

Diseñado para correr en Apple Silicon (MPS), CUDA o CPU; con batching para
inferencia eficiente. Para cada documento guarda:
  - top1 label + prob
  - top3 labels + probs
  - distribucion completa de 56 categorias (opcional)
  - dominio MARPOR (1..7) agregado a partir del primer digito del codigo
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1"
TOKENIZER_NAME = "xlm-roberta-large"
MAX_LEN = 200  # el modelo se entrenó con 200 tokens

# Dominios MARPOR (Handbook 4 / v5)
DOMAIN_NAMES = {
    1: "External Relations",
    2: "Freedom and Democracy",
    3: "Political System",
    4: "Economy",
    5: "Welfare and Quality of Life",
    6: "Fabric of Society",
    7: "Social Groups",
}


def pick_device(prefer: str | None = None) -> str:
    if prefer:
        return prefer
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_model(device: str | None = None):
    """Carga modelo + tokenizer y devuelve (model, tokenizer, device)."""
    device = pick_device(device)
    print(f"  device: {device}")
    print(f"  cargando tokenizer ({TOKENIZER_NAME})...")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    print(f"  cargando modelo ({MODEL_NAME})... [~2.2 GB la primera vez]")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, trust_remote_code=True
    )
    model.to(device)
    model.eval()
    return model, tokenizer, device


def code_from_label(label: str) -> str:
    """'501 - Environmental Protection: Positive' -> '501'."""
    return label.split(" -", 1)[0].strip()


def domain_from_code(code) -> int | None:
    """'501' -> 5  ('000' / '0' -> None). Tolerant to ints and NaN."""
    if code is None:
        return None
    try:
        s = str(code).strip()
    except Exception:
        return None
    if not s or s.lower() in {"nan", "none"} or not s[0].isdigit():
        return None
    d = int(s[0])
    return d if 1 <= d <= 7 else None


@torch.inference_mode()
def classify_batch(model, tokenizer, device: str, texts: Sequence[str]) -> torch.Tensor:
    inputs = tokenizer(
        list(texts),
        return_tensors="pt",
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)
    return probs.cpu()


def classify_dataframe(
    df: pd.DataFrame,
    text_col: str,
    *,
    out_dir: Path,
    extra_cols: Iterable[str] = (),
    batch_size: int = 16,
    device: str | None = None,
    keep_full_distribution: bool = False,
    log_every: int = 50,
) -> dict:
    """
    Clasifica `df[text_col]` con manifestoberta y persiste:

      out_dir/predictions.csv          : una fila por documento con top1/top3 + domain
      out_dir/topic_distribution.csv   : frecuencia y % por codigo MARPOR (top1)
      out_dir/domain_distribution.csv  : frecuencia y % por dominio (1..7)
      out_dir/summary.json             : metadata corrida

    `extra_cols` se preserva en el CSV (p.ej. ['political_group','deputy_id']).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(df)
    if n == 0:
        raise ValueError("DataFrame vacio.")

    model, tokenizer, device = load_model(device)
    id2label = model.config.id2label
    labels = [id2label[i] for i in range(len(id2label))]
    codes = [code_from_label(l) for l in labels]
    print(f"  modelo: 56 categorias OK ({len(labels)} labels)")

    extra_cols = [c for c in extra_cols if c in df.columns]
    rows = []
    dist_full = None
    if keep_full_distribution:
        import numpy as np
        dist_full = []

    t0 = time.time()
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        texts = df[text_col].iloc[start:end].astype(str).tolist()
        probs = classify_batch(model, tokenizer, device, texts).numpy()
        for i, p in enumerate(probs):
            idx_sorted = p.argsort()[::-1]
            top1_i, top2_i, top3_i = idx_sorted[0], idx_sorted[1], idx_sorted[2]
            top1_label = labels[top1_i]
            top1_code = codes[top1_i]
            row = {
                "text": texts[i][:300],
                "top1_label": top1_label,
                "top1_code": top1_code,
                "top1_prob": round(float(p[top1_i]), 4),
                "top2_label": labels[top2_i],
                "top2_code": codes[top2_i],
                "top2_prob": round(float(p[top2_i]), 4),
                "top3_label": labels[top3_i],
                "top3_code": codes[top3_i],
                "top3_prob": round(float(p[top3_i]), 4),
                "domain": domain_from_code(top1_code),
            }
            for c in extra_cols:
                row[c] = df[c].iloc[start + i]
            rows.append(row)
        if dist_full is not None:
            dist_full.append(probs)

        if ((start // batch_size) % log_every == 0) and start > 0:
            done = start + (end - start)
            elapsed = time.time() - t0
            eta = elapsed * (n - done) / max(done, 1)
            print(f"    progreso: {done:,}/{n:,} ({done/n*100:.1f}%)  "
                  f"elapsed={elapsed:.0f}s  eta={eta:.0f}s")

    elapsed = time.time() - t0
    print(f"  clasificacion lista en {elapsed:.0f}s ({n/elapsed:.1f} docs/s)")

    preds = pd.DataFrame(rows)
    preds.to_csv(out_dir / "predictions.csv", index=False)

    # Distribucion top1 por codigo MARPOR
    topic_dist = (
        preds["top1_code"].value_counts(dropna=False)
        .rename_axis("code").reset_index(name="count")
    )
    topic_dist["pct"] = (topic_dist["count"] / topic_dist["count"].sum() * 100).round(2)
    code2label = {codes[i]: labels[i] for i in range(len(labels))}
    topic_dist["label"] = topic_dist["code"].map(code2label)
    topic_dist.to_csv(out_dir / "topic_distribution.csv", index=False)

    # Distribucion por dominio
    dom_dist = (
        preds["domain"].value_counts(dropna=False).rename_axis("domain").reset_index(name="count")
    )
    dom_dist["pct"] = (dom_dist["count"] / dom_dist["count"].sum() * 100).round(2)
    dom_dist["name"] = dom_dist["domain"].map(DOMAIN_NAMES)
    dom_dist.to_csv(out_dir / "domain_distribution.csv", index=False)

    # Distribucion completa opcional (probabilidad media por categoria)
    if dist_full is not None:
        import numpy as np
        arr = np.vstack(dist_full)
        mean = arr.mean(axis=0)
        pd.DataFrame({
            "code": codes,
            "label": labels,
            "mean_prob": [round(float(x), 5) for x in mean],
        }).sort_values("mean_prob", ascending=False).to_csv(
            out_dir / "mean_prob_per_category.csv", index=False
        )

    summary = {
        "model": MODEL_NAME,
        "n_documents": int(n),
        "elapsed_seconds": round(elapsed, 1),
        "docs_per_second": round(n / elapsed, 2),
        "device": device,
        "batch_size": batch_size,
        "top1_distribution_top10": topic_dist.head(10).to_dict(orient="records"),
        "domain_distribution": dom_dist.to_dict(orient="records"),
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"  hecho. Resultados en {out_dir}")
    return summary
