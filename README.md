# Tesis — Diputados franceses, discursos, votos, Twitter y manifiestos (2017-2022)

Proyecto de datos para la tesis: diputados de la Assemblée nationale (XVe legislatura 2017-2022), sus intervenciones en el hemiciclo, votaciones sobre leyes, actividad en Twitter y programas electorales de sus partidos. Incluye análisis de **topic modeling (BERTopic)** para comparar los temas de cada fuente por grupo político.

**Documento de referencia:** [Propuesta Memoria .pdf](Propuesta%20Memoria%20.pdf)

---

## Estructura del repositorio

```
Tesis/
├── README.md                              ← Estás aquí
├── Propuesta Memoria .pdf
│
└── french_deputies/
    ├── README.md
    ├── ESTRUCTURA.md
    ├── requirements_bertopic.txt           ← dependencias para BERTopic
    │
    ├── datos_diputados/
    │   ├── data/                           ← CSVs fuente (AN, Twitter, nosdeputes)
    │   ├── processed/
    │   │   └── deputes_2017_2022.csv       ← 668 diputados (id, grupo, circunscripción, Twitter)
    │   └── scripts/
    │
    ├── hemicycle/
    │   ├── fuente/                         ← TSV.gz Regards Citoyens (no en GitHub)
    │   ├── processed/
    │   │   ├── interventions_xv_*.csv.gz   ← ~950k intervenciones (no en GitHub)
    │   │   └── interventions_xv_sample5000.csv
    │   ├── bertopic_analysis/
    │   │   ├── scripts/                    ← run_bertopic_hemicycle.py
    │   │   └── results/                    ← CSVs, HTMLs interactivos, RESULTADOS.md
    │   ├── scripts/
    │   ├── GUIA_IDENTIFICADORES_TESIS.md
    │   └── RESUMEN_CUANTITATIVO.md
    │
    ├── lois_votes/
    │   ├── votes_rd/processed/
    │   │   ├── leyes_votadas_2017_2022.csv ← 373 scrutins
    │   │   ├── votos_por_diputado.csv
    │   │   ├── votos_por_diputado_cohorte.csv
    │   │   └── leyes_texto_oficial.csv
    │   ├── scripts/
    │   └── README_LOIS_VOTES.md
    │
    ├── twitter_zeeschuimer/
    │   ├── captures/                       ← .ndjson Zeeschuimer (no en GitHub)
    │   ├── processed/
    │   │   ├── tweets_with_deputies.csv    ← (no en GitHub)
    │   │   ├── tweets_text_only.csv        ← (no en GitHub)
    │   │   └── deputies_capture_summary.csv
    │   ├── bertopic_analysis/
    │   │   ├── scripts/                    ← run_bertopic_tweets.py
    │   │   └── results/                    ← CSVs, HTMLs interactivos, RESULTADOS.md
    │   ├── scripts/
    │   └── README.md
    │
    └── manifestos/
        ├── data/
        │   ├── marpor_core_france_2017.csv ← dataset MARPOR (10 partidos)
        │   └── marpor_corpus_metadata.json
        ├── processed/
        │   ├── textos_por_partido/         ← un .txt por partido (manifiesto completo)
        │   ├── manifesto_full_texts.csv
        │   ├── manifesto_texts.csv         ← 3,801 frases con código temático
        │   └── party_positions.csv         ← score izquierda-derecha (rile)
        ├── bertopic_analysis/
        │   ├── scripts/                    ← run_bertopic_manifestos.py
        │   └── results/                    ← CSVs, HTMLs interactivos, RESULTADOS.md
        ├── group_to_party_mapping.csv
        ├── scripts/
        └── README.md
```

---

## Qué hay en cada carpeta

| Carpeta | Qué contiene | Cobertura |
|---|---|---|
| **`datos_diputados/`** | Lista base de 668 diputados (id, nombre, grupo político, circunscripción, Twitter) | Todos |
| **`hemicycle/`** | ~950,000 intervenciones en el hemiciclo (texto de debates, tipo, sección, fecha) | 646 diputados enlazados |
| **`lois_votes/`** | 373 leyes votadas y el voto de cada diputado (a favor / en contra / abstención) | Según scrutin |
| **`twitter_zeeschuimer/`** | Tweets capturados con Zeeschuimer, cruzados con diputados | Los que tienen cuenta |
| **`manifestos/`** | Programas electorales junio 2017 de 10 partidos (texto completo + codificación MARPOR) | ~85% por grupo |

Todos se enlazan por **`deputy_id`** o **`political_group_abbrev`** del CSV base `deputes_2017_2022.csv`.

---

## Análisis BERTopic (topic modeling)

Cada fuente textual tiene su propia carpeta `bertopic_analysis/` con un script, resultados en CSV/HTML y un `RESULTADOS.md` con hallazgos narrativos.

| Fuente | Input | Temas encontrados | Desglose por |
|---|---|---|---|
| **Hemiciclo** | muestra 5,000 intervenciones (≥80 palabras) | ~30+ topics | grupo parlamentario |
| **Twitter** | muestra 50,000 tweets (≥30 chars) | ~40+ topics | grupo parlamentario |
| **Manifestos** | 3,801 quasi-sentences MARPOR | ~37 topics | partido político |

Todos usan embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`) y n-gramas 1-2 palabras refinados con `KeyBERTInspired`. Dependencias en `requirements_bertopic.txt`.

---

## Cómo se conectan los datos

```
deputes_2017_2022.csv (id, grupo político, Twitter)
       │
       ├── hemicycle/             → qué dice cada diputado en la Asamblea
       │   └── bertopic_analysis/ → temas del debate por grupo
       │
       ├── lois_votes/            → cómo vota cada diputado
       │
       ├── twitter_zeeschuimer/   → qué publica en Twitter
       │   └── bertopic_analysis/ → temas de Twitter por grupo
       │
       └── manifestos/            → qué promete su partido
           └── bertopic_analysis/ → temas del programa por partido
```

La comparación cruzada permite ver si los **temas que un partido promete** (manifesto) coinciden con lo que sus diputados **dicen en el hemiciclo** y **publican en Twitter**.

---

## Dónde sigo leyendo

| Necesito… | Abro… |
|---|---|
| Estructura completa de archivos | [`french_deputies/ESTRUCTURA.md`](french_deputies/ESTRUCTURA.md) |
| Cómo armé la lista de diputados | [`french_deputies/datos_diputados/README.md`](french_deputies/datos_diputados/README.md) |
| Intervenciones en el hemiciclo | [`french_deputies/hemicycle/README.md`](french_deputies/hemicycle/README.md) |
| Leyes y votaciones | [`french_deputies/lois_votes/README_LOIS_VOTES.md`](french_deputies/lois_votes/README_LOIS_VOTES.md) |
| Twitter / Zeeschuimer | [`french_deputies/twitter_zeeschuimer/README.md`](french_deputies/twitter_zeeschuimer/README.md) |
| Manifiestos electorales (MARPOR) | [`french_deputies/manifestos/README.md`](french_deputies/manifestos/README.md) |
| Resultados BERTopic hemiciclo | [`french_deputies/hemicycle/bertopic_analysis/results/RESULTADOS.md`](french_deputies/hemicycle/bertopic_analysis/results/RESULTADOS.md) |
| Resultados BERTopic Twitter | [`french_deputies/twitter_zeeschuimer/bertopic_analysis/results/RESULTADOS.md`](french_deputies/twitter_zeeschuimer/bertopic_analysis/results/RESULTADOS.md) |
| Resultados BERTopic manifestos | [`french_deputies/manifestos/bertopic_analysis/results/RESULTADOS.md`](french_deputies/manifestos/bertopic_analysis/results/RESULTADOS.md) |
