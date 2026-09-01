# Contexto de la carpeta: `french_deputies/lois_votes/`

## Propósito

Esta carpeta construye el corpus de **actividad legislativa y votaciones nominales** de la XV legislatura francesa (2017–2022). Integra open data de la **Assemblée nationale** (scrutins, dossiers, enmiendas) con el **texto oficial promulgado** desde **Légifrance vía API PISTE**. Produce tablas que enlazan **qué se votó**, **cómo votó cada diputado** y **el texto de la ley o enmienda**. Es la fuente de **agenda revelada** (voto) del proyecto y alimenta BERTopic, ManifestoBERTa y `party_analysis/` en los módulos `lois/` y `amendements/`.

---

## Archivos importantes

### Documentación y configuración

| Archivo | Rol |
|---------|-----|
| `README_LOIS_VOTES.md` | Documentación principal: fuentes, flujo de reproducción, columnas, metodología. |
| `votes_rd/README.md` | Estructura de raw data y estado del dataset. |
| `.env.example` | Plantilla `PISTE_CLIENT_ID` / `PISTE_CLIENT_SECRET` para Légifrance (`.env` en `.gitignore`). |

### Scripts (`scripts/`) — pipeline en dos ramas

| Script | Función |
|--------|---------|
| `download_an_scrutins_and_dossiers.py` | Descarga y descomprime ZIP de **Scrutins** y **Dossiers** XV. |
| `build_laws_and_votes.py` | Filtra scrutins de **adopción de ley**; genera `leyes_votadas_2017_2022.csv` y votos por diputado (± cohorte). |
| `build_leyes_texte_oficial.py` | Cruza scrutin ↔ dossier (fuzzy match); extrae NOR/URL; incrusta textos locales en `leyes_texto_oficial.csv`. |
| `fetch_legifrance_texts_piste.py` | OAuth PISTE → descarga texto JORF por NOR → `textes_lois/<NOR>.txt`. |
| `fetch_missing_by_title.py` | Recupera leyes sin NOR por búsqueda de título en PISTE. |
| `download_amendements.py` | Descarga `Amendements_XV.xml.zip` (~704 MB) con reanudación. |
| `build_amendements_votes.py` | Extrae scrutins de **enmienda**; genera `amendements_votados.csv` y votos individuales. |
| `parse_amendements_xml.py` | Parsea ~311k XML → `amendements_textos.csv` (gitignored, ~496 MB). |
| `link_amendements_votes_textos.py` | Une scrutin de enmienda ↔ texto (`dispositif`, `expose_sommaire`) con fuzzy match. |

### Salidas clave (`votes_rd/processed/`)

| Archivo | Contenido |
|---------|-----------|
| **`leyes_votadas_2017_2022.csv`** | **373** scrutins de adopción del texto completo. |
| **`leyes_texto_oficial.csv`** | Mismos scrutins + dossier, NOR, `texto_oficial`, `texto_fuente`, `texto_confianza`. |
| **`votos_por_diputado.csv`** / **`votos_por_diputado_cohorte.csv`** | **78 116** votos individuales (globales); cohorte filtrada por `deputes_2017_2022.csv`. |
| **`amendements_votados.csv`** | **3 126** scrutins sobre enmiendas. |
| **`amendements_votos_con_texto.csv`** | Scrutin + metadatos + texto de enmienda + `match_confianza`. |
| **`votos_amendements_por_diputado.csv`** / **`_cohorte.csv`** | **297 574** votos individuales sobre enmiendas. |

### Textos locales (`votes_rd/textes_lois/`)

| Elemento | Rol |
|----------|-----|
| `<NOR>.txt` | Texto plano JORF (**184** archivos verificados). |
| `_index.csv`, `_index_titles.csv` | Índice de descargas PISTE. |
| `EJEMPLO_LEY.txt`, `EJEMPLO_AMENDEMENT.txt` | Ejemplos legibles del formato. |

---

## Flujo / lógica principal

```
                    datos_diputados/processed/deputes_2017_2022.csv
                                    │
┌───────────────────────────────────┴───────────────────────────────────┐
│ RAMA LEYES (texto promulgado)                                         │
│                                                                       │
│ AN: Scrutins + Dossiers ZIP → download_an_scrutins_and_dossiers.py   │
│         → build_laws_and_votes.py → leyes_votadas + votos_por_diputado│
│         → build_leyes_texte_oficial.py (match dossier, NOR)           │
│         → fetch_legifrance_texts_piste.py (+ fetch_missing_by_title)  │
│         → build_leyes_texte_oficial.py (re-embed textos)              │
│         → leyes_texto_oficial.csv                                     │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│ RAMA ENMIENDAS (texto del cambio propuesto)                           │
│                                                                       │
│ build_amendements_votes.py → amendements_votados + votos enmienda     │
│ AN: Amendements ZIP → download_amendements.py → XML                   │
│         → parse_amendements_xml.py → amendements_textos.csv           │
│         → link_amendements_votes_textos.py → amendements_votos_con_texto.csv
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        bertopic_analysis / manifestoberta_analysis / party_analysis
                    (lois/ y amendements/)
```

**Entradas externas:**
- Open data AN XV: [Scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins), [Dossiers](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs), [Amendements](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/amendements).
- API **PISTE / Légifrance**: [piste.gouv.fr](https://piste.gouv.fr).

**Clave de cruce con diputados:** `deputy_id` en votos = campo `id` de `deputes_2017_2022.csv` (sin prefijo `PA`).

---

## Metodología

Enfoque de **ETL multi-fuente** con entity linking parlamentario y recuperación de texto institucional. **No hay modelos de ML en esta carpeta**; los algoritmos son parseo JSON/XML, regex, fuzzy matching y APIs REST.

| Etapa | Técnica | Detalle |
|-------|---------|---------|
| **1. Adquisición AN** | HTTP + `zipfile` | ZIP de scrutins (~4 417 JSON), dossiers (~4 980), amendements (311k XML). |
| **2. Filtrado temporal** | Fechas legislatura | `2017-06-27` – `2022-06-21` en `build_laws_and_votes.py` / `build_amendements_votes.py`. |
| **3. Clasificación de scrutins** | Regex sobre título | Leyes: `is_law_adoption_scrutin()` («l'ensemble», «adoption du projet…»). Enmiendas: `PAT_AMEND`, sous-amendement, identiques. |
| **4. Votos nominales** | Parseo JSON AN | Extracción `PA(\d+)` → `deputy_id`; posiciones Pour/Contre/Abstention. |
| **5. Match scrutin↔dossier (leyes)** | `rapidfuzz` o `difflib` | Normalización NFKD, kernel de título, consistencia projet/proposition/organique; caché `.dossier_index_cache.pkl`. |
| **6. Texto promulgado** | API PISTE OAuth2 | `fetch_legifrance_texts_piste.py` por NOR; `fetch_missing_by_title.py` con score ≥ 0,5–0,7. |
| **7. Parseo enmiendas** | `xml.etree.ElementTree` | Strip HTML, campos `dispositif` / `exposeSommaire`. |
| **8. Link enmienda↔voto** | Token overlap + dossier fuzzy | Título scrutin → `dossier_uid`; dentro del dossier, match por `amendement_num` y proximidad de fecha. |

**Unidades de observación:**
- **Leyes:** scrutin de adopción del texto completo (*vote sur l'ensemble*). Una ley jurídica (`dossier_uid`) puede tener varios scrutins.
- **Enmiendas:** scrutin sobre un amendement concreto (~9× más datos que votos globales).

**Criterios de evaluación / calidad:**
- **`texto_confianza`** (leyes): `alta` (NOR directo), `media`/`baja` (búsqueda por título). NLP principal: solo `alta` (**335 / 373** filas).
- **`match_confianza`** (enmiendas): `alta` / `media` / `baja` / `ninguna`. BERTopic/ManifestoBERTa usan alta+media con texto ≥ 10 palabras → **2 575** docs enmiendas.
- **Cobertura textual leyes:** **337 / 373** scrutins con `texto_oficial` en CSV; **184 / 212** dossiers únicos con `.txt` local.
- **Cobertura textual enmiendas:** **2 689** con `dispositif`; **2 886** con `dispositif` o `expose_sommaire` (README documenta **2 904 / 3 126**, ~93 %).

**Supuestos de ingeniería:**
- El texto promulgado (JORF) representa la ley final, no el debate intermedio.
- El match scrutin↔enmienda es heurístico; filas `baja`/`ninguna` deben excluirse en análisis principal.
- Raw masivo (ZIP, JSON, `amendements_textos.csv`) no se versiona en Git; se regenera con los scripts.
- PISTE requiere credenciales personales y aceptación de CGU Légifrance.

**Dependencias:** Python 3, `requests`; opcional `rapidfuzz` para matching de dossiers.

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Introducción** | Fuentes oficiales francesas (AN + Légifrance); votación nominal como señal de preferencia revelada. |
| **Metodología — recolección** | Open data + API PISTE; dos granularidades (ley completa vs. enmienda). |
| **Metodología — agenda revelada** | Contraste con manifiestos/tweets (declarada) en `party_analysis/`. |
| **Implementación** | Pipeline de 9 scripts, orden en `README_LOIS_VOTES.md`, configuración `.env`. |
| **Experimentos / resultados** | Volúmenes de scrutins y votos; cobertura de texto; distribución temática vía NLP downstream. |
| **Discusión / limitaciones** | 28 dossiers sin texto; 7 % enmiendas sin link; confianza media/baja; leyes constitucionales/CMP. |
| **Anexos** | Esquema de columnas; ejemplos `EJEMPLO_*.txt`; URLs de ZIP AN. |

---

## Resultados, decisiones o detalles relevantes

**Cifras verificadas en `votes_rd/processed/`:**

| Métrica | Valor |
|---------|-------|
| Scrutins adopción ley | **373** |
| Dossiers únicos | **212** |
| Leyes con `texto_oficial` en CSV | **337 / 373** (90,3 %) |
| `texto_confianza == alta` | **335** |
| Archivos `.txt` en `textes_lois/` | **184** (~87 % de dossiers) |
| Votos individuales (leyes) | **78 116** (cohorte = mismo total) |
| Scrutins enmienda | **3 126** |
| Votos individuales (enmiendas) | **297 574** |
| Enmiendas con `dispositif` | **2 689 / 3 126** |
| `match_confianza`: alta / media / baja / ninguna | **2 155 / 565 / 304 / 102** |

**Downstream (BERTopic / ManifestoBERTa, tras filtros):**
- **Lois:** 23 267 párrafos (`texto_confianza == alta`, ≥ 10 palabras).
- **Amendements:** 2 575 enmiendas (`match_confianza` alta/media, `dispositif + expose_sommaire` ≥ 10 palabras).

**Decisiones técnicas:**
- Dos pipelines paralelos (ley promulgada vs. enmienda en debate).
- Texto de leyes: fuente institucional PISTE; enmiendas: XML AN (sin PISTE).
- Cohorte de diputados aplicada en `*_cohorte.csv` vía `deputes_2017_2022.csv`.
- Para análisis por ley jurídica: agrupar por `dossier_uid` (varias filas por lecturas/CMP).

**Limitaciones (documentadas en README):**
- 28 dossiers sin texto: propuestas rechazadas, leyes constitucionales, títulos genéricos.
- ~7 % scrutins de enmienda sin texto: sous-amendements, PLF en partes.
- Votos globales = postura sobre ley entera; enmiendas = matices intra-partido y temas focalizados (~544 caracteres promedio según README).

---

## Dudas o cosas a revisar

1. **Discrepancia enmiendas con texto — RESUELTO (criterios distintos + desfase menor):** **2 575** = entran al análisis NLP (`match_confianza` alta/media + ≥10 palabras, verificado); **2 886** = con `dispositif` o `expose_sommaire` (reproducible hoy); **2 689** = solo `dispositif`. El **2 904 (93 %) del README** está levemente desactualizado: desfase real de **18 filas** vs. 2 886 (probable regeneración del dataset). `match_confianza` verificado: alta 2 155 / media 565 / baja 304 / ninguna 102 (suma 3 126). **Usar 2 575 (análisis) y 2 886 (con texto).**
2. **Votos leyes:** `votos_por_diputado` y `_cohorte` tienen el mismo número de filas (**78 116**) — confirmar si implica que todos los votantes están en la cohorte o si el filtro no reduce.
3. **`amendements_textos.csv`:** gitignored (~496 MB); no está en el clone sin regenerar.
4. **Ruta README en `ESTRUCTURA.md`:** apunta a `lois_votes/votes_rd/README.md`; la guía completa está en `README_LOIS_VOTES.md`.
5. **Reproducibilidad PISTE:** fechas de descarga y versión de API no quedan en metadatos centralizados.
6. **`bertopic_analysis/lois/run.py`** menciona `articles_lois_xv.csv.gz` en un comentario del README de BERTopic — verificar si es alias o archivo distinto de `leyes_texto_oficial.csv`.

---

## Resumen corto

`lois_votes/` integra **votaciones nominales** y **textos legislativos** de la AN 2017–2022: **373** adopciones de ley (con **~90 %** de texto promulgado vía PISTE) y **3 126** votos sobre enmiendas (con texto del cambio en **~93 %** según documentación). Cruza cada voto con la cohorte de diputados y alimenta el análisis de **agenda revelada** por partido. Es el corpus más complejo del proyecto en ingeniería de datos (JSON, XML, API OAuth, fuzzy matching).

---

## Citas

- **Assemblée nationale — open data XV:** [Scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins), [Dossiers législatifs](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs), [Amendements](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/amendements).
- **PISTE / Légifrance:** [piste.gouv.fr](https://piste.gouv.fr); registro [piste.gouv.fr/registration](https://piste.gouv.fr/registration).
- **Cohorte diputados:** `french_deputies/datos_diputados/processed/deputes_2017_2022.csv`.
- **Análisis downstream:** `french_deputies/bertopic_analysis/README.md`, `french_deputies/manifestoberta_analysis/README.md`, `french_deputies/party_analysis/README.md`.
- **Documentación interna:** `french_deputies/lois_votes/README_LOIS_VOTES.md`, `french_deputies/lois_votes/votes_rd/README.md`, `french_deputies/ESTRUCTURA.md`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/lois_votes/` — corpus de **actividad legislativa y votaciones nominales** (leyes vía Légifrance/PISTE + enmiendas vía XML AN). Es la fuente de **agenda revelada** (el voto) y el **módulo de ingeniería de datos más complejo** del proyecto (JSON/XML/OAuth/fuzzy matching). No experimental.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Datos** (principal) | Fuentes oficiales (AN open data + Légifrance); dos granularidades: ley completa vs. enmienda. |
| **Implementación** (peso fuerte) | 9 scripts en dos ramas, OAuth PISTE, fuzzy matching scrutin↔dossier↔enmienda. |
| **Metodología** | El voto nominal como **preferencia revelada**; criterios de confianza de texto/match. |
| **Resultados** | Volúmenes de scrutins y votos; cobertura de texto. |
| **Discusión / limitaciones** | Matching heurístico, dossiers sin texto, confianza media/baja. |
| **Anexos** | Esquema de columnas; ejemplos `EJEMPLO_*.txt`; URLs de los ZIP AN. |

**Información concreta a extraer:**
- **Leyes:** 373 scrutins de adopción (212 dossiers); **78.116** votos individuales. **Enmiendas:** **3.126** scrutins; **297.574** votos.
- Insumos NLP tras filtros: **23.267** párrafos de leyes (`texto_confianza == alta`, ≥10 palabras) y **2.575** enmiendas (`match_confianza` alta/media, ≥10 palabras).
- **Cifras a usar en la memoria:** **2.575** (entran al análisis) y **2.886** (con texto) — **no** el 2.904 levemente desactualizado del README. Clave de cruce: `deputy_id` = `id` (sin `PA`).

**Figuras, tablas o métricas que contiene/menciona:**
- Tabla de cifras verificadas y distribución `match_confianza` (alta 2.155 / media 565 / baja 304 / ninguna 102) y `texto_confianza`. **Sin figuras propias.**

**Limitaciones / dudas a trasladar:**
- **Matching heurístico** scrutin↔dossier↔enmienda (filas baja/ninguna excluidas); `demandeur` de enmiendas **no controlado**.
- 28 dossiers sin texto; ~7 % de scrutins de enmienda sin texto (sous-amendements, PLF en partes).
- Raw masivo (ZIP, XML, `amendements_textos.csv` ~496 MB) **no versionado**; reproducibilidad PISTE (fechas/versión de API no centralizadas).
- Confirmar por qué `votos_por_diputado` y `_cohorte` tienen el mismo total (78.116).
