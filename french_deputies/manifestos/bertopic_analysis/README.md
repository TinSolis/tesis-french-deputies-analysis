# BERTopic — Análisis de manifiestos electorales (2017)

Análisis de topic modeling sobre los manifiestos de los partidos franceses para las elecciones 2017,
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar los **temas ideológicos centrales** de cada partido a partir de sus
manifiestos codificados por MARPOR (Manifesto Project). El análisis incluye:

- Detección de temas a nivel de quasi-sentence *(cuasi-oración)*
- Frecuencia de palabras clave por partido (top 50 por partido)
- Comparación cruzada de temas entre partidos

## Datos de entrada

- `../processed/manifesto_texts.csv` — quasi-sentences *(cuasi-oraciones)* codificadas (~3,800 frases)
- `../processed/manifesto_full_texts.csv` — mapeo manifesto_id → partido

## Ejecución

```bash
cd scripts/
python3 run_bertopic_manifestos.py
```

## Temas detectados (resumen)

El modelo identificó **37 temas**. Los principales:

| Topic | Palabras clave (francés) | Traducción |
|------:|--------------------------|------------|
| 0 | politiques publiques, parlement, services publics, citoyens, démocratie | políticas públicas, parlamento, servicios públicos, ciudadanos, democracia |
| 1 | salariés, contrat travail, emploi, travailleurs, entreprises | asalariados, contrato de trabajo, empleo, trabajadores, empresas |
| 2 | union européenne, europe, européens, niveau européen | unión europea, Europa, europeos, a nivel europeo |
| 3 | enseignement supérieur, éducation, scolaires, écoles, universités | educación superior, educación, escolares, escuelas, universidades |
| 4 | europe, libertés, majorité, droite centre, identité nationale | Europa, libertades, mayoría, derecha centro, identidad nacional |
| 5 | agriculture, agricole, écologique, environnement, produire | agricultura, agrícola, ecológico, medio ambiente, producir |
| 6 | évasion fiscale, fiscalité, impôts, taxation | evasión fiscal, fiscalidad, impuestos, tributación |
| 7 | politique santé, sanitaire, professionnels santé, soins, hôpitaux | política de salud, sanitario, profesionales de salud, cuidados, hospitales |
| 8 | hommes femmes, égalité réelle, discriminations | hombres mujeres, igualdad real, discriminaciones |
| 11 | immigration, asile, demandeurs | inmigración, asilo, solicitantes |
| 14 | modèle social, justice sociale, protection sociale | modelo social, justicia social, protección social |
| 15 | petites retraites, retraite, durée vie, âge | pensiones pequeñas, jubilación, esperanza de vida, edad |
| 17 | énergies renouvelables, transition énergétique, précarité énergétique | energías renovables, transición energética, precariedad energética |
| 18 | quotient familial, familles, famille, adoption, parents | cociente familiar, familias, familia, adopción, padres |

**Top 10 palabras más frecuentes** (sin stopwords):

| Palabra | Traducción | Frecuencia |
|---------|------------|----------:|
| doit | debe | 380 |
| politique | política | 271 |
| mesures | medidas | 257 |
| faut | hay que / es necesario | 232 |
| permettre | permitir | 192 |
| état | estado | 186 |
| sociale | social | 176 |
| droit | derecho | 175 |
| travail | trabajo | 170 |
| public | público | 161 |

## Resultados (en `results/`)

| Archivo | Contenido |
|---------|-----------|
| `topic_info.csv` | Tabla de temas detectados |
| `top_words_per_topic.csv` | Palabras clave por tema |
| `document_topics.csv` | Cada quasi-sentence *(cuasi-oración)* con su tema y partido |
| `topics_per_party.csv` | Distribución de temas por partido |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes |
| `word_frequency_per_party.csv` | Top 50 palabras por partido |
| `viz_*.html` | Visualizaciones interactivas |

## Dependencias

Ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
