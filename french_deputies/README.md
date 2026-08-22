# Francia – diputados 2017-2022

Esta carpeta reúne **todo el trabajo empírico** de la tesis sobre la XV legislatura francesa: la lista de diputados (Assemblée nationale + Twitter), la captura de timelines con Zeeschuimer, las leyes y votos del hemiciclo, las intervenciones parlamentarias, los manifiestos electorales y los tres módulos de análisis que se aplican sobre esos datos. La **memoria final** que documenta la investigación está en [`memoria/`](../memoria/); la **propuesta original** que la encuadra está en [`memoria/propuesta/`](../memoria/propuesta/).

La raíz de **french_deputies** contiene solo este **README** y **ESTRUCTURA.md** (índice de archivos); el resto se organiza en subcarpetas que separan fuentes, procesamiento y análisis.

## Corpus (las 5 fuentes textuales)

| Carpeta | Qué contiene y para qué sirve |
|--------|------------------------------|
| **`datos_diputados/`** | CSV maestro de diputados construido a partir de Twitter (twitter-parlementaires) y los datos abiertos de la AN 15e, limpiado y fusionado. El archivo de referencia para todo lo demás es **`processed/deputes_2017_2022.csv`**. Detalle en **datos_diputados/README.md**. |
| **`twitter_zeeschuimer/`** | Tweets capturados cuenta por cuenta con Zeeschuimer y unificados con la lista de diputados; se conserva el texto para el análisis. Detalle en **twitter_zeeschuimer/README.md**. |
| **`lois_votes/`** | Scrutins, dossiers y enmiendas de la AN, con las tablas de leyes votadas, votos por diputado y texto JORF promulgado. Detalle en **lois_votes/votes_rd/README.md**. |
| **`hemicycle/`** | Intervenciones del hemiciclo (Regards Citoyens): la fuente en **`fuente/`** y las tablas listas en **`processed/`**. **ND15** es la legislatura que coincide con los diputados 2017-2022. Detalle en **hemicycle/README.md**. |
| **`manifestos/`** | Programas electorales 2017 descargados de la API MARPOR junto con los textos completos por partido. Detalle en **manifestos/README.md**. |

## Módulos de análisis (sobre los 5 corpus)

Cada módulo tiene su propia carpeta con `<fuente>/run.py` por corpus, un runner común, `requirements.txt` y un README que explica datos, filtros, pipeline y resultados embebidos.

| Carpeta | Qué hace |
|---|---|
| **`bertopic_analysis/`** | Topic modeling **no supervisado** sobre los 5 corpus (embeddings multilingües + UMAP + HDBSCAN, reducido a 25 tópicos por fuente con c-TF-IDF). Stop-words ajustadas por dominio (`LEGAL_STOPWORDS`, `HEMICYCLE_STOPWORDS`, `TWITTER_STOPWORDS`). |
| **`manifestoberta_analysis/`** | Clasificación **supervisada** de cada documento en una de las **56 categorías MARPOR** + 7 dominios usando `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1`. Filtros alineados con `bertopic_analysis/` para que los resultados sean comparables doc-por-doc. Incluye validación contra el `cmp_code` humano (top-1 58%, top-3 82%, dominio 70%). |
| **`kg-gen/`** | Demo **experimental acotado** de extracción de triples (sujeto, predicado, objeto) sobre 25 intervenciones de un debate emblemático, con LLM local (Ollama + qwen2.5:3b). Documenta tiempos y calidad para justificar por qué KG-Gen no entra al pipeline final (~31 días para todas las intervenciones). |

## Orden de ejecución (reproducibilidad)

1. **`datos_diputados/`** — flujo del README (Twitter raw → limpieza → AN → merge) hasta obtener `processed/deputes_2017_2022.csv`.
2. **`twitter_zeeschuimer/`** — generar las URLs desde el CSV, capturar con Zeeschuimer y correr el merge.
3. **`lois_votes/`** — descargar Scrutins + Dossiers + Amendements y correr `build_laws_and_votes.py` y `build_leyes_texte_oficial.py`.
4. **`hemicycle/`** — colocar los `*.tsv.gz` en `hemicycle/fuente/` y ejecutar `python3 hemicycle/scripts/build_interventions_with_deputies.py`.
5. **`manifestos/`** — correr `manifestos/scripts/download_manifestos.py` con la API key de MARPOR.
6. **`bertopic_analysis/`** y **`manifestoberta_analysis/`** — con los 5 corpus ya en sus `processed/`, cada `<fuente>/run.py` los carga, aplica los filtros documentados y guarda resultados en `<fuente>/results/`.
7. **`kg-gen/`** — independiente del resto: instalar Ollama, descargar `qwen2.5:3b` y correr `scripts/01..03`.

**Índice detallado de archivos:** **[ESTRUCTURA.md](ESTRUCTURA.md)**.
