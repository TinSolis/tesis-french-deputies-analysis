# Contexto de la carpeta: `french_deputies/manifestoberta_analysis/`

## Propósito

Este módulo aplica **clasificación temática supervisada** sobre los **cinco corpus** del proyecto (manifiestos, enmiendas, leyes, tweets, intervenciones). A diferencia de `bertopic_analysis/` (no supervisado), asigna a cada documento una de las **56 categorías MARPOR** (+ uno de **7 dominios** macro) usando el modelo preentrenado **`manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1`**. El valor: una taxonomía **citable y comparable internacionalmente** (ciencia política comparada, MARPOR desde 1979), que permite contrastar el corpus francés XV contra cualquier país codificado por MARPOR. Es el gemelo supervisado de BERTopic y la base de `party_analysis/` y `ches_analysis/`.

---

## Archivos importantes

### Núcleo y configuración

| Archivo | Función |
|---------|---------|
| `common/classifier_runner.py` | Lógica compartida: `load_model()`, `classify_dataframe()`, `classify_batch()`, mapeo código→dominio. |
| `requirements.txt` | `torch>=2.0`, `transformers>=4.30`, `pandas`, `numpy`, `scikit-learn`. |
| `README.md` | Documentación exhaustiva: modelo, filtros, pipeline, tiempos, resultados por fuente, validación. |
| `test_smoke.py` | Prueba rápida del runner. |

### Runners por fuente (`<fuente>/run.py`)

| Script | Entrada | `text_col` | `extra_cols` | `batch_size` |
|--------|---------|------------|--------------|--------------|
| `manifestos/run.py` | `manifestos/processed/manifesto_texts.csv` | `text` | `cmp_code`, `party_abbrev` | 16 |
| `amendements/run.py` | `lois_votes/.../amendements_votos_con_texto.csv` | `dispositif + expose_sommaire` | `numero_scrutin`, `match_confianza` | 16 |
| `lois/run.py` | `lois_votes/.../leyes_texto_oficial.csv` | `paragraph` | `dossier_id` | 16 |
| `tweets/run.py` | `twitter_zeeschuimer/.../tweets_text_only.csv` | `clean_text` | `deputy_id`, `political_group` | 32 |
| `interventions/run.py` | `hemicycle/.../interventions_xv_2017_2022_with_deputies.csv.gz` | `text` | `deputy_id`, `political_group` | 16 |

### Validación

| Archivo | Función |
|---------|---------|
| `validate_against_marpor.py` | Compara top-1/top-3 vs. `cmp_code` humano (manifiestos 2017): accuracy, confusion matrix por dominio, F1 por categoría, top-50 errores. |
| `validation/` (gitignored) | `summary.json`, `confusion_matrix_domain.csv`, `per_code_classification_report.csv`, `top50_errors_high_confidence.csv`. |

Cada `<fuente>/results/` (gitignored) contiene `predictions.csv`, `topic_distribution.csv`, `domain_distribution.csv`, `summary.json`, `run.log`.

---

## Flujo / lógica principal

```
Corpus procesado (5 carpetas upstream, mismos filtros que bertopic_analysis)
         │
         ▼
<fuente>/run.py  — carga CSV, filtros, define text_col + extra_cols
         │
         ▼
common/classifier_runner.classify_dataframe()
         │
         ├── load_model: xlm-roberta-large tokenizer + manifestoberta head (mps→cuda→cpu)
         ├── tokeniza (max 200 tokens) → inferencia batch → softmax 56 logits
         ├── top-1/2/3 (label+code+prob) + dominio (1er dígito del código)
         └── export → <fuente>/results/predictions.csv + distribuciones + summary.json
         │
         ▼
validate_against_marpor.py (solo manifestos, vs cmp_code humano)
         │
         ▼
party_analysis/ y ches_analysis/ consumen predictions.csv
```

**Entradas:** mismas tablas finales que BERTopic (comparabilidad doc-a-doc por columna identificadora).

**Salida clave:** `predictions.csv` por fuente — base de los análisis a nivel partido y de la validación externa CHES.

---

## Metodología

Enfoque de **inferencia con transformer multilingüe preentrenado** (zero-shot sobre el corpus francés: el modelo no se reentrena, solo se aplica).

| Etapa | Herramienta / técnica | Detalle |
|-------|------------------------|---------|
| **1. Preprocesamiento** | Por `run.py` | Filtros idénticos a BERTopic (≥10 palabras salvo manifiestos; cascada de 3 filtros en intervenciones: `deputy_id` → ≥10 palabras → no procedimental). |
| **2. Modelo** | `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` | `xlm-roberta-large` (560 M params) fine-tuneado sobre 1.7 M quasi-oraciones MARPOR (38 idiomas, Handbook 4 / mp v5). ~2.2 GB. |
| **3. Tokenización** | tokenizer `xlm-roberta-large` | `max_length=200`, `padding="max_length"`, `truncation=True` (200 = max del entrenamiento). |
| **4. Inferencia** | `torch.inference_mode()` + softmax | Forward pass batch (16; 32 para tweets); `device` autoseleccionado MPS→CUDA→CPU. |
| **5. Top-K + dominio** | argsort de probabilidades | top-1/2/3 (label, código, prob); dominio = primer dígito del código top-1. |
| **6. Persistencia** | pandas → CSV/JSON | `predictions.csv` + agregados por categoría y dominio. |
| **7. Validación** | `scikit-learn` | accuracy top-1/3, accuracy de dominio, confusion matrix, `classification_report` (F1 por categoría). |

**Unidad de clasificación:** documento individual (quasi-frase, enmienda, párrafo de ley, tweet limpio, intervención).

**Criterios de evaluación (validación contra ground truth humano MARPOR):**
- Único corpus con etiquetas reales: **manifiestos 2017** (`cmp_code`), n = **3 430** quasi-frases utilizables.
- **Accuracy top-1: 58,3 %** (model card: 57,0 %).
- **Accuracy top-3: 82,0 %** (model card: 81,0 %).
- **Accuracy de dominio: 70,3 %**.
- **Macro F1 (56 categorías): 0,44**.
- Confusiones típicas entre dominios cercanos (4↔5 Economía/Welfare, 5↔7 Welfare/Social Groups, 6↔5).

**Supuestos de ingeniería:**
- Modelo aplicado **sin reentrenamiento** (transfer directo a francés político XV).
- **Una etiqueta por documento** (esquema MARPOR original es 1 quasi-frase → 1 categoría); para texto multitemático el top-1 reduce información (de ahí top-2/top-3).
- Truncamiento a 200 tokens: nunca activa en tweets; sí en leyes/intervenciones largas (se mitiga alimentando la unidad más pequeña: párrafo, enmienda).
- **Probabilidades no calibradas:** sirven para rankear, no como confianza literal.
- Categorías muy raras (408, 415, 705, 507) tienen F1 bajo; interpretación sólida a nivel **dominio** o agrupaciones.

**Dependencias:** `requirements.txt` (PyTorch + HuggingFace Transformers).

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Marco teórico** | Esquema MARPOR (56 categorías / 7 dominios), trazabilidad a ciencia política comparada. |
| **Metodología — clasificación supervisada** | Modelo, tokenización, inferencia, top-K, dominio. |
| **Metodología — validación** | Benchmark contra `cmp_code` humano; comparación con la model card. |
| **Implementación** | `classifier_runner.py`, runners por fuente, configuración de device/batch. |
| **Resultados** | Distribuciones por dominio/categoría de los 5 corpus; tabla comparada top-1 por fuente. |
| **Discusión** | Una-etiqueta-por-doc, probabilidades no calibradas, categorías raras, truncamiento. |
| **Anexos** | Las 56 categorías y 7 dominios; métricas de validación; esquema de `predictions.csv`. |

---

## Resultados, decisiones o detalles relevantes

**Tiempos de corrida (Apple Silicon, MPS — README):**

| Fuente | Docs | Tiempo | docs/seg |
|--------|------|--------|----------|
| manifestos | 3 801 | 3 min | 20,79 |
| amendements | 2 575 | 2 min | 19,60 |
| lois | 23 267 | 19 min | 20,50 |
| tweets | 224 466 | 2 h 46 min | 22,48 |
| interventions | 338 192 | 4 h 57 min | 18,98 |

> Costo total ≈ 8 h de GPU local; tweets e intervenciones son los pesados.

**Hallazgos por fuente (top-1 dominante):**
- **manifestos:** corpus más balanceado; domina Welfare (30,7 %), top-1 código 504.
- **amendements:** fuerte sesgo Welfare (43 %) + Economy (16 %); casi sin External Relations (0,6 %).
- **lois:** dominado por 303 *Govt. & Admin. Efficiency* (24 %) por lenguaje legal-administrativo del JORF.
- **tweets:** 305 *Political Authority* (26,5 %); más Internationalism/Military/Peace que otros corpus.
- **interventions:** 305 *Political Authority* (27 %) + 202 Democracy (8,9 %) por lenguaje procedimental.

**Lectura comparada:** *Welfare State Expansion* (504) siempre top-3 → columna vertebral del corpus XV; las divergencias muestran que un mismo diputado dice cosas distintas según la arena (programa/ley/tweet/intervención).

**Decisiones técnicas:**
- Filtros **alineados con BERTopic** para comparabilidad doc-a-doc (join por `deputy_id`/`numero_scrutin`/`dossier_id`/`partido`).
- `results/` y `validation/` en `.gitignore`; cifras canónicas embebidas en README.
- Nota tweets: 224 466 (no 222 644 de BERTopic) por diferencia en regex de hashtags.

**Limitaciones:** ver supuestos (una etiqueta/doc, probabilidades no calibradas, categorías raras, truncamiento).

---

## Dudas o cosas a revisar

1. **`results/` no versionados:** para la memoria, anexar `predictions.csv`/distribuciones regeneradas o citar tablas del README.
2. **`extra_cols` vs. CSV reales:** README lista `partido`, `political_group`, `dossier_id`, `texto_completo`, `numero_scrutin`; conviene verificar que esos nombres de columna existen en cada CSV de entrada (p. ej. `political_group` vs `political_group_abbrev`).
3. **n de validación:** README dice n = 3 430 «utilizables» frente a 3 801 quasi-frases totales — documentar el criterio de descarte (`cmp_code` nulo/no numérico/header).
4. **Probabilidades no calibradas:** no usar `top1_prob` como confianza literal en la memoria.
5. **Periodo tweets (mar/2017–2025):** excede la legislatura XV; coherente con la limitación ya señalada en `twitter_zeeschuimer`.
6. **Reproducibilidad:** confirmar versión exacta de `transformers`/`torch` usada y hardware, porque afecta tiempos y posibles diferencias numéricas.

---

## Resumen corto

`manifestoberta_analysis/` clasifica los **cinco corpus** del proyecto en las **56 categorías / 7 dominios MARPOR** con el modelo **`manifestoberta-xlm-roberta-large`** (sin reentrenar), guardando top-1/2/3 + dominio por documento en `predictions.csv`. Validado contra el `cmp_code` humano de los manifiestos (**top-1 58,3 %, top-3 82 %, dominio 70,3 %**, consistente con la model card). Es el análisis **supervisado y citable** de la tesis, gemelo de BERTopic y fuente de `party_analysis/` y `ches_analysis/`.

---

## Citas

- **ManifestoBERTa:** `manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` (Burst, Lehmann, Franzmann et al., 2024) — [Hugging Face](https://huggingface.co/manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1).
- **Esquema MARPOR (mp v5):** [manifestoproject.wzb.eu/coding_schemes/mp_v5](https://manifestoproject.wzb.eu/coding_schemes/mp_v5); Budge, Klingemann, Volkens, Bara et al. (desde 1979).
- **Base xlm-roberta-large:** Conneau et al., XLM-R — [Hugging Face](https://huggingface.co/xlm-roberta-large).
- **Frameworks:** HuggingFace Transformers, PyTorch (`requirements.txt`).
- **Corpus de entrada:** `french_deputies/manifestos/`, `lois_votes/`, `twitter_zeeschuimer/`, `hemicycle/` y contextos en `context/`.
- **Módulos hermanos/consumidores:** `french_deputies/bertopic_analysis/README.md`, `party_analysis/`, `ches_analysis/`.
- **Documentación interna:** `french_deputies/manifestoberta_analysis/README.md`, `common/classifier_runner.py`, `validate_against_marpor.py`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/manifestoberta_analysis/` — **clasificación supervisada MARPOR** (56 categorías / 7 dominios) con el modelo preentrenado ManifestoBERTa sobre los 5 corpus → `predictions.csv`. **★ NÚCLEO CITABLE** del proyecto: gemelo supervisado de BERTopic y **fuente directa de `party_analysis/` y `ches_analysis/`**.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Revisión de literatura** | Esquema MARPOR y trazabilidad a ciencia política comparada; XLM-RoBERTa. |
| **Metodología** (principal) | Modelo, tokenización (`max_length=200`), inferencia, top-K + dominio; aplicado **sin reentrenamiento**. |
| **Implementación** | `classifier_runner.py`, runners por fuente, selección de device/batch. |
| **Validación** (principal) | Benchmark contra `cmp_code` humano; comparación con la model card. |
| **Resultados** | Distribuciones por dominio/categoría de los 5 corpus; top-1 dominante por fuente. |
| **Discusión** | Una etiqueta/doc, probabilidades no calibradas, categorías raras, truncamiento. |
| **Anexos** | Las 56 categorías y 7 dominios; métricas de validación; esquema de `predictions.csv`. |

**Información concreta a extraer:**
- Modelo `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` (`xlm-roberta-large`, 560 M params, ~2,2 GB); device **MPS→CUDA→CPU**; salida top-1/2/3 + dominio.
- **Validación (manifiestos, n=3.430):** top-1 **58,3 %**, top-3 **82,0 %**, dominio **70,3 %**, **macro F1 0,44** (consistente con la model card).
- Top-1 dominante por fuente: manifiestos 504 Welfare; enmiendas Welfare 43 %+Economy 16 %; leyes 303 Eficiencia; tweets/intervenciones 305 Autoridad.

**Figuras, tablas o métricas que contiene/menciona:**
- **Tabla de tiempos** por fuente (docs, tiempo, docs/seg; ~8 h total de GPU local).
- **Métricas de validación** (accuracy top-1/3, dominio, macro F1) y **matriz de confusión por dominio** (`confusion_matrix_domain.csv`). Tabla comparada de top-1 por fuente.

**Limitaciones / dudas a trasladar:**
- Accuracy por-frase **~58 %**, macro F1 0,44; **probabilidades no calibradas** (no usar `top1_prob` como confianza literal); **una etiqueta por documento** (pierde texto multitemático).
- Truncamiento a 200 tokens en leyes/intervenciones largas; categorías raras con F1 bajo.
- `results/`/`validation/` no versionados; verificar nombres de `extra_cols` vs. CSV reales; fijar versión de `transformers`/`torch`.
