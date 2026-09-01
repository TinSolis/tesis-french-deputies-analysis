# Contexto de la carpeta: `french_deputies/manifestos/`

## Propósito

Esta carpeta almacena los **programas electorales (manifiestos) de los partidos franceses en la elección legislativa de junio 2017**, obtenidos del **[Manifesto Project (MARPOR)](https://manifesto-project.wzb.eu/)**. Sirve como corpus de **agenda declarada** en campaña: textos pre-segmentados en *quasi-sentences* con códigos temáticos humanos (`cmp_code`). En el proyecto enlaza la cohorte de diputados (`political_group_abbrev`) con la posición programática de su partido vía `group_to_party_mapping.csv`, y alimenta análisis downstream (BERTopic, ManifestoBERTa, `party_analysis/`, validación CHES).

---

## Archivos importantes

### Script

| Archivo | Función |
|---------|---------|
| `scripts/download_manifestos.py` | Pipeline automatizado contra la API REST de MARPOR: dataset core, metadatos del corpus y textos anotados. Requiere `MARPOR_API_KEY`. |

### Datos raw (`data/`)

| Archivo | Contenido |
|---------|-----------|
| `marpor_core_france_2017.csv` | **10 partidos**, ~100+ columnas MARPOR (`per101`…`per706`, `rile`, `planeco`, etc.). Filtrado de `MPDS2025a` por `countryname == France` y `edate` con «2017». |
| `marpor_corpus_metadata.json` | Metadatos del corpus por `manifesto_id` (idioma, PDF original, `annotations: true/false`, handbook v5). |

### Salidas procesadas (`processed/`)

| Archivo | Contenido |
|---------|-----------|
| **`manifesto_texts.csv`** | **3 801 quasi-frases** de **10 manifiestos**. Columnas: `manifesto_id`, `text`, `cmp_code`, `eu_code`. Unidad principal para NLP. |
| **`manifesto_full_texts.csv`** | Texto **completo por partido** (10 filas): `manifesto_id`, `party_abbrev`, `party_name`, `num_sentences`, `full_text`. **Generado manualmente** concatenando quasi-frases (no lo produce el script). |
| **`party_positions.csv`** | Resumen por partido: `rile`, `planeco`, `markeco`, `welfare`, `intpeace`. |
| **`textos_por_partido/*.txt`** | Un `.txt` por partido (ej. `LFI_31240_201706.txt`). Mismo contenido que `full_text`; **generado manualmente**. |

### Mapeo

| Archivo | Función |
|---------|---------|
| `group_to_party_mapping.csv` | Tabla `political_group_abbrev` → `party_name_marpor` + código/fecha MARPOR. Incluye notas sobre grupos sin manifiesto único (LT, EDS, AGIR-E). |

### Documentación

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Partidos descargados, flujo API, significado de `cmp_code`/`rile`, cadena de cruce con diputados. |

---

## Flujo / lógica principal

```
Registro MARPOR + MARPOR_API_KEY
         │
         ▼
download_manifestos.py
         │
         ├──► data/marpor_core_france_2017.csv      (posiciones agregadas por partido)
         ├──► data/marpor_corpus_metadata.json      (disponibilidad de texto)
         ├──► processed/manifesto_texts.csv         (quasi-frases + cmp_code)
         └──► processed/party_positions.csv         (rile, planeco, …)
         │
         ▼  [paso manual, documentado en README]
concatenación de quasi-frases por manifesto_id
         │
         ├──► processed/manifesto_full_texts.csv
         └──► processed/textos_por_partido/<PARTIDO>_<code>_201706.txt

deputes_2017_2022.csv (political_group_abbrev)
         │
         ▼
group_to_party_mapping.csv  →  manifesto_id / textos / party_positions
         │
         ▼
bertopic_analysis/manifestos/  |  manifestoberta_analysis/manifestos/
party_analysis/manifestos/     |  ches_analysis/manifestos/
```

**Entradas externas:** API MARPOR v1 (`https://manifesto-project.wzb.eu/api/v1`), dataset **`MPDS2025a`**, versión de corpus con tag más reciente (en metadatos locales: handbook **5**, corpus **2025-1**).

**Salida clave para el resto del proyecto:** `processed/manifesto_texts.csv` (3 801 documentos, sin filtro de longitud en análisis).

---

## Metodología

Enfoque de **adquisición vía API académica** + **normalización tabular** en Python. **No hay modelos de ML en esta carpeta**; la anotación temática humana viene ya en MARPOR (`cmp_code`).

| Etapa | Herramienta | Detalle |
|-------|-------------|---------|
| **1. Autenticación** | Variable `MARPOR_API_KEY` o `--api-key` | Cuenta gratuita en manifesto-project.wzb.eu. |
| **2. Dataset core** | `GET /get_core` (`kind=csv`, `key=MPDS2025a`) | Filtro programático: Francia + elección 2017 → 10 filas partido. |
| **3. Claves de corpus** | Construcción `{party}_{date}` | Ej.: `31240_201706` para LFI. |
| **4. Metadatos** | `POST /metadata` | Verifica qué manifiestos tienen `annotations: true`. |
| **5. Textos** | `POST /texts_and_annotations` | Extrae quasi-frases con `text`, `cmp_code`, `eu_code`. |
| **6. Posiciones** | Subconjunto de columnas del core | `save_positions()` → `party_positions.csv`. |
| **7. Textos completos** | **Manual** (post-script) | Concatenación de quasi-frases por `manifesto_id`. |
| **8. Entity linking** | `group_to_party_mapping.csv` | Une grupos parlamentarios AN con partidos MARPOR 2017. |

**Unidad de análisis:** *quasi-sentence* MARPOR (segmentación y codificación hecha por anotadores del proyecto según el Handbook). No se re-segmenta ni se filtra por longitud en los módulos de análisis (salvo descartar textos vacíos).

**Algoritmos en esta carpeta:** filtrado CSV, construcción de claves, parseo JSON de la API, escritura de tablas. Sin embeddings ni clasificación aquí.

**Criterios de evaluación / calidad (observables):**
- **Cobertura textual:** los 10 partidos del core tienen `annotations: true` en `marpor_corpus_metadata.json`.
- **Cardinalidad:** 3 801 quasi-frases distribuidas en 10 manifiestos (PCF: 39; LFI: 1 113; ver conteos por `manifesto_id` en `manifesto_texts.csv`).
- **Cobertura diputados:** **628 / 668** (94,0 %) tienen grupo mapeado a un `party_name_marpor` no vacío; **40** quedan fuera (LT, EDS, AGIR-E, grupo vacío).
- **Validación downstream (fuera de esta carpeta):** ManifestoBERTa vs. `cmp_code` humano → accuracy top-1 **58,3 %**, top-3 **82 %** (`manifestoberta_analysis/README.md`, script `validate_against_marpor.py`).

**Supuestos de ingeniería:**
- Los manifiestos corresponden a la **elección de 2017**, aunque algunos títulos en metadatos refieran documentos presidenciales (ej. EELV).
- Un diputado se asigna al manifiesto de su **grupo parlamentario** mapeado, no a un programa individual.
- Grupos menores / escisiones posteriores (EDS, AGIR-E) **no tienen** manifiesto propio en MARPOR 2017.
- `manifesto_full_texts.csv` y `textos_por_partido/` deben **regenerarse a mano** si se vuelve a correr el script de descarga.

**Dependencias:** Python 3, `requests`.

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Introducción / marco teórico** | Manifiestos como fuente estándar en ciencia política comparada (MARPOR desde 1979). |
| **Metodología — recolección** | API académica MARPOR, quasi-sentences, esquema de 56 categorías / 7 dominios. |
| **Metodología — agenda declarada** | Contraste con tweets, hemiciclo (declarada) vs. votos (revelada) en `party_analysis/`. |
| **Implementación** | Script `download_manifestos.py`, mapeo grupo→partido, paso manual de textos completos. |
| **Experimentos / resultados** | Distribución temática por partido; RILE oficial en `party_positions.csv`; validación ManifestoBERTa y CHES. |
| **Discusión / limitaciones** | Muestras pequeñas (PCF 39, PS 79); LR/UDI comparten contenido; grupos no mapeados. |
| **Anexos** | Tabla de 10 partidos con códigos MARPOR; ejemplos de `cmp_code`; URLs del Handbook. |

---

## Resultados, decisiones o detalles relevantes

**10 partidos** (junio 2017), con RILE en `party_positions.csv`:

| Partido | Código | RILE | Quasi-frases |
|---------|--------|------|--------------|
| LFI | 31240 | -30,0 | 1 113 |
| PS | 31320 | -28,9 | 79 |
| MoDem | 31624 | -17,9 | 493 |
| PCF | 31220 | -16,7 | 39 |
| PRG | 31230 | -10,1 | 625 |
| EELV | 31110 | -8,6 | 228 |
| LREM | 31425 | 0,0 | 386 |
| FN | 31720 | +1,7 | 274 |
| UDI | 31430 | +13,6 | 282 |
| LR | 31626 | +13,6 | 282 |

**Decisiones técnicas:**
- Corpus fijado a **Francia 2017** del dataset **MPDS2025a**.
- Sin filtro de longitud en análisis: la quasi-sentence es la unidad nativa MARPOR.
- `group_to_party_mapping.csv` agrupa variantes (MODEM/DEM, NG→PS, LC→LR, NI→FN).

**Limitaciones documentadas en el proyecto:**
- **LR y UDI son el mismo documento MARPOR (verificado).** `LR_31626_201706.txt` y `UDI_31430_201706.txt` son **byte-idénticos** (`diff` → idénticos): 282 quasi-frases cada uno, **31.438 caracteres = 33.032 bytes**, y métricas idénticas en `party_positions.csv` (rile 13.619, planeco 0.389, markeco 5.058, welfare 13.619). No es un error de exportación del proyecto: **MARPOR asignó el mismo manifiesto a los IDs 31626 (LR) y 31430 (UDI)**. En el análisis cuentan como uno; sus 282+282 frases idénticas forman parte del corpus de 3.801.
- **PCF y PS**: corpus muy pequeño para firmas temáticas robustas.
- **Cobertura de diputados (verificado): 628/668 = 94,0 %.** Quedan fuera exactamente **40 diputados** de los 4 grupos sin `party_name_marpor`: LT (13), grupo vacío (13), EDS (9), AGIR-E (5). El «~85 %» del README es aproximado y alude a un subconjunto de "partidos principales"; **usar 94 %** en la memoria.
- Constante `FRANCE_2017_EDATE = "200706"` en el script **no se usa** en el filtro (se filtra por `"2017" in edate`).

**Consumidores:** `bertopic_analysis/manifestos/run.py`, `manifestoberta_analysis/manifestos/run.py`, `party_analysis/manifestos/run.py`, `ches_analysis/manifestos/run.py` (este último usa también `party_positions.csv` como RILE oficial).

---

## Dudas o cosas a revisar

1. **`manifesto_full_texts.csv` / `textos_por_partido/`:** no hay script versionado que los genere; documentar el procedimiento exacto de concatenación para reproducibilidad.
2. ~~**Discrepancia 85 % vs 94 %**~~ **RESUELTO:** la cifra reproducible es **94,0 % (628/668)**; el 85 % era aproximado (subconjunto). 40 diputados fuera (LT, grupo vacío, EDS, AGIR-E).
3. ~~**LR vs UDI**~~ **RESUELTO:** comparten **el mismo documento MARPOR** (txt byte-idénticos, métricas idénticas); es un hecho del dataset MARPOR, no artefacto de exportación del proyecto.
4. **Ventana temporal:** metadatos EELV titulan medidas presidenciales 2017 — ¿es el manifiesto legislativo correcto para cada partido?
5. **Encoding:** `party_positions.csv` muestra `EÃLV` en `partyabbrev` — posible problema UTF-8 al re-exportar.
6. **Re-ejecución del script:** ¿sobrescribe solo lo automatizado y obliga a regenerar textos completos manualmente?

---

## Resumen corto

`manifestos/` descarga vía API MARPOR los **programas electorales franceses 2017** (10 partidos, **3 801 quasi-frases** anotadas) y los vincula a los diputados del proyecto mediante `group_to_party_mapping.csv`. Es el corpus de **agenda declarada en campaña** y el único con **ground truth humano** (`cmp_code`) para validar ManifestoBERTa. El script automatiza la descarga; los textos completos por partido se armaron **a mano** después.

---

## Citas

- **Manifesto Project (MARPOR):** [manifesto-project.wzb.eu](https://manifesto-project.wzb.eu/); dataset [MPDS2025a](https://manifesto-project.wzb.eu/datasets).
- **API REST MARPOR:** [documentación API](https://manifesto-project.wzb.eu/information/documents/api) — endpoints usados: `get_core`, `list_metadata_versions`, `metadata`, `texts_and_annotations`.
- **Esquema de categorías / Handbook:** [Category Scheme](https://manifesto-project.wzb.eu/information/documents/handbooks) (Handbook v5 en metadatos locales).
- **RILE:** índice izquierda–derecha estándar MARPOR (Laver & Budge; documentado en `README.md` y `ches_analysis/common/rile.py`).
- **ManifestoBERTa (análisis downstream):** [manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1](https://huggingface.co/manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1).
- **Documentación interna:** `french_deputies/manifestos/README.md`, `french_deputies/ESTRUCTURA.md`, `french_deputies/party_analysis/README.md`, `french_deputies/manifestoberta_analysis/README.md`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/manifestos/` — descarga vía API MARPOR de los **programas electorales franceses 2017** → `processed/manifesto_texts.csv`. Es el corpus de **agenda declarada en campaña** y **el único con ground truth humano** (`cmp_code`). Módulo de datos no experimental, pero **estratégico** porque habilita la validación de ManifestoBERTa y CHES.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Revisión de literatura** | MARPOR como fuente estándar en ciencia política comparada (desde 1979); concepto de *quasi-sentence*. |
| **Datos** (principal) | Corpus de manifiestos: 10 partidos, 3.801 quasi-frases, mapeo grupo→partido. |
| **Metodología** | Esquema MARPOR de 56 categorías / 7 dominios; unidad nativa (sin filtro de longitud). |
| **Implementación** | `download_manifestos.py` (API) + **paso manual** de textos completos. |
| **Validación** | Provee el `cmp_code` humano: base de la validación de ManifestoBERTa y del RILE oficial en CHES. |
| **Resultados** | Distribución temática y RILE oficial por partido. |
| **Discusión / limitaciones** | Muestras chicas; LR=UDI; grupos no mapeados. |
| **Anexos** | Tabla de 10 partidos con códigos/RILE; ejemplos de `cmp_code`. |

**Información concreta a extraer:**
- **10 partidos**, **3.801 quasi-frases**; cobertura de diputados **628/668 = 94,0 %** (**usar 94 %**, no el ~85 % aproximado del README); 40 diputados fuera (LT, grupo vacío, EDS, AGIR-E).
- **LR y UDI comparten el mismo documento MARPOR** (txt byte-idénticos, IDs 31626/31430): es un hecho del dataset MARPOR, no un bug; en el análisis **cuentan como uno**.
- RILE oficial por partido vive en `party_positions.csv` (insumo del *sanity check* de CHES).

**Figuras, tablas o métricas que contiene/menciona:**
- **Tabla partido → código → RILE → nº quasi-frases** (LFI 31240/−30,0/1.113 … LR/UDI 13,6/282) — lista para anexo o resultados. **Sin figuras propias.**

**Limitaciones / dudas a trasladar:**
- **Muestras pequeñas:** PCF (39 frases) y PS (79) → firmas indicativas, no robustas.
- **LR=UDI** duplicado (aclarar que es del dataset).
- `manifesto_full_texts.csv` y `textos_por_partido/` se generan **a mano** (riesgo de reproducibilidad); encoding `EÃLV` en `party_positions.csv`; ventana temporal (algunos metadatos EELV citan medidas presidenciales).
