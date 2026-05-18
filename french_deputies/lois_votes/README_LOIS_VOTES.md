# Leyes y votos — Assemblée nationale, XVe législature (2017–2022)

Este bloque conecta **qué se votó** con **cómo votó cada diputado** y **cuál es el texto de la ley**. Todo sale de fuentes oficiales con licencia ouverte. El marco general de la investigación está en `Propuesta_Memoria.txt` (raíz del repo).

---

## Qué tengo hasta ahora (estado actual)

| Elemento | Cantidad | Notas |
|---|---|---|
| **Votaciones (scrutins)** | 373 | Una fila = un momento de votación. Una ley puede tener varios. |
| **Leyes únicas** (por dossier) | 212 | Agrupadas por `dossier_uid` — una ley jurídica real. |
| **Leyes con texto oficial** | **184 / 212 (87%)** | Texto completo promulgado bajado de Légifrance. |
| **Scrutins con texto incrustado** | 337 / 373 (90%) | La mayoría de filas del CSV tienen `texto_oficial` poblado. |
| **Votos individuales (diputados)** | completo | 100% de los scrutins tienen votos por diputado. |

### Cobertura por fuente del texto

| Fuente | Cómo funciona | Confianza |
|---|---|---|
| `PISTE_NOR` | Encontrado por NOR oficial → Légifrance | Alta |
| `PISTE_TITLE_SEARCH` | Búsqueda por título normalizado → Légifrance | Alta (score ≥ 0.7) o Media (0.5–0.7) |

Para NLP de análisis principal: usar solo filas con `texto_confianza == "alta"`.

Los **28 dossiers restantes** sin texto son en su mayoría propuestas rechazadas en CMP, leyes constitucionales (tipo distinto a LOI/ORDONNANCE), o títulos demasiado genéricos para hacer match confiable.

---

## Fuentes de los datos

| Fuente | Qué contiene | URL |
|---|---|---|
| **Open data AN — Scrutins XV** | Votaciones nominales 2017–2022 | [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins) |
| **Open data AN — Dossiers XV** | Metadatos del expediente legislativo | [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs) |
| **API Légifrance vía PISTE** | Texto oficial promulgado (JORF) | [piste.gouv.fr](https://piste.gouv.fr) |

ZIP directos de la AN:
- Scrutins: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip`
- Dossiers: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip`

---

## Qué hay en cada carpeta

```
lois_votes/
├── .env.example              ← plantilla de credenciales PISTE (copiar como .env)
├── README_LOIS_VOTES.md      ← este archivo
├── scripts/
│   ├── download_an_scrutins_and_dossiers.py   ← Paso 1
│   ├── build_laws_and_votes.py                ← Paso 2
│   ├── build_leyes_texte_oficial.py           ← Paso 3
│   ├── fetch_legifrance_texts_piste.py        ← Paso 4a (por NOR)
│   └── fetch_missing_by_title.py             ← Paso 4b (por título, sin NOR)
└── votes_rd/
    ├── Scrutins_XV.json.zip                   ← descargado (gitignored)
    ├── Dossiers_Legislatifs_XV.json.zip       ← descargado (gitignored)
    ├── json/                                  ← descomprimidos (gitignored)
    │   ├── scrutin/VTANR5L15V*.json
    │   └── dossierParlementaire/DLR*.json
    ├── textes_lois/                           ← textos bajados de Légifrance
    │   ├── _index.csv                         ← qué NORs se bajaron y su estado
    │   ├── _index_titles.csv                  ← qué dossiers se bajaron por título
    │   ├── EJEMPLO_LEY.txt                    ← ejemplo legible para entender el formato
    │   ├── <NOR>.txt                          ← texto plano listo para NLP
    │   └── <NOR>.json                         ← respuesta cruda de PISTE (gitignored)
    └── processed/
        ├── leyes_votadas_2017_2022.csv        ← 373 scrutins de adopción
        ├── votos_por_diputado.csv             ← todos los votos (diputado × scrutin)
        ├── votos_por_diputado_cohorte.csv     ← votos filtrados a la cohorte de la tesis
        └── leyes_texto_oficial.csv            ← 33 MB, columna texto_oficial poblada al 90%
```

---

## Cómo leer el CSV principal (`leyes_texto_oficial.csv`)

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
# Paso 1 — Bajar los datos abiertos de la AN (~25 MB)
python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py

# Paso 2 — Construir las tablas de votaciones y votos por diputado
python3 lois_votes/scripts/build_laws_and_votes.py

# Paso 3 — Enlazar con dossiers, extraer NOR y URL Légifrance
python3 lois_votes/scripts/build_leyes_texte_oficial.py

# Paso 4a — Bajar texto oficial de las leyes que tienen NOR (requiere .env con credenciales PISTE)
python3 lois_votes/scripts/fetch_legifrance_texts_piste.py

# Paso 4b — Recuperar leyes sin NOR buscando por título en Légifrance
python3 lois_votes/scripts/fetch_missing_by_title.py

# Paso 5 — Regenerar CSV final con todos los textos incrustados
python3 lois_votes/scripts/build_leyes_texte_oficial.py
```

El Paso 3 puede tardar ~1 minuto la primera vez (indexa 4980 dossiers y guarda caché).
Los Pasos 4a y 4b requieren credenciales PISTE; ver sección siguiente.

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
| `download_an_scrutins_and_dossiers.py` | Baja los ZIP de la AN y los descomprime |
| `build_laws_and_votes.py` | Filtra scrutins por tipo legislativo y fecha; genera los 3 CSV de votos |
| `build_leyes_texte_oficial.py` | Cruza scrutins con dossiers; extrae NOR; incrusta textos locales en CSV |
| `fetch_legifrance_texts_piste.py` | Busca por NOR en PISTE → descarga texto oficial de Légifrance |
| `fetch_missing_by_title.py` | Para leyes sin NOR: busca por título normalizado en PISTE → descarga texto |

---

## Metodología (para la memoria)

- Unidad de observación: **scrutin de adopción**, no "la ley" en sentido coloquial. Una ley puede tener múltiples scrutins.
- Para análisis por ley jurídica: agrupar por `dossier_uid` y elegir el scrutin final (mayor fecha, o el que tenga `texto_oficial`).
- Los textos oficiales provienen de **Légifrance vía API PISTE** (fuente institucional oficial). Los obtenidos por búsqueda de título llevan la columna `texto_confianza` para distinguirlos de los obtenidos por NOR directo.
- Las 28 leyes sin texto son mayoritariamente: propuestas rechazadas o retiradas, leyes constitucionales (tipo no indexado como LOI/ORDONNANCE en JORF), o con títulos demasiado genéricos.
- Relación con los diputados: la columna `id` de `deputes_2017_2022.csv` es el mismo identificador que `deputy_id` en `votos_por_diputado.csv` (sin el prefijo `PA` de la AN).
