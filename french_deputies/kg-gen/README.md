# KG-Gen — exploracion acotada de extraccion de grafos de conocimiento sobre intervenciones del hemiciclo

Este modulo es una **exploracion experimental acotada** del enfoque KG-Gen (Mo et al., 2025, NeurIPS — [arxiv:2502.09956](https://arxiv.org/abs/2502.09956)) sobre una muestra estratificada de intervenciones del hemiciclo frances. La idea es medir empiricamente como se comporta este metodo sobre texto parlamentario en frances — tiempos, calidad de los triples, post-procesamiento que requeriria — para decidir si vale la pena integrarlo al pipeline general de la tesis o no.

Es deliberadamente un demo, no una corrida sobre el corpus completo: con los numeros que se muestran abajo se entiende rapido por que.

## Modelo

[KG-Gen](https://github.com/stair-lab/kg-gen) (Stair Lab, Stanford, NeurIPS 2025) es un extractor de grafos de conocimiento basado en LLMs que devuelve triples **(sujeto, predicado, objeto)** a partir de texto plano. Su aporte principal frente a OpenIE y Microsoft GraphRAG es un paso opcional de **clustering de entidades** que reduce duplicados (`Macron` y `Emmanuel Macron` se mergean).

En este experimento se usa un LLM local en lugar del paquete oficial:

- Backend: **Ollama 0.24.0** (servidor HTTP local).
- Modelo: **`qwen2.5:3b`** (cuantizado Q4, 1.9 GB, multilingue, soporta frances).
- Computo: Apple Silicon (CPU + Metal). 100% offline, costo USD 0.
- Implementacion: Python 3.9 con llamadas directas a `http://localhost:11434/api/chat` via `urllib`. El paquete oficial `kg-gen` requiere Python 3.10+ y DSPy; aca replicamos el pipeline esencial con un *system prompt* equivalente al de KG-Gen (extraccion de triples en JSON estructurado, temperatura 0). Se preserva el aporte conceptual sin la dependencia de la libreria.

## Corpus de entrada

El subset esta diseñado para tener varios registros discursivos representados (no un solo grupo) y unidades de longitud razonable (ni interjecciones ni discursos enteros), todo dentro de un debate emblematico:

| Atributo | Valor |
|---|---|
| Archivo de origen | `french_deputies/hemicycle/processed/interventions_xv_sample5000.csv` |
| Debate | *"renforcement du dialogue social"* (Ordonnances Macron, Code du travail) |
| Periodo | 10-11 julio 2017 |
| Filtro de largo | 60 ≤ palabras ≤ 400 (mediana 186) |
| Estratificacion | 5 intervenciones × 5 grupos politicos (LAREM, FI, GDR, LR, NG) |
| Docs finales | **25 intervenciones**, 4 648 palabras totales |

Subset construido por [`scripts/01_build_sample.py`](scripts/01_build_sample.py). Se ordenan las intervenciones por largo dentro de cada grupo y se toman 5 quantiles (min, Q1, mediana, Q3, max) para no quedar todos en el mismo registro.

## Pipeline

Implementado en [`scripts/02_extract_triples.py`](scripts/02_extract_triples.py). Por cada intervencion:

1. **Llamada al LLM**. Se manda el texto crudo de la intervencion al endpoint `/api/chat` de Ollama, con un *system prompt* en frances que pide identificar actores (personas, partidos, instituciones), conceptos (leyes, politicas publicas, valores) y relaciones, y devolver hasta 12 triples como JSON valido.
2. **Generacion estructurada**. Se setea `format: "json"`, `temperature: 0` y `num_predict: 600` para que la salida sea determinista y parseable. `keep_alive: "10m"` mantiene el modelo en memoria entre llamadas.
3. **Parseo robusto**. Se intenta `json.loads` directo; si falla, se extrae el primer bloque `{...}` con regex y se reintenta. Triples con sujeto / predicado / objeto vacio se descartan.
4. **Reintentos**. Hasta 2 reintentos por intervencion ante errores HTTP / timeout (300 s). Si todos fallan, se loguea SKIP y se sigue.
5. **Persistencia incremental**. `triples.csv` se reescribe completo despues de cada intervencion para que un Ctrl+C no pierda nada.

El analisis posterior (estadisticas + grafo PNG) corre en [`scripts/03_analyze.py`](scripts/03_analyze.py): cuenta entidades y predicados unicos (normalizados a lowercase), distribuye triples por grupo politico, arma un `MultiDiGraph` con NetworkX restringido a las top-40 entidades y lo dibuja con `spring_layout`, coloreando los ejes por grupo del orador.

## Detalle de la corrida

Numeros reales medidos en este repo (Apple Silicon, Ollama local):

| Metrica | Valor |
|---|---:|
| Intervenciones procesadas | 25 |
| Palabras totales | 4 648 |
| Triples extraidos | 102 |
| Entidades unicas | 140 |
| Predicados unicos | 85 |
| Tiempo total | 201.9 s (3 min 22 s) |
| Tiempo promedio por documento | 8.07 s |
| Tiempo minimo / maximo | 2.43 s / 21.58 s |
| Throughput | 0.124 docs/seg |
| Costo monetario | USD 0 (100% local) |

### Extrapolacion al corpus completo

A throughput constante (no es la mejor suposicion porque las intervenciones largas escalan peor que las cortas, pero sirve como cota inferior) y manteniendo `qwen2.5:3b`:

| Corpus | n docs | Tiempo estimado |
|---|---:|---:|
| Demo (este experimento) | 25 | 3.4 min |
| Un debate completo (ej. *retraites* 2019) | ~3 500 | ~7.8 horas |
| Un año de intervenciones (ej. 2020) | ~50 000 | ~4.7 dias non-stop |
| Corpus completo de intervenciones XV | 338 192 | ~31.6 dias non-stop |
| Las 5 fuentes integradas (manifestos + amendements + lois + tweets + interventions) | ~592 000 | ~55 dias non-stop |

Con un modelo de calidad superior (`qwen2.5:7b` o `qwen2.5:14b`) la calidad mejora pero el tiempo se multiplica por 2-4×.

> Nota: el `timing.json` versionado en este repo guarda extrapolaciones con `n=205 940` para intervenciones y `n=466 000` para las 5 fuentes, que eran las cifras pre-recalculo del pipeline general. Los numeros de la tabla de arriba estan re-calibrados a los conteos finales de los modulos `bertopic_analysis/` y `manifestoberta_analysis/` (`338 192` intervenciones validas; `592 301` documentos sumados sobre las 5 fuentes), que son los que mandan en la tesis.

## Salidas (que se genera)

| Archivo | Contenido |
|---|---|
| `data/sample_interventions.csv` | el subset de 25 intervenciones (texto + metadata) |
| `results/triples.csv` | una fila por triple extraido: `intervention_id`, `deputy`, `group`, `date`, `nb_mots`, `s`, `p`, `o` (102 filas) |
| `results/timing.json` | metadata de tiempos: throughput, tiempo medio/min/max, extrapolaciones |
| `results/stats.json` | estadisticas: n_entidades, n_predicados, top-20 entidades, top-20 predicados, triples por grupo, descripcion de la distribucion de triples/doc |
| `results/graph.png` | visualizacion del grafo (top-40 entidades como nodos, ejes coloreados por grupo del orador) |

## Resultados

### Cobertura por documento

20 de las 25 intervenciones produjeron al menos un triple; **5 (20%) quedaron vacias**. La distribucion de triples por documento entre los que si extrajeron algo:

| Estadistico | Triples / doc |
|---|---:|
| n (con triples) | 20 |
| media | 5.1 |
| std | 2.86 |
| min | 2 |
| Q1 | 3 |
| mediana | 4 |
| Q3 | 6.25 |
| max | 11 |

> 20% de fracaso silencioso es esperable con un modelo de 3B parametros sobre texto politico-juridico en frances. Un modelo mas grande (7B o 14B) reduce esta tasa al precio de multiplicar el tiempo por 2-4×.

### Distribucion de triples por grupo politico

| Grupo | Triples |
|---|---:|
| GDR | 24 |
| NG | 24 |
| FI | 23 |
| LAREM | 17 |
| LR | 14 |

> Lectura: el numero de triples por grupo es razonablemente parejo dado que cada grupo aporta 5 intervenciones de longitud comparable. La izquierda (GDR + NG + FI = 71) extrae un 50% mas de triples que LAREM + LR (31) — coherente con que las intervenciones de GDR/NG/FI tienden a ser mas argumentativas y nominales en este debate (atacan articulos especificos, citan a la ministra, mencionan principios juridicos), mientras que las del oficialismo (LAREM) y la derecha (LR) son mas declarativas.

### Top-10 entidades extraidas (con frecuencia)

| # | Entidad | Apariciones |
|--:|---|---:|
| 1 | article | 9 |
| 2 | madame la ministre | 6 |
| 3 | moniteur | 6 |
| 4 | alinea 5 | 5 |
| 5 | article 1er | 4 |
| 6 | abandon du motif economique | 4 |
| 7 | gouvernement | 4 |
| 8 | amendement | 3 |
| 9 | le gouvernement | 3 |
| 10 | republique | 3 |

> Lectura: el top esta dominado por **vocabulario procedural del hemiciclo** (`article`, `alinea 5`, `article 1er`, `amendement`, `madame la ministre`) mas que por actores politicos sustantivos. El nombre `moniteur` aparece 6 veces porque un diputado se cita repetidamente en una intervencion. Los unicos elementos sustantivos del top-10 son `abandon du motif economique` (un concepto tecnico del Code du travail) y `gouvernement`/`republique` como entidades-marco. Es la firma estilistica de un debate parlamentario: los actores reales (Macron, Pénicaud, los partidos por nombre) aparecen mas abajo y diluidos.

### Top-10 predicados (con frecuencia)

| # | Predicado | Apariciones |
|--:|---|---:|
| 1 | prevoit | 5 |
| 2 | implique | 4 |
| 3 | etre | 4 |
| 4 | est citee par nom | 3 |
| 5 | conduirait a | 2 |
| 6 | avance des arguments | 2 |
| 7 | deviendrait | 2 |
| 8 | appartenir a | 2 |
| 9 | concernant | 2 |
| 10 | avoir introduit un amendement | 1 |

> Lectura: 85 predicados unicos para 102 triples implica que **casi ningun predicado se repite entre documentos**. El LLM extrae predicados muy especificos a cada intervencion ("conduirait a", "ne serez pas d'accord avec", "n'a pas le monopole du") que no se canonicalizan solos. Para cualquier analisis cuantitativo agregado (centralidad, comunidades, motivos recurrentes) hace falta una capa posterior de **canonicalizacion semantica** — ya sea con el paso opcional de clustering de KG-Gen o con embeddings + clustering manual. Esto es una limitacion estructural del enfoque, no del modelo elegido.

### Visualizacion del grafo

![Grafo de conocimiento sobre 25 intervenciones del debate de las Ordonnances Macron](results/graph.png)

> Se construye con NetworkX restringiendo a las top-40 entidades. Los ejes estan coloreados por el grupo del orador (LAREM amarillo, FI rojo, GDR rojo oscuro, LR azul, NG naranja). El layout es `spring_layout` con `k=1.2` y semilla fija — es una vista cualitativa, no una metrica.

## Reproducir las corridas

```bash
# 1. Instalar Ollama (una vez)
curl -fsSL https://ollama.com/install.sh | sh

# 2. Iniciar el servidor (deja corriendo en otra terminal o en background)
ollama serve &

# 3. Descargar el modelo (una vez, ~1.9 GB)
ollama pull qwen2.5:3b

# 4. Correr el experimento completo
cd /Users/agustin.solis/Tesis/french_deputies/kg-gen
python3 -u scripts/01_build_sample.py    # ~1 s     -> data/sample_interventions.csv
python3 -u scripts/02_extract_triples.py  # ~3.5 min  -> results/triples.csv + timing.json
python3 -u scripts/03_analyze.py          # ~3 s     -> results/stats.json + graph.png
```

`02_extract_triples.py` reescribe `triples.csv` despues de cada intervencion, asi que un Ctrl+C no pierde lo procesado hasta ahi (`timing.json` y `stats.json` solo se generan al terminar).

## Notas y limitaciones

- **Cobertura del modelo chico**. 20% de las intervenciones no produjeron ningun triple. Es esperable con `qwen2.5:3b` sobre texto juridico-politico frances, pero significa que para una corrida seria habria que subir a un modelo mas grande (7B o 14B) o usar la API de un proveedor cerrado.
- **Predominio de entidades procedurales**. Las top-entidades incluyen `article`, `alinea 5`, `madame la ministre`, `mes chers collegues`, `monsieur le president` — vocabulario del registro parlamentario mas que actores o conceptos sustantivos. Los actores politicos reales aparecen pero diluidos. Filtrar este registro en preprocesamiento (regex sobre saludos / referencias internas a la sesion) ayudaria mucho.
- **Dispersion de predicados**. 85 predicados unicos para 102 triples → casi ninguno se repite. Sin canonicalizacion no hay analisis agregado posible.
- **Duplicacion de entidades**. Aparecen pares como `gouvernement`/`le gouvernement` o `article`/`article 1er` como nodos distintos. El paso opcional de clustering de KG-Gen lo resuelve, pero **duplica el tiempo de inferencia** (segunda ronda de llamadas al LLM para clusterizar).
- **Solapamiento con el resto del pipeline**. Las entidades sustantivas que si emergen (`gouvernement`, `republique`, `abandon du motif economique`) ya estan cubiertas indirectamente por la clasificacion MARPOR del modulo [`manifestoberta_analysis/`](../manifestoberta_analysis/), que asigna cada intervencion a un codigo entre 56 categorias. Lo que aportaria KG-Gen adicionalmente es la **dimension relacional** (quien interactua con quien, que predicado vincula a dos entidades) — no la dimension tematica.
- **Costo de aplicar a la totalidad**. Con `qwen2.5:3b` corriendo localmente, las extrapolaciones dan ~31 dias para clasificar todas las intervenciones XV y ~55 dias para las 5 fuentes. Con un modelo mas grande, factor ×2 a ×4. Sumando la canonicalizacion posterior y la validacion sobre muestra anotada manualmente, integrar esto al pipeline principal de la tesis no es viable en el plazo restante.

## Implicancias para la tesis

Los tiempos medidos indican que aplicar este pipeline al corpus completo de intervenciones (338 192 docs) requeriria **~31 dias de computo non-stop** con el modelo chico, o entre **60 y 120 dias** con un modelo de calidad razonable, mas el post-procesamiento (canonicalizacion de entidades y predicados, validacion sobre muestra anotada) y la integracion con el resto del pipeline.

Dado el plazo de entrega de la tesis, el aporte marginal de un grafo de conocimiento extraido por LLM se pondera frente a los experimentos sustantivos que aun restan en el pipeline principal basado en BERTopic + manifestoberta + MARPOR (medicion de congruencia programatica, polarizacion tematica, evolucion temporal, cumplimiento legislativo).

Este modulo queda versionado como **referencia empirica del experimento** y como base para extensiones futuras del trabajo. Los numeros de tiempo y las observaciones cualitativas son la justificacion explicita de por que el pipeline final no incluye un modulo de KG.

## Estructura del modulo

```
kg-gen/
├── README.md                        # este documento
├── data/
│   └── sample_interventions.csv     # 25 intervenciones estratificadas
├── scripts/
│   ├── 01_build_sample.py           # construye el subset
│   ├── 02_extract_triples.py        # llama a Ollama y extrae triples
│   └── 03_analyze.py                # estadisticas + visualizacion
└── results/
    ├── triples.csv                  # 102 triples extraidos
    ├── timing.json                  # metricas de tiempo + extrapolacion
    ├── stats.json                   # estadisticas exploratorias
    └── graph.png                    # visualizacion del grafo
```

## Modulos hermanos

- [`bertopic_analysis/`](../bertopic_analysis/) — analisis tematico **no supervisado** (BERTopic + UMAP + HDBSCAN) sobre las 5 fuentes. Descubre topicos por clustering.
- [`manifestoberta_analysis/`](../manifestoberta_analysis/) — analisis tematico **supervisado** (manifestoberta + 56 categorias MARPOR) sobre las mismas 5 fuentes. Asigna cada documento a una taxonomia citable.

KG-Gen apunta a una dimension distinta: en vez de etiquetar tematicamente, busca extraer **relaciones** (sujeto, predicado, objeto) entre entidades nominadas. Los resultados de este demo muestran que esa dimension es interesante pero requiere mas computo y mas post-procesamiento del que cabe en el plazo de la tesis.

## Citas

**KG-Gen**
> Mo, B., Yu, K., Kazdan, J., Cabezas, J., Mpala, P., Yu, L., Cundy, C., Kanatsoulis, C., & Koyejo, S. (2025). *KGGen: Extracting Knowledge Graphs from Plain Text with Language Models*. NeurIPS 2025. [arxiv:2502.09956](https://arxiv.org/abs/2502.09956).

**Antecedentes en literatura parlamentaria**
> - Hyvonen, E. et al. (2023). *Publishing and Using Parliamentary Linked Data on the Semantic Web: ParliamentSampo System for Parliament of Finland*. Semantic Web Journal.
> - Plenz, M. et al. (2024). *PAKT: Perspectivized Argumentation Knowledge Graph and Tool for Deliberation Analysis*. [arxiv:2404.10570](https://arxiv.org/abs/2404.10570).
