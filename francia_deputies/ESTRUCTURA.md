# Estructura y uso de archivos – francia_deputies

En la **raíz** solo están **README.md** y este **ESTRUCTURA.md**. Todo lo demás está en **datos_diputados/**, **zeeschuimer/** y **lois_votes/**.

---

## Lo principal (para análisis y tesis)


| Archivo o carpeta                                   | Qué es                                                                                                                                      |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **datos_diputados/processed/deputes_2017_2022.csv** | Lista consolidada de diputados 2017-2022 (id, nombre, grupo, circunscripción, Twitter). Base para zeeschuimer y lois_votes.                 |
| **zeeschuimer/processed/**                          | Salida del merge Zeeschuimer + diputados: tweets con autor y columnas del diputado; `deputies_capture_summary.csv`, `tweets_text_only.csv`. |
| **lois_votes/votes_rd/processed/**                  | `leyes_votadas_2017_2022.csv`, `votos_por_diputado.csv`, `votos_por_diputado_cohorte.csv`, `leyes_texto_oficial.csv` (NOR/Légifrance + texto si hay `.txt` en `textes_lois/`). |


---

## Scripts (reproducir o actualizar datos)


| Ubicación                                                   | Función                                                                                     |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **datos_diputados/scripts/fetch_an_15e_deputes.py**         | AN 15e (diputados, grupos) → data/deputes_an_rd.csv                                         |
| **datos_diputados/scripts/build_deputes_twitter_csv.py**    | deputes_twitter_rd → data/deputes_twitter.csv                                               |
| **datos_diputados/scripts/merge_deputes_2017_2022.py**      | deputes_an_rd + deputes_twitter → data/deputes_rd.csv y **processed/deputes_2017_2022.csv** |
| **zeeschuimer/scripts/generate_twitter_url_list.py**        | Lista de URLs desde datos_diputados/processed/deputes_2017_2022.csv                         |
| **zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py**  | ndjson en captures/ + diputados → processed/*.csv                                           |
| **lois_votes/scripts/download_an_scrutins_and_dossiers.py** | Descarga y descomprime Scrutins + Dossiers XV en `lois_votes/votes_rd/`.                   |
| **lois_votes/scripts/build_laws_and_votes.py**              | Todas las leyes (adopción) 2017-2022 + todos los votos; cohorte filtrada al CSV de diputados. |
| **lois_votes/scripts/build_leyes_texte_oficial.py**         | `leyes_texto_oficial.csv`: dossier + NOR/URL JORF; opcionalmente texto desde `votes_rd/textes_lois/`. |


---

## Datos intermedios y raw


| Ubicación                                      | Qué es                                                                                                           |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **datos_diputados/data/**                      | deputes_twitter_rd.csv, deputes_twitter.csv, deputes_an_rd.csv, deputes_rd.csv, ZIP AN, nosdeputes (referencia). |
| **zeeschuimer/captures/**                      | Exports ndjson de Zeeschuimer.                                                                                   |
| **lois_votes/votes_rd/**                       | ZIP + JSON abiertos AN (Scrutins XV, Dossiers XV); `processed/` con los CSV generados.                         |


---

## Guías


| Archivo                               | Contenido                                        |
| ------------------------------------- | ------------------------------------------------ |
| **README.md** (raíz)                  | Visión general y subcarpetas.                    |
| **ESTRUCTURA.md**                     | Este archivo.                                    |
| **datos_diputados/README.md**         | Flujo diputados (fetch → build twitter → merge). |
| **zeeschuimer/README.md** | Zeeschuimer y merge con diputados.               |
| **lois_votes/README_LOIS_VOTES.md**   | Leyes y votos (Scrutins/Dossiers).               |


---

## Resumen rápido

- **Diputados y Twitter:** `datos_diputados/processed/deputes_2017_2022.csv` y `zeeschuimer/processed/`.
- **Leyes y votos:** `lois_votes/votes_rd/processed/`.
- **Reproducir:** datos_diputados (orden en su README) → zeeschuimer / lois_votes según necesites.

