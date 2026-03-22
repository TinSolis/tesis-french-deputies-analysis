# Leyes 2017-2022 y votos por diputado (XVe législature)

En esta carpeta se obtienen **todas las votaciones de adopción de ley** (projet / proposition de loi, etc.) de la **législature 2017-2022** y **todos los votos individuales** de los diputados en esos scrutins, a partir de los datos abiertos de l’Assemblée nationale (*Propuesta_Memoria.pdf* en la raíz del repo).

---

## 1. Fuentes (open data Assemblée nationale)

Todo está en **data.assemblee-nationale.fr**, licence Ouverte.

| Recurso | Contenido | Enlace |
|--------|-----------|--------|
| **Scrutins XV** | Cada votación con título, fecha y posición de chaque député (Pour / Contre / Abstention / Non-votant). L’identifiant `PAxxxxxx` → `id` dans `deputes_2017_2022.csv`. | [Archives 15e – Scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins) |
| **Dossiers législatifs XV** | Dossiers de textes (optionnel pour enrichir plus tard). | [Archives 15e – Dossiers](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs) |

URLs directes des ZIP :

- Scrutins : `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip`
- Dossiers : `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip`

---

## 2. Los dos CSV “núcleo” para tu análisis

| CSV | Contenido |
|-----|-----------|
| **`votes_rd/processed/votos_por_diputado.csv`** | `deputy_id`, `scrutin_id`, `vote` — ya lo genera `build_laws_and_votes.py`. |
| **`votes_rd/processed/leyes_texto_oficial.csv`** | Una fila por `scrutin_id`: enlace al **dossier** AN, **NOR** / **URL Légifrance** del texto publicado en el JO (promulgación), y **`texto_oficial`** si pegas el texto en `votes_rd/textes_lois/` (ver abajo). |

Generación del segundo:

```bash
python3 lois_votes/scripts/build_leyes_texte_oficial.py
```

- Cruza `leyes_votadas_2017_2022.csv` con `votes_rd/json/dossierParlementaire/*.json` (emparejamiento por título; revisa filas con `match_score` bajo).
- Extrae **NOR** y **URL** del acto **PROM-PUB** (promulgación). Eso apunta al **texto oficial** en Légifrance.
- **No** descarga el HTML automáticamente (Légifrance suele bloquear scripts). Opciones: copiar/pegar en `.txt` en `textes_lois/`, o API **PISTE** / Légifrance.

La primera ejecución indexa todos los dossiers (lenta); se guarda caché en `votes_rd/.dossier_index_cache.pkl`.

---

## 3. Qué generan los scripts (datos brutos + votos)

1. **`scripts/download_an_scrutins_and_dossiers.py`**  
   Descarga los dos ZIP en **`lois_votes/votes_rd/`** y **los descomprime**. El ZIP de Scrutins ya no trae un solo `Scrutins_XV.json`, sino muchos archivos **`json/VTANR5L15V*.json`** (uno por votación); el build los recorre todos.  
   Si `pip install requests` falla (p. ej. índice PyPI interno), descarga con `curl` los enlaces del §1 y descomprime con `unzip`.

2. **`scripts/build_laws_and_votes.py`**  
   Lee `Scrutins_XV.json`, filtra scrutins cuyo título sea **adopción de texto legislativo** (projet de loi, proposition de loi, loi organique, ratificación vinculada a ley, etc.) y cuya **fecha** (si se puede parsear) esté entre **2017-06-27** y **2022-06-21**.  
   Escribe en **`lois_votes/votes_rd/processed/`**:

   | Archivo | Contenido |
   |---------|-----------|
   | **leyes_votadas_2017_2022.csv** | Una fila por scrutin: `scrutin_id`, `titulo`, `fecha`, `fecha_iso`, `dossier_ref` |
   | **votos_por_diputado.csv** | **Todos** los votos de diputados en esos scrutins: `deputy_id`, `scrutin_id`, `vote` (Pour / Contre / Abstention / NonVotant) |
   | **votos_por_diputado_cohorte.csv** | Igual, filtrado a los `id` de `datos_diputados/processed/deputes_2017_2022.csv` |

Opción CLI: `--sin-filtro-fechas` para incluir también scrutins fuera del rango de fechas (p. ej. depuración).

3. **`scripts/build_leyes_texte_oficial.py`**  
   Genera `leyes_texto_oficial.csv` y opcionalmente rellena `texto_oficial` desde `votes_rd/textes_lois/*.txt`.

---

## 4. Comandos (desde `francia_deputies`)

```bash
cd francia_deputies

# 1) Descargar + descomprimir (requiere: pip install requests)
python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py

# 2) Generar CSV de votos y leyes (scrutins)
python3 lois_votes/scripts/build_laws_and_votes.py

# 3) Enlazar leyes con dossiers + NOR Légifrance (+ textos si hay .txt en textes_lois/)
python3 lois_votes/scripts/build_leyes_texte_oficial.py
```

Si no tienes `requests`, descarga los ZIP a mano, ponlos en `lois_votes/votes_rd/` y descomprime hasta tener al menos `Scrutins_XV.json`.

---

## 5. Cruce con diputados

En **deputes_2017_2022.csv**, la columna **id** coincide con el acteur AN (ej. `PA720916` → `720916`). Puedes hacer JOIN de `votos_por_diputado.csv` (o la versión cohorte) con `deputy_id` = `id`.

---

## 6. Nota metodológica

Un **scrutin** es una votación concreta (a menudo adopción de un texto). Puede haber **varios scrutins** por el mismo expediente legislativo (lecturas, artículos). Si necesitas «una ley = una fila», agrupa o elige el scrutin de adopción final según tu marco.

Ya no se generan **leyes_50.csv** ni la lógica de ~50 leyes: la salida cubre **toda** la legislatura según los criterios anteriores.
