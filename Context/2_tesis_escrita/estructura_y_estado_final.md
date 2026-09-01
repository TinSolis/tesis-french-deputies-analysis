# Contexto de la tesis ESCRITA (documento final)

> Describe la memoria **tal como está escrita hoy** en los `.tex`, no como se planificó.
> Complementa:
> - `general_context.md` → síntesis del **proyecto empírico** (datos/pipeline/análisis).
> - `memoria_escritura.md` → **planificación** de la estructura (parcialmente superada; ver nota en ese archivo).
> - los 9 `*_context.md` de módulo → detalle de **código y datos**.
>
> Regla: no se inventan cifras; todas provienen del texto final y de los contextos de módulo.
> Estado del trabajo: **tesis aprobada**; implementados los comentarios de la comisión y de los guía; pendiente el "go-ahead" para subir a Biblioteca; defensa en **primeras semanas de octubre 2026**.

---

## 1. Metadatos (portada, `main.tex`)

- **Título:** *Clasificación temática y análisis de la relación entre el discurso político y las votaciones parlamentarias: aplicación a la Asamblea Nacional francesa*.
  (El título cambió respecto del que figura en `memoria_escritura.md` §1, que ya está desactualizado.)
- **Autor:** Agustín Sebastián Solís Meza. **Grado:** Ingeniero Civil en Computación. **Depto:** Ciencias de la Computación (FCFM, U. de Chile).
- **Guía:** Valentin Clement Barriere. **Co-guía:** Franziska Christl Wagner. **Comisión:** Claudio Gutiérrez Gallardo, Nicolás Varas Cortés. **Año:** 2026.
- **Clase LaTeX:** `umemoria` (plantilla DCC), **español**, compilación pdfLaTeX (Overleaf). Paquetes: `booktabs`, `float`, `tabularx`, `longtable`.
- **Notas de evaluación:** Claudio 6.8, Nicolás 6.8, Franziska 7, Valentin 7 (todas Aprobación).

---

## 2. Resumen (abstract, `\begin{resumen}` en `main.tex`)

Idea del resumen (redacción final): los partidos comunican prioridades por varios canales (programas, hemiciclo, redes), pero la **agenda declarada** no siempre coincide con la **revelada** al votar. Se construye un **sistema reproducible** que reúne cinco arenas sobre una **cohorte común de diputados**, se clasifica con **MARPOR** vía **ManifestoBERTa** (+ **BERTopic** exploratorio) y se valida con **CHES**. Tres hallazgos: (1) el canal importa pero la firma temática persiste; (2) el voto tiene dos capas (posición de bloque en leyes; clivaje cultural en enmiendas); (3) la coincidencia declarado–votado es baja en promedio pero se entiende como perfiles de coherencia, no como una nota única. **El aporte es metodológico** (marco común y reproducible), no un ranking de partidos ni una afirmación causal.

- **Inicio reescrito** (por feedback de "sonaba poco serio"): *"Los partidos políticos comunican sus prioridades por múltiples canales de información: las escriben en sus programas electorales, las defienden en el hemiciclo y las difunden en redes sociales. Esa agenda declarada, sin embargo, no siempre coincide con la que sus representantes revelan al votar cuando legislan."*

---

## 3. Estructura real (6 capítulos + anexos)

`main.tex` incluye, en orden: `intro`, `cap_marco_teorico`, `cap_metodologia`, `cap_resultados`, `cap_discusion`, `conclu`, y `anexoA` (appendices). Secciones tal como existen hoy:

### Cap. 1 — Introducción (`intro.tex`)
- **Párrafo de apertura + contribuciones:** define el trabajo y, en un párrafo agregado por feedback, enuncia **dos contribuciones con la de computación primero**: (i) **ingeniería** (resolución de entidades para anclar 5 fuentes a una cohorte única sin clave compartida, normalización a unidades comparables, transferencia de dominio de ManifestoBERTa con capa de validación, *pipeline* modular y reproducible); (ii) **analítica** (marco comparativo declarado vs. revelado). Remite a `\ref{sec:concl-contribuciones}`.
- **Contexto y motivación** · **Descripción del problema** · **Objetivos** (general + específicos; los específicos llevan la frase de enlace *"Los objetivos específicos concretan la contribución computacional del trabajo:"*) · **Alcances** · **Método y estructura de la memoria** · **Declaración de uso de inteligencia artificial** (subsecciones: modelos y herramientas, metodología de uso, ejemplos de prompts, qué cambiaría).

### Cap. 2 — Marco teórico y revisión de la literatura (`cap_marco_teorico.tex`)
- **Discurso político, agenda y coherencia partidaria** (issue ownership, saliencia, agenda-setting, disciplina) · **El Manifesto Project y la taxonomía MARPOR** (incluye la tabla de 7 dominios en español con un ejemplo) · **Procesamiento de lenguaje natural para texto político** (subs: Clasificación supervisada: ManifestoBERTa; Modelado de tópicos no supervisado: BERTopic) · **Trabajos relacionados**.

### Cap. 3 — Materiales y métodos (`cap_metodologia.tex`) — absorbe "Datos" e "Implementación"
- **3.1 Fuentes de datos y construcción de los corpus** — subs: Cohorte de diputados y grupos parlamentarios · Manifiestos electorales · Actividad en Twitter · Intervenciones en el hemiciclo · Leyes · Enmiendas y votaciones nominales.
- **3.2 Normalización, limpieza y enlace.**
- **3.3 Clasificación y modelado del contenido** — subs: Taxonomía MARPOR como espacio común de comparación · Clasificación supervisada con ManifestoBERTa (incluye la **justificación de elección del modelo** frente a la variante *context* y a LLMs generativos, agregada por feedback de Nicolás) · Modelado exploratorio con BERTopic · Diseño de validación.
- **3.4 Métricas de análisis a nivel de partido** — subs: Agenda declarada (énfasis, firma y concentración) · Agenda revelada (soporte, soporte relativo y cohesión) · Comparación entre canales declarados · Descomposición del voto · Cruce entre agenda declarada y revelada.
- **3.5 Arquitectura e implementación del pipeline** — subs: Diseño modular y flujo de ejecución · Reproducibilidad y entorno · Decisiones de implementación y límites.

### Cap. 4 — Resultados (`cap_resultados.tex`) — absorbe "Validación/Experimentos"
- **4.1 Validación del pipeline** — subs: Validación del clasificador contra MARPOR humano · Validación posicional: RILE frente a CHES · **Alcance de la validación** (aquí está, explícito, el límite de la **transferencia a tuits**: la calidad "se asume, no se mide", y se propone como validación futura una muestra pequeña anotada a mano por arena — agregado por feedback de Nicolás).
- **4.2 Modelado exploratorio con BERTopic** — sub: Por qué el análisis principal usa MARPOR (BERTopic es exploratorio; no valida ni reemplaza a ManifestoBERTa; el detalle se traslada al anexo).
- **4.3 Agenda declarada: el canal define de qué se habla** — subs: Cobertura y planteamiento · El canal reorganiza la mezcla temática · Identidad que persiste y estrategia que reorganiza · Lectura del análisis.
- **4.4 Agenda revelada por el voto** — subs: Cobertura y planteamiento · El eje se invierte entre leyes y enmiendas · ¿Posición o tema? Descomposición del apoyo · El clivaje temático es cultural y robusto · Cohesión: el voto valida el agrupamiento · Lectura del análisis.
- **4.5 Declarado frente a revelado: ¿votan lo que dicen?** — subs: Diseño de la comparación · Resultado principal: una tipología, no un ranking · Resultado secundario: la coherencia por partido es frágil · Resultado exploratorio: ningún canal anticipa mejor el voto · Lectura del análisis.

### Cap. 5 — Discusión (`cap_discusion.tex`)
- **El canal como condicionante de la agenda declarada** · **El voto como capa revelada del comportamiento partidario** · **La relación entre agenda declarada y agenda revelada** · **Alcances metodológicos del pipeline** · **Limitaciones**.

### Cap. 6 — Conclusiones (`conclu.tex`)
- **Cumplimiento de los objetivos** · **Principales hallazgos** · **Contribuciones** (contribución de ingeniería + analítica; el párrafo de detalle CS se **condensó** y remite a la introducción con `\ref{cap:introduccion}`) · **Trabajo futuro** (incluye la muestra anotada a mano por arena para medir la transferencia; sin KG-Gen).

### Anexos — Material complementario (`anexoA.tex`)
- **Detalle de los corpus y filtros** (sub: Reproducibilidad y orden de ejecución) · **Taxonomía MARPOR: dominios y categorías** (dominios en español, categorías en inglés) · **Validación del clasificador** (métricas + matriz de confusión por dominio) · **Tópicos de BERTopic por corpus** (sub: Cruce ilustrativo BERTopic × MARPOR) · **Ejemplos de clasificación temática en Twitter** (tuits en francés con traducción) · **Cruce declarado–revelado: detalle por canal**.

---

## 4. Convenciones aplicadas en el texto final

- **Dominios MARPOR en español** (canónicos en toda la tesis): 1. Relaciones exteriores · 2. Libertad y democracia · 3. Sistema político · 4. Economía · 5. Bienestar y calidad de vida · 6. Tejido social · 7. Grupos sociales. Las **categorías** (las 56, del handbook) se dejan en **inglés**; así se aclara en el anexo de taxonomía.
- **Coma decimal** en modo matemático con `{,}` (p. ej. `$-21{,}9$`, `$0{,}44$`).
- **Incisos con `--`** (no em-dash `—`).
- **Énfasis** `\emph{}`, negrita `\textbf{}` para conceptos clave.
- **Referencias:** `Cuadro~\ref`, `Figura~\ref`, `sección~\ref`, `capítulo~\ref`, `anexo~\ref`, `\cite`.
- **Tipos de columna `Y/Z/W`** (tabularx) definidos **una sola vez en el preámbulo de `main.tex`** (no redefinir dentro de floats).
- Detalle completo de estilo: `memoria/manual/Manual-de-normalizacion.md`.

---

## 5. Cifras y resultados clave (tal como aparecen en el texto)

- **Validación del clasificador** (contra `cmp_code` humano de manifiestos, n = 3.430 cuasi-frases utilizables): top-1 **58,3 %**, top-3 **82,0 %**, dominio **70,3 %**, macro F1 **0,44** (consistentes con la model card).
- **Validación posicional (RILE vs CHES 2019):** correlación sube a **ρ≈0,89** con partidos de ≥100 cuasi-frases; cae en la muestra completa (arrastrada por PCF, 39 cuasi-frases). RILE se usa **solo** para validar, no como eje del análisis.
- **Tamaños de corpus NLP:** manifiestos **3.801** · enmiendas **2.575** · leyes **23.267** párrafos · tuits **~222.644** (BERTopic) / **224.466** (ManifestoBERTa) · intervenciones **338.192**.
- **Agenda declarada:** manifiestos = programático (domina *Bienestar y calidad de vida*); tuits y hemiciclo = meta-política (domina *Sistema político*). El efecto de canal pesa ~12–16 pp; **FN** es el mayor reorganizador específico; la firma distintiva persiste (issue ownership).
- **Agenda revelada:** el eje se **invierte** leyes↔enmiendas; en leyes domina la posición de bloque; en enmiendas emerge un **clivaje cultural robusto** en soporte relativo: izquierda apoya de menos *Tejido social* (PS −21,9, GDR-PCF −17,5, LFI −15,9), derecha de menos *Libertad y democracia* (LR −19,1, FN −19,2); FN suma *Bienestar y calidad de vida* +14,0. Signos estables ~100 % en bootstrap por *scrutin*. Cohesión Rice valida el agrupamiento (LFI ~1,0; FN 0,955; NI residual 0,495).
- **Cruce declarado–revelado:** coherencia por partido **débil e inestable** (IC ≈ [−1,+1]) → **no rankeable**; el aporte es **tipológico** (tipología por celda partido×dominio: énfasis respaldado / énfasis no respaldado / apoyo no enfatizado / baja prioridad y menor apoyo relativo). Ningún canal anticipa el voto mejor que otro una vez igualada la cobertura.
- **FN** se trata como **familia analítica propia** (11 `deputy_id`), separada del residuo **NI** (que no es proxy de FN/RN).

---

## 6. Figuras y tablas que existen

- Heatmaps de énfasis por dominio/canal y de soporte relativo (enmiendas); scatter/quadrants del cruce; `scatter_rile_vs_ches.png` (regenerado con ejes en español); shift bruto vs. específico.
- Tablas de clivaje con IC por bootstrap (`tab:clivaje-ci`), casos canónicos de la tipología (`tab:cruce-casos`), resumen de métricas, corpus, validación.
- En anexo: taxonomía MARPOR (dominios español / categorías inglés), matriz de confusión por dominio, 24 tópicos BERTopic por corpus, ejemplos de tuits (francés + traducción).

---

## 7. Cómo se incorporó el feedback (edits recientes)

**Comisión (tesis ya aprobada; cambios pequeños y específicos):**
- **Claudio Gutiérrez** — contribución de computación explícita: párrafo en la **introducción** (contribuciones, CS primero) + frase de enlace en **objetivos** + versión condensada en **conclusiones**. Destaca el trabajo concreto (pipeline, entity resolution, transferencia de dominio, validación) sin decir "un cientista político no podría".
- **Nicolás Varas (a)** — **justificación de elección de modelo** en §3.3.2 (ManifestoBERTa a nivel de cuasi-frase sobre variante *context* y sobre LLMs generativos; solo el supervisado es comparable directo contra el código humano MARPOR).
- **Nicolás Varas (b)** — **límite de transferencia a tuits** en §4.1.3 (Alcance de la validación): se asume, no se mide; muestra anotada a mano por arena como validación futura (también en Trabajo futuro).
- **Resumen** — reescrito el inicio (más formal).

**Guía (feedback sobre esos cambios):**
- **Valentin** — mover la contribución CS a la introducción (hecho: párrafo A; y condensado el de conclusiones).
- **Franziska** — conectar contribuciones con objetivos (hecho: frase B). Para la defensa: mencionar los cambios incorporados del feedback.
- **Valentin (defensa)** — dominar a fondo lo escrito (si no, parecerá generado por IA).

**Consistencia previa:** traducción de todos los nombres de dominio MARPOR al español en el cuerpo (tablas y prosa de `cap_resultados`, `cap_discusion`, `anexoA`).

---

## 8. Limitaciones tal como se redactan

Cobertura temporal de Twitter (excede 2017–2022); modelo imperfecto y **no calibrado**, una etiqueta por documento, truncamiento a 200 tokens; validación **solo sobre manifiestos** (único canal con `cmp_code`); n pequeño de partidos; heterogeneidad de "partido" entre canales; matching heurístico scrutin↔dossier↔enmienda; `demandeur` de enmiendas no controlado; **sin causalidad** (alineaciones agregadas, no cumplimiento programático). Se enmarca el aporte como **metodológico y de sistema**.

---

## 9. Declaración de uso de IA (en `intro.tex`)

Sección explícita: uso de IA generativa (código y redacción) en el entorno Cursor (modelos: Claude Opus 4.8, GPT-5.5, Composer 2.5); metodología de uso (tareas acotadas y verificables, sin inventar cifras, verificando contra fuentes); ejemplos de prompts que funcionaron y que no; y "qué cambiaría". El diseño, las decisiones y la verificación de cifras son de autoría propia; no constituye coautoría.

---

## 10. Trazabilidad capítulo → contexto de módulo → carpeta

| Capítulo (real) | Contexto(s) de `memoria/context/` | Carpeta(s) `french_deputies/` (trazabilidad) |
|---|---|---|
| 1 Introducción | `general_context.md` §1,§6,§12 | (visión global) |
| 2 Marco teórico | `manifestos`, `manifestoberta_analysis`, `bertopic_analysis`, `ches_analysis` | conceptos MARPOR/RILE/CHES |
| 3 Materiales y métodos | `datos_diputado`, `twitter_zeeschuimer`, `manifestos`, `lois_votes`, `hemicycle`, `manifestoberta_analysis`, `bertopic_analysis`, `ches_analysis`, `party_analysis` | `datos_diputados/`, `twitter_zeeschuimer/`, `lois_votes/`, `hemicycle/`, `manifestos/`, `*_analysis/common/` |
| 4 Resultados | `manifestoberta_analysis`, `ches_analysis`, `party_analysis`, `bertopic_analysis` | `manifestoberta_analysis/validation/`, `ches_analysis/`, `party_analysis/` (`01_/02_/03_.md`, `results/`) |
| 5 Discusión | `party_analysis`, `ches_analysis`, `general_context.md` §9 | (interpretación) |
| 6 Conclusiones | `general_context.md` §6,§11,§12 | (síntesis) |
| Anexos | todos | tablas/heatmaps de `results/`, taxonomía, validación |

> Recordatorio: las carpetas/scripts/outputs son trazabilidad interna, **no** bibliografía. La bibliografía oficial está en `bibliografia.bib` (ver `memoria_escritura.md` §10).

---

## 11. Estado y pendientes

- **Hecho:** comentarios de comisión + follow-up de guía implementados; documentación de `french_deputies/` reescrita; nombres de dominio en español consistentes.
- **Pendiente:** go-ahead de los guía para subir el PDF a **Biblioteca**; luego **defensa (oct 2026)**.
- **Opcionales abiertos:** consistencia de rutas (`french_deputies/`, `twitter_zeeschuimer/`) dentro de los **scripts `.py`**; completar campos "[fecha por verificar]" en `bibliografia.bib`.
