# Contexto de la carpeta: `french_deputies/datos_diputados/`

## Propósito

Esta carpeta construye el **CSV maestro de diputados de la XV legislatura francesa (2017–2022)**. Integra identidad parlamentaria oficial (Assemblée nationale, 15e législature) con cuentas de Twitter (proyecto *twitter-parlementaires* de Regards Citoyens). La salida consolidada —`processed/deputes_2017_2022.csv`— es la **tabla de referencia** que el resto del proyecto usa para identificar siempre al mismo diputado con el mismo `id` y enlazar Twitter, votos, intervenciones y análisis por partido.

Convención interna (documentada en `README.md`): archivos con sufijo `_rd` = *raw* o casi sin transformar; sin `_rd` = tablas limpiadas o derivadas.

---

## Archivos importantes

### Scripts (`scripts/`)

| Archivo | Función |
|---------|---------|
| `fetch_an_15e_deputes.py` | Descarga (o reutiliza) el ZIP `AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip` desde `data.assemblee-nationale.fr`, parsea JSON de acteurs y organes políticos (tipo `GP`), y escribe `data/deputes_an_rd.csv`. |
| `build_deputes_twitter_csv.py` | Lee `data/deputes_twitter_rd.csv`, renombra columnas al inglés, extrae solo URLs `twitter.com` de `sites_web`, y escribe `data/deputes_twitter.csv`. |
| `merge_deputes_2017_2022.py` | Cruza AN + Twitter por `(family_name, first_name)`; produce `data/deputes_rd.csv` (solo AN, separador `;`) y `processed/deputes_2017_2022.csv` (AN + columnas Twitter). |

### Datos de entrada (`data/`)

| Archivo | Origen / rol |
|---------|----------------|
| `deputes_twitter_rd.csv` | CSV de [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) (Regards Citoyens). **599 filas** de datos (+ cabecera). |
| `deputes_an_rd.csv` | Salida del script AN. **668 diputados**. Columnas: `id`, identidad, circunscripción, fechas de mandato, grupo político. |
| `deputes_twitter.csv` | Twitter limpio. Mismas **599 filas**. |
| `deputes_rd.csv` | Copia tabular de AN con separador `;` (intermedio del merge). |

### Salida principal (`processed/`)

| Archivo | Rol |
|---------|-----|
| **`deputes_2017_2022.csv`** | **Tabla final del proyecto.** **668 filas**, separador `;`. 15 columnas AN + 6 de Twitter (`twitter_handle`, `twitter_verified`, `twitter_id`, `twitter_name`, `twitter_created_at`, `twitter_web_urls`). |

### Archivos presentes pero fuera del pipeline documentado

| Archivo | Nota |
|---------|------|
| `data/deputes_2017_2022_an.csv` | **668 filas**, columnas en francés (`nom_de_famille`, `groupe_sigle`, `id_an`, etc.). No está referenciado en `README.md` ni en ningún script de esta carpeta. Parece export alternativo (posiblemente NosDéputés o AN en formato distinto). |
| `data/nosdeputes.fr_deputes_2026-02-19.csv` | Snapshot de **618 filas** con metadatos ampliados de NosDéputés.fr. No participa en los scripts actuales. |

### Documentación

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Flujo de ejecución, convención `_rd`, fuentes y lógica de merge. |

---

## Flujo / lógica principal

```
deputes_twitter_rd.csv  ──► build_deputes_twitter_csv.py ──► deputes_twitter.csv
                                                                    │
ZIP AN 15e (data/)  ──► fetch_an_15e_deputes.py ──► deputes_an_rd.csv ──┤
                                                                    │
                                                                    ▼
                                          merge_deputes_2017_2022.py
                                                                    │
                                    ┌───────────────────────────────┴───────────────────────────────┐
                                    ▼                                                               ▼
                          data/deputes_rd.csv                              processed/deputes_2017_2022.csv
                          (solo AN, ;)                                     (AN + Twitter, ;)
```

**Entradas externas:**
1. [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) → `deputes_twitter_rd.csv`
2. Open data AN 15e: ZIP de acteurs/députés ([URL fija en `fetch_an_15e_deputes.py`](https://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_senateurs_ministres_legislature/AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip))

**Lógica del script AN (`fetch_an_15e_deputes.py`):**
- Extrae `id` numérico del UID (`PA(\d+)`).
- Toma mandato de tipo `ASSEMBLEE` (fechas, departamento, circunscripción).
- Asigna grupo político (`GP`) cuyo mandato solapa el periodo 2017-06-18 – 2022-06-21.
- Marca `former_deputy = 1` si existe `mandate_end`.

**Lógica del merge (`merge_deputes_2017_2022.py`):**
- Clave de cruce: `(family_name.strip(), first_name.strip())`.
- Si no hay match en Twitter, las columnas Twitter quedan vacías.
- Al ejecutar, el script imprime cuántos diputados recibieron `twitter_handle` (en los datos actuales: **587 de 668**).

**Consumidores downstream** (en otras carpetas del repo):
- `twitter_zeeschuimer/scripts/generate_twitter_url_list.py` y `merge_zeeschuimer_with_deputies.py` → cruce por `twitter_handle`.
- `lois_votes/scripts/build_laws_and_votes.py` → cohorte filtrada por `id` en `deputes_2017_2022.csv` (`votos_por_diputado_cohorte.csv`).
- `hemicycle/scripts/build_interventions_with_deputies.py` → cruce ND15 con el CSV consolidado.
- `party_analysis/lois/run.py` y `party_analysis/amendements/run.py` → usan `data/deputes_an_rd.csv` (no el consolidado con Twitter).

---

## Metodología

Enfoque de **integración de fuentes heterogéneas** (open data parlamentario + CSV de terceros) mediante un pipeline ETL en Python. **No hay modelos de ML en esta carpeta**; el núcleo computacional es parseo de JSON anidado + **entity linking** determinístico por nombre.

| Etapa | Script / herramienta | Detalle técnico |
|-------|----------------------|-----------------|
| **1. Adquisición AN** | `fetch_an_15e_deputes.py` | Descarga el ZIP vía `requests` (opcional) o lo reutiliza desde `data/`. Entrada: `AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip`. |
| **2. Parseo acteurs** | `zipfile`, `json`, `re` | Itera JSON de acteurs y organes (`codeType == "GP"`). Normaliza campos con `#text` / `@xsi:nil` del export AN. |
| **3. Limpieza Twitter** | `build_deputes_twitter_csv.py` | Mapeo de columnas FR→EN; regex `https?://(?:www\.)?twitter\.com/…` sobre `sites_web` (pipe-separated). |
| **4. Integración** | `merge_deputes_2017_2022.py` | Join en memoria: diccionario indexado por `(family_name.strip(), first_name.strip())`. Salida con separador `;`. |

**Algoritmos de extracción (AN):**
- **`id`:** regex `PA(\d+)` sobre el `uid` del acteur (identificador estable para votos e intervenciones).
- **Mandato Asamblea:** primer mandato con `typeOrgane == "ASSEMBLEE"` → fechas, departamento, circunscripción.
- **Grupo político:** primer mandato `typeOrgane == "GP"` cuyo intervalo solapa **2017-06-18 – 2022-06-21** (comparación lexicográfica de fechas ISO en el script).
- **`former_deputy`:** flag binario `1` si existe `mandate_end`, `0` en caso contrario.
- **Filtro de filas:** se conservan acteurs con `(mandate_start ∨ district_num)` y nombre presente.

**Entity linking (Twitter ↔ AN):**
- Clave única: tupla nombre de familia + nombre de pila, sin normalización fonética ni fuzzy match.
- Empates o homónimos: el diccionario conserva **un solo registro** Twitter por clave (último en orden de lectura del CSV).
- Diputados AN sin par: columnas Twitter vacías; registros Twitter sin par en AN: no entran al consolidado (12 claves Twitter sin match según conteo cruzado).

**Criterios de evaluación / control de calidad:**
- **Tasa de enlace Twitter:** impresa al correr el merge (**587 / 668** ≈ **87,9 %** en datos actuales).
- **Cardinalidad de cohorte:** 668 filas AN vs. 599 filas Twitter fuente → cobertura asimétrica documentada.
- **Consistencia de esquema:** 21 columnas fijas en el CSV final (15 AN + 6 Twitter); `id` como clave primaria lógica del proyecto.
- **Reproducibilidad:** orden de ejecución fijo en `README.md`; ZIP excluido de Git (`.gitignore`: `data/*.zip`).

**Supuestos de ingeniería:**
- La lista AN del export 15e define la **unidad de análisis**; no se filtra aquí a “solo elegidos en 2017” (hay mandatos desde 2012 y sustituciones hasta 2021).
- Se confía en la calidad del cruce por nombre de Regards Citoyens; no hay paso de validación manual ni uso de `id_an` / URL institucional como clave alternativa.
- `deputes_twitter_rd.csv` es un **snapshot externo** descargado manualmente; no hay re-fetch automático del repositorio GitHub.

**Dependencias:** Python 3; biblioteca estándar (`csv`, `json`, `re`, `zipfile`, `pathlib`); `requests` solo si se descarga el ZIP automáticamente.

---

## Información útil para la tesis

| Sección de la memoria | Qué aporta esta carpeta |
|-----------------------|-------------------------|
| **Introducción / marco empírico** | Define la unidad de análisis (diputado XV legislatura) y el alcance temporal francés. |
| **Metodología — recolección de datos** | Fuentes primarias (AN open data + Regards Citoyens), criterios de integración, convención de identificadores. |
| **Metodología — construcción de la cohorte** | 668 diputados; filtro de cohorte reutilizado en votos e intervenciones. |
| **Implementación** | Pipeline reproducible en 3 scripts Python; orden de ejecución en `README.md`. |
| **Resultados / cobertura** | Métricas de match Twitter (587/668), grupos políticos, diputados sin cuenta. |
| **Limitaciones / discusión** | Cruce por nombre (homónimos, variantes ortográficas); cobertura parcial de Twitter; mandatos que no empiezan en 2017. |
| **Anexos** | Esquema de columnas de `deputes_2017_2022.csv`; URLs de fuentes; tabla de grupos parlamentarios (`political_group_abbrev`). |

---

## Resultados, decisiones o detalles relevantes

**Cifras verificadas en `processed/deputes_2017_2022.csv`:**

| Métrica | Valor |
|---------|-------|
| Total diputados | **668** |
| Con `twitter_handle` | **587** (87,9 %) |
| Sin Twitter | **81** |
| `former_deputy = 1` | **196** (mandato con fecha de fin) |
| Grupos políticos distintos (`political_group_abbrev`) | **18** (13 filas con sigla vacía) |
| Filas en Twitter raw/limpio | **599** |

**Distribución aproximada de grupos** (top): LAREM 317, LR 117, MODEM 37, NI/SOC/DEM 23 c/u, GDR 18, FI 17, NG 15.

**Fechas de mandato:** `mandate_start` entre 2012-06-20 y 2021-07-07; la cohorte incluye diputados cuyo mandato en Asamblea no comenzó en junio 2017 (sustituciones, continuidad desde legislatura anterior).

**Decisiones técnicas:**
- `id` = identificador numérico AN (sin prefijo `PA`).
- Separador `;` en tablas consolidadas (estándar francés para CSV).
- Grupo político: primer mandato `GP` válido en la ventana legislativa XV.
- Twitter: solo handles y metadatos del repositorio Regards Citoyens; URLs web filtradas a `twitter.com`.

**Supuestos / limitaciones implícitas:**
- El merge nombre+apellido no usa `id_an` ni URL institucional como clave alternativa.
- 12 registros Twitter no encuentran par en AN por nombre; 81 diputados AN no tienen Twitter en el dataset fuente.
- El ZIP de la AN no se versiona en Git (`.gitignore`: `data/*.zip`); debe descargarse o colocarse manualmente.

---

## Dudas o cosas a revisar

1. **`deputes_2017_2022_an.csv`**: origen y propósito no documentados. ¿Backup manual, export NosDéputés o comparación con `deputes_an_rd.csv`? Conviene aclarar antes de citarlo en la memoria.
2. **`nosdeputes.fr_deputes_2026-02-19.csv`**: snapshot posterior (feb. 2026) con 618 filas — ¿solo referencia cruzada o descartado a propósito frente a AN?
3. **13 diputados sin `political_group_abbrev`**: ¿falta de mandato GP en el JSON, baja temprana o error de parseo?
4. **Homónimos / nombres compuestos**: el merge por `(family_name, first_name)` puede fallar en casos ambiguos; no hay métrica de duplicados publicada.
5. **`party_analysis`** usa `deputes_an_rd.csv` y no el consolidado: verificar coherencia de `id` y grupos entre módulos.
6. **Reproducibilidad**: confirmar fecha de descarga del ZIP AN y del CSV twitter-parlementaires para la memoria.

---

## Resumen corto

`datos_diputados/` es el **primer eslabón** del pipeline empírico francés: tres scripts Python unen open data de la Assemblée nationale (15e) con Twitter parlamentario de Regards Citoyens y producen **`processed/deputes_2017_2022.csv`** (668 diputados, 587 con handle). Ese archivo ancla identidad (`id`), afiliación (`political_group_abbrev`) y red social en `twitter_zeeschuimer`, `lois_votes`, `hemicycle` y análisis por partido. Sin esta tabla no hay cohorte única ni cruces consistentes en el resto del proyecto.

---

## Citas

- **Assemblée nationale — open data (15e législature, acteurs/députés):** [Archives 15e — députés, sénateurs et ministres](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/deputes-senateurs-et-ministres); archivo usado: `AMO20_dep_sen_min_tous_mandats_et_organes_XV.json.zip` (URL en `scripts/fetch_an_15e_deputes.py`).
- **Regards Citoyens — twitter-parlementaires:** repositorio GitHub [regardscitoyens/twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) (fuente de `deputes_twitter_rd.csv`).
- **Regards Citoyens / NosDéputés.fr:** sitio [nosdeputes.fr](https://www.nosdeputes.fr/) — posible origen del snapshot `nosdeputes.fr_deputes_2026-02-19.csv` (no integrado al pipeline actual).
- **Documentación interna del proyecto:** `french_deputies/datos_diputados/README.md`, `french_deputies/ESTRUCTURA.md`, `french_deputies/README.md`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/datos_diputados/` — construcción de la **cohorte maestra** de 668 diputados de la XV legislatura (AN open data + Twitter de Regards Citoyens) → `processed/deputes_2017_2022.csv`. Primer eslabón del pipeline; no es experimental. Es **infraestructura de datos**, no análisis.

**A qué parte de la memoria alimenta (orden de relevancia):**

| Parte | Rol de este contexto |
|---|---|
| **Datos** (principal) | Define la unidad de análisis (diputado XV) y la cohorte; fuentes primarias e identificadores (`id`, `political_group_abbrev`). |
| **Implementación** | Pipeline ETL reproducible de 3 scripts; merge por nombre; convención `_rd`. |
| **Introducción** | Acota el alcance empírico (Francia, 2017–2022) y la unidad observada. |
| **Resultados** (cobertura) | Cifras de cobertura Twitter y distribución de grupos. |
| **Discusión / limitaciones** | Cruce por nombre, cobertura parcial, mandatos que no empiezan en 2017. |
| **Anexos** | Esquema de columnas y tabla de grupos parlamentarios. |

**Información concreta a extraer:**
- **668 diputados**; **587 con `twitter_handle` (87,9 %)**; 81 sin Twitter; **18** grupos; ventana de solape **2017-06-18 – 2022-06-21**.
- `id` = identificador numérico AN (sin prefijo `PA`) → **clave primaria lógica de todo el proyecto**; `political_group_abbrev` → ancla de los cruces por partido. Separador `;`.
- Que esta tabla es la dependencia upstream de tweets, leyes/enmiendas, hemiciclo y análisis por partido (sin ella no hay cohorte única).

**Figuras, tablas o métricas que contiene/menciona:**
- Tabla de cifras verificadas (668 / 587 / 81 / 196 `former_deputy` / 18 grupos / 599 filas Twitter raw).
- Distribución aproximada de grupos (LAREM 317, LR 117, MODEM 37, …). **No produce figuras propias.**

**Limitaciones / dudas a trasladar:**
- *Entity linking* por `(family_name, first_name)` **sin fuzzy** → riesgo en homónimos/variantes; **12** handles Twitter sin par; **13** diputados sin grupo.
- `party_analysis/` usa `deputes_an_rd.csv` (no el consolidado con Twitter): verificar coherencia de `id`/grupos.
- Reproducibilidad: el ZIP AN no se versiona; falta fecha de descarga.
- Archivos **fuera del pipeline** (`deputes_2017_2022_an.csv`, `nosdeputes.fr_deputes_2026-02-19.csv`): **secundarios**, no citar como fuente sin aclarar su origen.
