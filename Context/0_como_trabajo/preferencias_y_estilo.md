# Contexto de trabajo — Tesis Agustín Solís (handoff para otro chat)

> Documento para pasar a un chat nuevo y que retome el trabajo sin perder contexto.
> Cubre: quién soy y cómo pido las cosas, mis preferencias y lo que corrijo,
> qué hemos hecho, y la estructura/lógica del repositorio.
> Para el detalle técnico del proyecto empírico ver `memoria/context/general_context.md`
> (síntesis completa) y `french_deputies/ESTRUCTURA.md`. Para el estilo LaTeX ver
> `memoria/manual/Manual-de-normalizacion.md`.

---

## 1. Quién soy y qué es esto

- Soy **Agustín Solís Meza**, estudiante de **Ingeniería Civil en Computación (FCFM, Universidad de Chile)**.
- Estoy terminando mi **memoria/tesis** (en **español**), escrita en **LaTeX** con la clase **`umemoria`** de la FCFM.
- Tema: **discurso vs. voto de los diputados franceses en la XV legislatura (2017–2022)**. Contrasto la **agenda declarada** (manifiestos, tuits, intervenciones en el hemiciclo) con la **agenda revelada** por el voto (leyes y enmiendas), clasificando todo con la taxonomía **MARPOR** (56 categorías / 7 dominios).
- La tesis **ya fue aprobada** por la comisión. Estoy en la fase final: **implementar los comentarios finales** de los evaluadores y luego **subir el PDF a la biblioteca** de la universidad. Después viene la **presentación/defensa** ante la comisión y mis profes guía (**primeras semanas de octubre de 2026**).
- Repositorio local: **`/Users/agustin.solis/Tesis`** (es un repo git; trabajo también en **Overleaf** sincronizado).

### Personas relevantes
- **Valentin Barriere** — profesor **guía**. Da feedback por "lotes"; suele responder corto ("All very good!"). Sugirió mover la contribución de computación a la introducción y advirtió: *hay que dominar lo escrito para la defensa* (si no sé responder algo, pensarán que es generado por IA y baja la nota).
- **Franziska Wagner** — profesora **co-guía**. Mirada desde ciencia política (agenda-setting, issue ownership, CHES). Sugiere conectar las contribuciones con los objetivos y mencionar en la defensa los cambios incorporados del feedback.
- **Comisión evaluadora:** **Claudio Gutiérrez** (nota 6.8) y **Nicolás Varas** (6.8). Guía Valentin (7) y co-guía Franziska (7).
- **César** — colaborador (proyecto INA/INRIA/SciencePo). Le comparto scripts y datos.

---

## 2. Cómo pido las cosas y cómo me gusta trabajar (IMPORTANTE)

Esto es lo que más quiero que un chat nuevo respete.

### Cómo escribo
- Escribo en **español, informal y directo**, a menudo **con typos y sin tildes** (p. ej. "dijieron", "correcion", "esxplicame", "haz", "coguia", "profesor guia", "porfa"). **No** hace falta que me corrijas la ortografía de mis mensajes; entiende la intención y sigue.
- Cuando redacto **mensajes o correos** a mis profes, los escribo en **inglés**. Puedo pegar textos largos (feedback, hilos de Slack) para que los uses de contexto.
- A veces pego bloques de LaTeX o de tablas directo en el chat para señalar qué tocar.

### Cómo quiero que trabajes
- **Para cambios no triviales: primero el plan, sin ejecutar.** Me gusta pedir *"dime exactamente qué cambiarías, dónde y cómo, antes de hacerlo"*. Frases típicas mías: "ayudame primero dandome que cambiar (sin hacerlo)", "que editamos... donde y como antes de hacer nada". **Muéstrame el plan (qué archivo, qué sección, qué texto propuesto) y espera mi OK.**
- **Me gusta elegir entre opciones.** Cuando hay alternativas (p. ej. "opción A textual" vs "opción B hacer el experimento"), preséntalas claras y dejo que yo elija ("prefiero A", "haz la opción de condensarlo").
- **Cambios quirúrgicos y aditivos, NO rehacer cosas grandes.** Repito mucho *"intentando no rehacer nada grande"*. Prefiero agregar/ajustar párrafos puntuales antes que reescrituras masivas. La tesis ya está madura: no la desarmes.
- **Después de editar, explícame claro y en detalle**: qué cambiaste, **dónde quedó** (archivo + sección), y por qué. Frase típica: *"explícame claro que editaste y agregaste donde quedo y todo"*.
- **Rigor científico absoluto.** **Nunca inventes cifras**, resultados ni referencias. Si hay que verificar un número, verifícalo contra los datos/CSV o dímelo. Me gusta que las afirmaciones sean modestas y con sus salvedades (la tesis evita sobre-afirmar; cada hallazgo lleva su cautela).
- **Consistencia.** Me molesta la inconsistencia (p. ej. nombres de dominio a medias en inglés/español, rutas de carpeta mal escritas). Cuando arreglo algo, quiero que quede consistente **en toda la tesis**.
- **Tono de tesis serio.** Si algo "suena poco serio / poco de tesis", lo quiero más formal (ej.: reescribí el inicio del resumen porque "sonaba muy poco serio").
- **Verifica antes de cerrar.** Me gusta que compiles/revises referencias cruzadas, que no queden `\ref` rotas, y que confirmes que no cambiaron cifras (p. ej. comparar tokens numéricos contra el estado anterior).
- No me molesta que uses subagentes/paralelismo para tareas grandes, siempre que **preserves los hechos** y luego **verifiques**.
- **Solo hago commit cuando lo pido explícitamente.** No commitees por tu cuenta.

---

## 3. Convenciones de estilo de la memoria (LaTeX)

Fuente autoritativa: `memoria/manual/Manual-de-normalizacion.md`. Lo esencial que aplico:

- **Idioma español**, clase `umemoria` (FCFM). Compilo en Overleaf.
- **Coma decimal** en números, escrita en modo matemático como `$-21{,}9$`, `$0{,}44$` (el `{,}` evita el espacio raro del babel-spanish).
- **Incisos con `--`** (raya corta), **no** em-dash (`—`) ni guiones largos. Ej.: `texto --inciso-- texto`.
- **Énfasis con `\emph{...}`**; negrita con `\textbf{...}` para conceptos clave.
- **Referencias**: `Cuadro~\ref{...}` para tablas, `Figura~\ref{...}`, `sección~\ref{...}`, `capítulo~\ref{...}`, `anexo~\ref{...}`. Citas con `\cite{...}`.
- **Comillas** estilo español; se normalizaron a `` `` '' `` (se sacaron las « » latinas).
- **Nombres de dominio MARPOR en español** en todo el cuerpo (ver §5). Los **nombres de categoría** del handbook MARPOR se dejan en **inglés** (nomenclatura estándar internacional), y así está aclarado en el anexo.
- **Tablas**: se definieron tipos de columna `Y`, `Z`, `W` (tabularx) **una sola vez en el preámbulo de `main.tex`** — NO redefinirlos dentro de floats (eso rompía la compilación con "Illegal pream-token").
- No agregar comentarios de código LaTeX que narren el cambio; nada de emojis salvo que lo pida.

---

## 4. Estructura del repositorio

```
/Users/agustin.solis/Tesis
├── README.md                      # README raíz del repo (proyecto de datos)
├── REFERENCIAS.md
├── Context.md                     # ESTE documento (contexto conversacional)
├── memoria/                       # LA TESIS (LaTeX)
│   ├── main.tex                   # preámbulo, portada, resumen (\begin{resumen}), agradecimientos
│   ├── intro.tex                  # Introducción (incluye Declaración de uso de IA)
│   ├── cap_marco_teorico.tex
│   ├── cap_metodologia.tex
│   ├── cap_resultados.tex
│   ├── cap_discusion.tex
│   ├── conclu.tex                 # Conclusiones (Contribuciones, Trabajo futuro)
│   ├── anexoA.tex                 # Anexos (taxonomía MARPOR, validación, BERTopic, ejemplos tuits)
│   ├── bibliografia.bib
│   ├── imagenes/                  # figuras (heatmaps, scatters)
│   ├── manual/Manual-de-normalizacion.md   # reglas de estilo
│   ├── context/                   # 9 contextos de módulo + general_context.md
│   └── propuesta/                 # "Propuesta Memoria .pdf" y "Propuesta_Memoria.txt" (propuesta original)
└── french_deputies/               # TODO el trabajo empírico (datos + análisis)
    ├── README.md, ESTRUCTURA.md
    ├── datos_diputados/           # cohorte única -> processed/deputes_2017_2022.csv (668 diputados)
    ├── twitter_zeeschuimer/       # captura de tuits (Zeeschuimer) + merge con cohorte
    ├── lois_votes/                # leyes+enmiendas (open data AN + Légifrance/PISTE) + votos
    ├── hemicycle/                 # intervenciones del hemiciclo (Regards Citoyens, ND15)
    ├── manifestos/                # manifiestos 2017 (MARPOR API)
    ├── bertopic_analysis/         # topic modeling NO supervisado (5 corpus)
    ├── manifestoberta_analysis/   # clasificación supervisada MARPOR (núcleo)
    ├── ches_analysis/             # validación RILE vs CHES 2019
    ├── party_analysis/            # 3 análisis: declarada / revelada / cruce
    └── kg-gen/                    # demo experimental acotado (LLM local), fuera del pipeline
```

- **Lógica del pipeline:** `datos_diputados/` (cohorte, clave `id`) → {tweets, manifiestos, hemiciclo, leyes/enmiendas} → {BERTopic, ManifestoBERTa} → {ches_analysis, party_analysis}. Nada aguas abajo funciona sin la cohorte ni sin `predictions.csv`.
- **Los `results/` grandes NO se versionan** (se regeneran con los scripts). Las cifras canónicas viven embebidas en los README.
- Detalle completo: `memoria/context/general_context.md` (§2 arquitectura, §3 corpus, §7 resultados, §8 decisiones, §9 limitaciones).

---

## 5. Hechos clave del proyecto (para no equivocarse)

- **Cohorte:** 668 diputados. **FN/RN** se trata como **familia analítica propia** (override por 11 `deputy_id`), **separada del residuo NI** (NI NO es proxy de FN/RN).
- **7 partidos comparables** en el cruce declarado–revelado: LFI, PS, PCF (grupo GDR-PCF en voto), MoDem, LREM, LR y **FN**.
- **MARPOR:** 56 categorías, 7 dominios. **Nombres de dominio en español (canónicos en la tesis):**
  1. Relaciones exteriores · 2. Libertad y democracia · 3. Sistema político · 4. Economía · 5. Bienestar y calidad de vida · 6. Tejido social · 7. Grupos sociales.
- **Modelos:** **ManifestoBERTa** (`manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1`, sobre XLM-RoBERTa-large; transferencia directa, sin reentrenar) = núcleo supervisado. **BERTopic** (MiniLM + UMAP + HDBSCAN + c-TF-IDF, 24 tópicos/corpus) = exploratorio. Validación externa con **RILE vs CHES 2019**.
- **Validación del clasificador (contra `cmp_code` humano de manifiestos):** top-1 **58,3 %**, top-3 **82,0 %**, dominio **70,3 %**, macro F1 **0,44**.
- **Tamaños de corpus NLP:** manifiestos 3.801 · enmiendas 2.575 · leyes 23.267 párrafos · tuits ~222.644 (BERTopic) / 224.466 (ManifestoBERTa) · intervenciones 338.192.
- **Cautela conocida:** el corpus de tuits capturado excede la legislatura (llega a ~2026); es una limitación reconocida. La calidad del clasificador en tuits se **asume por transferencia**, no se mide directamente.

---

## 6. Qué hemos hecho (historial del trabajo)

Arco general de las sesiones, de más viejo a más nuevo:

1. **Auditoría y reescritura por lotes** de Metodología, Resultados y Discusión según feedback de Valentin (guía) y Franziska (co-guía): resúmenes de capítulo más claros, tecnicismos movidos a anexos, tablas de corpus, límites de validación, orígenes de métricas citados, tabla-resumen de métricas.
2. **Declaración de uso de IA** integrada en la introducción (modelos usados, metodología de uso, ejemplos de prompts, "qué cambiaría").
3. **Respuestas a 6 ítems de feedback** sobre agenda declarada/revelada y cruce: ejemplos reales de tuits por partido (con reconocimiento de la limitación out-of-domain), interpretación de la inversión leyes↔enmiendas, si las enmiendas comparten dominio MARPOR con su ley madre, glosario de jerga (*scrutin*, bootstrap, estabilidad de signo), eliminación de columnas redundantes, y marco teórico modesto (citas `carey2007competing`, `sieberer2006partyunity`). Se añadieron tuits originales en francés **con traducción al español** en el cuerpo y en una tabla del anexo.
4. **Traducción de nombres de dominio MARPOR al español** en toda la tesis (tablas `tab:clivaje-ci`, `tab:cruce-casos`, prosa de `cap_resultados`, `cap_discusion`, `anexoA`; matriz de confusión). Se dejó explícito que los **dominios van en español** y las **categorías del handbook en inglés**.
5. **Comentarios finales de la comisión (tesis ya aprobada)** — cambios pequeños y específicos:
   - **Claudio Gutiérrez:** hacer explícita la **contribución desde la computación** (qué hizo un ingeniero que no haría un cientista político, pero **sin decirlo explícitamente**: destacando el trabajo concreto — pipeline, resolución de entidades, transferencia de dominio, validación).
   - **Nicolás Varas (a):** **justificar la elección del modelo** (ManifestoBERTa a nivel de cuasi-frase sobre su variante *context* y sobre LLMs generativos; solo el supervisado es comparable directamente contra el código humano MARPOR). Corto y claro, en `cap_metodologia.tex` §3.3.2.
   - **Nicolás Varas (b):** **limitación de la transferencia a tuits** — decir explícitamente que la calidad en tuits se **asume, no se mide**, y proponer como validación futura **una muestra pequeña anotada a mano por arena** (elegí la **opción A: textual**, no hacer el experimento). En `cap_resultados.tex` §4.1.3 (`sec:res-val-alcance`) + Trabajo futuro en `conclu.tex`.
   - **Franziska y Valentin:** solo elogios, sin correcciones.
   - **Resumen (abstract):** reescribí el inicio para que suene más de tesis. Quedó: *"Los partidos políticos comunican sus prioridades por múltiples canales de información: las escriben en sus programas electorales, las defienden en el hemiciclo y las difunden en redes sociales. Esa agenda declarada, sin embargo, no siempre coincide con la que sus representantes revelan al votar cuando legislan."* (en `main.tex`, `\begin{resumen}`).
6. **Feedback de los guía sobre esos cambios** (implementado):
   - **Valentin:** mover la definición de la contribución de computación a la **introducción** (al presentar las contribuciones, con el dominio CS al frente).
   - **Franziska:** conectar las contribuciones con los **objetivos**.
   - Se hizo: **(A)** párrafo nuevo de contribuciones en `intro.tex` (tras la apertura, antes de "Contexto y motivación"), con la contribución **de ingeniería primero** y la **analítica** segunda, remitiendo a `\ref{sec:concl-contribuciones}`. **(B)** frase de enlace en Objetivos específicos: *"Los objetivos específicos concretan la contribución computacional del trabajo:"*. **(C)** se **condensó** el párrafo equivalente en `conclu.tex` §Contribuciones para no duplicar, remitiendo a `\ref{cap:introduccion}`.
7. **Mejora general de la documentación de `french_deputies/`** (19 README + README raíz) vía subagentes, con reglas estrictas de **no tocar ninguna cifra/ruta/comando**: tono técnico y directo (se quitó el tono de "diario personal"), acentos corregidos en los README de `bertopic_analysis/` y `manifestoberta_analysis/` (estaban sin tildes), estructura consistente, y **bugs de rutas** arreglados:
   - `francia_deputies/` → **`french_deputies/`** (nombre real).
   - `zeeschuimer/` → **`twitter_zeeschuimer/`** (en comandos/árboles).
   - referencias a la propuesta en la raíz → ahora en **`memoria/propuesta/`**; la tesis final está en **`memoria/`**.
   - Verificado: los multiconjuntos de tokens numéricos quedaron **idénticos** al estado previo (ninguna cifra cambió) y el conteo de filas de tabla se preservó.
   - Pendiente opcional que ofrecí: dejar consistentes también los comentarios/rutas dentro de los **scripts `.py`** (aún tienen `francia_deputies/`/`zeeschuimer/`).
8. **Mensajes a los profes (en inglés)** redactados en el chat: uno anunciando la implementación del feedback de la comisión y pidiendo el "go-ahead" para subir a biblioteca (con link de Overleaf y los formularios de evaluación adjuntos).

---

## 7. Estado actual y próximos pasos

- La tesis está **aprobada**; ya **implementé los comentarios de la comisión** y el **follow-up de los guía** (contribuciones en intro + objetivos + conclusión condensada).
- **Falta:** el **go-ahead final** de Valentin y Franziska para **subir el PDF a la biblioteca** (Ucampus). Luego **defensa en octubre de 2026**.
- Para la **defensa**: (i) dominar a fondo lo escrito (advertencia de Valentin), (ii) mencionar los cambios incorporados del feedback (sugerencia de Franziska).
- Tareas opcionales abiertas: consistencia de rutas en los scripts `.py`; reforzar el objetivo general con "contribución computacional" si lo pido.

---

## 8. Cómo debe comportarse el próximo chat (resumen operativo)

- Habla en **español**, claro y directo. No corrijas mis typos; entiende y avanza.
- Para cambios de la tesis: **propón el plan (archivo + sección + texto) y espera mi OK** antes de editar; hazlo **quirúrgico y aditivo**, sin rehacer nada grande.
- **Nunca inventes cifras/resultados**; verifica y avísame de inconsistencias. Mantén el tono formal de tesis y la **consistencia** en toda la memoria.
- Respeta las **convenciones LaTeX** (§3): coma decimal `{,}`, incisos `--`, `\emph`/`\textbf`, refs `Cuadro~/Figura~/sección~/\cite`, dominios MARPOR en español / categorías en inglés.
- Al terminar, **explica claro qué cambiaste y dónde quedó**, y verifica referencias cruzadas.
- **No commitees** salvo que lo pida explícitamente.
- Para el detalle del proyecto empírico, apóyate en `memoria/context/general_context.md` y en los README de cada módulo.
