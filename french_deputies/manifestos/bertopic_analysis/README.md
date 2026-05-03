# BERTopic — Análisis de manifiestos electorales (2017)

Análisis de topic modeling sobre los manifiestos de los partidos franceses para las elecciones 2017,
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar los **temas ideológicos centrales** de cada partido a partir de sus manifiestos
codificados por MARPOR (Manifesto Project). El script:

- Trabaja a nivel de quasi-sentence *(cuasi-oración)* — la unidad de codificación de MARPOR
- Filtra frases con menos de 20 caracteres
- Aplica stopwords en francés + términos genéricos de país (france, français, république, etc.)
- Usa embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`)
- Extrae n-gramas (1 y 2 palabras) y refina con `KeyBERTInspired`
- Calcula frecuencia global, frecuencia por partido, y temas por partido
- Mapea cada manifesto_id a su partido usando `manifesto_full_texts.csv`

## Datos de entrada

- `../processed/manifesto_texts.csv` — quasi-sentences *(cuasi-oraciones)* codificadas (~3,800 frases, columnas: `manifesto_id`, `text`)
- `../processed/manifesto_full_texts.csv` — mapeo manifesto_id → partido (columna: `party_abbrev`)

## Ejecución

```bash
cd scripts/
python3 run_bertopic_manifestos.py
```

Tarda ~3 minutos (embedding + clustering de ~3,700 documentos).

## Qué genera

En `results/`:
- **CSV** con temas detectados, palabras clave, asignación por quasi-sentence, temas por partido, y frecuencia de palabras por partido
- **HTML** con visualizaciones interactivas
- **`RESULTADOS.md`** — resumen narrativo con los 37 temas traducidos, insights por partido, y análisis comparativo

Ver **[results/RESULTADOS.md](results/RESULTADOS.md)** para los datos y conclusiones.

## Dependencias

```bash
pip install bertopic sentence-transformers pandas scikit-learn plotly
```

O ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
