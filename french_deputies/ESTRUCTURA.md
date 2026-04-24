# Estructura y uso de archivos – francia_deputies

Yo dejé en la **raíz** solo **README.md** y este **ESTRUCTURA.md**. Todo lo demás lo repartí en **datos_diputados/**, **zeeschuimer/**, **lois_votes/** y **hemicycle/** para saber siempre qué es fuente, qué es script y qué es tabla final.

---

## Lo principal (lo que uso para la tesis)


| Archivo o carpeta                                   | Qué es para mí                                                                                                                                                      |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **datos_diputados/processed/deputes_2017_2022.csv** | Mi lista de diputados 2017-2022 (id, nombre, grupo, circunscripción, Twitter). Es la base que enlazo con zeeschuimer, lois_votes y hemicycle.                       |
| **zeeschuimer/processed/**                          | Tweets ya cruzados con diputados: texto, menciones, resúmenes por cuenta.                                                                                           |
| **lois_votes/votes_rd/processed/**                  | Leyes votadas (por scrutin), votos por diputado, cohorte, y cuando lo generé, **leyes_texto_oficial.csv** con NOR/Légifrance y texto si lo pegué en `textes_lois/`. |
| **hemicycle/processed/**                            | Intervenciones XV (ND15) con texto y columnas de diputado; también meta y textos separados. Detalle en **hemicycle/README.md**.                                     |
| **manifestos/processed/**                           | Manifiestos MARPOR Francia 2017: textos quasi-sentence codificados y posiciones por partido. Detalle en **manifestos/README.md**.                                   |


---

## Scripts 


| Ubicación                                                   | Para qué lo uso                                               |
| ----------------------------------------------------------- | ------------------------------------------------------------- |
| **datos_diputados/scripts/fetch_an_15e_deputes.py**         | AN 15e → `data/deputes_an_rd.csv`                             |
| **datos_diputados/scripts/build_deputes_twitter_csv.py**    | Twitter raw → `data/deputes_twitter.csv`                      |
| **datos_diputados/scripts/merge_deputes_2017_2022.py**      | Merge AN + Twitter → `processed/deputes_2017_2022.csv`        |
| **zeeschuimer/scripts/generate_twitter_url_list.py**        | Lista de URLs de perfiles desde mi CSV de diputados           |
| **zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py**  | ndjson en `captures/` + diputados → CSV en `processed/`       |
| **lois_votes/scripts/download_an_scrutins_and_dossiers.py** | Descarga y descomprime Scrutins + Dossiers en `votes_rd/`     |
| **lois_votes/scripts/build_laws_and_votes.py**              | Tablas de leyes filtradas y votos (y cohorte)                 |
| **lois_votes/scripts/build_leyes_texte_oficial.py**         | NOR / URL JORF y texto opcional desde `textes_lois/`          |
| **hemicycle/scripts/build_interventions_with_deputies.py**  | TSV en `hemicycle/fuente/` → tablas en `hemicycle/processed/` |
| **hemicycle/scripts/report_hemicycle_stats.py**             | Actualizo **RESUMEN_CUANTITATIVO.md**                         |
| **manifestos/scripts/download_manifestos.py**              | API MARPOR → dataset + textos Francia 2017 en `manifestos/`  |


---

## Datos intermedios y raw (lo que no es “tabla final”)


| Ubicación                 | Qué guardo ahí                                                             |
| ------------------------- | -------------------------------------------------------------------------- |
| **datos_diputados/data/** | CSV intermedios, ZIP de la AN, referencias nosdeputes, etc.                |
| **zeeschuimer/captures/** | Exports `.ndjson` de Zeeschuimer (pesados; no van a GitHub tal cual).      |
| **lois_votes/votes_rd/**  | ZIP descomprimidos, JSON de scrutins y dossiers, `processed/` con mis CSV. |
| **hemicycle/fuente/**     | TSV.gz de Regards Citoyens por legislatura.                                |


---

## Guías (donde explico el porqué)


| Archivo                                     | Contenido                                                    |
| ------------------------------------------- | ------------------------------------------------------------ |
| **README.md** (raíz de francia_deputies)    | Visión general y orden de carpetas.                          |
| **ESTRUCTURA.md**                           | Este índice.                                                 |
| **datos_diputados/README.md**               | Cómo armé el CSV de diputados.                               |
| **zeeschuimer/README.md**                   | Cómo capturé y fusioné Twitter.                              |
| **lois_votes/README_LOIS_VOTES.md**         | Leyes y votos: fuentes, pasos, archivos de salida.           |
| **hemicycle/README.md**                     | Hemiciclo: carpetas, comandos, resumen cuantitativo.         |
| **hemicycle/GUIA_IDENTIFICADORES_TESIS.md** | Diccionario de columnas y enlaces con el resto del proyecto. |
| **hemicycle/RESUMEN_CUANTITATIVO.md**       | Cifras (lo regenero con el script de reporte).               |
| **manifestos/README.md**                    | Cómo bajé los manifiestos, mapeo grupos → partidos, códigos. |


---

## Resumen rápido (para mí cuando vuelvo al repo después de un tiempo)

- **Diputados y Twitter:** `datos_diputados/processed/deputes_2017_2022.csv` y `zeeschuimer/processed/`.
- **Leyes y votos:** `lois_votes/votes_rd/processed/`.
- **Hemiciclo:** `hemicycle/processed/` (después de correr el build con archivos en `hemicycle/fuente/`).
- **Manifiestos:** `manifestos/processed/` (correr con API key de MARPOR; ver `manifestos/README.md`).
- **Reproducir:** diputados primero (orden en su README) → después zeeschuimer, lois_votes, hemicycle o manifestos según lo que esté actualizando.

