# Estructura propuesta para la memoria de título

> Documento de planificación (no es la memoria). Propone título, pregunta de investigación, objetivos, estructura de capítulos y narrativa central para la memoria de **Ingeniería Civil en Computación** basada en el proyecto `french_deputies/`. **Está alineado con la estructura real de `main.tex`**, con la plantilla `umemoria` del DCC ([dccuchile/memoria-tesis-latex](https://github.com/dccuchile/memoria-tesis-latex)) y con el `Manual-de-normalizacion.md` (FCFM/UChile). **No se inventan resultados:** todas las cifras provienen de los contextos de `memoria/context/`; lo no documentado se marca **(por verificar)**.

> **Estado de esta versión.** Corrige el desfase de la versión anterior, que listaba capítulos inexistentes (`cap_datos.tex`, `cap_implementacion.tex`, `cap_experimentos.tex`). La memoria tiene **6 capítulos + anexos**, exactamente los que `main.tex` incluye hoy. "Datos", "Implementación" y "Experimentos/Validación" **no son capítulos**: viven como **secciones** dentro de "Materiales y métodos" y "Resultados".

---

## 0. Decisiones ya tomadas (verificadas)

1. **Estructura = la que ya existe en `main.tex`** (6 capítulos + anexos). No se crean `cap_datos.tex`, `cap_implementacion.tex` ni `cap_experimentos.tex`.
2. **Resumen (`\begin{resumen}`) se redacta al final**, cuando los hallazgos estén consolidados (es lo último).
3. **Citas oficiales completadas en `bibliografia.bib`** (ver §10). Las carpetas, scripts y outputs internos **nunca** se citan como bibliografía: solo como trazabilidad interna / reproducibilidad.
4. **KG-Gen queda FUERA DE ALCANCE**: no se usa, no se analiza y no se vuelve a revisar. La entrada `mo2025kggen` quedó comentada en `bibliografia.bib` y no debe mencionarse en el cuerpo ni en trabajo futuro.
5. **Outputs no versionados** (`results/`, `validation/`): se decidirá más adelante, cuando se necesiten las figuras concretas (regenerar vs. citar tablas de README). **(pendiente operativo, no de estructura.)**
6. **Cifras canónicas a usar:** manifiestos cobertura **94 %** (628/668); enmiendas con texto **2.886**, en análisis NLP **2.575**; **LR = UDI** cuentan como uno (mismo documento MARPOR); hemiciclo **338.192** docs NLP.

---

## 1. Título

Título **registrado en portada** (`main.tex`, oficial salvo cambio administrativo):

> *Bases y análisis de discrepancias entre el discurso de los partidos políticos y la práctica de sus representantes parlamentarios*

Alternativas que enfatizan el aporte de **ingeniería/computación aplicada** (uso como hilo narrativo interno, no necesariamente como título de portada):

1. *Clasificación temática de discurso político y votaciones parlamentarias mediante modelos de lenguaje: aplicación a la Asamblea Nacional francesa*.
2. *Análisis computacional multi-fuente de agendas partidarias mediante clasificación temática y datos parlamentarios abiertos: aplicación a la Asamblea Nacional francesa*.

> Cambiar el título de portada requiere acuerdo con profesores guía y Biblioteca **(por verificar)**.

---

## 2. Pregunta principal de investigación

**Pregunta central:**

> ¿Es posible construir un *pipeline* reproducible que integre fuentes parlamentarias heterogéneas bajo una cohorte única de diputados y, mediante clasificación temática validada, contraste de forma comparable la **agenda declarada** (lo que los partidos dicen en programas, redes y hemiciclo) con la **agenda revelada** (lo que votan en leyes y enmiendas)?

**Sub-preguntas (derivadas de `party_analysis/`):**

- ¿Cambia la agenda temática de un partido según el canal (programa, Twitter, hemiciclo), o su "firma" persiste? (Análisis 1)
- ¿El voto revela tema propio o solo posición gobierno/oposición? (Análisis 2)
- ¿Lo que un partido enfatiza coincide con lo que apoya al votar? (Análisis 3)

> Encuadre de ingeniería: la pregunta primaria es de **diseño y validación de un sistema de datos + NLP**; las sub-preguntas politológicas son los **experimentos** que demuestran que el sistema produce señal interpretable y robusta.

---

## 3. Objetivo general

> Diseñar, implementar y validar un *pipeline* reproducible de ingeniería de datos y procesamiento de lenguaje natural que integre las cinco arenas discursivas de los diputados de la XV legislatura francesa (2017–2022) bajo una cohorte única, las clasifique con una taxonomía temática común y citable (MARPOR), y permita contrastar empíricamente la agenda **declarada** con la **revelada** por el voto a nivel de partido.

(Coherente con el objetivo general ya esbozado en `intro.tex`.)

---

## 4. Objetivos específicos

Reordenados como objetivos de ingeniería (recolección → integración → clasificación → validación → análisis), apoyados en `intro.tex` y en `general_context.md` §6:

1. **Recolectar** fuentes heterogéneas de cinco arenas (open data de la Assemblée nationale, twitter-parlementaires de Regards Citoyens, captura Zeeschuimer, API MARPOR, API Légifrance/PISTE) mediante scripts de adquisición reproducibles.
2. **Construir una cohorte única** de diputados como tabla maestra de identidad que ancle todos los cruces por `id` y `political_group_abbrev`.
3. **Integrar y normalizar** los cinco corpus (manifiestos, tweets, hemiciclo, leyes, enmiendas) a unidades textuales comparables con *entity linking* y filtros de calidad documentados.
4. **Clasificar** los cinco corpus con la taxonomía común MARPOR (56 categorías / 7 dominios) por dos vías: supervisada (ManifestoBERTa, núcleo) y exploratoria (BERTopic).
5. **Validar externamente** el pipeline de clasificación posicional contra un benchmark de expertos (RILE vs. CHES).
6. **Analizar y contrastar** la agenda declarada y la revelada a nivel de partido (énfasis/firma, soporte/cohesión, y el cruce declarado–revelado), con métricas robustas (bootstrap, descomposición de R²).
7. **Documentar** la reproducibilidad del sistema (orden de ejecución, dependencias, decisiones técnicas y limitaciones).

> Estos 7 objetivos **no** se vuelven 7 capítulos: se distribuyen entre Materiales y métodos (1–4, 7) y Resultados (5–6), como exige la estructura del manual.

---

## 5. Estructura de capítulos (la real, alineada con `main.tex`, la plantilla y el manual)

El manual FCFM (`Manual-de-normalizacion.md`, sección de estructura básica) lista: *Resumen ejecutivo, Introducción, Revisión de literatura, Materiales y métodos, Resultados, Discusión (optativo), Conclusiones, Referencias bibliográficas, Anexos (optativo)*. La plantilla `umemoria` la implementa con `\frontmatter` (portada, resumen, dedicatoria, agradecimientos, índices), `\mainmatter` (capítulos vía `\input`), `\bibliography` y `\begin{appendices}`.

**Mapa manual ↔ plantilla ↔ archivo real:**


| Manual FCFM                | Plantilla `umemoria`                                                                                                    | Archivo `.tex` (real)   | Estado                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------ |
| Páginas preliminares       | `\frontmatter`: `\maketitle`, `resumen`, `dedicatoria`, `thanks`, `\tableofcontents`, `\listoftables`, `\listoffigures` | `main.tex`              | existe; **resumen al final**                           |
| Introducción               | Cap. 1                                                                                                                  | `intro.tex`             | existe (esbozado)                                      |
| Revisión de literatura     | Cap. 2                                                                                                                  | `cap_marco_teorico.tex` | existe (esbozado)                                      |
| Materiales y métodos       | Cap. 3                                                                                                                  | `cap_metodologia.tex`   | existe (esbozado); **absorbe Datos + Implementación**  |
| Resultados                 | Cap. 4                                                                                                                  | `cap_resultados.tex`    | existe (esbozado); **absorbe Validación/Experimentos** |
| Discusión (optativo)       | Cap. 5                                                                                                                  | `cap_discusion.tex`     | existe (esbozado)                                      |
| Conclusiones               | Cap. 6                                                                                                                  | `conclu.tex`            | existe (esbozado)                                      |
| Referencias bibliográficas | `\bibliography`                                                                                                         | `bibliografia.bib`      | existe (completado, §10)                               |
| Anexos (optativo)          | `\begin{appendices}`                                                                                                    | `anexoA.tex`            | existe (esbozado)                                      |


`**main.tex` (mainmatter) hoy — no se modifica:**

```
\input{intro.tex}
\input{cap_marco_teorico.tex}
\input{cap_metodologia.tex}
\input{cap_resultados.tex}
\input{cap_discusion.tex}
\input{conclu.tex}
```

**Dónde viven los bloques que antes se proponían como capítulos:**

- **Datos** → sección *3.1 Fuentes de datos y construcción de los corpus* (ya existe en `cap_metodologia.tex`).
- **Implementación / pipeline** → sección *3.5 Arquitectura e implementación del pipeline* (a añadir en `cap_metodologia.tex`); el detalle fino baja a **Anexos**.
- **Experimentos / validación** → sección *4.1 Validación del pipeline* (a añadir como **primera** sección de `cap_resultados.tex`); su **diseño** va en *3.3* (Materiales y métodos).

> **Decisión (tarea 7):** **no** separar Datos/Implementación/Experimentos en capítulos. Caben como secciones y así se respeta el manual (Resultados único; Discusión optativa) y se minimiza el cambio de plantilla (0 capítulos nuevos, `main.tex` intacto).

---

## 6. Detalle por capítulo (secciones reales + qué lo alimenta)

Para cada capítulo se listan: secciones/subsecciones (las que ya tiene el stub `.tex`, marcando lo que se **añade**), contextos de `memoria/context/` que lo alimentan, figuras/tablas sugeridas, qué baja a anexos y los *caveats*. Donde una figura depende de outputs no versionados o de un dato no confirmado, va **(por verificar)**.

### Capítulo 1 — Introducción (`intro.tex`)

- **Secciones (existen):** Contexto y motivación · Descripción del problema · Objetivos (general + específicos) · Alcances · Estructura de la memoria.
- **Contextos:** `general_context.md` (§1 propósito, §6 lógica, §12 resumen).
- **Figuras/tablas:** Fig. 1 — diagrama de las cinco arenas discursivas → agenda declarada vs. revelada. Tabla 1 — las 5 fuentes con su rol (declarada/revelada) y tamaño aproximado.
- **A anexos:** nada propio; a lo sumo glosario de siglas de partidos franceses.
- **Caveats:** alcance a un país y una legislatura (Francia XV, 2017–2022); se describen **alineaciones agregadas, no causalidad**; izquierda-derecha **no es el objeto**, solo se usa para validar.

### Capítulo 2 — Marco teórico y revisión de la literatura (`cap_marco_teorico.tex`)

- **Secciones (existen):** Discurso político, agenda y coherencia partidaria · El Manifesto Project y la taxonomía MARPOR · PLN para texto político (subsecc.: ManifestoBERTa; BERTopic; Stance detection y marcos de valores) · Trabajos relacionados.
- **Contextos:** `manifestos_context.md`, `manifestoberta_analysis_context.md`, `bertopic_analysis_context.md`, `ches_analysis_context.md`.
- **Bibliografía (claves en `bibliografia.bib`):** `marpor_mp_v5`, `manifestoberta2024`, `conneau2020xlmr`, `grootendorst2022bertopic`, `reimers2019sentencebert`, `laver1992party` (RILE), `jolly2022ches`/`ches2019data` (CHES 2019), `ivanusch2024channels`, `sieberer2006partyunity`, `carey2007competing`, `barriere2022cofe`/`barriere2023multilingual`, `schwartz2012overview`, `graham2013moral`.
- **Figuras/tablas:** Tabla 2 — los 7 dominios MARPOR con ejemplos. Tabla 3 — comparación conceptual BERTopic (no superv.) vs. ManifestoBERTa (superv.). Sin resultados.
- **A anexos:** las 56 categorías MARPOR y los 13+13 códigos RILE.
- **Caveats:** RILE es posicional 1-D, frágil y ciego a la dirección; MARPOR fue diseñado para manifiestos → su transferencia a tweets/leyes/enmiendas es un supuesto a justificar.

### Capítulo 3 — Materiales y métodos (`cap_metodologia.tex`) — *absorbe Datos + Implementación*

- **3.1 Fuentes de datos y construcción de los corpus** *(existe)* — subsecc. (existen): Diputados y grupos · Programas electorales (manifiestos) · Intervenciones en el hemiciclo · Actividad en Twitter · Leyes, enmiendas y votaciones. → **aquí viven los "Datos".**
  - Contextos: `datos_diputado_context.md`, `manifestos_context.md`, `hemicycle_context.md`, `twitter_zeeschuimer_context.md`, `lois_votes_context.md`; tabla §3 de `general_context.md`.
  - Figuras/tablas: Tabla 4 (fuente · representa · unidad · filtros · tamaño · rol); Fig. 2 — cohorte única como ancla (`id`/`political_group_abbrev`); Tabla 5 — distribución de grupos.
  - Citas oficiales de fuentes: `an_opendata_xv`, `legifrance_piste`, `marpor_mpds2025a`, `regardscitoyens_twitter`, `regardscitoyens_nosdeputes`, `peeters2022zeeschuimer`.
- **3.2 Normalización, limpieza y enlace** *(existe)*.
- **3.3 Clasificación y modelado del contenido** *(existe)* — subsecc.: ManifestoBERTa; BERTopic. **Añadir** el *diseño de validación* (cómo se valida: contra `cmp_code` y las tres capas CHES); los **resultados** de validación van al Cap. 4.
  - Contextos: `manifestoberta_analysis_context.md`, `bertopic_analysis_context.md`, `ches_analysis_context.md`.
  - Figuras/tablas: Tabla 6 — parámetros BERTopic por fuente; Fig. 3 — esquema de las 3 capas de validación CHES.
  - Citas: `manifestoberta2024`, `conneau2020xlmr`, `grootendorst2022bertopic`, `reimers2019sentencebert`, `mcinnes2018umap`, `mcinnes2017hdbscan`, `laver1992party`.
- **3.4 Métricas de análisis a nivel de partido** *(existe)* — subsecc.: declarada · revelada · cruce.
  - Contexto: `party_analysis_context.md` (§Metodología A–E).
  - Tabla 7 — definición formal de cada métrica (énfasis, distintividad, *evenness*, Rice, soporte global/por tema/relativo, shift, persistencia, R², tipología).
  - Citas: `rice1928quantitative` (cohesión), `shannon1948mathematical` (entropía/evenness).
- **3.5 Arquitectura e implementación del pipeline (NUEVA, sección breve)** → **aquí vive la "Implementación"**, en alto nivel.
  - Contextos: todos los `*_context.md` (su "Flujo / lógica principal"); `general_context.md` §2 y §5.
  - Figuras/tablas: Fig. 4 — diagrama de arquitectura extremo a extremo (adaptado del ASCII de `general_context` §2). Tabla 8 — por módulo: entrada · salida · técnica.
  - Citas de herramientas: `wolf2020transformers`, `paszke2019pytorch`, `pedregosa2011scikit`, `harris2020numpy`, `mckinney2010pandas`, `virtanen2020scipy`, `peeters2022zeeschuimer`.
- **A anexos:** esquema de columnas de tablas maestras; URLs/versiones de fuentes; protocolo de captura Zeeschuimer; stop-words por dominio; orden de ejecución y `requirements.txt`; tiempos de cómputo.
- **Caveats:** modelo sin reentrenamiento; **una etiqueta por documento**; probabilidades **no calibradas**; truncamiento a 200 tokens; **7 dominios y no 56 categorías** para el voto; **énfasis y no RILE** para el análisis principal; "soporte relativo negativo" ≠ "vota en contra".

### Capítulo 4 — Resultados (`cap_resultados.tex`) — *absorbe Validación/Experimentos*

- **4.1 Validación del pipeline (NUEVA, primera sección)** → **aquí viven los "Experimentos".**
  - Contextos: `manifestoberta_analysis_context.md` (§criterios de evaluación), `ches_analysis_context.md` (tres capas y tabla de correlaciones).
  - Tablas/figuras: Tabla 10 — validación del clasificador (top-1 58,3 %, top-3 82,0 %, dominio 70,3 %, macro F1 0,44). Tabla 11 — correlaciones CHES (A 0,79; B 0,38; techo 0,76; ≥100 frases 0,89). Fig. 5 — `scatter_rile_vs_ches.png` (versionado). Matriz de confusión por dominio **(por verificar: regenerar `validation/`)**.
  - Caveats: validación **solo sobre manifiestos**; **n chico** (6–10 partidos) → Spearman y reportar n; outliers de RILE (FN/RN, MoDem/LREM, PCF 39 frases); desfase **CHES 2019 vs. manifiestos 2017**.
- **4.2 Las bases de datos construidas** *(existe)* — cobertura y volumen por corpus.
- **4.3 Agenda declarada: el canal define de qué se habla** *(existe)* — subsecc.: Manifiestos · Twitter · Hemiciclo.
- **4.4 Agenda revelada por el voto** *(existe)* — subsecc.: dos capas (posicional/temática) · cohesión · clivajes en enmiendas.
- **4.5 Declarado vs. revelado: ¿votan lo que dicen?** *(existe)* — tipología por celda.
  - Contextos: `party_analysis_context.md` (§Resultados con cifras) y los `01_/02_/03_.md` de prosa casi final; `general_context.md` §7. Lectura exploratoria: `bertopic_analysis_context.md`.
  - Tablas/figuras sugeridas: Tabla 12 dominio dominante por canal · Tabla 13 shift/persistencia (LFI 14,4/0,02 … LREM 5,7/0,557) · Tabla 14 inversión leyes↔enmiendas (% Pour) · Tabla 15 descomposición R² · Tabla 16 clivaje cultural · Tabla 17 coherencia por partido con IC · Tabla 18 tópicos BERTopic por corpus; heatmaps/scatters de `party_analysis/results/` **(por verificar: outputs gitignored, regenerar cuando se necesiten)**.
- **A anexos:** tablas completas por partido/canal; los 24 tópicos BERTopic por corpus; heatmaps en alta resolución; `domain_leverage*.csv`; CSVs de cohesión.
- **Caveats:** **no rankear** coherencia (IC ≈ [−1,+1]) → aporte **tipológico**; "partido" no homogéneo entre canales → solo **6 partidos** casan en el cruce; concentración por pocas voces en partidos chicos del hemiciclo; *External Relations* descartado por bajo leverage; R² saturado es **cota superior**; BERTopic ~48 % outliers; muestras chicas (PCF 39, PS 79).

### Capítulo 5 — Discusión (`cap_discusion.tex`)

- **Secciones (existen):** Interpretación de los hallazgos · Validez del enfoque MARPOR + NLP · Limitaciones.
- **Contextos:** `party_analysis_context.md`, `ches_analysis_context.md`, `general_context.md` §9.
- **Figuras/tablas:** reutilizar las del Cap. 4; opcional Tabla 19 — síntesis de la tipología por celda. Sin figuras nuevas obligatorias.
- **A anexos:** deep-dives por partido (`01_`); casos canónicos (`03_`).
- **Caveats:** **sin causalidad**; desfase temporal/organizacional manifiesto↔voto; `demandeur` de enmiendas no controlado; énfasis (no signado) vs. soporte (signado) → no se restan, se comparan como firmas; la definición de bloque (UDI-Agir en oposición) subestima R² del bloque.
- **Nota de plantilla:** el manual marca Discusión como **optativa**; aquí se mantiene como capítulo propio (existe). Podría fusionarse en Resultados, pero **se recomienda mantenerla separada**.

### Capítulo 6 — Conclusiones (`conclu.tex`)

- **Secciones (existen):** Cumplimiento de los objetivos · Principales hallazgos · Contribuciones · Trabajo futuro.
- **Contextos:** `general_context.md` §6, §11, §12; frase de validación clave (ρ≈0,89).
- **Figuras/tablas:** ninguna obligatoria.
- **A anexos:** lista de mejoras pendientes (de §11 de `general_context.md`).
- **Caveats:** no sobre-vender hallazgos politológicos (n chico, modelo imperfecto); enmarcar el aporte como **metodológico y de sistema**.
- **Trabajo futuro (sin KG-Gen):** deduplicación de tweets, filtrado temporal del corpus de Twitter, control de `demandeur`, ponderación por diputado, calibración de probabilidades, extensión a otra legislatura/país. **No incluir KG-Gen** (fuera de alcance). El comentario de `conclu.tex` que aún menciona KG-Gen debe quitarse al redactar.

### Anexos (`anexoA.tex`)

- **Secciones (existen):** Detalle de los corpus y filtros · Taxonomía MARPOR (7 dominios / 56 categorías) · Validación del clasificador.
- **A añadir al redactar:** Reproducibilidad (orden de ejecución, dependencias, URLs/versiones de fuentes, credenciales `.env`); esquemas de columnas de tablas maestras; 13+13 códigos RILE; stop-words por dominio; parámetros y tiempos de cómputo; tablas/heatmaps completos de `party_analysis/`; 24 tópicos por corpus de BERTopic; `correlations.json` y reportes de validación.

---

## 7. Narrativa central de la memoria (2–3 párrafos)

En las democracias representativas persiste una pregunta difícil de responder con datos: ¿lo que los partidos *dicen* coincide con lo que sus representantes *hacen* al legislar? Esta memoria aborda el problema desde la ingeniería de datos y el procesamiento de lenguaje natural, tomando como caso la XV legislatura de la Asamblea Nacional francesa (2017–2022). El núcleo del trabajo es un **pipeline reproducible** que integra cinco arenas discursivas muy heterogéneas —programas electorales (MARPOR), tweets (capturados con Zeeschuimer), intervenciones en el hemiciclo (Regards Citoyens), y votos sobre leyes y enmiendas (open data de la Assemblée nationale + texto oficial de Légifrance/PISTE)— bajo una **cohorte única de 668 diputados** que ancla todos los cruces por un identificador estable. El aporte de ingeniería está en resolver la integración de fuentes en formatos dispares (JSON, XML, TSV, NDJSON, APIs OAuth y académicas) y en clasificar cinco corpus distintos con una **taxonomía común y citable** (MARPOR: 56 categorías / 7 dominios), por una vía supervisada (ManifestoBERTa, el núcleo) y otra exploratoria (BERTopic).

El sistema no se da por bueno sin evidencia: antes de interpretar nada, se **valida**. El clasificador supervisado se contrasta contra el ground truth humano de los manifiestos (`cmp_code`), reproduciendo la model card (top-1 58,3 %, top-3 82,0 %), y la posición izquierda-derecha estimada (RILE) se correlaciona con un benchmark externo de expertos (CHES 2019): con suficiente texto por partido (≥100 quasi-frases) la correlación llega a ρ≈0,89, dentro del rango de la propia codificación humana de MARPOR. Recién sobre esa base se ejecuta el análisis central, que contrasta la **agenda declarada** (de qué habla cada partido: énfasis, firma, concentración) con la **agenda revelada** por el voto (qué apoya o rechaza: soporte global, soporte relativo, cohesión Rice). Tres análisis encadenados articulan el arco: el canal cambia la agenda pero la firma distintiva persiste; el voto tiene dos capas (una posicional dominante gobierno/oposición y un clivaje cultural robusto que aflora en enmiendas); y la coherencia entre lo dicho y lo votado es débil pero localizada en banderas identitarias.

El resultado no es un ranking de "qué partido cumple más", sino un **aporte tipológico y metodológico**: un sistema reproducible que mide énfasis y soporte de forma comparable, validado externamente, y que muestra que la relación discurso–voto es localizada y multidimensional, no resumible en un eje izquierda-derecha. La memoria enfatiza el diseño del pipeline, las decisiones técnicas (cohorte única, dominios en vez de categorías para el voto, énfasis en vez de RILE, filtros de calidad alineados entre vías) y sus límites honestos (cobertura temporal de Twitter, modelo imperfecto y no calibrado, muestras pequeñas, ausencia de causalidad), dejando la lectura politológica como demostración de que el sistema produce señal interpretable.

---

## 8. Mapa de trazabilidad capítulo → contexto → carpeta (uso interno, no bibliografía)


| Capítulo (real)                                 | Contexto(s) principal(es)                                                                                                                                           | Carpeta(s) / outputs clave (solo trazabilidad)                                                                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Introducción                                  | `general_context.md` §1,§6,§12                                                                                                                                      | (visión global)                                                                                                                                                       |
| 2 Marco teórico                                 | `manifestos`, `manifestoberta_analysis`, `bertopic_analysis`, `ches_analysis`                                                                                       | conceptos MARPOR/RILE/CHES                                                                                                                                            |
| 3 Materiales y métodos (Datos + Implementación) | `datos_diputado`, `twitter_zeeschuimer`, `manifestos`, `lois_votes`, `hemicycle`, `manifestoberta_analysis`, `bertopic_analysis`, `ches_analysis`, `party_analysis` | `deputes_2017_2022.csv`, `manifesto_texts.csv`, `leyes_texto_oficial.csv`, votos, `interventions_*.csv.gz`; `common/*.py`, `*_runner.py`, `rile.py`; `*/scripts/*.py` |
| 4 Resultados (Validación + Análisis)            | `manifestoberta_analysis`, `ches_analysis`, `party_analysis`, `bertopic_analysis`                                                                                   | `validate_against_marpor.py`, `correlations.json`, `scatter_rile_vs_ches.png`; `01_`, `02_`, `03_` `.md` + `results/*.csv/png`                                        |
| 5 Discusión                                     | `party_analysis`, `ches_analysis`, `general_context.md` §9                                                                                                          | (interpretación)                                                                                                                                                      |
| 6 Conclusiones                                  | `general_context.md` §6,§11,§12                                                                                                                                     | (síntesis)                                                                                                                                                            |


---

## 9. Pendientes "por verificar" antes de redactar

(Solo quedan los genuinamente abiertos; lo demás está resuelto en §0.)

1. **CHES — versión a citar:** el dato usado es **CHES 2019** (`CHES2019V3.csv`); en el `.bib` están `jolly2022ches` (trend file 1999–2019) y `ches2019data`, además del `rovny2025ches` (2024, no usado). Confirmar cuál se cita en el texto (recomendado: 2019).
2. **Reproducibilidad:** centralizar fechas de descarga y versiones (`torch`/`transformers`, AN ZIP, twitter-parlementaires, PISTE, TSV del hemiciclo). Las entradas de fuentes en el `.bib` llevan "[fecha por verificar]".
3. **Deduplicación de tweets** (74.659 duplicados) y 632 tweets sin diputado: confirmar tratamiento en análisis.
4. `**party_analysis/` usa `deputes_an_rd.csv`** (no el consolidado con Twitter): verificar coherencia de `id`/grupos.
5. `**results/` no versionados:** decidir más adelante si se anexan regenerados o se citan tablas de README (cuando se necesiten las imágenes).
6. **n de validación** ManifestoBERTa: 3.430 utilizables vs. 3.801 — documentar criterio de descarte de `cmp_code`.
7. **Datos MARPOR `MPDS2025a`:** verificar lista exacta de autores, versión y DOI de la cita `marpor_mpds2025a`.
8. **Título de portada:** decidir si se mantiene el registrado o se actualiza hacia el enfoque de ingeniería (con profesores guía y Biblioteca).

---

## 10. Referencias oficiales (estado de `bibliografia.bib`)

Las citas internas a carpetas/scripts/outputs **no son bibliografía**: se usan solo como trazabilidad/reproducibilidad. La bibliografía oficial corresponde a literatura, datasets, modelos, herramientas y fuentes oficiales. Estado actual de `bibliografia.bib`:

**Métodos y modelos:** `marpor_mp_v5`, `manifestoberta2024`, `conneau2020xlmr` (XLM-RoBERTa), `grootendorst2022bertopic`, `reimers2019sentencebert`.
**Benchmarks de validación:** `laver1992party` (RILE), `rovny2025ches` (CHES 2024), `jolly2022ches` + `ches2019data` (CHES 2019, el usado).
**Literatura teórica:** `ivanusch2024channels`, `sieberer2006partyunity`, `carey2007competing`, `barriere2022cofe`, `barriere2023multilingual`, `schwartz2012overview`, `graham2013moral`.
**Antecedentes (datos/grafos parlamentarios):** `hyvonen2023parliamentsampo`, `plenz2024pakt`.
**Índices y métodos estadísticos:** `rice1928quantitative` (cohesión Rice), `shannon1948mathematical` (entropía/evenness).
**Fuentes de datos oficiales y datasets:** `an_opendata_xv`, `legifrance_piste`, `marpor_mpds2025a`, `regardscitoyens_twitter`, `regardscitoyens_nosdeputes`, `peeters2022zeeschuimer`, `ches2019data`.
**Librerías y herramientas:** `wolf2020transformers`, `paszke2019pytorch`, `pedregosa2011scikit`, `mcinnes2018umap`, `mcinnes2017hdbscan`, `harris2020numpy`, `mckinney2010pandas`, `virtanen2020scipy`.
**Fuera de alcance (comentado, no citar):** `mo2025kggen` (KG-Gen).

> Varias entradas de fuentes/datasets llevan campos "[fecha por verificar]" o "(por verificar)"; completar antes de la entrega.

