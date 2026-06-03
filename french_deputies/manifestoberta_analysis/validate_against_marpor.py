"""
Validacion del clasificador manifestoberta contra el GROUND TRUTH humano
de MARPOR (`cmp_code` en manifesto_texts.csv).

Mide:
  - accuracy top-1
  - accuracy top-3
  - accuracy a nivel de DOMINIO (digito 1)
  - confusion matrix por dominio
  - tabla por etiqueta (precision/recall/f1) en codigo MARPOR
  - errores tipicos (peores 50 desacuerdos por confianza)

Esto sirve para responder: "¿el modelo, entrenado en 38 idiomas, sigue
funcionando en frances politico XV legislatura?"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from common.classifier_runner import DOMAIN_NAMES, code_from_label, domain_from_code  # noqa: E402

PREDS = THIS / "manifestos" / "results" / "predictions.csv"
OUT = THIS / "validation"


def normalize_code(code) -> str | None:
    """MARPOR cmp_code (e.g. 503, 503.1, 'H' for header) -> '503'."""
    if pd.isna(code):
        return None
    s = str(code).strip()
    if not s or s.lower() in {"nan", "none", "h", "0", "000"}:
        return None
    # Algunos codigos vienen como 503.1 (sub-categorias H5) - colapsamos al padre
    if "." in s:
        s = s.split(".")[0]
    if not s[0].isdigit():
        return None
    return s


def main():
    if not PREDS.exists():
        print(f"ERROR: corre primero manifestos/run.py para generar {PREDS}")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PREDS)
    print(f"Predicciones cargadas: {len(df):,}")

    if "cmp_code" not in df.columns:
        print("ERROR: predictions.csv no tiene la columna cmp_code (re-correr manifestos/run.py con extra_cols).")
        sys.exit(1)

    df["true_code"] = df["cmp_code"].apply(normalize_code)
    df = df[df["true_code"].notna()].copy()
    # Normalizar top1/2/3_code a str para comparar
    for c in ("top1_code", "top2_code", "top3_code"):
        df[c] = df[c].apply(lambda x: str(x).strip() if pd.notna(x) else "")
    df["true_code"] = df["true_code"].astype(str)
    print(f"Con cmp_code utilizable: {len(df):,}")

    df["true_domain"] = df["true_code"].apply(domain_from_code)
    df["pred_domain"] = df["top1_code"].apply(domain_from_code)

    # === Accuracy basica ===
    acc_top1 = (df["top1_code"] == df["true_code"]).mean()
    acc_top3 = (
        (df["top1_code"] == df["true_code"])
        | (df["top2_code"] == df["true_code"])
        | (df["top3_code"] == df["true_code"])
    ).mean()
    df_dom = df[df["true_domain"].notna() & df["pred_domain"].notna()]
    acc_domain = (df_dom["pred_domain"] == df_dom["true_domain"]).mean()

    print()
    print(f"=== Accuracy contra MARPOR human ground truth ===")
    print(f"  top-1 (codigo exacto)       : {acc_top1*100:5.1f}%")
    print(f"  top-3 (codigo en top-3)     : {acc_top3*100:5.1f}%")
    print(f"  acc a nivel de dominio (1-7): {acc_domain*100:5.1f}%")

    # === Confusion matrix por dominio ===
    cm = pd.crosstab(df_dom["true_domain"], df_dom["pred_domain"], margins=True)
    cm.to_csv(OUT / "confusion_matrix_domain.csv")
    print()
    print("Confusion matrix por dominio (filas=verdadero, cols=predicho):")
    print(cm.to_string())

    # === Per-code F1 ===
    from sklearn.metrics import classification_report
    rep = classification_report(
        df["true_code"], df["top1_code"], zero_division=0, output_dict=True
    )
    pd.DataFrame(rep).T.to_csv(OUT / "per_code_classification_report.csv")
    # Resumen macro
    macro = rep.get("macro avg", {})
    print()
    print(f"Macro avg: precision={macro.get('precision',0):.2f} "
          f"recall={macro.get('recall',0):.2f} f1={macro.get('f1-score',0):.2f}")

    # === Top errores ===
    errors = df[df["top1_code"] != df["true_code"]].copy()
    errors["confianza_modelo"] = errors["top1_prob"]
    errors = errors.sort_values("confianza_modelo", ascending=False).head(50)
    errors[["text", "true_code", "top1_code", "top1_label", "top1_prob",
            "top2_code", "top2_label", "top2_prob"]].to_csv(
        OUT / "top50_errors_high_confidence.csv", index=False
    )

    # === Resumen JSON ===
    summary = {
        "n_samples": int(len(df)),
        "accuracy_top1": round(float(acc_top1), 4),
        "accuracy_top3": round(float(acc_top3), 4),
        "accuracy_domain": round(float(acc_domain), 4),
        "macro_f1": round(float(macro.get("f1-score", 0)), 4),
        "expected_top1_from_model_card": 0.57,
        "expected_top3_from_model_card": 0.81,
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print()
    print(f"Resultados en {OUT}/")


if __name__ == "__main__":
    main()
