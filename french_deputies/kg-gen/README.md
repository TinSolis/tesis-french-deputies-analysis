# KG-Gen — exploración acotada de extracción de grafos de conocimiento sobre intervenciones del hemiciclo

Este módulo es una **exploración experimental acotada** del enfoque KG-Gen (Mo et al., 2025, NeurIPS — [arxiv:2502.09956](https://arxiv.org/abs/2502.09956)) sobre una muestra estratificada de intervenciones del hemiciclo francés. La idea es medir empíricamente cómo se comporta este método sobre texto parlamentario en francés —tiempos, calidad de los triples, post-procesamiento que requeriría— para decidir si vale la pena integrarlo al pipeline general de la tesis.

Es deliberadamente un demo, no una corrida sobre el corpus completo: con los números que se muestran abajo se entiende rápido por qué.

## Modelo

[KG-Gen](https://github.com/stair-lab/kg-gen) (Stair Lab, Stanford, NeurIPS 2025) es un extractor de grafos de conocimiento basado en LLMs que devuelve triples **(sujeto, predicado, objeto)** a partir de texto plano. Su aporte principal frente a OpenIE y Microsoft GraphRAG es un paso opcional de **clustering de entidades** que reduce duplicados (`Macron` y `Emmanuel Macron` se fusionan).

En este experimento se usa un LLM local en lugar del paquete oficial:

- Backend: **Ollama 0.24.0** (servidor HTTP local).
- Modelo: **`qwen2.5:3b`** (cuantizado Q4, 1.9 GB, multilingüe, soporta francés).
- Cómputo: Apple Silicon (CPU + Metal). 100% offline, costo USD 0.
- Implementación: Python 3.9 con llamadas directas a `http://localhost:11434/api/chat` vía `urllib`. El paquete oficial `kg-gen` requiere Python 3.10+ y DSPy; aquí replicamos el pipeline esencial con un *system prompt* equivalente al de KG-Gen (extracción de triples en JSON estructurado, temperatura 0). Se preserva el aporte conceptual sin la dependencia de la librería.

## Corpus de entrada

El subset está diseñado para representar varios registros discursivos (no un solo grupo) y unidades de longitud razonable (ni interjecciones ni discursos enteros), todo dentro de un debate emblemático:

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

Implementado en [`scripts/02_extract_triples.py`](scripts/02_extract_triples.py). Por cada intervención:

1. **Llamada al LLM**. Se envía el texto crudo de la intervención al endpoint `/api/chat` de Ollama, con un *system prompt* en francés que pide identificar actores (personas, partidos, instituciones), conceptos (leyes, políticas públicas, valores) y relaciones, y devolver hasta 12 triples como JSON válido.
2. **Generación estructurada**. Se fijan `format: "json"`, `temperature: 0` y `num_predict: 600` para que la salida sea determinista y parseable. `keep_alive: "10m"` mantiene el modelo en memoria entre llamadas.
3. **Parseo robusto**. Se intenta `json.loads` directo; si falla, se extrae el primer bloque `{...}` con regex y se reintenta. Los triples con sujeto, predicado u objeto vacío se descartan.
4. **Reintentos**. Hasta 2 reintentos por intervención ante errores HTTP / timeout (300 s). Si todos fallan, se registra SKIP y se sigue.
5. **Persistencia incremental**. `triples.csv` se reescribe completo después de cada intervención para que un Ctrl+C no pierda nada.

El análisis posterior (estadísticas + grafo PNG) corre en [`scripts/03_analyze.py`](scripts/03_analyze.py): cuenta entidades y predicados únicos (normalizados a minúsculas), distribuye los triples por grupo político, arma un `MultiDiGraph` con NetworkX restringido a las top-40 entidades y lo dibuja con `spring_layout`, coloreando los ejes por grupo del orador.

## Detalle de la corrida

Números reales medidos en este repo (Apple Silicon, Ollama local):

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

### Extrapolación al corpus completo

A throughput constante (no es la mejor suposición, porque las intervenciones largas escalan peor que las cortas, pero sirve como cota inferior) y manteniendo `qwen2.5:3b`:

| Corpus | n docs | Tiempo estimado |
|---|---:|---:|
| Demo (este experimento) | 25 | 3.4 min |
| Un debate completo (ej. *retraites* 2019) | ~3 500 | ~7.8 horas |
| Un año de intervenciones (ej. 2020) | ~50 000 | ~4.7 dias non-stop |
| Corpus completo de intervenciones XV | 338 192 | ~31.6 dias non-stop |
| Las 5 fuentes integradas (manifestos + amendements + lois + tweets + interventions) | ~592 000 | ~55 dias non-stop |

Con un modelo de calidad superior (`qwen2.5:7b` o `qwen2.5:14b`) la calidad mejora, pero el tiempo se multiplica por 2-4×.

> Nota: el `timing.json` versionado en este repo guarda extrapolaciones con `n=205 940` para intervenciones y `n=466 000` para las 5 fuentes, que eran las cifras previas al recálculo del pipeline general. Los números de la tabla de arriba están recalibrados a los conteos finales de los módulos `bertopic_analysis/` y `manifestoberta_analysis/` (`338 192` intervenciones válidas; `592 301` documentos sumados sobre las 5 fuentes), que son los que mandan en la tesis.

## Salidas (qué se genera)

| Archivo | Contenido |
|---|---|
| `data/sample_interventions.csv` | el subset de 25 intervenciones (texto + metadata) |
| `results/triples.csv` | una fila por triple extraido: `intervention_id`, `deputy`, `group`, `date`, `nb_mots`, `s`, `p`, `o` (102 filas) |
| `results/timing.json` | metadata de tiempos: throughput, tiempo medio/min/max, extrapolaciones |
| `results/stats.json` | estadisticas: n_entidades, n_predicados, top-20 entidades, top-20 predicados, triples por grupo, descripcion de la distribucion de triples/doc |
| `results/graph.png` | visualizacion del grafo (top-40 entidades como nodos, ejes coloreados por grupo del orador) |

## Resultados

### Cobertura por documento

20 de las 25 intervenciones produjeron al menos un triple; **5 (20%) quedaron vacías**. La distribución de triples por documento, entre las que sí extrajeron algo:

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

> Un 20% de fracaso silencioso es esperable con un modelo de 3B parámetros sobre texto político-jurídico en francés. Un modelo más grande (7B o 14B) reduce esta tasa al precio de multiplicar el tiempo por 2-4×.

### Distribución de triples por grupo político

| Grupo | Triples |
|---|---:|
| GDR | 24 |
| NG | 24 |
| FI | 23 |
| LAREM | 17 |
| LR | 14 |

> Lectura: el número de triples por grupo es razonablemente parejo, dado que cada grupo aporta 5 intervenciones de longitud comparable. La izquierda (GDR + NG + FI = 71) extrae un 50% más de triples que LAREM + LR (31), coherente con que las intervenciones de GDR/NG/FI tienden a ser más argumentativas y nominales en este debate (atacan artículos específicos, citan a la ministra, mencionan principios jurídicos), mientras que las del oficialismo (LAREM) y la derecha (LR) son más declarativas.

### Top-10 entidades extraídas (con frecuencia)

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

> Lectura: el top está dominado por **vocabulario procedural del hemiciclo** (`article`, `alinea 5`, `article 1er`, `amendement`, `madame la ministre`) más que por actores políticos sustantivos. El nombre `moniteur` aparece 6 veces porque un diputado se cita repetidamente en una intervención. Los únicos elementos sustantivos del top-10 son `abandon du motif economique` (un concepto técnico del Code du travail) y `gouvernement`/`republique` como entidades-marco. Es la firma estilística de un debate parlamentario: los actores reales (Macron, Pénicaud, los partidos por nombre) aparecen más abajo y diluidos.

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

> Lectura: 85 predicados únicos para 102 triples implica que **casi ningún predicado se repite entre documentos**. El LLM extrae predicados muy específicos de cada intervención ("conduirait a", "ne serez pas d'accord avec", "n'a pas le monopole du") que no se canonicalizan solos. Para cualquier análisis cuantitativo agregado (centralidad, comunidades, motivos recurrentes) hace falta una capa posterior de **canonicalización semántica**, ya sea con el paso opcional de clustering de KG-Gen o con embeddings + clustering manual. Es una limitación estructural del enfoque, no del modelo elegido.

### Visualización del grafo

![Grafo de conocimiento sobre 25 intervenciones del debate de las Ordonnances Macron](results/graph.png)

> Se construye con NetworkX restringiendo a las top-40 entidades. Los ejes están coloreados por el grupo del orador (LAREM amarillo, FI rojo, GDR rojo oscuro, LR azul, NG naranja). El layout es `spring_layout` con `k=1.2` y semilla fija: es una vista cualitativa, no una métrica.

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

`02_extract_triples.py` reescribe `triples.csv` después de cada intervención, así que un Ctrl+C no pierde lo procesado hasta ahí (`timing.json` y `stats.json` solo se generan al terminar).

## Notas y limitaciones

- **Cobertura del modelo chico**. El 20% de las intervenciones no produjeron ningún triple. Es esperable con `qwen2.5:3b` sobre texto jurídico-político francés, pero significa que para una corrida seria habría que subir a un modelo más grande (7B o 14B) o usar la API de un proveedor cerrado.
- **Predominio de entidades procedurales**. Las entidades top incluyen `article`, `alinea 5`, `madame la ministre`, `mes chers collegues`, `monsieur le president`: vocabulario del registro parlamentario más que actores o conceptos sustantivos. Los actores políticos reales aparecen, pero diluidos. Filtrar este registro en el preprocesamiento (regex sobre saludos y referencias internas a la sesión) ayudaría mucho.
- **Dispersión de predicados**. 85 predicados únicos para 102 triples → casi ninguno se repite. Sin canonicalización no hay análisis agregado posible.
- **Duplicación de entidades**. Aparecen pares como `gouvernement`/`le gouvernement` o `article`/`article 1er` como nodos distintos. El paso opcional de clustering de KG-Gen lo resuelve, pero **duplica el tiempo de inferencia** (segunda ronda de llamadas al LLM para clusterizar).
- **Solapamiento con el resto del pipeline**. Las entidades sustantivas que sí emergen (`gouvernement`, `republique`, `abandon du motif economique`) ya están cubiertas indirectamente por la clasificación MARPOR del módulo [`manifestoberta_analysis/`](../manifestoberta_analysis/), que asigna cada intervención a un código entre 56 categorías. Lo que KG-Gen aportaría adicionalmente es la **dimensión relacional** (quién interactúa con quién, qué predicado vincula a dos entidades), no la dimensión temática.
- **Costo de aplicar a la totalidad**. Con `qwen2.5:3b` corriendo localmente, las extrapolaciones dan ~31 días para clasificar todas las intervenciones XV y ~55 días para las 5 fuentes. Con un modelo más grande, factor ×2 a ×4. Sumando la canonicalización posterior y la validación sobre muestra anotada manualmente, integrar esto al pipeline principal de la tesis no es viable en el plazo restante.

## Implicancias para la tesis

Los tiempos medidos indican que aplicar este pipeline al corpus completo de intervenciones (338 192 docs) requeriría **~31 días de cómputo non-stop** con el modelo chico, o entre **60 y 120 días** con un modelo de calidad razonable, más el post-procesamiento (canonicalización de entidades y predicados, validación sobre muestra anotada) y la integración con el resto del pipeline.

Dado el plazo de entrega de la tesis, el aporte marginal de un grafo de conocimiento extraído por LLM se pondera frente a los experimentos sustantivos que aún restan en el pipeline principal basado en BERTopic + manifestoberta + MARPOR (medición de congruencia programática, polarización temática, evolución temporal, cumplimiento legislativo).

Este módulo queda versionado como **referencia empírica del experimento** y como base para extensiones futuras del trabajo. Los números de tiempo y las observaciones cualitativas son la justificación explícita de por qué el pipeline final no incluye un módulo de KG.

## Estructura del módulo

```
kg-gen/
├── README.md                        # este documento
├── data/
│   └── sample_interventions.csv     # 25 intervenciones estratificadas
├── scripts/
│   ├── 01_build_sample.py           # construye el subset
│   ├── 02_extract_triples.py        # llama a Ollama y extrae triples
│   └── 03_analyze.py                # estadísticas + visualización
└── results/
    ├── triples.csv                  # 102 triples extraídos
    ├── timing.json                  # métricas de tiempo + extrapolación
    ├── stats.json                   # estadísticas exploratorias
    └── graph.png                    # visualización del grafo
```

## Módulos hermanos

- [`bertopic_analysis/`](../bertopic_analysis/) — análisis temático **no supervisado** (BERTopic + UMAP + HDBSCAN) sobre las 5 fuentes. Descubre tópicos por clustering.
- [`manifestoberta_analysis/`](../manifestoberta_analysis/) — análisis temático **supervisado** (manifestoberta + 56 categorías MARPOR) sobre las mismas 5 fuentes. Asigna cada documento a una taxonomía citable.

KG-Gen apunta a una dimensión distinta: en vez de etiquetar temáticamente, busca extraer **relaciones** (sujeto, predicado, objeto) entre entidades nominadas. Los resultados de este demo muestran que esa dimensión es interesante, pero requiere más cómputo y más post-procesamiento del que cabe en el plazo de la tesis.

## Citas

**KG-Gen**
> Mo, B., Yu, K., Kazdan, J., Cabezas, J., Mpala, P., Yu, L., Cundy, C., Kanatsoulis, C., & Koyejo, S. (2025). *KGGen: Extracting Knowledge Graphs from Plain Text with Language Models*. NeurIPS 2025. [arxiv:2502.09956](https://arxiv.org/abs/2502.09956).

**Antecedentes en literatura parlamentaria**
> - Hyvonen, E. et al. (2023). *Publishing and Using Parliamentary Linked Data on the Semantic Web: ParliamentSampo System for Parliament of Finland*. Semantic Web Journal.
> - Plenz, M. et al. (2024). *PAKT: Perspectivized Argumentation Knowledge Graph and Tool for Deliberation Analysis*. [arxiv:2404.10570](https://arxiv.org/abs/2404.10570).
