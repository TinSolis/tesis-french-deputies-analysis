# Leyes, enmiendas y votos — Assemblée nationale, XVe législature (2017–2022)

Este bloque conecta **qué se votó** con **cómo votó cada diputado** y **cuál es el texto de la ley o de la enmienda**. Todo sale de fuentes oficiales con licencia ouverte. El marco general de la investigación está en `Propuesta_Memoria.txt` (raíz del repo).

---

## Qué tengo hasta ahora (estado actual)

### Leyes (votos globales sobre el texto completo)

| Elemento | Cantidad | Notas |
|---|---|---|
| **Votaciones (scrutins) de adopción** | 373 | Una fila = un momento de votación. Una ley puede tener varios. |
| **Leyes únicas** (por dossier) | 212 | Agrupadas por `dossier_uid` — una ley jurídica real. |
| **Leyes con texto oficial** | **184 / 212 (87%)** | Texto completo promulgado bajado de Légifrance. |
| **Scrutins con texto incrustado** | 337 / 373 (90%) | La mayoría de filas del CSV tienen `texto_oficial` poblado. |
| **Votos individuales (diputados)** | completo | 100% de los scrutins tienen votos por diputado. |

### Enmiendas (votos granulares durante el debate)

| Elemento | Cantidad | Notas |
|---|---|---|
| **Votaciones (scrutins) sobre enmiendas** | 3.126 | Cambios puntuales propuestos durante el debate; ~9× más datos que los votos globales. |
| **Enmiendas con texto vinculado** | **2.904 / 3.126 (93%)** | Texto completo del cambio propuesto + justificación del autor. |
| **Votos individuales** | 297.574 | Todos en la cohorte de la tesis. |
| **Universo total parseado** | 311.934 | Enmiendas registradas en la XVe légis. (no todas llegaron a vote en hemiciclo). |

### Cobertura por fuente del texto

| Fuente | Cómo funciona | Confianza |
|---|---|---|
| `PISTE_NOR` | Encontrado por NOR oficial → Légifrance | Alta |
| `PISTE_TITLE_SEARCH` | Búsqueda por título normalizado → Légifrance | Alta (score ≥ 0.7) o Media (0.5–0.7) |

Para NLP de análisis principal: usar solo filas con `texto_confianza == "alta"`.

Los **28 dossiers restantes** sin texto son en su mayoría propuestas rechazadas en CMP, leyes constitucionales (tipo distinto a LOI/ORDONNANCE), o títulos demasiado genéricos para hacer match confiable.

### Cuándo usar votos globales vs enmiendas

- **Votos globales** = una posición clara de cada diputado sobre toda una ley. Útil para análisis de "stance" general (postura ideológica sobre el tema completo).
- **Votos sobre enmiendas** = posiciones específicas sobre cambios concretos dentro de una ley. Útil para detectar:
  - matices y rupturas dentro de un mismo grupo,
  - cambios de postura a lo largo de la tramitación,
  - alineación con topics más finos (Manifesto Project, valores morales).
  - El texto de cada enmienda suele ser un párrafo (~544 caracteres en promedio) muy temáticamente focalizado, ideal para clasificadores de tópicos.

---

## Fuentes de los datos

| Fuente | Qué contiene | URL |
|---|---|---|
| **Open data AN — Scrutins XV** | Votaciones nominales 2017–2022 | [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins) |
| **Open data AN — Dossiers XV** | Metadatos del expediente legislativo | [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs) |
| **Open data AN — Amendements XV** | Texto + metadatos de las 311k enmiendas presentadas | [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/amendements) |
| **API Légifrance vía PISTE** | Texto oficial promulgado (JORF) | [piste.gouv.fr](https://piste.gouv.fr) |

ZIP directos de la AN:
- Scrutins: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip`
- Dossiers: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip`
- Amendements: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/amendements_legis/Amendements_XV.xml.zip` *(704 MB, descarga con `download_amendements.py` ya que el server corta conexiones largas)*

---

## Qué hay en cada carpeta

```
lois_votes/
├── .env.example              ← plantilla de credenciales PISTE (copiar como .env)
├── README_LOIS_VOTES.md      ← este archivo
├── scripts/
│   ├── download_an_scrutins_and_dossiers.py   ← Paso 1: scrutins + dossiers
│   ├── download_amendements.py                ← Paso 1b: zip de enmiendas (con reanudación)
│   ├── build_laws_and_votes.py                ← Paso 2: votos globales sobre leyes
│   ├── build_amendements_votes.py             ← Paso 2b: votos sobre enmiendas
│   ├── build_leyes_texte_oficial.py           ← Paso 3: leyes + texto oficial
│   ├── fetch_legifrance_texts_piste.py        ← Paso 4a: leyes por NOR
│   ├── fetch_missing_by_title.py              ← Paso 4b: leyes por título sin NOR
│   ├── parse_amendements_xml.py               ← Paso 5: parsear los 311k XML
│   └── link_amendements_votes_textos.py       ← Paso 6: unir votos ↔ texto enmienda
└── votes_rd/
    ├── Scrutins_XV.json.zip                   ← descargado (gitignored)
    ├── Dossiers_Legislatifs_XV.json.zip       ← descargado (gitignored)
    ├── json/                                  ← scrutins descomprimidos (gitignored)
    │   └── VTANR5L15V*.json
    ├── Amendements/                           ← gitignored (704 MB ZIP, 2.8 GB descomprimido)
    │   ├── Amendements_XV.xml.zip
    │   └── xml/<DOSSIER>/<TEXTE_LEG>/AMANR5L15...*.xml
    ├── textes_lois/                           ← textos bajados de Légifrance
    │   ├── _index.csv                         ← qué NORs se bajaron y su estado
    │   ├── _index_titles.csv                  ← qué dossiers se bajaron por título
    │   ├── EJEMPLO_LEY.txt                    ← ejemplo legible de texto de LEY
    │   ├── EJEMPLO_AMENDEMENT.txt             ← ejemplo legible de texto de ENMIENDA
    │   ├── <NOR>.txt                          ← texto plano listo para NLP
    │   └── <NOR>.json                         ← respuesta cruda de PISTE (gitignored)
    └── processed/
        ├── leyes_votadas_2017_2022.csv        ← 373 scrutins de adopción
        ├── votos_por_diputado.csv             ← todos los votos (diputado × scrutin)
        ├── votos_por_diputado_cohorte.csv     ← votos filtrados a la cohorte de la tesis
        ├── leyes_texto_oficial.csv            ← 33 MB, leyes + texto oficial (90%)
        ├── amendements_votados.csv            ← 3.126 scrutins de enmienda
        ├── votos_amendements_por_diputado.csv ← 297k votos individuales
        ├── votos_amendements_por_diputado_cohorte.csv
        ├── amendements_textos.csv             ← 496 MB, 311k enmiendas con texto crudo (gitignored)
        └── amendements_votos_con_texto.csv    ← 7.7 MB, votos + texto enmienda linkeado (93%)
```

---

## Cómo leer el CSV de enmiendas (`amendements_votos_con_texto.csv`)

| Columna | Qué es |
|---|---|
| `scrutin_id` | ID de la votación |
| `fecha` | Fecha del voto |
| `sort_voto` | Resultado del voto (`adopté` / `rejeté`) |
| `amendement_num` | Número de la enmienda |
| `es_sous_amendement` | 1 si es sous-amendement |
| `es_identiques` | 1 si el voto cubre varias enmiendas idénticas |
| `demandeur` | Autor (extraído del título del scrutin) |
| `article_ref` | Artículo al que aplica |
| `ley_titulo_corto` | Ley sobre la que opera la enmienda |
| `dossier_uid_matched` | Dossier al que se vinculó |
| `match_score` / `match_confianza` | Calidad del matcheo título→dossier |
| `amendement_uid` | ID único en el catálogo AN |
| `auteur_type` / `auteur_ref` | "Député" o "Gouvernement" + ID PA |
| `signataires_libelle` | Lista legible de autores |
| `article_titre` | Artículo según el XML |
| `sort_amend` / `etat_amend` | Resultado real de la enmienda en la AN |
| `dispositif` | **Texto completo del cambio propuesto** |
| `expose_sommaire` | **Justificación del autor** |

Ver `votes_rd/textes_lois/EJEMPLO_AMENDEMENT.txt` para un ejemplo legible.

Los votos individuales por diputado están en `votos_amendements_por_diputado_cohorte.csv` (297k filas) — se cruza con esta tabla por `scrutin_id`.

---

## Cómo leer el CSV de leyes (`leyes_texto_oficial.csv`)

| Columna | Qué es |
|---|---|
| `scrutin_id` | ID de la votación en la AN |
| `titulo_scrutin` | Título tal como aparece en el scrutin |
| `fecha` | Fecha de la votación |
| `dossier_uid` | Expediente legislativo (DLR…) — agrupa scrutins de una misma ley |
| `dossier_titre` | Título del dossier (puede diferir del scrutin) |
| `match_score` | Calidad del match dossier↔scrutin (0–1) |
| `nor_jo` | NOR oficial en el Journal officiel (ej. `INTX1716366L`) |
| `url_legifrance` | URL directa a Légifrance |
| `texto_oficial` | Texto completo de la ley en francés (vacío si no se pudo obtener) |
| `texto_fuente` | `PISTE_NOR` o `PISTE_TITLE_SEARCH` |
| `texto_confianza` | `alta`, `media` o `baja` |

**Nota clave:** un mismo `dossier_uid` puede aparecer en varias filas (varias lecturas de la misma ley). Para análisis por ley jurídica, agrupar por `dossier_uid` y quedarse con la primera fila que tenga `texto_oficial`.

---

## Cómo reproducir todo desde cero

Desde la carpeta **`french_deputies/`**:

```bash
# === LEYES (texto promulgado) ===

# Paso 1 — Bajar los datos abiertos de la AN (~25 MB)
python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py

# Paso 2 — Construir las tablas de votaciones globales y votos por diputado
python3 lois_votes/scripts/build_laws_and_votes.py

# Paso 3 — Enlazar con dossiers, extraer NOR y URL Légifrance
python3 lois_votes/scripts/build_leyes_texte_oficial.py

# Paso 4a — Bajar texto oficial de las leyes con NOR (requiere .env PISTE)
python3 lois_votes/scripts/fetch_legifrance_texts_piste.py

# Paso 4b — Recuperar leyes sin NOR buscando por título
python3 lois_votes/scripts/fetch_missing_by_title.py

# Paso 5 — Regenerar CSV final con textos incrustados
python3 lois_votes/scripts/build_leyes_texte_oficial.py

# === ENMIENDAS (texto del cambio propuesto) ===

# Paso A — Construir tabla de los 3.126 votos sobre enmiendas
python3 lois_votes/scripts/build_amendements_votes.py

# Paso B — Bajar el ZIP de enmiendas (704 MB; reanuda solo si se corta)
python3 lois_votes/scripts/download_amendements.py
#   Después: descomprimir en votes_rd/Amendements/ (Mac: doble-click sobre el zip)

# Paso C — Parsear los 311k archivos XML (~3 min, genera CSV de 496 MB)
python3 lois_votes/scripts/parse_amendements_xml.py

# Paso D — Linkear votos ↔ texto de enmienda (cobertura final 93%)
python3 lois_votes/scripts/link_amendements_votes_textos.py
```

El Paso 3 puede tardar ~1 minuto la primera vez (indexa 4980 dossiers y guarda caché).
Los Pasos 4a y 4b requieren credenciales PISTE; ver sección siguiente.
El Paso B suele cortar conexión varias veces (el server de la AN no aguanta descargas largas) pero el script reanuda con `Range` headers y termina en ~15 minutos.

---

## Configurar las credenciales PISTE (una sola vez)

1. Crear cuenta gratis en [https://piste.gouv.fr/registration](https://piste.gouv.fr/registration)
2. En **"API → Consentement CGU API"** aceptar las CGU de **"Légifrance"** (no "Beta")
3. En **"Applications"** crear una app y vincularla a la API **"Légifrance" entorno PROD**
4. Copiar `client_id` y `client_secret` de la pestaña **Authentication → OAuth credentials**

```bash
cp lois_votes/.env.example lois_votes/.env
# editar .env con los valores reales
```

El archivo `.env` está en `.gitignore` — no se sube nunca al repo.

**Punto que confunde más:** en la pantalla Authentication hay dos secciones (API Keys y OAuth credentials). El `client_secret` que necesita el script está en **OAuth credentials**, no en API Keys.

---

## Qué hace cada script

| Script | Qué hace en una frase |
|---|---|
| `download_an_scrutins_and_dossiers.py` | Baja los ZIP de scrutins + dossiers de la AN y los descomprime |
| `download_amendements.py` | Baja `Amendements_XV.xml.zip` (704 MB) con reanudación robusta |
| `build_laws_and_votes.py` | Filtra scrutins de adopción y genera los CSV de votos globales |
| `build_amendements_votes.py` | Filtra scrutins de enmiendas y genera los CSV de votos granulares |
| `build_leyes_texte_oficial.py` | Cruza scrutins con dossiers; extrae NOR; incrusta textos locales |
| `fetch_legifrance_texts_piste.py` | Busca por NOR en PISTE → descarga texto oficial de Légifrance |
| `fetch_missing_by_title.py` | Para leyes sin NOR: busca por título normalizado en PISTE |
| `parse_amendements_xml.py` | Parsea los 311k XML de enmiendas → tabla con texto + metadatos |
| `link_amendements_votes_textos.py` | Une scrutin de enmienda ↔ texto de la enmienda (fuzzy match por título + dossier + número) |

---

## Metodología (para la memoria)

### Sobre los votos

- Unidad de observación principal en "leyes": **scrutin de adopción** del texto completo (vote sur l'ensemble). Una ley jurídica puede tener varios scrutins (lecturas, CMP, etc.).
- Unidad de observación principal en "enmiendas": **scrutin sobre un amendement** específico. Es ~9 veces más datos (3.126 vs 373 scrutins) y permite detectar:
  - Variación intra-partido en posturas concretas.
  - Cambios de postura durante la tramitación de una misma ley.
  - Mejor alineación con clasificadores temáticos (Manifesto, MFT/valores morales) porque cada enmienda toca un punto delimitado.

### Sobre las fuentes de los textos

- **Textos promulgados de las leyes**: vienen de **Légifrance vía API PISTE** (fuente institucional). Los obtenidos por NOR directo tienen `texto_confianza = alta`; los recuperados por búsqueda de título llevan `media` o `baja` y deberían revisarse si se usan para análisis principales.
- **Textos de las enmiendas**: vienen del **open data de la AN** (XML por enmienda). El matching scrutin→enmienda se hace por (título de la ley → dossier_uid) + (numero de enmienda en el título). Cada fila lleva `match_confianza` (alta/media/baja) para filtrar.
- Las 28 leyes sin texto: propuestas rechazadas/retiradas, leyes constitucionales (no indexadas como LOI/ORDONNANCE en JORF), o títulos demasiado genéricos.
- Los 222 votos sobre enmiendas sin texto vinculado (7%): mayoritariamente sous-amendements con numeración propia y enmiendas de leyes de finanzas en partes/lecturas que el matching no cubre perfectamente.

### Relación con los diputados

La columna `id` de `deputes_2017_2022.csv` es el mismo identificador que `deputy_id` en los CSV de votos (sin el prefijo `PA` de la AN).
