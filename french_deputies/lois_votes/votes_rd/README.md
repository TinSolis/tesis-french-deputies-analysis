# votes_rd — datos brutos y textos oficiales (AN 2017–2022)

Esta carpeta contiene todo lo que se bajó de la Asamblea nacional y de Légifrance antes de generar las tablas finales en `processed/`.

## Estructura

```
votes_rd/
├── Scrutins_XV.json.zip           ← ZIP original de la AN (gitignored por tamaño)
├── Dossiers_Legislatifs_XV.json.zip
├── json/                          ← ZIPs descomprimidos (gitignored)
│   ├── scrutin/VTANR5L15V*.json  ← un JSON por votación
│   └── dossierParlementaire/DLR*.json
├── processed/                     ← CSV finales que se usan en el análisis
│   ├── leyes_votadas_2017_2022.csv
│   ├── votos_por_diputado.csv
│   ├── votos_por_diputado_cohorte.csv
│   └── leyes_texto_oficial.csv    ← 33 MB, texto de las leyes incrustado
└── textes_lois/                   ← textos descargados de Légifrance vía PISTE
    ├── _index.csv                 ← 184 leyes bajadas por NOR
    ├── _index_titles.csv          ← leyes adicionales bajadas por título
    ├── EJEMPLO_LEY.txt            ← ejemplo anotado del formato (leer esto primero)
    ├── <NOR>.txt                  ← texto plano listo para NLP (ej. INTX1716366L.txt)
    └── <NOR>.json                 ← respuesta cruda de PISTE (gitignored)
```

## Estado actual

- **373 scrutins** de adopción identificados en la XVe législature
- **337 / 373 (90%)** con texto oficial incrustado en `leyes_texto_oficial.csv`
- **184 / 212 (87%)** dossiers únicos con texto
- Los textos más extensos son varios cientos de KB (leyes de presupuesto, etc.)

## Cómo usar

Ver la explicación completa del flujo (qué es un scrutin, cómo reproducir, qué significa cada columna) en **`../README_LOIS_VOTES.md`**.

Para entender el formato de los textos: leer **`textes_lois/EJEMPLO_LEY.txt`**.
