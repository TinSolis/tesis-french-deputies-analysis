# Datos diputados 2017-2022

Aquí explico cómo obtuve el CSV consolidado de diputados **processed/deputes_2017_2022.csv**, que luego uso en **zeeschuimer** y **lois_votes**.

**Convención que uso:** `_rd` = raw (tal como viene de la fuente); sin sufijo = limpio o derivado.

---

## Flujo que seguí (orden de ejecución)

1. **Raw Twitter**  
   Descargué el CSV de [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) (RegardsCitoyens), lo renombré a **deputes_twitter_rd.csv** y lo puse en `data/`.

2. **Limpieza Twitter**  
   Ejecuté `python3 scripts/build_deputes_twitter_csv.py`. Eso genera `data/deputes_twitter.csv` con las columnas que me interesan y solo URLs de Twitter en formato estándar.

3. **Raw Assemblée nationale**  
   Descargué (o dejé que el script descargue) el ZIP de la AN 15e ([data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/deputes-senateurs-et-ministres)) y lo puse en `data/`. Ejecuté `python3 scripts/fetch_an_15e_deputes.py` y obtuve `data/deputes_an_rd.csv` con identidad, circunscripción y grupo político por diputado.

4. **Merge**  
   Ejecuté `python3 scripts/merge_deputes_2017_2022.py`. El script lee `deputes_an_rd.csv` y `deputes_twitter.csv`, cruza por nombre y apellido y escribe `data/deputes_rd.csv` y **processed/deputes_2017_2022.csv** (este último es el que uso en todo lo demás).

---

## Estructura que dejé

| Carpeta / archivo | Contenido |
|-------------------|-----------|
| **scripts/** | fetch_an_15e_deputes.py, build_deputes_twitter_csv.py, merge_deputes_2017_2022.py |
| **data/** | deputes_twitter_rd.csv, deputes_twitter.csv, deputes_an_rd.csv, deputes_rd.csv, ZIP de la AN, nosdeputes (referencia), etc. |
| **processed/** | **deputes_2017_2022.csv** — salida principal; lo usan zeeschuimer y lois_votes |

---

## Origen de cada dato

- **deputes_twitter_rd.csv:** [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires).
- **deputes_an_rd.csv:** open data de la Assemblée nationale (ZIP acteurs + organes 15e). El script extrae identidad, mandat ASSEMBLEE (circonscription) y mandat GP (grupo político).

El merge cruza AN y Twitter por **family_name** + **first_name** para rellenar twitter_handle y el resto de campos de Twitter.
