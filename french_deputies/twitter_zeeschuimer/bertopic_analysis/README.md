# BERTopic — Análisis de tweets de diputados franceses

Análisis de topic modeling sobre los tweets capturados de los diputados de la XV legislatura (2017–2022),
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar las **palabras e ideas centrales** del discurso político en Twitter,
más allá de las palabras conectoras. El análisis incluye:

- Detección automática de temas (topics) con BERTopic
- Representación refinada de topics con KeyBERTInspired (menos stopwords, más coherencia)
- Frecuencia global de palabras (top 200)
- Temas desglosados por grupo parlamentario

## Datos de entrada

- `../processed/tweets_text_only.csv` — texto de tweets con grupo político
- Se toma una muestra de 50,000 tweets por rendimiento

## Ejecución

```bash
cd scripts/
python3 run_bertopic_tweets.py
```

## Temas detectados (resumen)

El modelo identificó **32 temas**. Los principales:

| Topic | Palabras clave (francés) | Traducción |
|------:|--------------------------|------------|
| 0 | politique, france, démocratie, europe, paris | política, Francia, democracia, Europa, París |
| 1 | enfants, jeunes, familles, parents | niños, jóvenes, familias, padres |
| 2 | eau, environnement, durable | agua, medio ambiente, sostenible |
| 3 | prévention, sanitaire, santé | prevención, sanitario, salud |
| 6 | défense, protection, sécurité, protéger | defensa, protección, seguridad, proteger |
| 9 | justice, peine, dignité, liberté | justicia, pena, dignidad, libertad |
| 10 | travail, travailler, engagé, professionnels | trabajo, trabajar, comprometido, profesionales |
| 11 | femmes, soutenir, soutien | mujeres, apoyar, apoyo |
| 14 | projet loi, proposition loi, environnement | proyecto de ley, proposición de ley, medio ambiente |
| 18 | parlement, europe, européen | parlamento, Europa, europeo |
| 23 | entreprises, entreprise, stratégique | empresas, empresa, estratégico |
| 30 | femmes, défendre, droits, politiques | mujeres, defender, derechos, políticas |

**Top 10 palabras más frecuentes** (sin stopwords):

| Palabra | Traducción | Frecuencia |
|---------|------------|----------:|
| france | Francia | 4,577 |
| merci | gracias | 2,740 |
| contre | contra | 2,388 |
| ans | años | 2,100 |
| français | franceses | 2,025 |
| président | presidente | 2,002 |
| aujourd'hui | hoy | 1,992 |
| loi | ley | 1,985 |
| ministre | ministro | 1,868 |
| soutien | apoyo | 1,735 |

## Resultados (en `results/`)

| Archivo | Contenido |
|---------|-----------|
| `topic_info.csv` | Tabla de temas: id, conteo, nombre, palabras representativas |
| `top_words_per_topic.csv` | Palabras clave por tema con puntaje c-TF-IDF |
| `document_topics.csv` | Cada tweet con su tema asignado y grupo político |
| `topics_per_group.csv` | Distribución de temas por grupo parlamentario |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes (sin stopwords) |
| `viz_barchart.html` | Gráfico de barras de palabras por tema |
| `viz_topics_map.html` | Mapa 2D de proximidad entre temas |
| `viz_heatmap.html` | Matriz de similitud entre temas |
| `viz_hierarchy.html` | Dendrograma jerárquico de temas |
| `viz_topics_per_group.html` | Temas por grupo parlamentario |

## Dependencias

Ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
