# contexto

Aquí dejé mis notas de trabajo de la memoria. Las fui escribiendo durante el proyecto para retomar después de un tiempo sin tocarlo o para darle contexto a quien me ayudara, sea una persona o una IA. La memoria ya está defendida, así que estas notas quedan como registro.

- `contexto_general.md` es el resumen de todo el proyecto: propósito, cómo funciona el pipeline, corpus, métodos, resultados, decisiones y limitaciones. Es el mejor punto de partida.
- `preferencias_y_estilo.md` explica cómo trabajo, cómo me gusta que me ayuden y las convenciones que usé en el LaTeX.
- `referencias.md` tiene los papers y recursos, y para qué usé cada uno.
- `manuscrito/` es sobre la memoria como documento. `estructura_y_estado_final.md` muestra cómo quedó escrita, capítulo por capítulo, y cómo incorporé el feedback de la comisión y de mis profesores. `planificacion_historica.md` es la planificación inicial de la estructura, que en parte cambió, pero la guardo como registro.
- `pipeline/` tiene una nota técnica por módulo de `french_deputies/`, en el orden del pipeline.

## pipeline/

| Archivo | Módulo | De qué trata |
|---|---|---|
| `01_datos_diputados.md` | `datos_diputados/` | Los 668 diputados, que son la base para enlazar todo lo demás |
| `02_manifiestos.md` | `manifestos/` | Programas electorales 2017 (MARPOR), el único corpus con codificación humana |
| `03_twitter.md` | `twitter_zeeschuimer/` | Captura de tuits con Zeeschuimer y cruce con los diputados |
| `04_hemiciclo.md` | `hemicycle/` | Intervenciones en el hemiciclo (Regards Citoyens) |
| `05_leyes_y_votos.md` | `lois_votes/` | Leyes y enmiendas (open data de la Asamblea y Légifrance) y votos por diputado |
| `06_bertopic.md` | `bertopic_analysis/` | Topic modeling no supervisado, exploratorio |
| `07_manifestoberta.md` | `manifestoberta_analysis/` | Clasificación supervisada MARPOR, el núcleo del análisis |
| `08_validacion_ches.md` | `ches_analysis/` | Validación de posiciones RILE contra CHES 2019 |
| `09_party_analysis.md` | `party_analysis/` | Agenda declarada, agenda revelada y el cruce entre ambas |

## Rutas antiguas

Muchas de estas notas las escribí antes de ordenar el repo, así que a veces citan rutas o nombres que ya no existen:

| En las notas aparece | Hoy está en |
|---|---|
| `memoria/` (el LaTeX) | `manuscrito/`, que es el repo [memoria_french_deputies](https://github.com/TinSolis/memoria_french_deputies) |
| `memoria/main.pdf` | `memoria_agustin_solis_meza.pdf` |
| `memoria/context/…` | esta carpeta |
| `memoria/propuesta/` | `documentos/propuesta_memoria/` |
| `memoria/manual/Manual-de-normalizacion.md` | `documentos/manual_normalizacion/manual_normalizacion_fcfm.md` |
| `feedback.txt` | `documentos/feedback_coguia_franziska.txt` |
| `REFERENCIAS.md` | `contexto/referencias.md` |
| `kg-gen/` | `french_deputies/kg_gen/` |
| `ESTRUCTURA.md`, `GUIA_IDENTIFICADORES_TESIS.md`, `RESUMEN_CUANTITATIVO.md`, `README_LOIS_VOTES.md` | `french_deputies/estructura.md`, `hemicycle/guia_identificadores.md`, `hemicycle/resumen_cuantitativo.md` y `lois_votes/README.md` |

Las notas también tenían otros nombres al principio:

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
