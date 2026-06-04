# Francia – diputados 2017-2022

En esta carpeta junto **todo el trabajo empírico** de la tesis sobre la XV legislatura francesa: lista de diputados (Assemblée nationale + Twitter), captura de timelines con Zeeschuimer, leyes y votos del hemiciclo, intervenciones parlamentarias, manifiestos electorales, y los tres módulos de análisis que se aplican sobre todo eso. El documento que encuadra la investigación está en la raíz del repo (*Propuesta_Memoria.pdf*).

En la raíz de **french_deputies** dejé solo este **README** y **ESTRUCTURA.md** (índice de archivos); todo lo demás está en subcarpetas separando fuentes, procesamiento y análisis.

## Corpus (las 5 fuentes textuales)

| Carpeta | Qué hice yo y para qué sirve |
|--------|------------------------------|
| **`datos_diputados/`** | Construí el CSV maestro de diputados a partir de Twitter (twitter-parlementaires) y los datos abiertos de la AN 15e; limpié y fusioné todo. El archivo que uso en **todo** lo demás es **`processed/deputes_2017_2022.csv`**. Detalle en **datos_diputados/README.md**. |
| **`twitter_zeeschuimer/`** | Capturé tweets cuenta por cuenta con Zeeschuimer y unifiqué los exports con mi lista de diputados; me quedé con el texto para el análisis. Detalle en **twitter_zeeschuimer/README.md**. |
| **`lois_votes/`** | Bajé los scrutins, dossiers y enmiendas de la AN; generé las tablas de leyes votadas, votos por diputado y texto JORF promulgado. Detalle en **lois_votes/votes_rd/README.md**. |
| **`hemicycle/`** | Procesé las intervenciones del hemiciclo (Regards Citoyens): la fuente va en **`fuente/`**, las tablas listas en **`processed/`**; **ND15** es la legislatura que coincide con mis diputados 2017-2022. Detalle en **hemicycle/README.md**. |
| **`manifestos/`** | Bajé los programas electorales 2017 de la API MARPOR + los textos completos por partido. Detalle en **manifestos/README.md**. |

## Módulos de análisis (sobre los 5 corpus)

Cada módulo tiene su propia carpeta con `<fuente>/run.py` por corpus, runner común, `requirements.txt` y un README que explica datos, filtros, pipeline y resultados embebidos.

| Carpeta | Qué hace |
|---|---|
| **`bertopic_analysis/`** | Topic modeling **no supervisado** sobre los 5 corpus (embeddings multilingües + UMAP + HDBSCAN, reducido a 25 tópicos por fuente con c-TF-IDF). Stop-words tuneadas por dominio (`LEGAL_STOPWORDS`, `HEMICYCLE_STOPWORDS`, `TWITTER_STOPWORDS`). |
| **`manifestoberta_analysis/`** | Clasificación **supervisada** de cada documento en una de las **56 categorías MARPOR** + 7 dominios usando `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1`. Filtros alineados con `bertopic_analysis/` para que los resultados sean comparables doc-por-doc. Incluye validación contra el `cmp_code` humano (top-1 58%, top-3 82%, dominio 70%). |
| **`kg-gen/`** | Demo **experimental acotado** de extracción de triples (sujeto, predicado, objeto) sobre 25 intervenciones de un debate emblemático, con LLM local (Ollama + qwen2.5:3b). Documenta tiempos y calidad para justificar por qué KG-Gen no entra al pipeline final (~31 días para todas las intervenciones). |

## Orden en que lo fui haciendo (y cómo lo volvería a correr)

1. **`datos_diputados/`** — flujo del README (Twitter raw → limpieza → AN → merge) hasta tener `processed/deputes_2017_2022.csv`.
2. **`twitter_zeeschuimer/`** — generé URLs desde el CSV, capturé con Zeeschuimer y corrí el merge.
3. **`lois_votes/`** — descargué Scrutins + Dossiers + Amendements, corrí `build_laws_and_votes.py` y `build_leyes_texte_oficial.py`.
4. **`hemicycle/`** — puse los `*.tsv.gz` en `hemicycle/fuente/` y ejecuté `python3 hemicycle/scripts/build_interventions_with_deputies.py`.
5. **`manifestos/`** — corrí `manifestos/scripts/download_manifestos.py` con la API key de MARPOR.
6. **`bertopic_analysis/`** y **`manifestoberta_analysis/`** — una vez que los 5 corpus están en sus `processed/`, cada `<fuente>/run.py` los carga, aplica los filtros documentados y guarda resultados en `<fuente>/results/`.
7. **`kg-gen/`** — independiente del resto: instalar Ollama, descargar `qwen2.5:3b` y correr `scripts/01..03`.

**Índice detallado de archivos:** **[ESTRUCTURA.md](ESTRUCTURA.md)**.
