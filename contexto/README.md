# contexto — hub de contexto de la memoria de Ingeniería Civil

Reúne **todo el contexto** de la memoria de Ingeniería Civil en Computación (diputados franceses, XV legislatura 2017-2022) en un solo lugar. Sirve para retomar el trabajo, pasarle contexto a otro chat/IA o entender el proyecto de cero.

> **Estado: memoria cerrada.** Defendida el 16-nov-2026 y aprobada por la comisión. Este hub es la única fuente de verdad del contexto de la memoria.
>
> La tesis de Magíster (MDS) tiene su propio hub, con la misma estructura, en `../tesis_magister_mds/contexto/`. Los dos hubs son independientes: si algo cambia en el magíster, se actualiza allá y no aquí.

## Estructura (igual en la memoria y en el magíster)

| Archivo o carpeta | Qué es |
|---|---|
| `README.md` | Este índice |
| `contexto_general.md` | **Empezar aquí.** Síntesis integradora: propósito, arquitectura del pipeline, corpus, métodos, resultados, decisiones y limitaciones |
| `preferencias_y_estilo.md` | Cómo pido las cosas, qué corrijo, tono, convenciones LaTeX y handoff para otro chat |
| `referencias.md` | Papers, modelos y recursos, con el rol que cumple cada uno |
| `manuscrito/` | La memoria como documento escrito (solo existe en este hub) |
| `pipeline/` | Detalle técnico de cada módulo de `french_deputies/`, en orden del pipeline |

### `manuscrito/`

| Archivo | Qué es |
|---|---|
| `estructura_y_estado_final.md` | La memoria tal como quedó escrita: estructura por capítulo y sección, cifras, figuras y cómo se incorporó el feedback de comisión y guía |
| `planificacion_historica.md` | Planificación de la estructura (parcialmente superada); se conserva como registro histórico |

### `pipeline/`

| Archivo | Módulo (`french_deputies/…`) | Qué cubre |
|---|---|---|
| `01_datos_diputados.md` | `datos_diputados/` | Cohorte única de 668 diputados (ancla de identidad) |
| `02_manifiestos.md` | `manifestos/` | Programas electorales 2017 (MARPOR); único con ground truth humano |
| `03_twitter.md` | `twitter_zeeschuimer/` | Captura de tuits (Zeeschuimer) y cruce con la cohorte |
| `04_hemiciclo.md` | `hemicycle/` | Intervenciones en el hemiciclo (Regards Citoyens, ND15) |
| `05_leyes_y_votos.md` | `lois_votes/` | Leyes y enmiendas (open data AN + Légifrance) y votos por diputado |
| `06_bertopic.md` | `bertopic_analysis/` | Topic modeling no supervisado (exploratorio) |
| `07_manifestoberta.md` | `manifestoberta_analysis/` | Clasificación supervisada MARPOR (núcleo) |
| `08_validacion_ches.md` | `ches_analysis/` | Validación posicional RILE vs CHES 2019 |
| `09_party_analysis.md` | `party_analysis/` | Los 3 análisis: agenda declarada, revelada y el cruce |

## Rutas antiguas que aparecen dentro de los documentos

Los documentos se escribieron antes de reordenar el repo y a veces citan rutas o nombres viejos. Equivalencias:

| Ruta o nombre citado en los textos | Ruta actual |
|---|---|
| `memoria/` (LaTeX) | `manuscrito/` (repo aparte [TinSolis/memoria_french_deputies](https://github.com/TinSolis/memoria_french_deputies)) |
| `memoria/main.pdf` | `memoria_agustin_solis_meza.pdf` (versión final defendida) |
| `memoria/context/<nombre>.md` | `contexto/…` (ver la tabla de nombres originales) |
| `memoria/propuesta/` | `documentos/propuesta_memoria/` |
| `memoria/manual/Manual-de-normalizacion.md` | `documentos/manual_normalizacion/manual_normalizacion_fcfm.md` |
| `feedback.txt` | `documentos/feedback_coguia_franziska.txt` |
| `REFERENCIAS.md` | `contexto/referencias.md` |
| `kg-gen/` | `french_deputies/kg_gen/` |
| `ESTRUCTURA.md`, `GUIA_IDENTIFICADORES_TESIS.md`, `RESUMEN_CUANTITATIVO.md`, `README_LOIS_VOTES.md` | `french_deputies/estructura.md`, `hemicycle/guia_identificadores.md`, `hemicycle/resumen_cuantitativo.md`, `lois_votes/README.md` |

| Nombre actual | Nombre original |
|---|---|
| `contexto_general.md` | `general_context.md` |
| `preferencias_y_estilo.md` | `Context.md` |
| `manuscrito/estructura_y_estado_final.md` | `tesis_escrita_context.md` |
| `manuscrito/planificacion_historica.md` | `memoria_escritura.md` |
| `pipeline/01_datos_diputados.md` | `datos_diputado_context.md` |
| `pipeline/02_manifiestos.md` | `manifestos_context.md` |
| `pipeline/03_twitter.md` | `twitter_zeeschuimer_context.md` |
| `pipeline/04_hemiciclo.md` | `hemicycle_context.md` |
| `pipeline/05_leyes_y_votos.md` | `lois_votes_context.md` |
| `pipeline/06_bertopic.md` | `bertopic_analysis_context.md` |
| `pipeline/07_manifestoberta.md` | `manifestoberta_analysis_context.md` |
| `pipeline/08_validacion_ches.md` | `ches_analysis_context.md` |
| `pipeline/09_party_analysis.md` | `party_analysis_context.md` |
