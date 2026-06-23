# Resumen global del proyecto

> Síntesis integradora de los 9 contextos de `context/`: `datos_diputado`, `twitter_zeeschuimer`, `manifestos`, `lois_votes`, `hemicycle`, `bertopic_analysis`, `manifestoberta_analysis`, `ches_analysis`, `party_analysis`. Todas las cifras provienen de esos contextos; lo no documentado se marca **(por verificar)**.

---

## 1. Propósito general del proyecto

El proyecto estudia la **agenda temática de los partidos de la XV legislatura francesa (2017–2022)** observándolos en **cinco arenas discursivas distintas**: el programa electoral (manifiestos 2017), la comunicación en redes (tweets), el debate parlamentario (hemiciclo), y el voto nominal sobre **leyes** y **enmiendas**. La pregunta central, que articula `party_analysis/`, es doble:

1. **¿De qué habla cada partido y cómo cambia su agenda según el canal?** (agenda **declarada** = énfasis temático).
2. **¿Lo que un partido *dice* coincide con lo que *vota*?** (contraste agenda declarada vs. agenda **revelada** por el voto).

El problema **político** es caracterizar *issue ownership*, coherencia discurso-voto y clivajes (cultural vs. económico) sin reducir a los partidos a un eje izquierda-derecha. El problema **computacional/ingenieril** es construir un pipeline reproducible que (a) integre fuentes heterogéneas (open data parlamentario JSON/XML, API académica, captura de tráfico web, API legal OAuth) bajo una **cohorte única de diputados**, (b) clasifique cinco corpus muy distintos con una **taxonomía temática común y citable** (MARPOR), y (c) agregue a nivel partido con métricas robustas y validadas externamente. La posición izquierda-derecha **no** es el objeto: se usa solo para **validar** el pipeline (`ches_analysis/`).

---

## 2. Arquitectura general del pipeline

Flujo de extremo a extremo, de datos brutos a figuras:

```
(1) FUENTES BRUTAS                         (2) ETL / CORPUS                          (3) CLASIFICACIÓN          (4) ANÁLISIS
─────────────────────                      ──────────────────────────               ─────────────────         ──────────────────────
AN open data (acteurs JSON) ┐
twitter-parlementaires CSV  ┴─► datos_diputados/ ─► deputes_2017_2022.csv (cohorte, id)
                                                   │  (clave id / political_group_abbrev)
Zeeschuimer .ndjson ───────────► twitter_zeeschuimer/ ─► tweets_text_only.csv ──┐
MARPOR API ────────────────────► manifestos/ ─► manifesto_texts.csv (cmp_code) ─┤
AN Scrutins/Dossiers/Amend. ┐                                                   ├─► bertopic_analysis/  (no superv.)
Légifrance PISTE (texto) ───┴──► lois_votes/ ─► leyes_texto_oficial.csv,        ├─► manifestoberta_analysis/ ─► predictions.csv ─┐
                                              amendements_votos_con_texto.csv,  │      (56 cat. / 7 dominios MARPOR)             │
                                              votos_*_por_diputado.csv ─────────┤                                                │
Regards Citoyens TSV (ND15) ───► hemicycle/ ─► interventions_xv_*.csv.gz ───────┘                                                │
                                                                                                                                 ▼
                                                                                          ches_analysis/  (valida RILE vs CHES 2019)
                                                                                          party_analysis/ (3 análisis: declarada,
                                                                                                           revelada, cruce)
                                                                                                 │
                                                                                                 ▼
                                                                                          CSV + JSON + heatmaps/scatters
```

- **Fuentes de datos:** open data Assemblée nationale (diputados, scrutins, dossiers, enmiendas), Regards Citoyens (twitter-parlementaires + intervenciones del hemiciclo), MARPOR API (manifiestos), Légifrance/PISTE (texto oficial de leyes), captura Zeeschuimer (tweets).
- **Preprocesamiento / ETL:** parseo JSON/XML/TSV/NDJSON, limpieza HTML y de URLs, *entity linking* determinístico (por nombre o por `twitter_handle`/`id`), fuzzy matching scrutin↔dossier↔enmienda.
- **Segmentación / unidad textual:** quasi-frase (manifiestos), tweet, intervención (turno de palabra), párrafo de ley, enmienda.
- **Filtros:** ≥10 palabras (salvo manifiestos, que usan la quasi-frase nativa), exclusión de habla procedimental (hemiciclo), umbrales de confianza de match (`texto_confianza`/`match_confianza`).
- **Clasificación temática:** dos vías paralelas — **BERTopic** (no supervisado, descubre tópicos) y **ManifestoBERTa** (supervisado, asigna categorías MARPOR citables).
- **Agregación:** distribuciones por dominio/categoría a nivel partido; soporte y cohesión a nivel voto.
- **Análisis:** por **canal** (cross-channel), por **voto** (leyes vs. enmiendas), y el **cruce declarada–revelada**; más la **validación externa** (CHES).
- **Salidas:** CSV, JSON, heatmaps y scatters por módulo (`results/`).

---

## 3. Fuentes de datos y corpus

| Fuente / corpus | Qué representa | Unidad textual | Filtros documentados | Tamaño (según contextos) | Rol en la tesis |
|---|---|---|---|---|---|
| **Cohorte** (`datos_diputados/`) | identidad oficial de los diputados XV + handle de Twitter | — (tabla maestra) | grupo `GP` que solapa 2017-06-18 – 2022-06-21 | **668 diputados**, 587 con `twitter_handle` (87,9 %), 18 grupos | ancla de identidad (`id`, `political_group_abbrev`) para todos los cruces |
| **Manifiestos** (`manifestos/`) | programa electoral 2017 (agenda declarada en campaña) | quasi-frase MARPOR | sin filtro de longitud (unidad nativa) | **10 partidos, 3.801 quasi-frases**; cobertura 628/668 (94 %) | corpus declarado **y único con ground truth humano** (`cmp_code`) |
| **Tweets** (`twitter_zeeschuimer/`) | comunicación pública en redes | tweet | ≥10 palabras tras limpieza | ~244.876 ítems (244.244 con diputado; 170.217 `tweet_id` únicos); 533/587 cuentas capturadas; NLP ≈ 222.644 (BERTopic) / 224.466 (ManifestoBERTa) | canal declarado "comunicativo" |
| **Hemiciclo** (`hemicycle/`) | intervenciones en sesión (compte rendu ND15) | intervención (turno) | `deputy_id` + ≥10 palabras + no procedimental | **949.718 intervenciones**, 661.690 con diputado (70 %), 646 diputados; **338.192 docs NLP** | canal declarado "institucional" |
| **Leyes** (`lois_votes/`, rama leyes) | adopción de texto completo + texto JORF | párrafo de ley | `texto_confianza = alta`, ≥10 palabras | **373 scrutins** de adopción (212 dossiers); 78.116 votos; NLP ≈ 23.267 párrafos; **335** con texto+votos en `party_analysis` | agenda revelada (voto final) |
| **Enmiendas** (`lois_votes/`, rama enmiendas) | voto sobre cambios propuestos | enmienda (`dispositif`+`expose_sommaire`) | `match_confianza` alta/media, ≥10 palabras | **3.126 scrutins**; 297.574 votos; **2.575** con texto en análisis | agenda revelada (voto granular) |

Las cinco fuentes textuales (manifiestos, tweets, hemiciclo, leyes, enmiendas) son las que clasifican BERTopic y ManifestoBERTa. **No se inventan tamaños:** los valores anteriores están en los contextos respectivos.

> **Nota de cobertura temporal:** el corpus de tweets capturado con Zeeschuimer llega hasta ~feb. 2026 (timeline reciente), **excede la legislatura 2017–2022** — limitación señalada en `twitter_zeeschuimer` y `manifestoberta_analysis`.

---

## 4. Modelos y métodos computacionales

**Clasificación temática (dos enfoques complementarios sobre los mismos 5 corpus):**

- **ManifestoBERTa** (`manifestoberta_analysis/`): modelo preentrenado `manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` (base `xlm-roberta-large`, 560 M params, ~2,2 GB), aplicado **sin reentrenamiento** (transfer directo). Tokenización a `max_length=200`, inferencia batch (`torch.inference_mode`, softmax sobre 56 logits), device MPS→CUDA→CPU. Salida: top-1/2/3 (label+código+prob) + dominio (primer dígito) por documento → `predictions.csv`. Es el **núcleo citable** que alimenta `party_analysis/` y `ches_analysis/`.
- **BERTopic** (`bertopic_analysis/`): pipeline no supervisado unificado en `common/bertopic_runner.py` — embeddings `paraphrase-multilingual-MiniLM-L12-v2` (384-D), reducción UMAP, clustering HDBSCAN, etiquetado c-TF-IDF + `KeyBERTInspired`, `CountVectorizer` con stop-words de dominio (FR/legal/hemiciclo/Twitter), **reducción post-hoc a 25 (→24 finales) tópicos** por fuente. Es el análisis **exploratorio**; descubre agrupaciones empíricas, no categorías teóricas.

**Taxonomía:** esquema **MARPOR** (Manifesto Project): **56 categorías** y **7 dominios** macro (1 External Relations, 2 Freedom & Democracy, 3 Political System, 4 Economy, 5 Welfare & QoL, 6 Fabric of Society, 7 Social Groups).

**Validación posicional (`ches_analysis/`):** índice **RILE** (Laver & Budge, 1992; 13+13 categorías) calculado desde las predicciones, correlacionado (Pearson + Spearman) contra el **Chapel Hill Expert Survey (CHES) 2019** (`lrgen`), benchmark externo de expertos.

**Métricas de agregación (`party_analysis/`):**
- **Énfasis / distintividad:** % de quasi-frases por dominio/categoría; distintividad = desviación vs. promedio del corpus (pp); **concentración** = entropía normalizada (*evenness*).
- **Voto:** **soporte global** (%Pour sobre expresados), **cohesión (índice Rice)** `|Pour−Contre|/(Pour+Contre)`, **soporte por tema** (ponderado por composición MARPOR del texto) y **soporte relativo** (centrado por la base del partido).
- **Comparación entre canales:** distancia **euclídea** (shift bruto vs. específico), **persistencia de firma** (correlación de vectores-firma).
- **Descomposición de poder explicativo:** **R² ponderado** de 4 modelos anidados (bloque / partido / +dominio / partido×dominio), WLS con dummies.
- **Robustez:** **bootstrap** multinomial (firmas) y por **clúster/scrutin** (clivaje del voto); IC95 y estabilidad de signo.

**Herramientas:** Python 3, `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`/`plotly`, `torch`+`transformers`, `sentence-transformers`, `bertopic`, `requests`, `rapidfuzz`/`difflib`, `zipfile`/`xml.etree`. **KG-Gen** se referencia (`hemicycle` y muestra `interventions_xv_sample5000.csv`) pero **no tiene contexto propio entre los 9** → su alcance y resultados están **(por verificar)**.

---

## 5. Módulos principales y cómo se conectan

**A. Extracción y preparación de datos (la "capa de corpus")**
- `datos_diputados/` — produce `processed/deputes_2017_2022.csv`, la **cohorte única**. Scripts: `fetch_an_15e_deputes.py`, `build_deputes_twitter_csv.py`, `merge_deputes_2017_2022.py`. Es el **primer eslabón**: su `id` y `political_group_abbrev` se reutilizan en todos los demás módulos.
- `twitter_zeeschuimer/` — captura (Zeeschuimer + autoscroll) y `merge_zeeschuimer_with_deputies.py` → `tweets_text_only.csv`.
- `manifestos/` — `download_manifestos.py` (API MARPOR) → `manifesto_texts.csv` (+ `group_to_party_mapping.csv`, `party_positions.csv`).
- `lois_votes/` — el módulo de ingeniería de datos más complejo: 9 scripts, dos ramas (leyes vía PISTE; enmiendas vía XML AN) → `leyes_texto_oficial.csv`, `amendements_votos_con_texto.csv`, `votos_*_por_diputado.csv`.
- `hemicycle/` — `build_interventions_with_deputies.py` → `interventions_xv_2017_2022_*.csv.gz`.

**B. Clasificación temática (la "capa de etiquetado")**
- `manifestoberta_analysis/` (supervisado, MARPOR) y `bertopic_analysis/` (no supervisado). Ambos consumen las **mismas tablas finales** con **filtros alineados** para comparabilidad doc-a-doc. La salida `predictions.csv` de ManifestoBERTa es la entrada de los análisis posteriores.

**C. Validación externa**
- `ches_analysis/` — `common/rile.py`, `common/ches.py`, `manifestos/run.py`; compara RILE (modelo/humano/oficial) vs. CHES 2019.

**D. Análisis principal (la "capa de hallazgos") — `party_analysis/`**
- Motores reutilizables: `common/analysis.py` (énfasis) y `common/votes.py` (voto).
- Por corpus: `manifestos/`, `tweets/`, `interventions/` (declarada); `lois/`, `amendements/` (revelada).
- Transversales: `cross_channel/build.py` (+`01_canal_cambia_agenda.md`), `agenda_revelada/build.py` (+`02_voto_dos_capas.md`), `declarado_vs_revelado/build.py` (+`03_declarado_vs_revelado.md`).

**Cadena de dependencias:** `datos_diputados/` → {tweets, manifiestos, hemiciclo, leyes/enmiendas} → {BERTopic, ManifestoBERTa} → {`ches_analysis/`, `party_analysis/`}. Nada aguas abajo funciona sin la cohorte y sin `predictions.csv`.

---

## 6. Lógica de investigación

El proyecto se lee como un arco en tres movimientos, sostenido por una capa de validación:

1. **Construcción y etiquetado.** Las 5 fuentes se normalizan a una cohorte común y se etiquetan con MARPOR (ManifestoBERTa) y se exploran con BERTopic. Pregunta: *¿de qué se habla en cada superficie?*
2. **Validación del pipeline (`ches_analysis/`).** Antes de interpretar, se comprueba que las posiciones estimadas desde texto correlacionan con un benchmark externo de expertos (CHES). Pregunta: *¿el método mide lo que dice medir?* Solo se valida sobre manifiestos (único canal con `cmp_code`).
3. **Análisis declarado (`party_analysis/` Análisis 1).** Se mide el énfasis y la firma de cada partido y cómo cambian entre canales. Pregunta: *¿un partido habla igual en su programa, en Twitter y en el hemiciclo?*
4. **Análisis revelado (Análisis 2).** Se mide qué apoya/rechaza cada partido al votar leyes y enmiendas. Pregunta: *¿el voto revela tema o solo posición gobierno/oposición?*
5. **El cruce (Análisis 3).** Se conectan ambas agendas: la **declarada** (salience, no signada) y la **revelada** (soporte, signada). Como viven en unidades distintas, no se restan: se comparan como firmas relativas y se construye una **tipología por celda** (partido × dominio). Pregunta: *¿votan lo que dicen?*

Así, **declarada** y **revelada** son las dos caras del mismo partido; CHES valida el instrumento; BERTopic ofrece la lectura exploratoria; y la comparación cruzada (canales, partidos, votos, temas) es el aporte central.

---

## 7. Resultados principales

**Validación (CHES, `ches_analysis/`):** el cálculo de RILE es correcto (techo humano vs. CHES ρ=0,76, en rango de literatura). El modelo reproduce la codificación humana al agregar por partido (ρ=0,79) pese a accuracy por-frase ~58 %. La validación externa sube de ρ=0,38 (n=8, arrastrada por PCF de 39 frases) a **ρ≈0,89** restringiendo a partidos con ≥100 quasi-frases.

**Clasificación (ManifestoBERTa):** validada contra `cmp_code` humano de manifiestos — **top-1 58,3 %, top-3 82,0 %, dominio 70,3 %, macro F1 0,44** (consistente con la model card). Top-1 dominante por fuente: manifiestos 504 Welfare; enmiendas Welfare 43 % + Economy 16 %; leyes 303 Eficiencia (lenguaje JORF); tweets 305 Autoridad 26,5 %; intervenciones 305 Autoridad 27 %.

**El canal define la agenda (Análisis 1):** manifiestos = *programa* (domina Welfare & QoL); tweets y hemiciclo = *meta-política* (domina Political System, 30–41 %). El efecto canal pesa 13–17 pp para todos. Descontado, **LFI** reorganiza más su firma (shift específico 14,4; persistencia 0,02 = megáfono anti-gobierno en Twitter) y **LREM** la mantiene (5,7; persistencia 0,557). Pero la **firma distintiva persiste** (issue ownership: ecologistas→ambiente, PCF→trabajadores, RN/NI→ley y orden).

**El voto tiene dos capas (Análisis 2):** el eje se **invierte** leyes↔enmiendas (LREM 99,1 %→15,7 %; LFI 11,5 %→83,7 %). En leyes el binario mayoría/oposición ya explica R²=0,47; en enmiendas todo explica menos (0,33) y el tema como dominio dominante casi no añade varianza (+1 pp). Pero aparece un **clivaje cultural robusto** en el soporte relativo de enmiendas: la izquierda apoya *de menos* *Fabric of Society* (PS −21,9, GDR-PCF −17,5, LFI −15,9) y la derecha *de menos* *Freedom & Democracy* (LR −19,1, NI −19,9) — signos estables en ~100 % del bootstrap por scrutin, repartidos en >50 leyes. La **economía polariza menos**. **Cohesión Rice** valida el agrupamiento (LFI 0,998; NI/LT ~0,74, grupos heterogéneos).

**Brecha declarado–revelado (Análisis 3):** la coherencia por partido es **débil e inestable** (IC ≈ [−1,+1]; pooled 0,12–0,19) → **no rankeable**; el aporte es **tipológico**. Patrones localizados: banderas afirmativas (LFI↔libertades +6,9; PS↔bienestar; centro gubernamental↔economía), **coherencia negativa** de la izquierda en el eje cultural (el patrón más limpio), y uso **oposicional** (LR↔cultura, NI↔libertades). Ningún canal anticipa el voto mejor que otro una vez igualada la cobertura.

**Exploratorio (BERTopic):** 24 tópicos por corpus; manifiestos = temas de campaña; enmiendas = temas focalizados (fiscalidad, vivienda, COVID); leyes = sustancia + boilerplate; tweets = actualidad + meta-política; intervenciones = UE/salud/educación + tramos procedurales.

---

## 8. Decisiones técnicas importantes

- **Cohorte única por `id`:** todo el cruce se ancla en `deputes_2017_2022.csv`; el `id` numérico AN (sin prefijo `PA`) es la clave primaria lógica. *Entity linking* determinístico por nombre (sin fuzzy), asumiendo la calidad del cruce de Regards Citoyens.
- **Dominios MARPOR (7) en vez de 56 categorías para el voto:** decisión deliberada — las enmiendas no tienen densidad para estimar soporte relativo estable en 56 categorías; los dominios sacrifican detalle pero preservan robustez y comparabilidad.
- **Énfasis y no RILE para el análisis principal:** RILE es posicional 1-D, frágil y ciego a la dirección; el análisis cross-canal se hace por **énfasis temático**, y RILE queda confinado a validar el pipeline en `ches_analysis/`.
- **Soporte relativo (no absoluto) en el voto:** centra por la base del partido para aislar la señal temática del efecto gobierno/oposición. "Relativo negativo" ≠ "vota en contra".
- **Filtros de calidad de texto:** ≥10 palabras (salvo manifiestos), exclusión procedimental en hemiciclo, y umbrales `texto_confianza`/`match_confianza` en leyes/enmiendas (solo alta, o alta+media).
- **Filtros alineados BERTopic↔ManifestoBERTa** para comparabilidad doc-a-doc.
- **Reducción manual a 25 tópicos** en BERTopic (no auto-reduce) y stop-words de dominio para evitar clusters de forma (sin ellas, un tópico procedural absorbía 56 % de leyes).
- **Correlaciones por partido como secundarias:** con n=6 dominios y 6–10 partidos, los coeficientes son ruidosos; se reportan con IC para mostrar fragilidad, no para concluir → el peso recae en la **tipología** y los **signos por celda**.
- **Manejo de escala/ruido/muestra:** bootstrap (multinomial y por clúster), umbral de fiabilidad (≥100 frases; ≥3 diputados expresando voto), descarte de *External Relations* por bajo leverage (5 leyes / 16 enmiendas), y marcado explícito de muestras chicas (PCF 39, PS 79).
- **Carpetas/artefactos experimentales o secundarios:** `kg-gen/` (sin contexto entre los 9; usa `interventions_xv_sample5000.csv`); en `datos_diputados/` hay exports fuera del pipeline (`deputes_2017_2022_an.csv`, `nosdeputes.fr_*.csv`).
- **Reproducibilidad:** raw masivo (ZIP, XML, `.ndjson`, `results/`) **no versionado** en Git; se regenera con los scripts. Cifras canónicas embebidas en los README.

---

## 9. Limitaciones y riesgos metodológicos

- **Cobertura temporal de Twitter:** captura el timeline reciente (hasta ~2026), no el archivo 2017–2022; mezcla actividad fuera de la legislatura.
- **Cobertura de cuentas/diputados:** 54 cuentas sin captura (533/587); 81 diputados sin Twitter; ~30 % de intervenciones sin `deputy_id`; 40 diputados sin partido MARPOR mapeado.
- **Heterogeneidad de "partido" entre canales:** manifiesto = texto oficial del partido; tweets/hemiciclo = texto de diputados individuales; voto = grupo parlamentario. El manifiesto se indexa por partido electoral y el voto por grupo → **solo 6 partidos** casan limpio en el Análisis 3. Desfase temporal/organizacional (campaña 2017 vs. legislatura).
- **Modelo imperfecto:** ManifestoBERTa accuracy top-1 ~58 %, macro F1 0,44, categorías raras con F1 bajo, **probabilidades no calibradas**, una etiqueta por documento (pierde texto multitemático), truncamiento a 200 tokens en leyes/intervenciones largas.
- **Muestras chicas:** PCF (39) y PS (79) en manifiestos → firmas indicativas; **LR y UDI idénticos** en manifiestos (posible duplicación). En CHES/Análisis 3, n=6–10 partidos.
- **Riesgo de comparar unidades distintas:** énfasis (no signado) vs. soporte (signado) → no se restan; se comparan firmas relativas (decisión explícita en `03_`).
- **Matching heurístico:** scrutin↔dossier↔enmienda por fuzzy; filas de confianza baja/ninguna se excluyen. `demandeur` de enmiendas no controlado.
- **Duplicación:** 74.659 tweets duplicados por `tweet_id` (deduplicación **por verificar** en análisis).
- **BERTopic:** ~48 % outliers en corpus grandes, boilerplate residual, embedder pequeño elegido por velocidad, sin coherence scores; reproducibilidad parcial (semillas UMAP/HDBSCAN por defecto).
- **Sin causalidad:** el proyecto describe alineaciones agregadas; no prueba cumplimiento programático ni que el discurso cause el voto.

---

## 10. Qué partes usar en la memoria

| Sección de la memoria | Módulos / contextos a usar |
|---|---|
| **Introducción** | Propósito (este doc §1); justificación de las 5 arenas (manifiestos, tweets, hemiciclo, leyes, enmiendas). |
| **Estado del arte** | MARPOR / esquema de categorías (`manifestos`, `manifestoberta_analysis`); CHES (`ches_analysis`); RILE; BERTopic; XLM-R. |
| **Datos** | `datos_diputados`, `twitter_zeeschuimer`, `manifestos`, `lois_votes`, `hemicycle` (fuentes, unidades, filtros, tamaños). |
| **Metodología** | Taxonomía MARPOR; métricas de `party_analysis/common/*`; RILE/CHES; BERTopic vs. ManifestoBERTa. |
| **Implementación** | Scripts de ETL por módulo; `classifier_runner.py`, `bertopic_runner.py`; los `run.py`/`build.py` de `party_analysis/`. |
| **Experimentos** | Validación CHES y validación ManifestoBERTa; descomposición R²; bootstrap. |
| **Resultados** | §7 de este doc + los 3 `.md` de `party_analysis/` (prosa casi final) + tablas de BERTopic. |
| **Discusión** | Identidad vs. estrategia; clivaje cultural > económico; brecha declarado-revelado; límites de RILE. |
| **Conclusiones** | Síntesis del arco (§6) + frase de validación (ρ≈0,89). |
| **Anexos** | Esquema de columnas y de las 56 categorías/7 dominios; heatmaps/scatters; CSVs de soporte/cohesión; stop-words; URLs de fuentes. |

---

## 11. Qué falta revisar antes de escribir

1. **`kg-gen/`** no tiene contexto entre los 9: documentar qué hace, qué consume y qué produce, o decidir si queda fuera de la memoria **(por verificar)**.
2. **Reproducibilidad de fechas/versiones:** fecha de descarga del ZIP AN, del CSV twitter-parlementaires, de PISTE y del TSV del hemiciclo; versiones de `transformers`/`torch`. No están centralizadas.
3. **Cobertura de manifiestos — RESUELTO.** La cifra reproducible es **628/668 = 94,0 %**; quedan fuera exactamente **40 diputados** (LT 13, grupo vacío 13, EDS 9, AGIR-E 5 — los 4 grupos sin `party_name_marpor`). El "85 %" del README es aproximado (subconjunto de "partidos principales"), no contradictorio. **Usar 94 % en la memoria.** Pendiente menor: encoding `EÃLV` en `party_positions.csv`.
4. **LR = UDI — RESUELTO (no es bug del proyecto).** `LR_31626_201706.txt` y `UDI_31430_201706.txt` son **byte-idénticos** (282 quasi-frases cada uno, 31.438 caracteres = 33.032 bytes) y `party_positions.csv` les da métricas idénticas (rile 13.619, etc.): es **MARPOR** quien asignó el mismo documento a los IDs 31626 y 31430. En el análisis cuentan como uno; sus 282+282 frases idénticas son parte del corpus de 3.801.
5. **Conteos de enmiendas con texto — RESUELTO (miden cosas distintas).** **2.575** = entran al análisis NLP (`match_confianza` alta/media + ≥10 palabras); **2.886** = con `dispositif` o `expose_sommaire` (reproducible hoy); 2.689 = solo `dispositif`. El **2.904 (93 %) del README** está levemente desactualizado (desfase real de 18 filas vs. 2.886; `match_confianza`: alta 2.155 / media 565 / baja 304 / ninguna 102, suma 3.126). **Usar 2.575 (análisis) y 2.886 (con texto).**
6. **Votos de leyes:** `votos_por_diputado` y `_cohorte` tienen el mismo total (78.116) — confirmar si el filtro de cohorte no reduce.
7. **Deduplicación de tweets** (74.659 duplicados) y **632 tweets sin diputado** — confirmar tratamiento en análisis.
8. **`party_analysis/` usa `deputes_an_rd.csv`** (no el consolidado con Twitter): verificar coherencia de `id`/grupos entre módulos.
9. **Discrepancias de nombres de archivo** en READMEs (`articles_lois_xv.csv.gz` vs. `leyes_texto_oficial.csv`; `manifestos_clean.csv` vs. `manifesto_texts.csv`; rutas `zeeschuimer/` vs. `twitter_zeeschuimer/`).
10. **Enlace hemiciclo↔ley** es heurístico (por `section`), no por `dossier_uid`: no sobre-interpretar.
11. **`results/` no versionados** (BERTopic, ManifestoBERTa, party_analysis parcial): decidir si se anexan regenerados o se citan tablas de README.

---

## 12. Resumen corto

El proyecto caracteriza la **agenda temática de los partidos de la XV legislatura francesa (2017–2022)** observándolos en cinco arenas: manifiestos, tweets, hemiciclo, leyes y enmiendas. Una **cohorte única** de 668 diputados (`datos_diputados/`) ancla la integración de fuentes muy heterogéneas (open data AN, Regards Citoyens, MARPOR API, Légifrance/PISTE, captura Zeeschuimer). Los cinco corpus se etiquetan con una taxonomía común y citable, **MARPOR (56 categorías / 7 dominios)**, mediante **ManifestoBERTa** (supervisado, núcleo) y se exploran con **BERTopic** (no supervisado). El pipeline se **valida externamente** contra **CHES 2019** vía RILE (ρ≈0,89 con suficiente texto). El análisis central (`party_analysis/`) contrasta la **agenda declarada** (énfasis: el canal cambia la agenda, pero la firma persiste) con la **agenda revelada** por el voto (dos capas: una posicional dominante y un clivaje cultural robusto en enmiendas), y cierra con el **cruce declarado–revelado** (coherencia débil pero localizada en banderas identitarias). El aporte es **tipológico y comparativo**, no posicional ni causal.

---

## 13. Citas y referencias necesarias

**Referencias metodológicas (papers / esquemas):**
- **MARPOR / Manifesto Project** — esquema de 56 categorías / 7 dominios (mp v5); Budge, Klingemann, Volkens, Bara et al. (desde 1979).
- **RILE** — Laver, M. & Budge, I. (1992), índice izquierda-derecha estándar MARPOR (implementado en `ches_analysis/common/rile.py`).
- **Índice de cohesión Rice** — Rice, S. A. (1928), *Quantitative Methods in Politics* (`party_analysis/common/votes.py`).
- **CHES** — Bakker, Hooghe, Jolly, Marks, Polk, Rovny, Steenbergen & Vachudova (2020), *2019 Chapel Hill Expert Survey*; trend file Jolly et al. (2022), *Electoral Studies*, doi:10.1016/j.electstud.2021.102420.

**Datasets / fuentes:**
- **Assemblée nationale — open data XV:** acteurs/députés (`AMO20_..._XV.json.zip`), Scrutins, Dossiers législatifs, Amendements (data.assemblee-nationale.fr).
- **Regards Citoyens:** [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) y export de intervenciones del hemiciclo (ND15); NosDéputés.fr.
- **Manifesto Project (MARPOR):** dataset **MPDS2025a**, API REST (`get_core`, `metadata`, `texts_and_annotations`).
- **Légifrance / PISTE:** [piste.gouv.fr](https://piste.gouv.fr) (texto JORF por NOR).
- **CHES 2019:** `CHES2019V3.csv` (chesdata.eu).

**Modelos:**
- **ManifestoBERTa:** `manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1` (Burst, Lehmann, Franzmann et al., 2024).
- **XLM-RoBERTa large:** Conneau et al. (base del modelo anterior).
- **Embeddings BERTopic:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

**Benchmarks externos:**
- **CHES 2019** (`lrgen`, `lrecon`, `galtan`) como vara de validación posicional.
- **`cmp_code` humano de MARPOR** (manifiestos 2017) como ground truth de la validación de ManifestoBERTa.

**Librerías / herramientas:**
- **NLP/ML:** `torch`, `transformers`, `sentence-transformers`, `bertopic` (UMAP, HDBSCAN, c-TF-IDF, KeyBERTInspired), `scikit-learn`.
- **Datos/estadística:** `pandas`, `numpy`, `scipy`, `rapidfuzz`/`difflib`.
- **Captura/ETL:** **Zeeschuimer** (Digital Methods Initiative) + **FoxScroller**; `requests`, `zipfile`, `xml.etree.ElementTree`.
- **Visualización:** `matplotlib`, `plotly`.

**Documentación interna del proyecto:** los `README.md` de cada módulo; los nueve archivos de `context/`; y la prosa de capítulo de `party_analysis/` (`01_canal_cambia_agenda.md`, `02_voto_dos_capas.md`, `03_declarado_vs_revelado.md`).

---

## 14. Mapa maestro: contexto → capítulo de la memoria

> Índice transversal de los 9 contextos de módulo. Cada uno lleva al final su propia sección **"Mapa a la memoria"** (carpeta que resume · parte que alimenta · qué extraer · figuras/tablas · limitaciones). Esta tabla es la vista de conjunto para decidir qué leer al escribir cada capítulo. **Negrita** = destino principal de ese contexto.

| Contexto (`context/…`) | Tipo / rol | Intro | Rev. lit. | Datos | Metodol. | Implem. | Validación | Resultados | Discusión | Anexos |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `datos_diputado` | Datos · cohorte ancla | ○ | | **●** | ○ | ● | | ○ | ○ | ● |
| `manifestos` | Datos · declarada (ground truth) | | ● | **●** | ● | ○ | ● | ○ | ○ | ● |
| `hemicycle` | Datos · declarada institucional | | | **●** | ● | ● | | ○ | ○ | ● |
| `twitter_zeeschuimer` | Datos · declarada comunicativa | ○ | | **●** | ● | ● | | ○ | ● | ● |
| `lois_votes` | Datos · revelada (voto) | | | **●** | ● | **●** | | ○ | ○ | ● |
| `manifestoberta_analysis` | **★ Núcleo** · clasificación MARPOR | | ● | | **●** | ● | **●** | ● | ● | ● |
| `bertopic_analysis` | **⚠ Secundario / exploratorio** | | ● | | ● | ● | | ○ (explor.) | ○ | **●** |
| `ches_analysis` | Validación externa (CHES/RILE) | | ● | | ● | | **●** | ● | ● | ● |
| `party_analysis` | **★ Central** · 3 análisis | | | | **●** | ● | | **●** | **●** | ● |

**Lecturas rápidas de la tabla:**
- **Datos** se nutre de los 5 contextos de corpus (`datos_diputado`, `manifestos`, `hemicycle`, `twitter_zeeschuimer`, `lois_votes`).
- **Resultados** y **Discusión** se apoyan sobre todo en `party_analysis` (cuerpo central) + `manifestoberta_analysis` y `ches_analysis`.
- **Validación** = `ches_analysis` (externa) + la validación de `manifestoberta_analysis` contra `cmp_code`.
- `bertopic_analysis` es **exploratorio**: aporta un resultado de triangulación y, sobre todo, **anexos**; no alimenta `party_analysis`.
- Este `general_context` resume **todos** los módulos; su §10 ya da la correspondencia sección→módulos y su §11 lista lo pendiente por revisar antes de escribir.




