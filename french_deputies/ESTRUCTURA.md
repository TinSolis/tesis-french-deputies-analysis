# Estructura y uso de archivos – french_deputies

La **raíz** contiene solo **README.md** y este **ESTRUCTURA.md**. El resto se reparte en cinco carpetas de **corpus** (`datos_diputados/`, `twitter_zeeschuimer/`, `lois_votes/`, `hemicycle/`, `manifestos/`) y tres carpetas de **análisis** (`bertopic_analysis/`, `manifestoberta_analysis/`, `kg-gen/`), de modo que siempre quede claro qué es fuente, qué es script y qué es tabla final.

## Archivos principales (los que usa la tesis)

| Archivo o carpeta | Qué es |
|---|---|
| **`datos_diputados/processed/deputes_2017_2022.csv`** | Lista de 668 diputados 2017-2022 (id, nombre, grupo, circunscripción, Twitter). Es la base que enlaza con todo el resto. |
| **`twitter_zeeschuimer/processed/`** | Tweets ya cruzados con diputados: texto, metadata, resúmenes por cuenta. |
| **`lois_votes/votes_rd/processed/`** | Leyes votadas (por scrutin), votos por diputado y cohorte; **`leyes_texto_oficial.csv`** con NOR/Légifrance y **`amendements_votos_con_texto.csv`** con el texto de cada enmienda. |
| **`hemicycle/processed/`** | Intervenciones XV (ND15) con texto y columnas de diputado; también meta y textos separados. Detalle en **`hemicycle/README.md`**. |
| **`manifestos/processed/`** | Manifiestos MARPOR Francia 2017: textos quasi-sentence codificados (`manifesto_texts.csv`) y posiciones por partido. Detalle en **`manifestos/README.md`**. |

## Scripts de procesamiento (construyen los CSV de cada corpus)

| Ubicación | Función |
|---|---|
| **`datos_diputados/scripts/fetch_an_15e_deputes.py`** | AN 15e → `data/deputes_an_rd.csv` |
| **`datos_diputados/scripts/build_deputes_twitter_csv.py`** | Twitter raw → `data/deputes_twitter.csv` |
| **`datos_diputados/scripts/merge_deputes_2017_2022.py`** | Merge AN + Twitter → `processed/deputes_2017_2022.csv` |
| **`twitter_zeeschuimer/scripts/generate_twitter_url_list.py`** | Lista de URLs de perfiles desde el CSV de diputados |
| **`twitter_zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py`** | `.ndjson` en `captures/` + diputados → CSV en `processed/` |
| **`lois_votes/scripts/download_an_scrutins_and_dossiers.py`** | Descarga y descomprime Scrutins + Dossiers en `votes_rd/` |
| **`lois_votes/scripts/build_laws_and_votes.py`** | Tablas de leyes filtradas y votos (y cohorte) |
| **`lois_votes/scripts/build_leyes_texte_oficial.py`** | NOR / URL JORF y texto opcional desde `textes_lois/` |
| **`hemicycle/scripts/build_interventions_with_deputies.py`** | TSV en `hemicycle/fuente/` → tablas en `hemicycle/processed/` |
| **`hemicycle/scripts/report_hemicycle_stats.py`** | Actualiza **`RESUMEN_CUANTITATIVO.md`** |
| **`manifestos/scripts/download_manifestos.py`** | API MARPOR → dataset + textos Francia 2017 en `manifestos/` |

## Módulos de análisis (sobre los 5 corpus)

| Ubicación | Función |
|---|---|
| **`bertopic_analysis/`** | Topic modeling no supervisado sobre las 5 fuentes (manifestos, amendements, lois, tweets, interventions). Un `<fuente>/run.py` por corpus + `common/bertopic_runner.py` con la pipeline compartida (embed → UMAP → HDBSCAN → c-TF-IDF, reducción a 25 tópicos). Stop-words por dominio. README con datos, filtros, configuración y resultados embebidos. |
| **`manifestoberta_analysis/`** | Clasificación supervisada con `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` sobre las mismas 5 fuentes. Mismos filtros que BERTopic para que los corpus sean comparables. `validate_against_marpor.py` mide accuracy top-1/3 y confusion matrix contra `cmp_code` humano (manifiestos 2017). |
| **`kg-gen/`** | Demo acotado de KG-Gen sobre 25 intervenciones de un debate emblemático ("renforcement du dialogue social", Ordonnances Macron). Backend local Ollama + `qwen2.5:3b`. Documenta tiempos y calidad para justificar por qué no se aplica al corpus completo. |

> Los `<fuente>/results/` de los tres módulos no se versionan (CSVs, HTMLs interactivos, logs y `predictions.csv` grandes); se regeneran corriendo el `run.py` correspondiente. Sí se versionan los códigos (`run.py`, `common/`, `requirements.txt`) y el README con resultados embebidos.

## Datos intermedios y raw (lo que no es "tabla final")

| Ubicación | Contenido |
|---|---|
| **`datos_diputados/data/`** | CSV intermedios, ZIP de la AN, referencias nosdeputes |
| **`twitter_zeeschuimer/captures/`** | Exports `.ndjson` de Zeeschuimer (pesados; no van a GitHub) |
| **`lois_votes/votes_rd/`** | ZIP descomprimidos, JSON de scrutins / dossiers / enmiendas (no en GitHub) |
| **`hemicycle/fuente/`** | TSV.gz de Regards Citoyens por legislatura (no en GitHub) |
| **`manifestos/data/`** | Dataset MARPOR raw + metadata |

## Guías (documentación del porqué)

| Archivo | Contenido |
|---|---|
| **`README.md`** (raíz `french_deputies/`) | Visión general, los 5 corpus y los 3 módulos de análisis |
| **`ESTRUCTURA.md`** | Este índice |
| **`datos_diputados/README.md`** | Construcción del CSV de diputados |
| **`twitter_zeeschuimer/README.md`** | Captura y fusión de Twitter |
| **`lois_votes/votes_rd/README.md`** | Leyes y votos: fuentes, pasos, archivos de salida |
| **`hemicycle/README.md`** | Hemiciclo: carpetas, comandos, resumen cuantitativo |
| **`hemicycle/GUIA_IDENTIFICADORES_TESIS.md`** | Diccionario de columnas y enlaces con el resto del proyecto |
| **`hemicycle/RESUMEN_CUANTITATIVO.md`** | Cifras del corpus de intervenciones (regenerado con el script de reporte) |
| **`manifestos/README.md`** | Descarga de los manifiestos, mapeo grupos → partidos, códigos MARPOR |
| **`bertopic_analysis/README.md`** | Topic modeling no supervisado: corpus, filtros, pipeline, configuración por fuente, resultados (top tópicos por corpus) |
| **`manifestoberta_analysis/README.md`** | Clasificación supervisada MARPOR: corpus, filtros, configuración por fuente, distribución de las 56 categorías y 7 dominios, validación |
| **`kg-gen/README.md`** | Demo KG-Gen: subset, pipeline, tiempos medidos, extrapolaciones e implicancias para la tesis |

## Resumen rápido

- **Diputados y Twitter:** `datos_diputados/processed/deputes_2017_2022.csv` y `twitter_zeeschuimer/processed/`.
- **Leyes y votos:** `lois_votes/votes_rd/processed/`.
- **Hemiciclo:** `hemicycle/processed/` (tras correr el build con los TSV en `hemicycle/fuente/`).
- **Manifiestos:** `manifestos/processed/` (correr con API key de MARPOR).
- **BERTopic** (no supervisado): `bertopic_analysis/<fuente>/run.py` para cada uno de los 5 corpus.
- **ManifestoBERTa** (supervisado, MARPOR): `manifestoberta_analysis/<fuente>/run.py` + `validate_against_marpor.py`.
- **KG-Gen** (demo experimental): `kg-gen/scripts/01_build_sample.py` → `02_extract_triples.py` → `03_analyze.py`, con Ollama + `qwen2.5:3b` en local.
- **Reproducir todo:** primero los 5 corpus en orden (datos_diputados → twitter_zeeschuimer → lois_votes → hemicycle → manifestos), después los módulos de análisis (cualquiera, son independientes).
