# Datos diputados 2017-2022

Acá documento **cómo armé** el CSV **`processed/deputes_2017_2022.csv`**, que es el que después uso en **zeeschuimer**, **lois_votes** y **hemicycle** para identificar siempre al mismo diputado con el mismo `id`.

**Convención que me inventé para no confundirme:** los archivos con sufijo **`_rd`** son *raw* (tal como vienen o casi); los que no tienen `_rd` son tablas que ya limpié o derivé.

---

## Flujo que seguí (orden de ejecución)

1. **Twitter en bruto**  
   Bajé el CSV de [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) (Regards Citoyens), lo guardé como **`data/deputes_twitter_rd.csv`**.

2. **Limpieza Twitter**  
   Corrí `python3 scripts/build_deputes_twitter_csv.py`. Eso me dejó **`data/deputes_twitter.csv`** con las columnas que me interesan y handles normalizados.

3. **Assemblée nationale en bruto**  
   Descargué el ZIP de actores 15e desde [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/deputes-senateurs-et-ministres), lo puse en `data/` y ejecuté `python3 scripts/fetch_an_15e_deputes.py` → **`data/deputes_an_rd.csv`** (identidad, circunscripción, grupo).

4. **Merge final**  
   Corrí `python3 scripts/merge_deputes_2017_2022.py`. Cruza AN + Twitter por nombre y apellido y escribe **`data/deputes_rd.csv`** y, lo importante, **`processed/deputes_2017_2022.csv`**.

---

## Cómo dejé ordenada la carpeta

| Carpeta / archivo | Qué hay |
|-------------------|---------|
| **scripts/** | `fetch_an_15e_deputes.py`, `build_deputes_twitter_csv.py`, `merge_deputes_2017_2022.py` |
| **data/** | mis `_rd`, tablas intermedias, ZIP de la AN, referencias nosdeputes, etc. |
| **processed/** | **`deputes_2017_2022.csv`** — la salida que uso en todo el resto del proyecto |

---

## De dónde salió cada cosa

- **`deputes_twitter_rd.csv`:** [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires).
- **`deputes_an_rd.csv`:** open data AN (ZIP acteurs + organes 15e); el script me deja mandato en Asamblea y grupo político.

En el merge yo cruzo AN y Twitter por **`family_name`** + **`first_name`** para rellenar `twitter_handle` y el resto de campos de Twitter cuando hay match.
