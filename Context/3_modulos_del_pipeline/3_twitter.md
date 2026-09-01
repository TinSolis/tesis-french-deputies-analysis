# Contexto de la carpeta: `french_deputies/twitter_zeeschuimer/`

## Propósito

Esta carpeta captura y procesa el **corpus de tweets** de los diputados de la XV legislatura francesa. No usa la API oficial de X/Twitter: recolecta el tráfico del navegador con la extensión **Zeeschuimer** mientras se hace scroll manual (automatizado) en cada perfil. Los exports `.ndjson` se transforman en CSV tabulares cruzados con `datos_diputados/processed/deputes_2017_2022.csv`. El **texto** de los tweets alimenta los módulos de análisis (`bertopic_analysis/tweets/`, `manifestoberta_analysis/tweets/`).

---

## Archivos importantes

### Documentación

| Archivo | Rol |
|---------|-----|
| `README.md` | Protocolo de captura (cuenta por cuenta, ~15 min de scroll, ~400 tweets), instalación de Zeeschuimer, comandos de procesamiento. |
| `captures/README.md` | Indica que los `.ndjson` son locales, pesados (>100 MB) y no se suben a GitHub. |

### Scripts (`scripts/`)

| Archivo | Función |
|---------|---------|
| `generate_twitter_url_list.py` | Lee `deputes_2017_2022.csv`, filtra diputados con `twitter_handle`, escribe `url_list.csv` y `url_list.txt` (una URL `https://twitter.com/<handle>` por línea). **Opcional**; en el repo actual esos archivos no están generados. |
| `merge_zeeschuimer_with_deputies.py` | Lee todos los `captures/*.ndjson`, parsea tweets del JSON de Zeeschuimer, cruza autor por `screen_name` con el CSV de diputados, escribe tres CSV en `processed/`. |

### Entrada manual (`captures/`)

| Ubicación | Contenido |
|-----------|-----------|
| `captures/*.ndjson` | Exports de Zeeschuimer (una línea JSON por ítem capturado). **Carpeta vacía de datos en el clone de Git** (solo README); los archivos viven en la máquina local del autor. |

### Salidas procesadas (`processed/`)

| Archivo | Contenido |
|---------|-----------|
| **`tweets_with_deputies.csv`** | Tabla completa: `tweet_id`, `timestamp`, `text`, `author_handle`, `mentioned_handles`, columnas del diputado (`deputy_id`, `full_name`, `political_group_abbrev`, etc.). |
| **`tweets_text_only.csv`** | Subconjunto para NLP: diputado + grupo + menciones + `text`. Entrada directa de BERTopic y ManifestoBERTa. |
| **`deputies_capture_summary.csv`** | Agregado por diputado: `tweets_en_captura`, `top_mentions` (handles más mencionados con conteo). |

> Los dos CSV grandes están en `.gitignore`; se regeneran con el script de merge. `deputies_capture_summary.csv` sí está versionado.

---

## Flujo / lógica principal

```
datos_diputados/processed/deputes_2017_2022.csv
         │
         ├──► [opcional] generate_twitter_url_list.py ──► url_list.csv / url_list.txt
         │
         ▼
Captura manual (Firefox + Zeeschuimer + autoscroller, ~15 min/cuenta)
         │
         ▼
captures/*.ndjson
         │
         ▼
merge_zeeschuimer_with_deputies.py  (cruce por author_handle normalizado)
         │
         ├──► processed/tweets_with_deputies.csv
         ├──► processed/tweets_text_only.csv
         └──► processed/deputies_capture_summary.csv
         │
         ▼
bertopic_analysis/tweets/run.py  |  manifestoberta_analysis/tweets/run.py
```

**Entrada upstream:** `deputes_2017_2022.csv` (587 diputados con `twitter_handle`).

**Lógica del merge (`merge_zeeschuimer_with_deputies.py`):**
- Normaliza handles (minúsculas, sin `@`).
- Extrae de cada línea NDJSON: `screen_name` desde `data.core.user_results.result.core.screen_name`; texto desde `data.legacy.full_text` o `note_tweet.note_tweet_results.result.text` (tweets largos); `tweet_id`, `created_at`.
- Fallbacks de autor: `source_platform_url`, campos legacy del export.
- Menciones: `entities.user_mentions` + regex `@handle` en el texto.
- Texto truncado a 5000 caracteres.
- Si el handle no está en el CSV de diputados, las columnas de diputado quedan vacías.

---

## Metodología

Enfoque de **recolección por captura de tráfico web** (web scraping pasivo en navegador), no API REST de X.

| Etapa | Herramienta / técnica | Detalle |
|-------|----------------------|---------|
| **1. Definición de cohorte** | `deputes_2017_2022.csv` | Universo: diputados XV legislatura con cuenta Twitter identificada por Regards Citoyens + AN. |
| **2. Captura estandarizada** | Zeeschuimer (extensión Firefox, Digital Methods Initiative) + FoxScroller | Por cuenta: abrir perfil, refrescar, activar captura, autoscroll **~15 min** → ~**400 tweets** según README. Protocolo fijo para volumen comparable entre diputados. |
| **3. Almacenamiento** | NDJSON (JSON Lines) | Un objeto JSON por línea; formato nativo de export de Zeeschuimer. |
| **4. ETL** | Python 3 (`json`, `csv`, `re`) | Parseo del esquema anidado de la API interna de X que Zeeschuimer intercepta. Sin dependencias externas en el script de merge. |
| **5. Entity linking** | Join por `twitter_handle` | Asignación diputado ↔ tweet por `screen_name` del autor (no por URL de perfil visitado). |
| **6. Análisis downstream** | BERTopic / ManifestoBERTa | Limpieza de texto (URLs, `@`, hashtags), filtro **≥ 10 palabras**, clasificación o topic modeling. |

**Supuestos de ingeniería:**
- El scroll de ~15 min aproxima una **ventana reciente** del timeline, no el archivo histórico completo de cada cuenta.
- La captura es **reproducible en procedimiento**, no en contenido exacto (X cambia qué muestra; fechas de captura afectan el corpus).
- Zeeschuimer captura lo visible en el navegador; no garantiza cobertura temporal 2017–2022 pese a que los módulos de análisis etiquetan el periodo como «mar/2017–2025».

**Criterios de evaluación / calidad (documentados en módulos de análisis):**
- Filtro de longitud: tweets con **≥ 10 palabras** tras limpieza (~93 % de retención según `bertopic_analysis/tweets/run.py`).
- Cobertura de diputados: cuentas capturadas vs. lista maestra (ver Resultados).
- Duplicados: mismo `tweet_id` puede aparecer en varios archivos NDJSON o sesiones.

**No hay modelos ni algoritmos de ML dentro de esta carpeta**; el procesamiento es parseo JSON + join relacional. El ML ocurre aguas abajo.

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Introducción** | Justificación de Twitter como fuente de comunicación política de diputados (alineado con *Propuesta_Memoria.txt*). |
| **Metodología — recolección** | Alternativa a API de X: Zeeschuimer, limitaciones legales/técnicas de scraping, protocolo estandarizado por cuenta. |
| **Metodología — integración de datos** | Cruce tweet–diputado por handle; extracción de menciones. |
| **Implementación** | Pipeline manual + script Python; estructura de carpetas `captures/` / `processed/`. |
| **Experimentos / resultados** | Volumen del corpus, cobertura por diputado, distribución de menciones (`deputies_capture_summary.csv`). |
| **Discusión / limitaciones** | Sesgo temporal (timeline reciente), duplicados, 54 cuentas sin captura, tweets de terceros en la línea de tiempo (632 ítems sin `deputy_id`). |
| **Anexos** | Esquema de columnas; comando de reproducción; referencias a Zeeschuimer y FoxScroller. |

---

## Resultados, decisiones o detalles relevantes

**Cifras verificadas en `processed/` (marzo 2026):**

| Métrica | Valor |
|---------|-------|
| Ítems totales en `tweets_with_deputies.csv` | **244 876** |
| Con `deputy_id` asignado | **244 244** (99,7 %) |
| Sin diputado (autor externo en timeline) | **632** |
| `tweet_id` únicos | **170 217** |
| Duplicados por `tweet_id` | **74 659** filas repetidas |
| Diputados en `deputies_capture_summary.csv` | **533** |
| Diputados con handle en maestro (`deputes_2017_2022.csv`) | **587** |
| **Sin captura** | **54** cuentas |
| Total tweets atribuidos a diputados (summary) | **244 244** |
| Media tweets/diputado capturado | **~458** (min 1, max **1402** — Alexandra Louis) |

**Downstream (tras limpieza ≥ 10 palabras):**
- BERTopic: **222 644** documentos (`bertopic_analysis/README.md`).
- ManifestoBERTa: **224 466** documentos (`manifestoberta_analysis/README.md`; pequeña diferencia en regex de hashtags).

**Decisiones técnicas:**
- Captura **cuenta por cuenta** con duración fija (~15 min), no por fecha ni por keyword.
- Salida analítica prioriza `text` + metadatos de diputado; menciones en columna aparte.
- CSVs pesados excluidos de Git; solo código, README y summary versionados.

**Limitaciones observables:**
- Timestamps en captura llegan hasta **feb. 2026** → corpus mezcla actividad reciente, no solo legislatura 2017–2022.
- Duplicación masiva entre sesiones NDJSON.
- `party_analysis/` no consume directamente esta carpeta.

---

## Dudas o cosas a revisar

1. **Cobertura temporal:** ¿se filtrará por fecha de legislatura antes del análisis o se asume el timeline reciente como proxy de comunicación parlamentaria?
2. **54 diputados sin captura:** ¿omitidos, pendientes o cuentas inactivas/protegidas?
3. **Deduplicación:** 74 659 duplicados por `tweet_id` — ¿se deduplican en análisis o se contaron varias veces?
4. **632 tweets sin diputado:** retweets o contenido de terceros en el feed; ¿se excluyen explícitamente en la memoria?
5. **Discrepancia de rutas:** README y `captures/README.md` dicen `zeeschuimer/`; la carpeta real es `twitter_zeeschuimer/` (`.gitignore` lista ambas).
6. **`url_list.csv`:** no generado en el repo; confirmar si se usó lista manual desde el CSV maestro.
7. **Reproducibilidad:** sin los `.ndjson` en Git, otro investigador debe re-capturar o recibir los archivos por otro canal.

---

## Resumen corto

`twitter_zeeschuimer/` obtiene tweets de diputados franceses mediante **Zeeschuimer** (captura en Firefox, ~15 min/cuenta) y los unifica con el CSV maestro de diputados en **`processed/tweets_text_only.csv`** (~245k ítems, 533/587 cuentas, texto listo para NLP). Es la fuente de **comunicación pública en redes** del proyecto; BERTopic y ManifestoBERTa la consumen tras limpieza y filtro de longitud. La principal limitación metodológica es que captura el **timeline reciente**, no el archivo histórico completo de la legislatura.

---

## Citas

- **Zeeschuimer** (extensión de captura, Digital Methods Initiative): [github.com/digitalmethodsinitiative/zeeshuimer](https://github.com/digitalmethodsinitiative/zeeschuimer); guía [zeeschuimer.4cat.nl](https://zeeschuimer.4cat.nl/).
- **FoxScroller** (autoscroll Firefox, citado en `README.md`): [addons.mozilla.org — FoxScroller](https://addons.mozilla.org/en-US/firefox/addon/foxscroller/).
- **Lista de diputados y handles:** `french_deputies/datos_diputados/processed/deputes_2017_2022.csv` (fuente: AN + [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires)).
- **Análisis downstream:** `french_deputies/bertopic_analysis/README.md`, `french_deputies/manifestoberta_analysis/README.md`; scripts `bertopic_analysis/tweets/run.py`, `manifestoberta_analysis/tweets/run.py`.
- **Documentación interna:** `french_deputies/twitter_zeeschuimer/README.md`, `french_deputies/ESTRUCTURA.md`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/twitter_zeeschuimer/` — captura y ETL del **corpus de tweets** de los diputados vía Zeeschuimer → `processed/tweets_text_only.csv`. Es el canal **declarado "comunicativo"**. Módulo de datos, sin ML propio. **Secundario en una vía:** alimenta el Análisis 1 (cross-channel) pero **no** la agenda revelada por el voto.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Datos** (principal) | Fuente Twitter, unidad = tweet, filtro ≥10 palabras, cobertura. |
| **Metodología / Implementación** | Captura por **tráfico de navegador** (no API de X), protocolo estandarizado, merge por handle. |
| **Resultados** | Volumen del corpus y cobertura por diputado. |
| **Discusión / limitaciones** | Sesgo temporal del timeline reciente; duplicados; cuentas sin captura. |
| **Anexos** | Esquema de columnas, comando de reproducción, referencias a Zeeschuimer/FoxScroller. |

**Información concreta a extraer:**
- ~**244.876** ítems (**244.244** con diputado; **170.217** `tweet_id` únicos); **533/587** cuentas capturadas (**54** sin captura); media ~458 tweets/cuenta.
- Docs NLP tras limpieza (≥10 palabras): **222.644** (BERTopic) / **224.466** (ManifestoBERTa) — la pequeña diferencia es por la regex de hashtags.
- Metodología clave: captura **reproducible en procedimiento, no en contenido** (X decide qué muestra).

**Figuras, tablas o métricas que contiene/menciona:**
- Tabla de cifras verificadas (244.876 / 244.244 / 170.217 / 533 / 54 …) y `deputies_capture_summary.csv` (tweets y top-mentions por diputado). **No produce figuras propias** (las visualizaciones de Twitter salen de BERTopic / `party_analysis/`).

**Limitaciones / dudas a trasladar (centrales):**
- **Cobertura temporal:** la captura llega hasta ~feb. 2026 → mezcla actividad **fuera** de la legislatura 2017–2022. Es la limitación metodológica principal; debe declararse explícitamente.
- **74.659** duplicados por `tweet_id` (tratamiento en análisis **por verificar**); **632** tweets sin diputado.
- Reproducibilidad: los `.ndjson` no están en Git (re-captura necesaria); discrepancia de rutas `zeeschuimer/` vs. `twitter_zeeschuimer/`.
