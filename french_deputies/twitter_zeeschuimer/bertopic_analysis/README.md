# BERTopic — Análisis de tweets de diputados franceses

Análisis de topic modeling sobre los tweets capturados de los diputados de la XV legislatura (2017–2022),
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar las **palabras e ideas centrales** del discurso político en Twitter,
más allá de las palabras conectoras (stopwords). El script:

- Limpia el texto (elimina URLs, menciones, conserva el texto de hashtags)
- Filtra tweets con menos de 30 caracteres
- Toma una muestra de 50,000 tweets por rendimiento
- Usa embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`)
- Aplica stopwords en francés + términos de Twitter (http, rt, amp, via)
- Extrae n-gramas (1 y 2 palabras) con `CountVectorizer`
- Refina representaciones con `KeyBERTInspired` para mayor coherencia
- Calcula frecuencia global de palabras y temas por grupo parlamentario

## Datos de entrada

- `../processed/tweets_text_only.csv` — texto de tweets con grupo político (columnas: `text`, `political_group_abbrev`)

## Ejecución

```bash
cd scripts/
python3 run_bertopic_tweets.py
```

Tarda ~2 minutos en una laptop estándar (embedding de 50k documentos).

## Qué genera

En `results/`:
- **CSV** con temas detectados, palabras clave, asignación por documento y por grupo parlamentario
- **HTML** con visualizaciones interactivas (abrir en navegador)
- **`RESULTADOS.md`** — resumen narrativo con los principales hallazgos, temas traducidos al español, e insights

Ver **[results/RESULTADOS.md](results/RESULTADOS.md)** para los datos y conclusiones.

## Dependencias

```bash
pip install bertopic sentence-transformers pandas scikit-learn plotly
```

O ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
