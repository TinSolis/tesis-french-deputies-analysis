# votes_rd — datos brutos, textos oficiales y enmiendas (AN 2017–2022)

Esta carpeta contiene los datos brutos descargados de la Assemblée nationale y de Légifrance, previos a la generación de las tablas finales en `processed/`.

## Estructura

```
votes_rd/
├── Scrutins_XV.json.zip                 ← ZIP original de la AN (gitignored)
├── Dossiers_Legislatifs_XV.json.zip     ← ZIP de dossiers (gitignored)
├── json/                                ← scrutins descomprimidos (gitignored)
│   └── VTANR5L15V*.json                ← un JSON por votación (4.417 en total)
├── Amendements/                         ← gitignored: pesa varios GB
│   ├── Amendements_XV.xml.zip          ← 704 MB, todas las enmiendas XV
│   └── xml/<DOSSIER>/<TEXTE_LEG>/      ← 311.934 XML, uno por enmienda
├── processed/                           ← CSV finales que se usan en el análisis
│   ├── leyes_votadas_2017_2022.csv     ← 373 scrutins de adopción de ley
│   ├── votos_por_diputado.csv          ← votos globales (todos)
│   ├── votos_por_diputado_cohorte.csv  ← votos globales (cohorte)
│   ├── leyes_texto_oficial.csv         ← 33 MB, leyes + texto promulgado
│   ├── amendements_votados.csv         ← 3.126 scrutins de enmienda
│   ├── votos_amendements_por_diputado.csv          ← 297k votos
│   ├── votos_amendements_por_diputado_cohorte.csv  ← 297k votos (cohorte)
│   ├── amendements_textos.csv          ← 496 MB, 311k enmiendas con texto crudo (gitignored)
│   └── amendements_votos_con_texto.csv ← 7.7 MB, votos + texto enmienda linkeado
└── textes_lois/                         ← textos descargados de Légifrance vía PISTE
    ├── _index.csv                       ← 184 leyes bajadas por NOR
    ├── _index_titles.csv                ← leyes adicionales bajadas por título
    ├── EJEMPLO_LEY.txt                  ← ejemplo de texto de LEY (leer esto primero)
    ├── EJEMPLO_AMENDEMENT.txt           ← ejemplo de texto de ENMIENDA (leer también)
    ├── <NOR>.txt                        ← texto plano listo para NLP (ej. INTX1716366L.txt)
    └── <NOR>.json                       ← respuesta cruda de PISTE (gitignored)
```

## Estado actual del dataset

### Leyes (vote sur l'ensemble)

- **373 scrutins** de adopción identificados en la XVe législature.
- **337 / 373 (90%)** con texto oficial incrustado en `leyes_texto_oficial.csv`.
- **184 / 212 (87%)** dossiers únicos con texto.

### Enmiendas (vote sur amendement)

- **3.126 scrutins** de enmiendas en la XVe législature.
- **2.904 / 3.126 (93%)** con texto del cambio propuesto vinculado en `amendements_votos_con_texto.csv`.
- **297.574 votos individuales** (todos en la cohorte de la tesis).
- Texto promedio por enmienda: ~544 caracteres (suficiente y bien focalizado para clasificación temática).

## Cómo usar

Ver la explicación completa del flujo (qué es un scrutin, cómo reproducir, qué significa cada columna) en **`../README_LOIS_VOTES.md`**.

Para entender el formato de los textos: leer **`textes_lois/EJEMPLO_LEY.txt`** (leyes) y **`textes_lois/EJEMPLO_AMENDEMENT.txt`** (enmiendas).
