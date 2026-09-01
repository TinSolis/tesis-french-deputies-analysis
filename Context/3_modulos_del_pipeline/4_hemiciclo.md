# Contexto de la carpeta: `french_deputies/hemicycle/`

## Propósito

Esta carpeta procesa el **corpus de intervenciones en el hemiciclo** de la Assemblée nationale (compte rendu integral): lo que dicen diputados y otras figuras en sesión. La fuente es **Regards Citoyens** (export `*_ND##_interventions_hemicycle_rich.tsv.gz`). Para la tesis, el subconjunto **ND15 = XV legislatura (2017–2022)** se cruza con `deputes_2017_2022.csv`. Es la fuente de **discurso parlamentario oral/escrito en sesión** (agenda declarada en el hemiciclo), complementaria de Twitter, manifiestos y votos.

---

## Archivos importantes

### Documentación

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Estructura, columnas clave, comandos, orden de magnitud del corpus. |
| `GUIA_IDENTIFICADORES_TESIS.md` | Diccionario de columnas y enlaces con diputados, Twitter y votos. |
| `RESUMEN_CUANTITATIVO.md` | Métricas regenerables (949 718 intervenciones, tipos, ejemplos). |

### Scripts (`scripts/`)

| Archivo | Función |
|---------|---------|
| `build_interventions_with_deputies.py` | Lee TSV.gz en `fuente/`, limpia HTML, parsea URLs CRI, cruza ND15 con diputados por nombre, escribe tablas en `processed/`. |
| `report_hemicycle_stats.py` | Lee `interventions_xv_2017_2022_meta.csv.gz` y regenera `RESUMEN_CUANTITATIVO.md`. |

### Entrada manual (`fuente/`)

| Archivo | Nota |
|---------|------|
| `20250916_ND15_interventions_hemicycle_rich.tsv.gz` | Export ND15 presente en el repo local (~116 MB). **Gitignored** (`fuente/*.tsv.gz`). |

### Salidas (`processed/`)

| Archivo | Contenido |
|---------|-----------|
| **`interventions_xv_2017_2022_with_deputies.csv.gz`** | Tabla maestra (~139 MB): texto + metadatos + columnas `deputy_*`. Entrada de BERTopic/ManifestoBERTa. |
| **`interventions_xv_2017_2022_meta.csv.gz`** | Igual sin `intervention_plain` (~24 MB). |
| **`interventions_xv_2017_2022_texts.csv.gz`** | `intervention_id` + texto (~100 MB). |
| **`interventions_xv_sample5000.csv`** | Muestra de 5 000 filas sin comprimir (versionada; usada por `kg-gen/`). |
| `interventions_xiii_xiv_xvi_speaker_text.csv.gz` | Agregado ND13/14/16 **solo si** hay esos TSV en `fuente/`; no se sobrescribe si solo hay ND15. |

---

## Flujo / lógica principal

```
Regards Citoyens: *_ND15_interventions_hemicycle_rich.tsv.gz  →  fuente/
         │
         ▼
build_interventions_with_deputies.py
         │  (strip HTML → intervention_plain; parse source_url → cri_*)
         │  (ND15: match parlementaire ↔ full_name en deputes_2017_2022.csv)
         ▼
processed/interventions_xv_2017_2022_*.csv.gz  +  sample5000.csv
         │
         ▼
report_hemicycle_stats.py  →  RESUMEN_CUANTITATIVO.md
         │
         ▼
bertopic_analysis/interventions/  |  manifestoberta_analysis/interventions/
party_analysis/interventions/     |  kg-gen/ (muestra)
```

**Entrada upstream:** `datos_diputados/processed/deputes_2017_2022.csv`.

**Salida analítica principal:** `intervention_plain` con `deputy_id`, `political_group_abbrev`, `type`, `section`, `date`, `source_url`.

**No hay ID de ley** por fila: el vínculo hemiciclo ↔ ley concreta requiere razonamiento por `section`/fecha/contexto (documentado en README y RESUMEN).

---

## Metodología

Enfoque de **ETL sobre export tabular** + **entity linking por nombre**. **No hay modelos de ML en esta carpeta.**

| Etapa | Técnica | Detalle |
|-------|---------|---------|
| **1. Ingesta** | TSV gzip, delimitador tab | `csv.DictReader` sobre `*_ND##_interventions_hemicycle_rich.tsv.gz`. |
| **2. Legislatura** | Regex `_ND(\d+)_` en nombre de archivo | ND15 → pipeline XV con cruce a diputados; otras → agregado opcional sin `deputy_*`. |
| **3. Limpieza texto** | Regex HTML + `html.unescape` | Campo `intervention` → `intervention_plain`. |
| **4. Entity linking** | Normalización NFKD + lowercase | `parlementaire` vs. `full_name` en CSV diputados; primer match gana. |
| **5. Enriquecimiento URL** | Regex CRI AN | `cri_url_legislature_num`, `cri_session_period`, `cri_page_file`, `cri_anchor_id`. |
| **6. Partición de salidas** | CSV gzip + muestra | Meta/textos separados para pipelines NLP sin cargar columnas pesadas. |
| **7. Estadísticas** | Agregación en memoria | `report_hemicycle_stats.py` → markdown con conteos y heurística `section` legislativa. |

**Unidad de observación:** una **intervención** (turno en el acta), no un “discurso” de campaña ni una sesión completa.

**Criterios de evaluación / calidad:**
- **`nb_mots` > 0:** señal de texto analizable (949 718 / 949 718 en export actual).
- **Cobertura diputado:** **661 690** filas con `deputy_id` (**69,7 %** del total); **646** diputados distintos con al menos una intervención.
- **Filtros NLP downstream** (`bertopic_analysis/interventions/run.py`, alineados con ManifestoBERTa):
  - `deputy_id` no nulo
  - **≥ 10 palabras** (`nb_mots`)
  - Exclusión procedimental por regex (apertura/cierre sesión, «je mets aux voix», «la parole est à», etc.)
  - **Resultado final: 338 192** documentos para análisis temático

**Supuestos de ingeniería:**
- `parlementaire_groupe` (acta) puede diferir de `political_group_abbrev` (CSV) por cambios de bancada.
- `section`/`sous_section` son **proxy temático**, no taxonomía oficial de leyes.
- Match por nombre completo sin fuzzy matching; oradores sin match conservan metadatos del acta pero sin `deputy_id`.
- Archivos `.csv.gz` grandes no se versionan; solo `sample5000` y documentación en Git.

**Dependencias:** Python 3, stdlib (`csv`, `gzip`, `re`, `unicodedata`).

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Introducción** | Discurso parlamentario como canal institucional vs. redes / manifiestos. |
| **Metodología — recolección** | Export Regards Citoyens; ND15 alineado con cohorte 2017–2022. |
| **Metodología — construcción del corpus** | Limpieza HTML, cruce diputado, filtros procedurales para NLP. |
| **Implementación** | Dos scripts Python; separación meta/texto; regeneración de estadísticas. |
| **Resultados** | Volumen (~950k intervenciones); dominancia `type=loi` (839 970); análisis por partido en `party_analysis/`. |
| **Discusión** | Sesgo hacia meta-política (dominio Political System en NLP); límite de enlace con votos/leyes. |
| **Anexos** | `GUIA_IDENTIFICADORES_TESIS.md`; ejemplos en `RESUMEN_CUANTITATIVO.md`; `source_url` para citar acta. |

---

## Resultados, decisiones o detalles relevantes

**Cifras (ND15, `RESUMEN_CUANTITATIVO.md`):**

| Métrica | Valor |
|---------|-------|
| Intervenciones totales | **949 718** |
| Con `nb_mots` > 0 | **949 718** |
| Con `deputy_id` | **661 690** (~70 %) |
| Diputados distintos con intervención | **646** |
| `seance_id` distintos | **1 561** |
| Días con actividad (`date`) | **737** |
| Títulos `section` distintos | **18 547** |
| `type = loi` | **839 970** |
| `type = question` | **109 748** |
| Scrutins adopción ley (comparación) | **373** (`leyes_votadas_2017_2022.csv`) |
| Docs NLP (post-filtros) | **338 192** |

**Decisiones técnicas:**
- Cuatro artefactos ND15 (completo, meta, textos, muestra 5 000).
- Columnas `deputy_*` y Twitter propagadas desde CSV maestro al hacer match.
- Si solo hay ND15 en `fuente/`, no se regenera el agregado de otras legislaturas.

**Limitaciones:**
- ~30 % de intervenciones sin `deputy_id` (ministros, presidentes de sesión, nombres no en cohorte, errores de match).
- Granularidad distinta a votos (turno de palabra vs. scrutin).
- `party_analysis`: dominio dominante Political System; oposición sobre-enfatiza 305 Autoridad Política (documentado en `party_analysis/README.md`).

**Consumidores:** `bertopic_analysis/interventions/`, `manifestoberta_analysis/interventions/`, `party_analysis/interventions/`, `kg-gen/scripts/01_build_sample.py`.

---

## Dudas o cosas a revisar

1. **Conteo exacto sin match:** el build imprime aviso de `parlementaire` sin match; no está consolidado en `RESUMEN_CUANTITATIVO.md`.
2. **BERTopic docstring** menciona ~508k docs tras filtros iniciales vs. **338 192** finales tras regex procedimental — usar cifra de `manifestoberta_analysis/README.md` para la memoria.
3. **URL de descarga** del TSV Regards Citoyens no está documentada en el repo (solo nombre de archivo `20250916_ND15_…`).
4. **Enlace hemiciclo ↔ ley:** heurística de `section` (5 132 títulos con palabras clave) no sustituye cruce con `dossier_uid` de `lois_votes/`.
5. **`parlementaire_groupe` vs. `political_group_abbrev`:** no hay métrica de discordancia publicada.
6. **Otras legislaturas:** actualmente solo ND15 en `fuente/`; agregado XIII/XIV/XVI no generado en este clone.

---

## Resumen corto

`hemicycle/` transforma el export **Regards Citoyens ND15** en tablas de **~950k intervenciones** de la XV legislatura, con texto plano y cruce a **646 diputados** de la cohorte (**661 690** filas con `deputy_id`). Es el corpus de **debate parlamentario en sesión**; tras filtros (cohorte, ≥10 palabras, no procedimental) alimenta el NLP con **338k** documentos. No enlaza automáticamente cada intervención con una ley votada.

---

## Citas

- **Regards Citoyens** (export intervenciones hemiciclo): citado en `README.md` y `build_interventions_with_deputies.py`; proyecto [regardscitoyens.org](https://www.regardscitoyens.org/).
- **Assemblée nationale — Compte rendu intégral (CRI):** URLs en `source_url` / campos `cri_*` (ej. `assemblee-nationale.fr/15/cri/...`).
- **Cohorte diputados:** `french_deputies/datos_diputados/processed/deputes_2017_2022.csv`.
- **Votos (comparación):** `french_deputies/lois_votes/votes_rd/processed/leyes_votadas_2017_2022.csv`.
- **Análisis downstream:** `french_deputies/bertopic_analysis/README.md`, `french_deputies/manifestoberta_analysis/README.md`, `french_deputies/party_analysis/README.md`, `french_deputies/kg-gen/README.md`.
- **Documentación interna:** `french_deputies/hemicycle/README.md`, `GUIA_IDENTIFICADORES_TESIS.md`, `RESUMEN_CUANTITATIVO.md`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/hemicycle/` — corpus de **intervenciones en el hemiciclo** (Regards Citoyens ND15) → tablas `interventions_xv_2017_2022_*.csv.gz`. Es el canal **declarado "institucional"** (debate parlamentario en sesión). Módulo de datos, sin ML propio.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Datos** (principal) | Corpus de ~950k intervenciones; texto, sección, fecha, `deputy_id`. |
| **Metodología** | Unidad = intervención (turno); filtros NLP (cohorte + ≥10 palabras + no procedimental). |
| **Implementación** | 2 scripts; limpieza HTML; separación meta/texto; regeneración de estadísticas. |
| **Resultados** | Volumen y dominancia de *Political System* (meta-política) por canal. |
| **Discusión / limitaciones** | Sesgo meta-político; sin enlace automático intervención↔ley. |
| **Anexos** | `GUIA_IDENTIFICADORES_TESIS.md`; ejemplos; `source_url` para citar el acta. |

**Información concreta a extraer:**
- **949.718** intervenciones; **661.690** con `deputy_id` (**~70 %**); **646** diputados distintos.
- Insumo NLP tras filtros: **338.192** documentos — **usar esta cifra** (no el ~508k del docstring de BERTopic).
- Composición por tipo: `type=loi` 839.970, `type=question` 109.748.

**Figuras, tablas o métricas que contiene/menciona:**
- Tabla de cifras de `RESUMEN_CUANTITATIVO.md` (intervenciones, `seance_id`, días con actividad, títulos `section`, tipos). **Sin figuras propias** (heatmaps por grupo salen de BERTopic/`party_analysis/`).

**Limitaciones / dudas a trasladar:**
- **~30 %** de intervenciones **sin `deputy_id`** (ministros, presidencia, no-cohorte, errores de match por nombre sin fuzzy).
- `section`/`sous_section` son **proxy temático**, no taxonomía oficial; el enlace hemiciclo↔ley es heurístico (no por `dossier_uid`) → no sobre-interpretar.
- `parlementaire_groupe` (acta) puede diferir de `political_group_abbrev` (CSV); sin métrica de discordancia publicada. URL de descarga del TSV no documentada.
