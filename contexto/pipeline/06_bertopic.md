# Contexto de la carpeta: `french_deputies/bertopic_analysis/`

## Propósito

Este módulo aplica **topic modeling no supervisado** con **BERTopic** sobre los **cinco corpus textuales** del proyecto (manifiestos, enmiendas, leyes, tweets, intervenciones en hemiciclo). El objetivo es triangular el **agenda parlamentaria** desde distintas superficies discursivas (campaña, trabajo legislativo, comunicación pública, debate en sesión) con una **representación temática comparable**: 24 tópicos finales + bucket de outliers (`-1`) por fuente, tras la misma pipeline compartida en `common/bertopic_runner.py`.

Complementa a `manifestoberta_analysis/` (clasificación supervisada MARPOR); no sustituye etiquetas teóricas estándar, sino que **descubre** agrupaciones empíricas en el texto.

---

## Archivos importantes

### Núcleo compartido

| Archivo | Función |
|---------|---------|
| `common/bertopic_runner.py` | Pipeline reutilizable `run_bertopic()`: embeddings, BERTopic, reducción a 25 tópicos, export CSV/HTML/JSON. Define `FRENCH_STOPWORDS`, `LEGAL_STOPWORDS`, `HEMICYCLE_STOPWORDS`, `TWITTER_STOPWORDS`. |
| `requirements.txt` | `bertopic>=0.17`, `sentence-transformers`, `pandas`, `scikit-learn`, `plotly`. |
| `README.md` | Documentación completa: filtros por fuente, parámetros, tiempos, **24 tópicos por corpus** (tablas embebidas), limitaciones. |

### Runners por fuente (`<fuente>/run.py`)

| Script | Entrada | Clase agrupadora |
|--------|---------|------------------|
| `manifestos/run.py` | `manifestos/processed/manifesto_texts.csv` (+ `manifesto_full_texts.csv`) | `party_abbrev` |
| `amendements/run.py` | `lois_votes/.../amendements_votos_con_texto.csv` | `ley_titulo_corto` |
| `lois/run.py` | `lois_votes/.../leyes_texto_oficial.csv` | `dossier_uid` |
| `tweets/run.py` | `twitter_zeeschuimer/.../tweets_text_only.csv` | `political_group_abbrev` |
| `interventions/run.py` | `hemicycle/.../interventions_xv_2017_2022_with_deputies.csv.gz` | `political_group_abbrev` |

Cada `<fuente>/results/` (gitignored) contiene salidas de una corrida: `topic_info.csv`, `document_topics.csv`, `top_words_per_topic.csv`, `summary.json`, visualizaciones Plotly HTML, etc.

---

## Flujo / lógica principal

```
Corpus procesado (5 carpetas upstream)
         │
         ▼
<fuente>/run.py  — carga CSV, filtros específicos, limpieza, lista docs + classes
         │
         ▼
common/bertopic_runner.run_bertopic()
         │
         ├── SentenceTransformer (paraphrase-multilingual-MiniLM-L12-v2)
         ├── BERTopic: HDBSCAN + c-TF-IDF + KeyBERTInspired
         ├── reduce_topics → target_nr_topics=25
         └── export → <fuente>/results/
```

**Entradas:** tablas finales de `manifestos/`, `lois_votes/`, `twitter_zeeschuimer/`, `hemicycle/` (documentadas en cada módulo de corpus).

**Salidas analíticas:** asignación tópico por documento (`document_topics.csv`), palabras representativas (`top_words_per_topic.csv`), prevalencia por partido/grupo/ley (`topics_per_<class>.csv`), visualizaciones interactivas.

---

## Metodología

Enfoque de **clustering semántico no supervisado** sobre embeddings multilingües, unificado para las cinco fuentes.

| Etapa | Herramienta / algoritmo | Detalle |
|-------|-------------------------|---------|
| **1. Preprocesamiento** | Por `run.py` | Filtros de longitud (≥10 palabras salvo manifiestos), regex procedimental (hemiciclo), limpieza Twitter, split en párrafos (leyes), concat `dispositif+expose_sommaire` (enmiendas). |
| **2. Embeddings** | `sentence-transformers` | Modelo **`paraphrase-multilingual-MiniLM-L12-v2`** (384-D, multilingüe). |
| **3. Reducción + clustering** | BERTopic (UMAP + HDBSCAN por defecto) | README documenta UMAP 384→5-D y HDBSCAN; tópicos crudos: 27–173 según fuente. |
| **4. Etiquetado** | c-TF-IDF + `KeyBERTInspired` | Top palabras por tópico en `top_words_per_topic.csv`. |
| **5. Reducción post-hoc** | `reduce_topics(nr_topics=25)` | Desactivado `nr_topics="auto"` interno (evita error `min_df`); vectorizer con `min_df=1` solo en esta fase. |
| **6. Vectorización** | `CountVectorizer` | `ngram_range=(1,2)`; `min_df` escala con corpus (3–50). Stop-words FR + dominio. |
| **7. Visualización** | Plotly (BERTopic) | barchart, mapa 2D, heatmap, jerarquía, heatmap por clase. |

**Parámetros por fuente** (`README.md`):

| Fuente | Docs | `min_topic_size` | `min_df` | Tópicos crudos → finales | Tiempo CPU (s) | Outliers |
|--------|------|------------------|----------|--------------------------|----------------|----------|
| manifestos | 3 801 | 15 | 3 | 51 → 24 | 19 | 1 169 |
| amendements | 2 575 | 20 | 5 | 27 → 24 | 33 | 656 |
| lois | 23 267 | 50 | 10 | 126 → 24 | 96 | 8 833 |
| tweets | 222 644 | 100 | 30 | 173 → 24 | 407 | 105 894 |
| interventions | 338 192 | 150 | 50 | 156 → 24 | 2 355 | 165 439 |

**Criterios de evaluación / calidad:**
- **Comparabilidad:** mismo embedder, mismo `target_nr_topics=25`, mismos tipos de salida.
- **Sanity check:** `global_word_frequency.csv` tras stop-words.
- **Interpretabilidad:** tablas de 24 tópicos con lectura humana en README; tópicos residuales/procedurales marcados explícitamente (leyes tópico 0 ~36 % boilerplate; hemiciclo tópicos 0, 1, 9, 11, 17).
- **No hay métricas de coherencia automática** (NPMI, etc.) documentadas en el repo.

**Supuestos:**
- Un documento = una unidad (quasi-frase, párrafo, tweet, intervención, enmienda).
- Tópicos descubiertos son **empíricos**, no categorías MARPOR.
- ~48 % outliers en tweets e intervenciones es esperable (HDBSCAN estricto).
- Reproducibilidad **parcial** (semillas UMAP/HDBSCAN por defecto).

**Dependencias:** ver `requirements.txt`; no incluye `umap-learn`/`hdbscan` explícitos (vienen con `bertopic`).

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Metodología — análisis no supervisado** | BERTopic, embeddings, HDBSCAN, c-TF-IDF, reducción a 25 tópicos. |
| **Metodología — comparación multi-corpus** | Misma pipeline sobre 5 fuentes con filtros alineados a ManifestoBERTa. |
| **Implementación** | `bertopic_runner.py`, un `run.py` por fuente, comandos de reproducción. |
| **Resultados** | Tablas de tópicos por fuente en `README.md`; `viz_topics_per_political_group.html` (tweets/intervenciones). |
| **Discusión** | Limitaciones: outliers, boilerplate legal/procedimental, modelo embedding pequeño. |
| **Anexos** | Esquema de archivos en `results/`; stop-words por dominio. |

---

## Resultados, decisiones o detalles relevantes

**Hallazgos transversales (documentados en README):**
- **Manifiestos:** agenda de campaña (educación, fiscalidad, servicios públicos, energía).
- **Enmiendas:** temas focalizados (fiscalidad, vivienda, salud, COVID, jubilaciones).
- **Leyes:** mezcla de sustancia y boilerplate de informes (`rapport mentionnés`).
- **Tweets:** actualidad (Ucrania, Macron, Olimpiadas, retraites) + meta-política.
- **Intervenciones:** UE, reforma/salud/educación + tramos procedurales residuales.

**Decisiones técnicas clave:**
- Reducción manual a **25** tópicos (no auto-reduce de BERTopic).
- Stop-words de dominio para evitar clusters de forma (p. ej. sin `LEGAL_STOPWORDS`, un tópico procedural absorbía 56 % de leyes).
- Manifiestos **sin** filtro de longitud (unidad MARPOR).
- `**/results/` en `.gitignore`; resultados canónicos **embebidos en README**.

**Limitaciones conocidas** (`README.md`):
- Outliers altos en corpus grandes.
- Tópicos residuales en leyes e intervenciones pese a stop-words extendidas.
- `paraphrase-multilingual-MiniLM-L12-v2` elegido por velocidad (~118 MB), no por máximo rendimiento semántico.

**Relación con otros módulos:** `manifestoberta_analysis/` usa los mismos filtros de entrada para comparabilidad doc-a-doc; `party_analysis/` se basa en predicciones MARPOR, no en BERTopic directamente.

---

## Dudas o cosas a revisar

1. **`README.md` estructura:** menciona `articles_lois_xv.csv.gz` y `manifestos_clean.csv`; los scripts reales usan `leyes_texto_oficial.csv` y `manifesto_texts.csv`.
2. **`results/` no versionados:** para la memoria, ¿se anexan HTML/CSV regenerados o solo tablas del README?
3. **UMAP/HDBSCAN:** parámetros no expuestos en `bertopic_runner.py` (defaults de BERTopic); documentar si se dejaron intencionalmente.
4. **Tiempos:** README dice ~40 min intervenciones en CPU M-series; `interventions/run.py` advierte 2–6 h — alinear según hardware usado.
5. **Evaluación cuantitativa:** no hay coherence scores ni validación humana sistemática de tópicos.
6. **`requirements.txt`** no fija `umap-learn` ni `hdbscan` como dependencias directas.

---

## Resumen corto

`bertopic_analysis/` ejecuta **BERTopic** de forma unificada sobre los **cinco corpus** del proyecto: embeddings con **`paraphrase-multilingual-MiniLM-L12-v2`**, clustering HDBSCAN, etiquetado c-TF-IDF y **reducción a 24 tópicos finales** (+ outliers) por fuente. Cada `<fuente>/run.py` aplica filtros propios y delega en `common/bertopic_runner.py`. Es el análisis **exploratorio temático** de la tesis; los resultados interpretativos están documentados en `README.md` (tópicos por corpus, tiempos, limitaciones).

---

## Citas

- **BERTopic:** Grootendorst, M. — [github.com/MaartenGr/BERTopic](https://github.com/MaartenGr/BERTopic); paquete `bertopic>=0.17`.
- **Embeddings:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — [Hugging Face](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
- **KeyBERTInspired:** representation model en BERTopic (`bertopic.representation.KeyBERTInspired`).
- **Corpus de entrada:** documentación en `french_deputies/manifestos/`, `lois_votes/`, `twitter_zeeschuimer/`, `hemicycle/` y contextos en `context/`.
- **Enfoque complementario supervisado:** `french_deputies/manifestoberta_analysis/README.md`.
- **Documentación interna:** `french_deputies/bertopic_analysis/README.md`, `common/bertopic_runner.py`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/bertopic_analysis/` — **topic modeling no supervisado** (BERTopic) sobre los 5 corpus → 24 tópicos por fuente. **⚠️ Módulo SECUNDARIO / EXPLORATORIO:** complementa, no sustituye, a ManifestoBERTa (el núcleo citable). **No alimenta `party_analysis/`** (que trabaja sobre MARPOR). En la memoria pesa sobre todo como **lectura exploratoria + anexo metodológico**.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Revisión de literatura** | BERTopic, embeddings, UMAP, HDBSCAN, c-TF-IDF. |
| **Metodología** | Vía no supervisada; comparación multi-corpus con filtros **alineados** a ManifestoBERTa. |
| **Implementación** | `bertopic_runner.py` + un `run.py` por fuente; parámetros de reducción a 25 tópicos. |
| **Resultados** (secundario) | Tablas de 24 tópicos por corpus como **triangulación exploratoria**. |
| **Discusión** | Limitaciones del clustering (outliers, boilerplate). |
| **Anexos** (peso fuerte) | Parámetros por fuente, stop-words de dominio, esquema de `results/`. |

**Información concreta a extraer:**
- Pipeline único: embeddings `paraphrase-multilingual-MiniLM-L12-v2` (384-D) → UMAP → HDBSCAN → c-TF-IDF/`KeyBERTInspired` → **reducción post-hoc a 25 (→24 finales)** tópicos por fuente.
- Que es **exploratorio**: descubre agrupaciones empíricas, **no categorías MARPOR teóricas**.
- Hallazgos cualitativos por corpus (campaña / temas focalizados en enmiendas / sustancia+boilerplate en leyes / actualidad+meta-política en tweets / UE-salud-educación en intervenciones).

**Figuras, tablas o métricas que contiene/menciona:**
- **Tabla de parámetros por fuente** (docs, `min_topic_size`, `min_df`, tópicos crudos→24, tiempo CPU, outliers).
- Visualizaciones Plotly HTML (barchart, mapa 2D, heatmap por clase) — **gitignored**, regenerables. No hay coherence scores.

**Limitaciones / dudas a trasladar:**
- **Reproducibilidad parcial** (semillas UMAP/HDBSCAN por defecto); **sin métricas de coherencia** (NPMI); embedder pequeño elegido por velocidad.
- ~**48 %** outliers en corpus grandes; tópicos residuales/boilerplate pese a stop-words.
- `results/` no versionados; discrepancias de nombres de archivo en el README (`articles_lois_xv.csv.gz`, `manifestos_clean.csv`).
