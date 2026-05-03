# BERTopic — Análisis de intervenciones en hemiciclo

Análisis de topic modeling sobre las intervenciones parlamentarias de la XV legislatura (2017–2022),
usando [BERTopic](https://maartengr.github.io/BERTopic/) con embeddings multilingües.

## Objetivo

Identificar los **temas centrales del debate parlamentario** y las palabras que transmiten
ideas sustantivas en el hemiciclo francés. El script:

- Filtra intervenciones con **≥80 palabras** (las más cortas son procedimentales)
- Excluye entradas de aplausos (applaudissements *(aplausos)*), suspensiones de sesión, votaciones
- Aplica stopwords en francés + jerga parlamentaria específica:
  madame *(señora)*, monsieur *(señor)*, président *(presidente)*, amendement *(enmienda)*,
  rapporteur *(ponente)*, commission *(comisión)*, assemblée *(asamblea)*, etc.
- Usa embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`)
- Extrae n-gramas (1 y 2 palabras) y refina con `KeyBERTInspired`
- Calcula frecuencia global y temas por grupo parlamentario

## Datos de entrada

- `../processed/interventions_xv_sample5000.csv` — muestra de 5,000 intervenciones
- Si no existe, usa `interventions_xv_2017_2022_with_deputies.csv.gz` (muestreando 20k)

Columnas usadas: `intervention_plain` (texto), `nb_mots` (conteo de palabras), `political_group_abbrev` (grupo político).

## Ejecución

```bash
cd scripts/
python3 run_bertopic_hemicycle.py
```

Tarda ~40 segundos con la muestra de 5,000.

## Qué genera

En `results/`:
- **CSV** con temas detectados, palabras clave, asignación por intervención y por grupo
- **HTML** con visualizaciones interactivas
- **`RESULTADOS.md`** — resumen narrativo con hallazgos, traducciones, e insights

Ver **[results/RESULTADOS.md](results/RESULTADOS.md)** para los datos y conclusiones.

## Dependencias

```bash
pip install bertopic sentence-transformers pandas scikit-learn plotly
```

O ver `requirements_bertopic.txt` en la raíz de `french_deputies/`.
