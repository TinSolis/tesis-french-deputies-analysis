# ManifestoBERTa — clasificacion tematica supervisada del corpus de diputados franceses (XV legislatura)

Este modulo clasifica los mismos cinco corpus que `bertopic_analysis/` pero con un enfoque **supervisado**: en vez de descubrir topicos por clustering, asigna a cada documento una de las **56 categorias MARPOR** definidas por el Manifesto Project. Cada documento queda etiquetado con su top-1, top-2 y top-3 codigos + sus probabilidades, y agregado a uno de los **7 dominios** macro.

El objetivo es complementar el analisis exploratorio de BERTopic con una taxonomia citable y comparable internacionalmente: no inventamos las categorias, las heredamos del esquema estandar de la ciencia politica comparada (Budge, Klingemann, Volkens, Bara et al., desde 1979). Asi se puede comparar el corpus frances XV contra cualquier otro pais codificado por MARPOR.

## Modelo

[`manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1`](https://huggingface.co/manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1) (Burst, Lehmann, Franzmann et al., 2024). Es un `xlm-roberta-large` (560 M parametros) fine-tuneado sobre 1.7 M quasi-oraciones del Manifesto Corpus 2024a (38 idiomas, anotadas a mano por codificadores oficiales del WZB Berlin con el Handbook 4 / `mp v5`).

- Tamaño en disco: ~2.2 GB. Se descarga la primera vez via `transformers`.
- Tokenizer: `xlm-roberta-large` (no el del modelo afinado, asi recomienda la model card).
- Max tokens por documento: 200 (truncamiento con `padding="max_length"`).
- Salida: softmax sobre 56 categorias.

## Corpus de entrada

Filtros **identicos** a los de `bertopic_analysis/`, asi un mismo `text_id` es clasificable con ambos metodos y los resultados son comparables doc-por-doc.

| Fuente | Archivo de origen | Periodo | Filtro de largo | Docs finales |
|---|---|---|---|---|
| `manifestos` | `french_deputies/manifestos/processed/manifesto_texts.csv` (+ `manifesto_full_texts.csv` para mapeo de partido) | Eleccion 2017 | **sin filtro de largo** (quasi-frases pre-segmentadas por MARPOR; solo se descartan vacias) | 3 801 |
| `amendements` | `french_deputies/lois_votes/votes_rd/processed/amendements_votos_con_texto.csv` | XV legis. | enmiendas con `match_confianza` alta/media y texto concatenado (`dispositif + expose_sommaire`) **>= 10 palabras** | 2 575 |
| `lois` | `french_deputies/lois_votes/votes_rd/processed/leyes_texto_oficial.csv` | XV legis. | parrafos del texto promulgado **>= 10 palabras** (solo leyes con `texto_confianza == "alta"`) | 23 267 |
| `tweets` | `french_deputies/twitter_zeeschuimer/processed/tweets_text_only.csv` | mar/2017-2025 | tweets **>= 10 palabras** tras limpieza (urls, menciones, hashtags) | 224 466 |
| `interventions` | `french_deputies/hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz` | 2017-2022 | intervenciones **>= 10 palabras**, con `deputy_id` y no procedurales | 338 192 |

Origen completo de cada corpus en sus respectivos modulos del proyecto. Aca solo importa que los textos llegan ya procesados desde su carpeta y manifestoberta se aplica con la politica de filtrado descrita en cada `run.py`.

> Nota sobre tweets: el filtro `>= 10 palabras` se calcula sobre el `clean_text` (despues de sacar urls y arroba/almohadilla), por eso 224 466 (no 222 644 como en bertopic). La limpieza tiene una pequeña diferencia: en bertopic se "abre" el hashtag (`#climat` -> `climat`), en manifestoberta el regex actual lo deja igual. Esa variacion afecta a un puñado de tweets en el borde del threshold.

### Politica de filtrado (resumen por fuente)

La regla general que sigue el modulo: **>= 10 palabras solo en las fuentes con cola corta ruidosa** (tweets, intervenciones, parrafos de leyes, enmiendas con texto trivial); **sin filtro de largo** en manifiestos que ya vienen pre-segmentados por sus anotadores.

- **Manifestos**. **Sin filtro de largo**. Los manifiestos vienen pre-segmentados en *quasi-sentences* por los anotadores del Manifesto Project (MARPOR), que es la unidad nativa de codificacion del esquema. Filtrar por largo equivaldria a descartar texto ya validado por expertos como codificable, y ademas sub-representaria al PCF (39 quasi-frases en total, estilo telegrafico).
- **Amendements**. **>= 10 palabras** sobre el texto concatenado `dispositif + expose_sommaire`, ademas de `match_confianza` alta/media entre el numero de scrutin y el texto de la enmienda. La distribucion del corpus tiene mediana ~206 palabras, asi que el filtro corta ~5% formado mayormente por filas donde ambos campos del CSV vienen vacios (NaN) y la concatenacion produce texto basura ("nan nan") y por enmiendas tipo "Supprimer cet article".
- **Lois**. Cada ley es un texto largo (cientos o miles de palabras); para que el classifier reciba unidades coherentes se la parte en **parrafos** y se filtran los parrafos con **< 10 palabras** (descarta encabezados, referencias huerfanas y fragmentos de tabla). Solo se usan leyes con `texto_confianza == "alta"`.
- **Tweets**. Limpieza previa: se sacan urls, menciones `@`, hashtags `#`, se normaliza espacios. Luego se filtran tweets con **< 10 palabras** (descarta puro emoji, urls residuales o reactivos cortos tipo "merci!").
- **Interventions**. Cascada de tres filtros sobre el corpus crudo del hemiciclo XV (949 718 intervenciones):
  1. `deputy_id` no nulo → 661 690 (descarta intervenciones de presidentes de sesion, primeros ministros, ministros, secretarios de Estado y demas no-cohorte).
  2. `>= 10 palabras` → 412 535 (descarta interjecciones tipo "Tres bien!", "Merci.", "Mme la Presidente.", "Sur cet amendement.").
  3. No procedurales (regex) → **338 192** (descarta formulas tipo "la seance est ouverte/suspendue/reprise", "l'ordre du jour appelle", "je mets aux voix", "le scrutin est ouvert", "la parole est a").

## Pipeline

Implementado en [`common/classifier_runner.py`](common/classifier_runner.py). Cada `run.py` (uno por fuente) carga su CSV, aplica los filtros descritos arriba, llama a `classify_dataframe()` y guarda los resultados en `<fuente>/results/`.

1. **Carga del modelo y tokenizer**. `xlm-roberta-large` tokenizer + `manifestoberta-...-2024-1-1` head fine-tuneado, en GPU si esta disponible (orden de preferencia: `mps` → `cuda` → `cpu`).
2. **Tokenizacion en batch**. Cada documento se trunca a 200 tokens (igual que en el entrenamiento) con padding a longitud fija.
3. **Inferencia**. Forward pass con `torch.inference_mode()`, softmax sobre los 56 logits de salida, batch size 16 (32 para tweets que son cortos).
4. **Top-K + dominio**. Para cada doc se guardan top-1, top-2 y top-3 (label + codigo + probabilidad), y el dominio (1..7) derivado del primer digito del codigo top-1.
5. **Persistencia**. Una fila por documento en `predictions.csv`, mas tres agregados (`topic_distribution.csv`, `domain_distribution.csv`, `summary.json`).

### Las 56 categorias y los 7 dominios MARPOR

El esquema MARPOR (Manifesto Research on Political Representation, antes Comparative Manifesto Project) es la taxonomia estandar de la ciencia politica comparada para clasificar contenido programatico de partidos. Los 7 dominios y ejemplos de codigos:

| Dominio | Nombre | Ejemplos |
|---|---|---|
| 1 | External Relations | 101 Foreign Special Relationships+, 104 Military+, 107 Internationalism+, 108 European Union+ |
| 2 | Freedom and Democracy | 201 Freedom and Human Rights, 202 Democracy, 203 Constitutionalism+ |
| 3 | Political System | 301 Federalism, 303 Governmental and Administrative Efficiency, 305 Political Authority |
| 4 | Economy | 401 Free Market Economy, 403 Market Regulation, 410 Economic Growth+, 411 Technology and Infrastructure |
| 5 | Welfare and Quality of Life | 501 Environmental Protection+, 503 Equality+, 504 Welfare State Expansion, 506 Education Expansion |
| 6 | Fabric of Society | 601 National Way of Life+, 603 Traditional Morality+, 605 Law and Order+ |
| 7 | Social Groups | 701 Labour Groups+, 705 Underprivileged Minority Groups, 706 Non-Economic Demographic Groups |

Lista completa con definiciones: <https://manifestoproject.wzb.eu/coding_schemes/mp_v5>.

### Configuracion por fuente

| Fuente | `text_col` (input) | `extra_cols` preservadas | `batch_size` | `device` |
|---|---|---|---|---|
| manifestos | `text` (quasi-frase) | `cmp_code`, `partido` | 16 | mps |
| amendements | `texto_completo` (dispositif + expose_sommaire) | `numero_scrutin`, `match_confianza` | 16 | mps |
| lois | `paragraph` (texto JORF en parrafos) | `dossier_id` | 16 | mps |
| tweets | `clean_text` | `deputy_id`, `political_group` | 32 | mps |
| interventions | `text` | `deputy_id`, `political_group` | 16 | mps |

## Detalle de la corrida

Numeros reales medidos en este repo (Apple Silicon M2/M3, MPS):

| Fuente | Docs clasificados | Tiempo total | docs/seg | `batch_size` | Dispositivo |
|---|---:|---:|---:|---:|---|
| manifestos    | 3 801   | 3 min        | 20.79 | 16 | mps |
| amendements   | 2 575   | 2 min        | 19.60 | 16 | mps |
| lois          | 23 267  | 19 min       | 20.50 | 16 | mps |
| tweets        | 224 466 | 2 h 46 min   | 22.48 | 32 | mps |
| interventions | 338 192 | 4 h 57 min   | 18.98 | 16 | mps |

> Costo total: ~8 h de GPU local sumando los cinco corpus. tweets e interventions son los dos pesados; los otros tres son rapidos.

## Salidas (que se genera por fuente)

Cada `<fuente>/results/` contiene:

| Archivo | Contenido |
|---|---|
| `predictions.csv` | una fila por documento: `text` (truncado a 300 chars), `top1_label`, `top1_code`, `top1_prob`, `top2_*`, `top3_*`, `domain`, mas las `extra_cols` (deputy_id / political_group / cmp_code / numero_scrutin segun fuente) |
| `topic_distribution.csv` | recuento y porcentaje del top-1 por categoria MARPOR (las 56) |
| `domain_distribution.csv` | recuento y porcentaje por dominio (1..7) |
| `summary.json` | metadata de la corrida: modelo, n_documentos, segundos, docs/seg, device, batch_size, top-10 categorias y distribucion por dominio |
| `run.log` | log textual emitido por `run.py` (output line-buffered) |

## Resultados

Todas las cifras estan tomadas directamente de los archivos generados por la corrida en `<fuente>/results/`. Para cada fuente se muestran:

1. la **distribucion por dominio** (1..7), util para una vision macro,
2. la **distribucion por categoria** (las 25 mas frecuentes; el archivo CSV trae las 56).

### 1) Manifestos (programas electorales 2017) — 3 801 quasi-frases

**Distribucion por dominio**

| Dominio | Nombre | Docs | % |
|---|---|---:|---:|
| 5 | Welfare and Quality of Life | 1 168 | 30.73 |
| 4 | Economy | 758 | 19.94 |
| 6 | Fabric of Society | 502 | 13.21 |
| 1 | External Relations | 396 | 10.42 |
| 3 | Political System | 353 | 9.29 |
| 7 | Social Groups | 344 | 9.05 |
| 2 | Freedom and Democracy | 280 | 7.37 |

**Top-25 categorias MARPOR**

| # | Codigo | Etiqueta | Docs | % |
|--:|:--:|---|---:|---:|
| 1 | 504 | Welfare State Expansion | 410 | 10.79 |
| 2 | 503 | Equality: Positive | 278 | 7.31 |
| 3 | 605 | Law and Order: Positive | 240 | 6.31 |
| 4 | 506 | Education Expansion | 225 | 5.92 |
| 5 | 202 | Democracy | 205 | 5.39 |
| 6 | 701 | Labour Groups: Positive | 202 | 5.31 |
| 7 | 411 | Technology and Infrastructure | 190 | 5.00 |
| 8 | 501 | Environmental Protection: Positive | 172 | 4.53 |
| 9 | 403 | Market Regulation | 157 | 4.13 |
| 10 | 108 | European Community/Union: Positive | 156 | 4.10 |
| 11 | 305 | Political Authority | 140 | 3.68 |
| 12 | 303 | Governmental and Administrative Efficiency | 138 | 3.63 |
| 13 | 402 | Incentives | 127 | 3.34 |
| 14 | 601 | National Way of Life: Positive | 122 | 3.21 |
| 15 | 107 | Internationalism: Positive | 119 | 3.13 |
| 16 | 416 | Anti-Growth Economy: Positive | 107 | 2.82 |
| 17 | 703 | Agriculture and Farmers: Positive | 78 | 2.05 |
| 18 | 502 | Culture: Positive | 73 | 1.92 |
| 19 | 104 | Military: Positive | 64 | 1.68 |
| 20 | 201 | Freedom and Human Rights | 54 | 1.42 |
| 21 | 604 | Traditional Morality: Negative | 51 | 1.34 |
| 22 | 606 | Civic Mindedness: Positive | 43 | 1.13 |
| 23 | 301 | Federalism | 41 | 1.08 |
| 24 | 406 | Protectionism: Positive | 41 | 1.08 |
| 25 | 414 | Economic Orthodoxy | 39 | 1.03 |

> Lectura: el corpus de programas refleja la agenda clasica de campaña. Casi un tercio de las quasi-frases caen en *Welfare and Quality of Life*: estado de bienestar, igualdad, educacion, ambiente. Lo siguen Economia (regulacion, infraestructura tecnologica) y Fabric of Society (orden, modo de vida nacional). Es el corpus mas balanceado entre los cinco — coherente con que es el unico explicitamente diseñado para cubrir toda la agenda programatica.

### 2) Amendements (enmiendas votadas en hemicycle) — 2 575 enmiendas

**Distribucion por dominio**

| Dominio | Nombre | Docs | % |
|---|---|---:|---:|
| 5 | Welfare and Quality of Life | 1 107 | 42.99 |
| 4 | Economy | 423 | 16.43 |
| 2 | Freedom and Democracy | 266 | 10.33 |
| 3 | Political System | 264 | 10.25 |
| 6 | Fabric of Society | 253 | 9.83 |
| 7 | Social Groups | 246 | 9.55 |
| 1 | External Relations | 16 | 0.62 |

**Top-25 categorias MARPOR**

| # | Codigo | Etiqueta | Docs | % |
|--:|:--:|---|---:|---:|
| 1 | 504 | Welfare State Expansion | 652 | 25.32 |
| 2 | 403 | Market Regulation | 243 | 9.44 |
| 3 | 501 | Environmental Protection: Positive | 212 | 8.23 |
| 4 | 303 | Governmental and Administrative Efficiency | 189 | 7.34 |
| 5 | 605 | Law and Order: Positive | 185 | 7.18 |
| 6 | 201 | Freedom and Human Rights | 119 | 4.62 |
| 7 | 701 | Labour Groups: Positive | 111 | 4.31 |
| 8 | 202 | Democracy | 108 | 4.19 |
| 9 | 503 | Equality: Positive | 97 | 3.77 |
| 10 | 506 | Education Expansion | 92 | 3.57 |
| 11 | 703 | Agriculture and Farmers: Positive | 89 | 3.46 |
| 12 | 411 | Technology and Infrastructure | 74 | 2.87 |
| 13 | 402 | Incentives | 60 | 2.33 |
| 14 | 301 | Federalism | 55 | 2.14 |
| 15 | 502 | Culture: Positive | 54 | 2.10 |
| 16 | 604 | Traditional Morality: Negative | 33 | 1.28 |
| 17 | 704 | Middle Class and Professional Groups | 32 | 1.24 |
| 18 | 204 | Constitutionalism: Negative | 25 | 0.97 |
| 19 | 416 | Anti-Growth Economy: Positive | 22 | 0.85 |
| 20 | 601 | National Way of Life: Positive | 21 | 0.82 |
| 21 | 304 | Political Corruption | 18 | 0.70 |
| 22 | 203 | Constitutionalism: Positive | 14 | 0.54 |
| 23 | 413 | Nationalisation | 10 | 0.39 |
| 24 | 107 | Internationalism: Positive | 8 | 0.31 |
| 25 | 706 | Non-economic Demographic Groups | 7 | 0.27 |

> Lectura: el corpus de enmiendas esta fuertemente sesgado hacia *Welfare* (43%) y *Economy* (16%): tiene sentido, son las dos arenas mas tocadas por la legislacion XV (presupuesto, salud, fiscalidad, jubilacion, mercado laboral). Llama la atencion la casi-ausencia de External Relations (0.62%): las enmiendas de la Asamblea casi no tocan politica exterior. Tambien se ve un pico de 303 *Governmental and Administrative Efficiency* (7.3%), tipico del lenguaje burocratico de muchas enmiendas tecnicas.

### 3) Lois (parrafos del texto JORF promulgado) — 23 267 parrafos

**Distribucion por dominio**

| Dominio | Nombre | Docs | % |
|---|---|---:|---:|
| 3 | Political System | 6 323 | 27.18 |
| 5 | Welfare and Quality of Life | 5 543 | 23.82 |
| 4 | Economy | 5 295 | 22.76 |
| 6 | Fabric of Society | 2 828 | 12.15 |
| 2 | Freedom and Democracy | 1 588 | 6.83 |
| 7 | Social Groups | 1 453 | 6.24 |
| 1 | External Relations | 237 | 1.02 |

**Top-25 categorias MARPOR**

| # | Codigo | Etiqueta | Docs | % |
|--:|:--:|---|---:|---:|
| 1 | 303 | Governmental and Administrative Efficiency | 5 570 | 23.94 |
| 2 | 504 | Welfare State Expansion | 3 158 | 13.57 |
| 3 | 403 | Market Regulation | 2 190 | 9.41 |
| 4 | 605 | Law and Order: Positive | 2 174 | 9.34 |
| 5 | 411 | Technology and Infrastructure | 2 016 | 8.66 |
| 6 | 501 | Environmental Protection: Positive | 1 039 | 4.47 |
| 7 | 701 | Labour Groups: Positive | 960 | 4.13 |
| 8 | 301 | Federalism | 612 | 2.63 |
| 9 | 506 | Education Expansion | 596 | 2.56 |
| 10 | 201 | Freedom and Human Rights | 564 | 2.42 |
| 11 | 604 | Traditional Morality: Negative | 506 | 2.17 |
| 12 | 402 | Incentives | 498 | 2.14 |
| 13 | 202 | Democracy | 465 | 2.00 |
| 14 | 203 | Constitutionalism: Positive | 456 | 1.96 |
| 15 | 503 | Equality: Positive | 411 | 1.77 |
| 16 | 414 | Economic Orthodoxy | 354 | 1.52 |
| 17 | 502 | Culture: Positive | 339 | 1.46 |
| 18 | 703 | Agriculture and Farmers: Positive | 253 | 1.09 |
| 19 | 704 | Middle Class and Professional Groups | 151 | 0.65 |
| 20 | 304 | Political Corruption | 132 | 0.57 |
| 21 | 108 | European Community/Union: Positive | 108 | 0.46 |
| 22 | 204 | Constitutionalism: Negative | 103 | 0.44 |
| 23 | 601 | National Way of Life: Positive | 89 | 0.38 |
| 24 | 107 | Internationalism: Positive | 79 | 0.34 |
| 25 | 705 | Underprivileged Minority Groups | 74 | 0.32 |

> Lectura: el texto promulgado tiene la firma estilistica del lenguaje legal-administrativo. La categoria 303 *Governmental and Administrative Efficiency* sola se lleva un 24% — es el codigo prototipico de la maquinaria del Estado, y aparece masivamente en parrafos de tipo "Le ministre charge de... fixe par decret en Conseil d'Etat...". Le sigue Welfare (codigo bandera de toda ley con prestaciones, jubilacion, salud), Economy (regulacion de mercados, sectores) y *Law and Order* (codigo penal, seguridad, codigo del trabajo). Casi no hay relaciones externas, coherente con que las leyes XV son mayoritariamente domesticas.

### 4) Tweets (cohorte de diputados, 2017-2025) — 224 466 tweets

**Distribucion por dominio**

| Dominio | Nombre | Docs | % |
|---|---|---:|---:|
| 3 | Political System | 67 562 | 30.10 |
| 5 | Welfare and Quality of Life | 55 046 | 24.52 |
| 6 | Fabric of Society | 29 461 | 13.12 |
| 4 | Economy | 21 367 | 9.52 |
| 1 | External Relations | 21 118 | 9.41 |
| 2 | Freedom and Democracy | 16 646 | 7.42 |
| 7 | Social Groups | 13 266 | 5.91 |

**Top-25 categorias MARPOR**

| # | Codigo | Etiqueta | Docs | % |
|--:|:--:|---|---:|---:|
| 1 | 305 | Political Authority | 59 409 | 26.47 |
| 2 | 504 | Welfare State Expansion | 19 272 | 8.59 |
| 3 | 605 | Law and Order: Positive | 13 741 | 6.12 |
| 4 | 502 | Culture: Positive | 13 621 | 6.07 |
| 5 | 202 | Democracy | 10 473 | 4.67 |
| 6 | 411 | Technology and Infrastructure | 10 294 | 4.59 |
| 7 | 503 | Equality: Positive | 9 150 | 4.08 |
| 8 | 107 | Internationalism: Positive | 7 543 | 3.36 |
| 9 | 703 | Agriculture and Farmers: Positive | 7 517 | 3.35 |
| 10 | 501 | Environmental Protection: Positive | 7 390 | 3.29 |
| 11 | 601 | National Way of Life: Positive | 6 769 | 3.02 |
| 12 | 201 | Freedom and Human Rights | 5 847 | 2.60 |
| 13 | 506 | Education Expansion | 5 609 | 2.50 |
| 14 | 104 | Military: Positive | 4 016 | 1.79 |
| 15 | 108 | European Community/Union: Positive | 3 676 | 1.64 |
| 16 | 606 | Civic Mindedness: Positive | 3 676 | 1.64 |
| 17 | 701 | Labour Groups: Positive | 3 083 | 1.37 |
| 18 | 301 | Federalism | 3 075 | 1.37 |
| 19 | 304 | Political Corruption | 3 059 | 1.36 |
| 20 | 403 | Market Regulation | 2 745 | 1.22 |
| 21 | 604 | Traditional Morality: Negative | 2 426 | 1.08 |
| 22 | 106 | Peace | 2 296 | 1.02 |
| 23 | 402 | Incentives | 2 217 | 0.99 |
| 24 | 303 | Governmental and Administrative Efficiency | 2 012 | 0.90 |
| 25 | 416 | Anti-Growth Economy: Positive | 1 834 | 0.82 |

> Lectura: el tweet politico esta dominado por **305 Political Authority** (26.5% — uno de cada cuatro tweets): es el codigo "yo o mi partido somos competentes para gobernar / X es incompetente / candidatos y cargos / liderazgo". Es el codigo natural de la comunicacion electoral y de auto-promocion en redes ("nous proposons", "le gouvernement echoue", "le president decide"). Comparado con manifestos, en Twitter aparecen mucho mas *Internationalism* (3.4%), *Military* (1.8%) y *Peace* (1%) — los diputados usan Twitter para reaccionar a noticias internacionales (Ucrania, Israel, OTAN) que casi no tocan en sus enmiendas.

### 5) Interventions (hemicycle XV, 2017-2022) — 338 192 intervenciones

**Distribucion por dominio**

| Dominio | Nombre | Docs | % |
|---|---|---:|---:|
| 3 | Political System | 123 696 | 36.58 |
| 5 | Welfare and Quality of Life | 75 639 | 22.37 |
| 2 | Freedom and Democracy | 42 666 | 12.62 |
| 4 | Economy | 36 243 | 10.72 |
| 6 | Fabric of Society | 30 738 | 9.09 |
| 7 | Social Groups | 20 369 | 6.02 |
| 1 | External Relations | 8 841 | 2.61 |

**Top-25 categorias MARPOR**

| # | Codigo | Etiqueta | Docs | % |
|--:|:--:|---|---:|---:|
| 1 | 305 | Political Authority | 91 208 | 26.97 |
| 2 | 504 | Welfare State Expansion | 38 566 | 11.40 |
| 3 | 202 | Democracy | 30 172 | 8.92 |
| 4 | 303 | Governmental and Administrative Efficiency | 20 133 | 5.95 |
| 5 | 605 | Law and Order: Positive | 14 094 | 4.17 |
| 6 | 503 | Equality: Positive | 11 552 | 3.42 |
| 7 | 411 | Technology and Infrastructure | 11 548 | 3.41 |
| 8 | 403 | Market Regulation | 11 242 | 3.32 |
| 9 | 501 | Environmental Protection: Positive | 10 607 | 3.14 |
| 10 | 604 | Traditional Morality: Negative | 10 013 | 2.96 |
| 11 | 506 | Education Expansion | 9 327 | 2.76 |
| 12 | 301 | Federalism | 9 220 | 2.73 |
| 13 | 703 | Agriculture and Farmers: Positive | 8 606 | 2.54 |
| 14 | 201 | Freedom and Human Rights | 8 063 | 2.38 |
| 15 | 701 | Labour Groups: Positive | 7 895 | 2.33 |
| 16 | 502 | Culture: Positive | 5 572 | 1.65 |
| 17 | 402 | Incentives | 5 164 | 1.53 |
| 18 | 108 | European Community/Union: Positive | 3 283 | 0.97 |
| 19 | 304 | Political Corruption | 3 050 | 0.90 |
| 20 | 107 | Internationalism: Positive | 2 671 | 0.79 |
| 21 | 416 | Anti-Growth Economy: Positive | 2 505 | 0.74 |
| 22 | 601 | National Way of Life: Positive | 2 502 | 0.74 |
| 23 | 204 | Constitutionalism: Negative | 2 370 | 0.70 |
| 24 | 414 | Economic Orthodoxy | 2 258 | 0.67 |
| 25 | 704 | Middle Class and Professional Groups | 2 233 | 0.66 |

> Lectura: las intervenciones del hemiciclo replican el patron de Twitter en el codigo dominante (305 *Political Authority*, 27%) pero cambian los pesos en torno a la mecanica institucional. Aparece un peso mucho mayor de **202 Democracy** (8.9% vs 4.7% en Twitter) y **303 Governmental and Administrative Efficiency** (5.9%): son los codigos del lenguaje parlamentario sobre como se hacen las cosas — debate, voto, procedimiento legislativo, mocion, comision. Tambien es interesante el peso de **604 *Traditional Morality: Negative*** (3%): incluye discusiones sobre PMA, fin-de-vida, laicidad, IVG — temas valorados por las leyes XV. La cola de External Relations es muy fina (2.6%): el hemiciclo toca poca politica exterior, igual que en enmiendas.

### Lectura comparada (los cinco corpus de un vistazo)

Top-1 categoria MARPOR por fuente, en la misma tabla:

| # | manifestos (3 801) | amendements (2 575) | lois (23 267) | tweets (224 466) | interventions (338 192) |
|--:|---|---|---|---|---|
| 1 | **504** Welfare State Expansion (10.8%) | **504** Welfare State Expansion (25.3%) | **303** Govt. & Admin. Efficiency (23.9%) | **305** Political Authority (26.5%) | **305** Political Authority (27.0%) |
| 2 | 503 Equality+ (7.3%) | 403 Market Regulation (9.4%) | 504 Welfare State Expansion (13.6%) | 504 Welfare State Expansion (8.6%) | 504 Welfare State Expansion (11.4%) |
| 3 | 605 Law and Order+ (6.3%) | 501 Environmental Protection+ (8.2%) | 403 Market Regulation (9.4%) | 605 Law and Order+ (6.1%) | 202 Democracy (8.9%) |
| 4 | 506 Education Expansion (5.9%) | 303 Govt. & Admin. Efficiency (7.3%) | 605 Law and Order+ (9.3%) | 502 Culture+ (6.1%) | 303 Govt. & Admin. Efficiency (5.9%) |
| 5 | 202 Democracy (5.4%) | 605 Law and Order+ (7.2%) | 411 Technology & Infrastructure (8.7%) | 202 Democracy (4.7%) | 605 Law and Order+ (4.2%) |

Patron observable:

- **manifestos** → corpus mas balanceado, dominado por la agenda de bienestar e igualdad. Refleja la promesa de campaña.
- **amendements** → fuertemente sesgado a *Welfare* (prestaciones, salud, jubilacion) y *Economy* (regulacion). Casi sin politica exterior.
- **lois** → dominado por el codigo legalista 303 (mecanica administrativa) por la naturaleza prescriptiva del JORF.
- **tweets** + **interventions** → dominados por **305 Political Authority**, el codigo de la comunicacion politica sobre quien decide / quien gobierna / quien lidera. Twitter ademas gana en politica exterior y militar; el hemiciclo gana en *Democracy* y procedimiento.

Estos contrastes son justamente la motivacion del cruce 5-fuentes: un mismo diputado dice cosas distintas segun donde habla. La superposicion en *Welfare State Expansion* (siempre top-3) sugiere que es la columna vertebral del corpus politico XV; las divergencias estan en como cada arena (programa, ley, tweet, intervencion) modula esa agenda.

## Validacion contra MARPOR (ground truth humano)

Para responder *"¿el modelo, entrenado en 38 idiomas, sigue siendo confiable en frances politico de la XV legislatura?"* se compara la prediccion top-1/top-3 contra el `cmp_code` humano de MARPOR sobre el unico corpus que tiene etiquetas reales (los manifiestos 2017). Script: [`validate_against_marpor.py`](validate_against_marpor.py). Resultados en [`validation/`](validation/).

### Metricas globales (n = 3 430 quasi-frases con `cmp_code` utilizable)

| Metrica | Valor | Esperado por la model card | Observacion |
|---|---:|---:|---|
| Accuracy top-1 (codigo exacto) | **58.3%** | 57.0% | el modelo se desempeña ligeramente mejor de lo prometido en frances |
| Accuracy top-3 (codigo en top-3) | **82.0%** | 81.0% | reproduce el numero del paper |
| Accuracy a nivel de **dominio** (1-7) | **70.3%** | — | 7 de cada 10 quasi-frases caen en el dominio correcto |
| Macro F1 (sobre las 56 categorias) | **0.44** | — | tipico para clasificacion multiclase muy desbalanceada |

> Estos numeros son **consistentes con la performance reportada por los autores** del modelo en su paper original. Significa que el corpus frances XV no es un caso fuera de distribucion, y que las predicciones a nivel de dominio (que son las que mas se interpretan en una tesis) tienen 7 de cada 10 correctas.

### Confusion matrix por dominio (filas = verdadero, columnas = predicho)

| → | 1 | 2 | 3 | 4 | 5 | 6 | 7 | All |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| **1** External | **246** | 6 | 8 | 14 | 5 | 8 | 3 | 290 |
| **2** Freedom | 18 | **158** | 18 | 1 | 11 | 15 | 1 | 222 |
| **3** Pol. Sys. | 7 | 39 | **182** | 24 | 42 | 24 | 5 | 323 |
| **4** Economy | 36 | 6 | 27 | **498** | 115 | 11 | 28 | 721 |
| **5** Welfare | 15 | 5 | 27 | 90 | **724** | 19 | 24 | 904 |
| **6** Society | 29 | 27 | 27 | 24 | 85 | **358** | 8 | 558 |
| **7** Social Gr. | 4 | 9 | 16 | 42 | 84 | 13 | **244** | 412 |
| **All** | 355 | 250 | 305 | 693 | 1066 | 448 | 313 | 3 430 |

> La diagonal concentra la mayoria de la masa, como se espera. Las confusiones tipicas son entre dominios cercanos: 4-5 (Economia ↔ Welfare, frecuente porque presupuesto y prestaciones se solapan), 5-7 (Welfare ↔ Social Groups, porque "ayudas a familias" puede ir a 503 *Equality* o 706 *Non-economic Demographic Groups*) y 6-5 (Fabric of Society ↔ Welfare).

### Reportes adicionales

- `validation/per_code_classification_report.csv` — precision / recall / f1 por las 56 categorias.
- `validation/top50_errors_high_confidence.csv` — los 50 errores donde el modelo predijo con mayor confianza un codigo que no era el ground-truth (util para inspeccion cualitativa).

## Reproducir las corridas

Cada fuente tiene un `run.py` autocontenido que lee su CSV de entrada, aplica los filtros descritos arriba y llama a `classify_dataframe()`. Cualquiera se puede correr de forma independiente.

```bash
cd /Users/agustin.solis/Tesis/french_deputies/manifestoberta_analysis
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Para ver el progreso en vivo (sin nohup) y guardar el log al mismo tiempo, conviene combinar `python3 -u` con `tee` (NO usar `head`, corta con SIGPIPE las corridas largas):

```bash
# manifestos (~3 min)
python3 -u manifestos/run.py 2>&1 | tee manifestos/results/run.log

# amendements (~2 min)
python3 -u amendements/run.py 2>&1 | tee amendements/results/run.log

# lois (~19 min)
python3 -u lois/run.py 2>&1 | tee lois/results/run.log

# tweets (~2 h 46 min)
python3 -u tweets/run.py 2>&1 | tee tweets/results/run.log

# interventions (~4 h 57 min)
python3 -u interventions/run.py 2>&1 | tee interventions/results/run.log

# validacion contra MARPOR (manifestos)
python3 -u validate_against_marpor.py 2>&1 | tee validation/run.log
```

> Pausar/reanudar una corrida larga: `Ctrl+Z` para suspender (SIGTSTP), `fg` para retomar en primer plano, `bg` para mandarla a segundo plano. Equivalente con PID: `kill -STOP <pid>` y `kill -CONT <pid>`. La GPU MPS libera automaticamente al pausar el proceso.

## Notas y limitaciones

- **Truncamiento a 200 tokens**. Es el max len del entrenamiento del modelo y la model card lo recomienda explicitamente. En tweets nunca activa (todos < 200 tokens), en intervenciones largas y leyes si trunca: lo recomendado es alimentar al modelo con la unidad mas chica posible (intervencion completa, parrafo de ley, enmienda) en vez de una sesion entera o un texto JORF entero.
- **Una etiqueta por documento**. El esquema MARPOR original asigna **una sola** quasi-frase a una sola categoria (por eso los manifiestos vienen pre-segmentados). Cuando aplicamos el modelo a un tweet, intervencion o parrafo, asumimos que el documento es coherente tematicamente. Esto vale en general (los tweets son cortos por diseño, las intervenciones largas se cortan en otra etapa, los parrafos de ley son unidades semanticas) pero no es perfecto. Para un texto multitematico, el top-1 reduce informacion; por eso guardamos top-1, top-2 y top-3 + probabilidades en `predictions.csv`.
- **Calibracion de probabilidades**. Las `top1_prob` no estan calibradas. Sirven para rankear (ej. top-50 errores de alta confianza) pero no para interpretar literalmente como "estoy 73% seguro".
- **Categorias muy raras**. Codigos como 408 (*Economic Goals*), 415 (*Marxist Analysis: Positive*), 705 (*Underprivileged Minorities*) o 507 (*Education Limitation*) son intrinsicamente raros en el corpus MARPOR original — su F1 individual es bajo y sus predicciones son ruidosas. La interpretacion solida pasa por dominio o por agrupaciones (ej. Welfare = 501-507).
- **Comparabilidad con bertopic_analysis**. Los corpus son **los mismos** (mismos filtros, mismos `text_id` cuando aplican). El `predictions.csv` de cada fuente puede joinearse con el `topics_per_*.csv` de su gemelo en `bertopic_analysis/` por la columna identificadora correspondiente (`deputy_id`/`numero_scrutin`/`dossier_id`/`partido`).

## Estructura del modulo

```
manifestoberta_analysis/
├── README.md                      # este documento
├── requirements.txt               # transformers, torch, pandas, scikit-learn
├── common/
│   └── classifier_runner.py       # logica compartida (load_model, classify_dataframe)
├── manifestos/
│   ├── run.py
│   └── results/                   # predictions.csv + topic_distribution.csv + ...
├── amendements/
│   ├── run.py
│   └── results/
├── lois/
│   ├── run.py
│   └── results/
├── tweets/
│   ├── run.py
│   └── results/
├── interventions/
│   ├── run.py
│   └── results/
├── validate_against_marpor.py     # accuracy top-1/3, confusion matrix, F1, top errores
└── validation/                    # outputs del script anterior
    ├── summary.json
    ├── confusion_matrix_domain.csv
    ├── per_code_classification_report.csv
    └── top50_errors_high_confidence.csv
```

## Modulo hermano

[`bertopic_analysis/`](../bertopic_analysis/) es la version **no supervisada** del mismo analisis sobre los mismos cinco corpus: en vez de mapear cada documento a una de 56 categorias preexistentes, descubre 25 topicos por fuente via embeddings + UMAP + HDBSCAN. Idealmente se leen juntos: BERTopic muestra **que tematicas emergen del corpus** (con su vocabulario propio: "macron", "ukraine", "covid"), manifestoberta muestra **donde caen esos topicos en la grilla MARPOR** que la ciencia politica viene usando desde 1979.
