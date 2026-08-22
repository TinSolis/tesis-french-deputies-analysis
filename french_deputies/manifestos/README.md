# Manifestos — programas electorales de los partidos (Francia 2017)

## Propósito

Almacena los **manifiestos (programmes électoraux)** de los partidos que presentaron candidatos en las **legislativas de junio 2017** (XVe legislatura). La fuente es el **[Manifesto Project (MARPOR)](https://manifesto-project.wzb.eu/)**, que codifica los programas electorales frase por frase con categorías temáticas estandarizadas.

Esto permite asignar a cada diputado de `deputes_2017_2022.csv` la **posición programática oficial** de su partido al momento de la elección, y comparar el texto del manifiesto con lo que se dice en el hemiciclo.

---

## Qué contiene

**10 partidos franceses**, elección legislativa junio 2017, con el **texto completo** de cada programa electoral:

| Partido | Abreviatura | Código MARPOR | RILE (izq ← → der) | Caracteres |
|---|---|---|---|---|
| La France Insoumise | LFI | 31240 | -30.0 | 139,096 |
| Parti Socialiste | PS | 31320 | -28.9 | 8,973 |
| Mouvement Démocrate | MoDem | 31624 | -17.9 | 64,918 |
| Parti Communiste Français | PCF | 31220 | -16.7 | 3,072 |
| Parti Radical de Gauche | PRG | 31230 | -10.1 | 84,406 |
| Europe Écologie - Les Verts | EELV | 31110 | -8.6 | 23,726 |
| La République en Marche | LREM | 31425 | 0.0 | 41,182 |
| Front National | FN | 31720 | +1.7 | 36,170 |
| Union des Démocrates et Indépendants | UDI | 31430 | +13.6 | 31,438 |
| Les Républicains | LR | 31626 | +13.6 | 31,438 |

### Organización de la carpeta

| Carpeta / archivo | Qué hay |
|---|---|
| **`processed/textos_por_partido/`** | **Un `.txt` por partido con el manifiesto completo** (texto corrido, listo para leer o pasar a NLP). Ejemplo: `LFI_31240_201706.txt` contiene "L'Avenir en Commun" entero. |
| **`processed/manifesto_full_texts.csv`** | Lo mismo en formato CSV: una fila por partido, columnas `party_abbrev`, `party_name`, `num_sentences`, `full_text`. |
| **`processed/manifesto_texts.csv`** | Textos **frase por frase** (quasi-sentences) con su código temático MARPOR (`cmp_code`). Útil para análisis por tema. |
| **`processed/party_positions.csv`** | Resumen cuantitativo: `rile` (score izquierda-derecha), `planeco`, `markeco`, `welfare`, `intpeace`, etc. |
| **`data/marpor_core_france_2017.csv`** | Dataset MARPOR completo filtrado: una fila por partido con ~100 columnas de posiciones (% de quasi-sentences por categoría temática). |
| **`data/marpor_corpus_metadata.json`** | Metadatos del corpus: disponibilidad de texto, anotaciones, idioma. |
| **`group_to_party_mapping.csv`** | Tabla de mapeo `political_group_abbrev` → partido MARPOR. |
| **`scripts/download_manifestos.py`** | Script que descarga todo vía API. |

---

## Cómo reproducir

### Requisitos previos

1. **Registrarse** en [manifesto-project.wzb.eu](https://manifesto-project.wzb.eu/) (gratis con email académico).
2. **Generar un API key** desde el perfil (login → Profile → Generate API Key).
3. **Guardar el key** como variable de entorno:

```bash
export MARPOR_API_KEY="mi_key_aqui"
```

### Ejecución

Desde la raíz del repo (**`Tesis/`**):

```bash
export MARPOR_API_KEY="mi_key_aqui"
python3 french_deputies/manifestos/scripts/download_manifestos.py
```

O pasando el key directamente:

```bash
python3 french_deputies/manifestos/scripts/download_manifestos.py --api-key MI_KEY
```

El script hace todo automáticamente:
1. Descarga el dataset principal de MARPOR y filtra Francia 2017 → `data/`
2. Identifica los 10 party codes de esa elección
3. Consulta el corpus y verifica qué manifiestos tienen texto digitalizado
4. Descarga los textos frase por frase con sus códigos temáticos → `processed/manifesto_texts.csv`
5. Guarda posiciones políticas por partido → `processed/party_positions.csv`

Los textos completos (`manifesto_full_texts.csv` y `textos_por_partido/`) se generaron después, de forma manual, concatenando las quasi-sentences.

---

## Cómo se enlaza con los diputados

La cadena de cruce es:

```
deputes_2017_2022.csv  (political_group_abbrev = "FI")
       ↓
group_to_party_mapping.csv  (FI → La France Insoumise → 31240)
       ↓
textos_por_partido/LFI_31240_201706.txt  (texto completo del manifiesto)
       ↓
manifesto_texts.csv  (cada frase con su cmp_code temático)
       ↓
party_positions.csv  (rile = -30.0, welfare, markeco, ...)
```

El mapeo cubre **~85% de los diputados** (los 7 partidos principales: LREM, LR, MoDem, PS, LFI, PCF, FN). Los grupos pequeños (LT, EDS, AGIR-E) son escisiones o coaliciones que MARPOR puede no cubrir individualmente.

---

## Qué significan los códigos temáticos (cmp_code)

MARPOR clasifica cada frase del manifiesto con un código de 3 dígitos. Algunos relevantes para la tesis:

| Código | Dominio | Ejemplo |
|---|---|---|
| `per401` | Free-Market Economy | "Reducir impuestos a empresas" |
| `per403` | Market Regulation | "Regular el sector bancario" |
| `per504` | Welfare State Expansion | "Ampliar cobertura de salud" |
| `per506` | Education Expansion | "Invertir en educación pública" |
| `per601` | National Way of Life: Positive | "Defender la identidad nacional" |
| `per607` | Multiculturalism: Positive | "Celebrar la diversidad cultural" |

El score **`rile`** (right-left) se calcula como diferencia entre códigos "de derecha" y "de izquierda". Va de -100 (extrema izquierda) a +100 (extrema derecha).

Esquema completo: [Category Scheme](https://manifesto-project.wzb.eu/information/documents/handbooks).

---

## Fuentes de cada archivo

- **Dataset MARPOR:** [manifesto-project.wzb.eu/datasets](https://manifesto-project.wzb.eu/datasets) — versión 2025a.
- **Corpus (textos):** descargados vía [API REST](https://manifesto-project.wzb.eu/information/documents/api), versión 2025-1.
- **Mapeo grupos → partidos:** elaborado a partir de `deputes_2017_2022.csv` y la lista de partidos MARPOR.
