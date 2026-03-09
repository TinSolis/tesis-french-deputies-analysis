# Tesis – Diputados Francia 2017-2022, Twitter y votaciones

Proyecto de datos para la tesis: diputados de la Assemblée nationale (XVª legislatura 2017-2022), sus cuentas de Twitter, captura de tweets con Zeeschuimer, y leyes/votos para análisis de valores.

**Documento de referencia:** [Propuesta_Memoria.pdf](Propuesta_Memoria.pdf)

---

## Estructura del repositorio

```
Tesis/
├── README.md                 ← Estás aquí (índice general)
├── Propuesta_Memoria.pdf     ← Propuesta / memoria de la tesis
│
└── francia_deputies/         ← Todo el trabajo empírico
    ├── README.md             ← Fuentes de datos y flujo de los CSV de diputados
    ├── ESTRUCTURA.md         ← Qué es cada carpeta/archivo (principal vs apoyo)
    │
    │── PRINCIPAL (para análisis y tesis)
    │   ├── deputes_2017_2022.csv        Lista consolidada de diputados + Twitter
    │   ├── zeeschuimer/processed/       Tweets asociados a diputados (CSV)
    │   └── lois_votes/processed/        Leyes y votos por diputado (cuando se generen)
    │
    │── Scripts y guías
    │   ├── fetch_an_15e_deputes.py      Diputados desde Assemblée nationale
    │   ├── merge_deputes_2017_2022.py   Merge AN + Twitter → deputes_2017_2022
    │   ├── build_deputes_twitter_csv.py Limpieza Twitter
    │   ├── zeeschuimer/                 Captura Twitter (Zeeschuimer + merge)
    │   │   ├── README_ZEESCHUIMER.md
    │   │   └── scripts/
    │   └── lois_votes/                  Leyes y votos (Scrutins AN)
    │       ├── README_LOIS_VOTES.md
    │       └── scripts/
    │
    └── Datos intermedios y raw
        ├── deputes_twitter_rd.csv, deputes_an_rd.csv, deputes_rd.csv, etc.
        ├── zeeschuimer/captures/        Exports ndjson de Zeeschuimer
        └── lois_votes/data/             Scrutins/Dossiers (ZIP o JSON)
```

---

## Qué es lo importante

| Para qué | Dónde |
|----------|--------|
| **Lista de diputados con Twitter y grupo político** | `francia_deputies/deputes_2017_2022.csv` |
| **Tweets capturados por diputado (texto, menciones)** | `francia_deputies/zeeschuimer/processed/` (tweets_with_deputies.csv, deputies_capture_summary.csv, tweets_text_only.csv) |
| **Leyes y votos (a favor/en contra por diputado)** | `francia_deputies/lois_votes/processed/` (leyes_50.csv, votos_por_diputado.csv) — se generan con los scripts |

El resto son **fuentes raw**, **CSV intermedios** o **scripts** para reproducir o ampliar los datos.

---

## Orden sugerido

1. Leer **francia_deputies/README.md** para entender el origen de los datos de diputados.
2. Para Twitter: **zeeschuimer/README_ZEESCHUIMER.md** y ejecutar los scripts de `zeeschuimer/scripts/` cuando haya nuevos exports en `zeeschuimer/captures/`.
3. Para leyes y votos: **lois_votes/README_LOIS_VOTES.md** y ejecutar los scripts de `lois_votes/scripts/` (descarga Scrutins, luego build_laws_and_votes).
4. Detalle de cada archivo/carpeta: **francia_deputies/ESTRUCTURA.md**.
