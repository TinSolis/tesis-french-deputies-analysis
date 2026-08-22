# Datos diputados 2017-2022

## Propósito

Documenta cómo se construye el CSV **`processed/deputes_2017_2022.csv`**, que sirve como tabla de referencia de diputados de la XVe legislatura. Este archivo se reutiliza en **twitter_zeeschuimer**, **lois_votes** y **hemicycle** para identificar siempre al mismo diputado con el mismo `id`.

**Convención de nombres:** los archivos con sufijo **`_rd`** son *raw* (datos originales o casi sin modificar); los que no tienen `_rd` son tablas ya limpiadas o derivadas.

---

## Qué contiene

| Carpeta / archivo | Qué hay |
|-------------------|---------|
| **scripts/** | `fetch_an_15e_deputes.py`, `build_deputes_twitter_csv.py`, `merge_deputes_2017_2022.py` |
| **data/** | archivos `_rd`, tablas intermedias, ZIP de la AN, referencias nosdeputes, etc. |
| **processed/** | **`deputes_2017_2022.csv`** — la salida que se usa en el resto del proyecto |

---

## Cómo reproducir (orden de ejecución)

1. **Twitter en bruto**  
   Descargar el CSV de [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires) (Regards Citoyens) y guardarlo como **`data/deputes_twitter_rd.csv`**.

2. **Limpieza de Twitter**  
   Ejecutar `python3 scripts/build_deputes_twitter_csv.py`, que produce **`data/deputes_twitter.csv`** con las columnas relevantes y los handles normalizados.

3. **Assemblée nationale en bruto**  
   Descargar el ZIP de actores 15e desde [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/deputes-senateurs-et-ministres), colocarlo en `data/` y ejecutar `python3 scripts/fetch_an_15e_deputes.py` → **`data/deputes_an_rd.csv`** (identidad, circunscripción, grupo).

4. **Merge final**  
   Ejecutar `python3 scripts/merge_deputes_2017_2022.py`. Cruza AN + Twitter por nombre y apellido y escribe **`data/deputes_rd.csv`** y la salida principal, **`processed/deputes_2017_2022.csv`**.

---

## Fuentes de cada archivo

- **`deputes_twitter_rd.csv`:** [twitter-parlementaires](https://github.com/regardscitoyens/twitter-parlementaires).
- **`deputes_an_rd.csv`:** open data de la Assemblée nationale (ZIP acteurs + organes 15e); el script deja el mandato en la Asamblea y el grupo político.

El merge cruza AN y Twitter por **`family_name`** + **`first_name`** para completar `twitter_handle` y el resto de campos de Twitter cuando hay coincidencia.
