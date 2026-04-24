# Tesis — Diputados franceses, discursos, votos, Twitter y manifiestos (2017-2022)

Proyecto de datos para la tesis: diputados de la Assemblée nationale (XVe legislatura 2017-2022), sus intervenciones en el hemiciclo, votaciones sobre leyes, actividad en Twitter y programas electorales de sus partidos.

**Documento de referencia:** [Propuesta Memoria .pdf](Propuesta%20Memoria%20.pdf)

---

## Estructura real del repositorio

```
Tesis/
├── README.md                          ← Estás aquí
├── Propuesta Memoria .pdf             ← Propuesta / memoria de la tesis
│
└── french_deputies/
    ├── README.md
    ├── ESTRUCTURA.md
    │
    ├── datos_diputados/
    │   ├── data/                      ← CSVs fuente (AN, Twitter, nosdeputes)
    │   ├── processed/
    │   │   └── deputes_2017_2022.csv  ← 668 diputados con grupo, circunscripción, Twitter
    │   └── scripts/                   ← fetch, build, merge
    │
    ├── hemicycle/
    │   ├── fuente/                    ← TSV.gz de Regards Citoyens (pesado, no en GitHub)
    │   ├── processed/
    │   │   ├── interventions_xv_*.csv.gz  ← ~950k intervenciones (pesados, no en GitHub)
    │   │   └── interventions_xv_sample5000.csv
    │   ├── scripts/                   ← build + reporte
    │   ├── GUIA_IDENTIFICADORES_TESIS.md
    │   └── RESUMEN_CUANTITATIVO.md
    │
    ├── lois_votes/
    │   ├── votes_rd/
    │   │   └── processed/
    │   │       ├── leyes_votadas_2017_2022.csv    ← 373 scrutins
    │   │       ├── votos_por_diputado.csv
    │   │       ├── votos_por_diputado_cohorte.csv
    │   │       └── leyes_texto_oficial.csv
    │   ├── scripts/                   ← download, build, texte oficial
    │   └── README_LOIS_VOTES.md
    │
    ├── twitter_zeeschuimer/
    │   ├── captures/                  ← Exports .ndjson (pesados, no en GitHub)
    │   ├── processed/
    │   │   ├── tweets_with_deputies.csv   ← (pesado, no en GitHub)
    │   │   ├── tweets_text_only.csv       ← (pesado, no en GitHub)
    │   │   └── deputies_capture_summary.csv
    │   ├── scripts/                   ← generate URLs, merge
    │   └── README.md
    │
    └── manifestos/
        ├── data/
        │   ├── marpor_core_france_2017.csv    ← dataset MARPOR (10 partidos)
        │   └── marpor_corpus_metadata.json
        ├── processed/
        │   ├── textos_por_partido/            ← un .txt por partido (manifiesto completo)
        │   ├── manifesto_full_texts.csv       ← lo mismo en CSV
        │   ├── manifesto_texts.csv            ← 3,801 frases con código temático
        │   └── party_positions.csv            ← score izquierda-derecha (rile)
        ├── group_to_party_mapping.csv         ← grupo parlamentario → partido MARPOR
        ├── scripts/                           ← download vía API
        └── README.md
```

---

## Qué hay en cada carpeta

| Carpeta | Qué contiene | Diputados cubiertos |
|---|---|---|
| **`datos_diputados/`** | Lista base de 668 diputados (id, nombre, grupo político, circunscripción, Twitter) | Todos |
| **`hemicycle/`** | ~950,000 intervenciones en el hemiciclo (texto de debates, tipo, sección, fecha) | 646 enlazados |
| **`lois_votes/`** | 373 leyes votadas y el voto de cada diputado (a favor / en contra / abstención) | Según scrutin |
| **`twitter_zeeschuimer/`** | Tweets capturados con Zeeschuimer, cruzados con diputados | Los que tienen cuenta |
| **`manifestos/`** | Programas electorales 2017 de 10 partidos (texto completo + codificación MARPOR) | ~85% por grupo |

Todos se enlazan por **`deputy_id`** o **`political_group_abbrev`** del CSV base `deputes_2017_2022.csv`.

---

## Cómo se conectan los datos

```
deputes_2017_2022.csv (id, grupo, Twitter)
       │
       ├── hemicycle/        → qué dice cada diputado en la Asamblea
       ├── lois_votes/       → cómo vota cada diputado
       ├── twitter/          → qué publica en Twitter
       └── manifestos/       → qué promete su partido
```

---

## Dónde sigo leyendo

| Necesito… | Abro… |
|---|---|
| Entender la estructura completa | [`french_deputies/ESTRUCTURA.md`](french_deputies/ESTRUCTURA.md) |
| Cómo armé la lista de diputados | [`french_deputies/datos_diputados/README.md`](french_deputies/datos_diputados/README.md) |
| Intervenciones en el hemiciclo | [`french_deputies/hemicycle/README.md`](french_deputies/hemicycle/README.md) |
| Leyes y votaciones | [`french_deputies/lois_votes/README_LOIS_VOTES.md`](french_deputies/lois_votes/README_LOIS_VOTES.md) |
| Twitter / Zeeschuimer | [`french_deputies/twitter_zeeschuimer/README.md`](french_deputies/twitter_zeeschuimer/README.md) |
| Manifiestos electorales (MARPOR) | [`french_deputies/manifestos/README.md`](french_deputies/manifestos/README.md) |
