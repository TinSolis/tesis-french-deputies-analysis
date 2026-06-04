# Tesis — Diputados franceses, discursos, votos, Twitter y manifiestos (2017-2022)

Proyecto de datos para la tesis: diputados de la Assemblée nationale (XV legislatura, 2017-2022), sus intervenciones en el hemiciclo, votaciones sobre leyes, actividad en Twitter y programas electorales de sus partidos. Sobre esos cinco corpus se aplican tres módulos de análisis: **BERTopic** (no supervisado), **ManifestoBERTa** (supervisado, taxonomía MARPOR) y un demo acotado de **KG-Gen** (extracción de triples con LLM local).

**Documento de referencia:** [Propuesta Memoria .pdf](Propuesta%20Memoria%20.pdf)

## Estructura del repositorio

```
Tesis/
├── README.md                              ← estás aquí
├── Propuesta Memoria .pdf
│
└── french_deputies/
    ├── README.md
    ├── ESTRUCTURA.md
    │
    ├── datos_diputados/                   ← CSV maestro de 668 diputados (id, grupo, Twitter)
    ├── hemicycle/                         ← ~950k intervenciones del hemiciclo (Regards Citoyens)
    ├── lois_votes/                        ← 373 leyes XV con texto JORF + votos por diputado
    ├── twitter_zeeschuimer/               ← tweets capturados con Zeeschuimer y cruzados con la cohorte
    ├── manifestos/                        ← programas electorales 2017 (MARPOR + texto completo)
    │
    ├── bertopic_analysis/                 ← topic modeling no supervisado sobre los 5 corpus
    │   ├── README.md
    │   ├── common/bertopic_runner.py      ← pipeline compartido (embed → UMAP → HDBSCAN → c-TF-IDF)
    │   ├── manifestos/run.py
    │   ├── amendements/run.py
    │   ├── lois/run.py
    │   ├── tweets/run.py
    │   └── interventions/run.py
    │
    ├── manifestoberta_analysis/           ← clasificación supervisada MARPOR (56 categorías) sobre los 5 corpus
    │   ├── README.md
    │   ├── common/classifier_runner.py
    │   ├── validate_against_marpor.py     ← accuracy top-1/3 + confusion matrix vs cmp_code humano
    │   ├── manifestos/run.py
    │   ├── amendements/run.py
    │   ├── lois/run.py
    │   ├── tweets/run.py
    │   └── interventions/run.py
    │
    └── kg-gen/                            ← demo acotado de extracción de triples (Ollama + qwen2.5:3b)
        ├── README.md
        └── scripts/01_build_sample.py … 03_analyze.py
```

> Los `*/results/` de los tres módulos de análisis no están versionados (CSVs, HTMLs y logs grandes); se regeneran corriendo cada `run.py`. Tampoco se versionan los CSVs procesados pesados de `hemicycle/processed/` y `twitter_zeeschuimer/processed/` ni los ZIP/JSON crudos de `lois_votes/`. Lo que sí se versiona: scripts, READMEs, lista base de diputados, `manifesto_texts.csv`, `interventions_xv_sample5000.csv` y los CSVs livianos de `lois_votes/votes_rd/processed/`.

## Qué hay en cada corpus

| Carpeta | Qué contiene | Cobertura |
|---|---|---|
| **`datos_diputados/`** | CSV base de 668 diputados (id, nombre, grupo, circunscripción, Twitter) | Todos |
| **`hemicycle/`** | ~950k intervenciones del hemiciclo (texto, sección, fecha, deputy_id) | 646 diputados enlazados |
| **`lois_votes/`** | 373 leyes votadas + voto de cada diputado + texto JORF promulgado + enmiendas | Según scrutin |
| **`twitter_zeeschuimer/`** | Tweets capturados con Zeeschuimer y cruzados con la cohorte | Diputados con cuenta |
| **`manifestos/`** | Programas electorales junio 2017 de 10 partidos (texto completo + codificación MARPOR) | ~85% por grupo |

Todos se enlazan por **`deputy_id`** o **`political_group_abbrev`** del CSV base `deputes_2017_2022.csv`.

## Módulos de análisis

Los tres módulos toman los **mismos cinco corpus** (manifestos, amendements, lois, tweets, interventions) con **filtros idénticos** entre BERTopic y ManifestoBERTa, así los resultados son comparables doc-por-doc.

| Módulo | Enfoque | Qué produce | README |
|---|---|---|---|
| **`bertopic_analysis/`** | No supervisado: descubre tópicos por embeddings + UMAP + HDBSCAN, los reduce a 25 con c-TF-IDF | Por fuente: `topic_info.csv`, `top_words_per_topic.csv`, `topics_per_<class>.csv`, `summary.json`, HTMLs interactivos | [link](french_deputies/bertopic_analysis/README.md) |
| **`manifestoberta_analysis/`** | Supervisado: clasifica cada doc en una de las 56 categorías MARPOR + 7 dominios (xlm-roberta-large fine-tuneado por el Manifesto Project) | Por fuente: `predictions.csv` (top-1/2/3 + probs), `topic_distribution.csv`, `domain_distribution.csv`, `summary.json` + reporte de validación contra `cmp_code` humano | [link](french_deputies/manifestoberta_analysis/README.md) |
| **`kg-gen/`** | Demo acotado: extracción de triples (sujeto, predicado, objeto) con LLM local sobre 25 intervenciones de un debate emblemático | `triples.csv`, `stats.json`, `timing.json`, `graph.png` | [link](french_deputies/kg-gen/README.md) |

> BERTopic y ManifestoBERTa son complementarios: el primero muestra **qué temáticas emergen del corpus** con su vocabulario propio (`macron`, `ukraine`, `covid`); el segundo muestra **dónde caen esos tópicos en la grilla MARPOR** que la ciencia política comparada usa desde 1979. KG-Gen quedó documentado como referencia empírica de lo que costaría aplicar extracción de grafos sobre el corpus completo (~31 días de cómputo solo para intervenciones), no como un módulo del pipeline final.

## Cómo se conectan los datos

```
deputes_2017_2022.csv (id, grupo político, Twitter)
       │
       ├── hemicycle/             → qué dice cada diputado en la Asamblea
       ├── lois_votes/            → cómo vota cada diputado (y el texto promulgado)
       ├── twitter_zeeschuimer/   → qué publica en Twitter
       └── manifestos/            → qué promete su partido
              │
              ▼
    bertopic_analysis/            → tópicos emergentes por fuente
    manifestoberta_analysis/      → categorías MARPOR por fuente
    kg-gen/                       → triples (sujeto, predicado, objeto) sobre una muestra
```

La triangulación cruzada permite ver si los temas que un partido **promete** (manifesto) coinciden con lo que sus diputados **dicen en el hemiciclo**, **votan en leyes** y **publican en Twitter**.

## Dónde sigo leyendo

| Necesito… | Abro… |
|---|---|
| Visión general de `french_deputies/` | [`french_deputies/README.md`](french_deputies/README.md) |
| Estructura completa de archivos | [`french_deputies/ESTRUCTURA.md`](french_deputies/ESTRUCTURA.md) |
| Cómo armé la lista de diputados | [`french_deputies/datos_diputados/README.md`](french_deputies/datos_diputados/README.md) |
| Intervenciones en el hemiciclo | [`french_deputies/hemicycle/README.md`](french_deputies/hemicycle/README.md) |
| Leyes y votaciones | [`french_deputies/lois_votes/votes_rd/README.md`](french_deputies/lois_votes/votes_rd/README.md) |
| Twitter / Zeeschuimer | [`french_deputies/twitter_zeeschuimer/README.md`](french_deputies/twitter_zeeschuimer/README.md) |
| Manifiestos electorales (MARPOR) | [`french_deputies/manifestos/README.md`](french_deputies/manifestos/README.md) |
| Análisis BERTopic (5 fuentes) | [`french_deputies/bertopic_analysis/README.md`](french_deputies/bertopic_analysis/README.md) |
| Clasificación ManifestoBERTa (5 fuentes) | [`french_deputies/manifestoberta_analysis/README.md`](french_deputies/manifestoberta_analysis/README.md) |
| Demo KG-Gen sobre intervenciones | [`french_deputies/kg-gen/README.md`](french_deputies/kg-gen/README.md) |
