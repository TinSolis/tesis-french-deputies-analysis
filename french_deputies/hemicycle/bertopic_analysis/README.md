# BERTopic — Análisis de intervenciones en hemiciclo

Análisis de topic modeling sobre las intervenciones parlamentarias de la XV legislatura (2017–2022),
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar los **temas centrales del debate parlamentario** y las palabras
que transmiten ideas sustantivas en el hemiciclo francés. El script añade
stopwords parlamentarios específicos (madame *(señora)*, monsieur *(señor)*, président *(presidente)*, amendement *(enmienda)*, etc.)
para filtrar la jerga procedimental y captar el contenido ideológico.
Además filtra intervenciones con menos de 80 palabras (que suelen ser procedimentales)
y elimina notas de aplausos (applaudissements), suspensiones de sesión, etc.

## Datos de entrada

- `../processed/interventions_xv_sample5000.csv` — muestra de 5,000 intervenciones
- Si no existe, usa `interventions_xv_2017_2022_with_deputies.csv.gz` (muestreando 20k)

## Ejecución

```bash
cd scripts/
python3 run_bertopic_hemicycle.py
```

## Temas detectados (resumen)

El modelo identificó **5 temas** sustantivos (tras filtrar intervenciones procedimentales):

| Topic | Palabras clave (francés) | Traducción |
|------:|--------------------------|------------|
| 0 | organisations syndicales, réforme, syndicales, sujet | organizaciones sindicales, reforma, sindicales, asunto |
| 1 | politique, politiques, parlementaires, france, démocratie | política, políticas, parlamentarios, Francia, democracia |
| 2 | contre terrorisme, état urgence, antiterroriste, actes terroristes | contra el terrorismo, estado de emergencia, antiterrorista, actos terroristas |
| 3 | société, réformes, réforme, travail, évoluer | sociedad, reformas, reforma, trabajo, evolucionar |
| 4 | état urgence, contrôle parlementaire, autorité, état droit | estado de emergencia, control parlamentario, autoridad, estado de derecho |

**Top 10 palabras más frecuentes** (sin stopwords):

| Palabra | Traducción | Frecuencia |
|---------|------------|----------:|
| salariés | asalariados | 726 |
| travail | trabajo | 647 |
| entreprise | empresa | 599 |
| état | estado | 586 |
| entreprises | empresas | 497 |
| urgence | urgencia/emergencia | 361 |
| droit | derecho | 360 |
| social | social | 358 |
| dialogue | diálogo | 292 |
| sécurité | seguridad | 210 |

## Resultados (en `results/`)

| Archivo | Contenido |
|---------|-----------|
| `topic_info.csv` | Tabla de temas detectados |
| `top_words_per_topic.csv` | Palabras clave por tema con puntaje |
| `document_topics.csv` | Cada intervención con su tema y grupo político |
| `topics_per_group.csv` | Distribución de temas por grupo parlamentario |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes (sin stopwords) |
| `viz_*.html` | Visualizaciones interactivas (barchart *(barras)*, mapa de temas, heatmap *(mapa de calor)*, jerarquía, por grupo) |

## Dependencias

Ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
