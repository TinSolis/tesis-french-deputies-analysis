# Context — hub de contexto de la tesis

Reúne **todo el contexto** de la memoria de Ingeniería Civil en Computación (diputados franceses, XV legislatura 2017–2022) en un solo lugar. Sirve para retomar el trabajo, pasarle contexto a otro chat/IA o entender el proyecto de cero.

> **Estado: memoria cerrada.** Defendida el 16-nov-2026 y aprobada por la comisión. Este hub es la **única fuente de verdad** del contexto de la memoria (la antigua carpeta `memoria/context/` se eliminó del repo por ser un duplicado exacto).
>
> La tesis de Magíster (MDS) tiene su propio hub de contexto en `../2_Tesis_Magister_MDS/Context/`.

## Rutas antiguas que aparecen dentro de los documentos

Los documentos se escribieron antes de reordenar el repo y citan rutas viejas. Equivalencias:

| Ruta citada en los textos | Ruta actual |
|---|---|
| `memoria/` (LaTeX) | `memoria_latex/` (repo aparte [TinSolis/memoria_french_deputies](https://github.com/TinSolis/memoria_french_deputies)) |
| `memoria/main.pdf` | `Memoria_Agustin_Solis_Meza.pdf` (versión final defendida) |
| `memoria/context/<nombre>.md` | `Context/…` (ver el mapa de nombres más abajo) |
| `memoria/propuesta/` | `docs/propuesta_memoria/` |
| `memoria/manual/Manual-de-normalizacion.md` | `docs/manual_normalizacion/Manual-de-normalizacion.md` |
| `Context.md` | `Context/0_como_trabajo/preferencias_y_estilo.md` |
| `feedback.txt` | `docs/feedback_coguia_franziska.txt` |

## Por dónde empezar

1. **`0_como_trabajo/`** — cómo trabajo y cómo me gusta que me ayuden (leer primero si sos otro chat/IA).
2. **`1_vision_general/`** — qué es el proyecto completo (datos + pipeline + análisis) de un vistazo.
3. **`2_tesis_escrita/`** — la memoria como documento final (estructura, estado, feedback incorporado).
4. **`3_modulos_del_pipeline/`** — el detalle técnico de cada módulo, en orden del pipeline.

## Estructura y contenido

### `0_como_trabajo/`
| Archivo | Qué es |
|---|---|
| `preferencias_y_estilo.md` | Cómo pido las cosas, qué corrijo, tono, convenciones LaTeX, y handoff para otro chat. |

### `1_vision_general/`
| Archivo | Qué es |
|---|---|
| `proyecto_completo.md` | Síntesis integradora: propósito, arquitectura del pipeline, corpus, métodos, resultados, decisiones y limitaciones. |

### `2_tesis_escrita/`
| Archivo | Qué es |
|---|---|
| `estructura_y_estado_final.md` | La memoria **tal como está escrita hoy**: estructura real por capítulo/sección, cifras, figuras, y cómo se incorporó el feedback de comisión y guía. |
| `planificacion_historica.md` | Documento de **planificación** de la estructura (parcialmente superado); se conserva como registro histórico. |

### `3_modulos_del_pipeline/` (orden del pipeline)
| Archivo | Módulo (`french_deputies/…`) | Qué cubre |
|---|---|---|
| `1_datos_diputados.md` | `datos_diputados/` | Cohorte única de 668 diputados (ancla de identidad). |
| `2_manifiestos.md` | `manifestos/` | Programas electorales 2017 (MARPOR); único con ground truth humano. |
| `3_twitter.md` | `twitter_zeeschuimer/` | Captura de tuits (Zeeschuimer) y cruce con la cohorte. |
| `4_hemiciclo.md` | `hemicycle/` | Intervenciones en el hemiciclo (Regards Citoyens, ND15). |
| `5_leyes_y_votos.md` | `lois_votes/` | Leyes y enmiendas (open data AN + Légifrance) + votos por diputado. |
| `6_bertopic.md` | `bertopic_analysis/` | Topic modeling no supervisado (exploratorio). |
| `7_manifestoberta.md` | `manifestoberta_analysis/` | Clasificación supervisada MARPOR (núcleo). |
| `8_validacion_ches.md` | `ches_analysis/` | Validación posicional RILE vs CHES 2019. |
| `9_party_analysis.md` | `party_analysis/` | Los 3 análisis: declarada, revelada y el cruce. |

## Mapa de nombres (nuevo ↔ original)

Los documentos se **renombraron** para que sean más intuitivos. Ojo: las referencias *dentro* de los textos usan a veces los **nombres originales** (columna derecha).

| Nuevo | Original |
|---|---|
| `0_como_trabajo/preferencias_y_estilo.md` | `Context.md` |
| `1_vision_general/proyecto_completo.md` | `general_context.md` |
| `2_tesis_escrita/estructura_y_estado_final.md` | `tesis_escrita_context.md` |
| `2_tesis_escrita/planificacion_historica.md` | `memoria_escritura.md` |
| `3_modulos_del_pipeline/1_datos_diputados.md` | `datos_diputado_context.md` |
| `3_modulos_del_pipeline/2_manifiestos.md` | `manifestos_context.md` |
| `3_modulos_del_pipeline/3_twitter.md` | `twitter_zeeschuimer_context.md` |
| `3_modulos_del_pipeline/4_hemiciclo.md` | `hemicycle_context.md` |
| `3_modulos_del_pipeline/5_leyes_y_votos.md` | `lois_votes_context.md` |
| `3_modulos_del_pipeline/6_bertopic.md` | `bertopic_analysis_context.md` |
| `3_modulos_del_pipeline/7_manifestoberta.md` | `manifestoberta_analysis_context.md` |
| `3_modulos_del_pipeline/8_validacion_ches.md` | `ches_analysis_context.md` |
| `3_modulos_del_pipeline/9_party_analysis.md` | `party_analysis_context.md` |