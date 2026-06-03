"""
Smoke test del clasificador manifestoberta sobre 6 frases francesas
representativas de las cinco fuentes del corpus.

Verifica:
  - el modelo descarga / carga,
  - corre en MPS / CUDA / CPU sin errores,
  - devuelve top-3 etiquetas MARPOR con probabilidades sensatas.
"""

import sys
from pathlib import Path

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from common.classifier_runner import load_model, classify_batch, code_from_label


SAMPLES = [
    # Ecologia
    "Nous proposons une transition écologique ambitieuse pour réduire les émissions de gaz à effet de serre.",
    # Educacion
    "Il faut renforcer les moyens de l'éducation prioritaire dans les zones rurales.",
    # Migracion
    "Le droit d'asile doit être respecté tout en luttant contre l'immigration clandestine.",
    # Salud / sanitario
    "Le système de santé public manque cruellement de personnels soignants et de lits d'hospitalisation.",
    # Defensa
    "La programmation militaire 2024 augmente significativement le budget des armées.",
    # Igualdad de genero
    "L'égalité entre les femmes et les hommes reste un combat quotidien contre les discriminations.",
]


def main():
    print("=" * 70)
    print("Smoke test — manifestoberta-xlm-roberta-56policy-topics-sentence")
    print("=" * 70)
    model, tokenizer, device = load_model()
    probs = classify_batch(model, tokenizer, device, SAMPLES).numpy()
    id2label = model.config.id2label

    for i, p in enumerate(probs):
        idx = p.argsort()[::-1][:3]
        print(f"\nFrase {i+1}: {SAMPLES[i][:90]}...")
        for j, k in enumerate(idx):
            lab = id2label[k]
            print(f"   top{j+1}: {p[k]*100:5.1f}%  {lab}")


if __name__ == "__main__":
    main()
