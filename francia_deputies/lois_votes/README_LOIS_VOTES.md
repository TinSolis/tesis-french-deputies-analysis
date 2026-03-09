# Leyes 2017-2022 y votos por diputado

En esta carpeta explico cómo obtuve unas **50 leyes** de la XV legislatura (2017-2022) y el **voto de cada diputado** (a favor / en contra / abstención) para poder analizar valores en las leyes y asignarlos a los diputados que votaron a favor o en contra, en el marco de la tesis (*Propuesta_Memoria.pdf* en la raíz del repo).

---

## 1. Fuentes que usé (open data Assemblée nationale)

Todo está en **data.assemblee-nationale.fr**, licencia Ouverte.

| Recurso | Qué contiene | Enlace directo |
|--------|----------------|-----------------|
| **Scrutins XV** | Cada votación con título, fecha y posición de cada député (Pour / Contre / Abstention / Non-votant). El identificador del diputado (UID tipo PA123456) coincide con el `id` de mi CSV de diputados. | [Archives 15e – Scrutins](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins) → `Scrutins_XV.json.zip` |
| **Dossiers législatifs XV** | Projets et propositions de loi, textes adoptés, títulos, números, fechas. Lo uso para elegir las ~50 leyes y tener título/identificador. | [Archives 15e – Dossiers législatifs](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs) → `Dossiers_Legislatifs_XV.json.zip` |

URLs que uso para descargar:
- Scrutins: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip`
- Dossiers: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip`

Filtro scrutins de **adopción** de proyecto o proposición de ley (título tipo « Adoption du projet de loi ... ») y me quedo con ~50 para tener una ley = un scrutin de adopción.

---

## 2. Identificación de diputados

En **datos_diputados/processed/deputes_2017_2022.csv** la columna **id** coincide con el número del acteur en la AN (ej. UID `PA720916` → id `720916`). En los scrutins cada voto lleva ese identificador, así que cruzo directo sin otro diccionario.

---

## 3. Flujo que seguí

1. **Descargar** (una vez): los dos ZIP con el script `download_an_scrutins_and_dossiers.py` (o a mano) y descomprimir en `lois_votes/data/`.

2. **Seleccionar ~50 leyes:** desde Scrutins filtré por título "Adoption" (du projet de loi / de la proposition de loi) y tomé 50. Así cada “ley” es un scrutin de adopción.

3. **Construir tablas** con `build_laws_and_votes.py`:
   - **leyes_50.csv:** scrutin_id, título, fecha (y opcionalmente dossier_id).
   - **votos_por_diputado.csv:** deputy_id, scrutin_id, vote (Pour/Contre/Abstention/Non-votant).

4. **Cruzar con mis diputados:** el script solo mantiene votos donde `deputy_id` está en **deputes_2017_2022.csv**, así puedo hacer JOIN con nombre, grupo político, etc.

5. **Análisis:** sobre las 50 leyes clasifico dimensiones de valor; asigno a cada diputado “votó a favor de X leyes de tipo Y”, “en contra de Z…”, y cruzo con Twitter u otras variables para la tesis.

---

## 4. Scripts en esta carpeta

- **scripts/download_an_scrutins_and_dossiers.py**  
  Descarga los dos ZIP a `lois_votes/data/`.

- **scripts/build_laws_and_votes.py**  
  Carga Scrutins_XV.json (y opcionalmente Dossiers), filtra 50 scrutins de adopción, extrae el voto de cada diputado, filtra por deputy_id en deputes_2017_2022 y escribe **leyes_50.csv** y **votos_por_diputado.csv** en `processed/`. Lee el CSV de diputados desde `datos_diputados/processed/deputes_2017_2022.csv`.

Si el JSON de scrutins tiene otra estructura, hay que revisar las claves en el script (ventilationVotes, voteIndividuel, etc.).

---

## 5. Resumen para la tesis

Para el análisis de valores en las leyes y su asignación a los diputados utilicé los datos abiertos de la Assemblée nationale (XVª legislatura): Scrutins (posición de voto por diputado) y Dossiers législatifs (textos adoptados). Seleccioné 50 votaciones de adopción de proyectos o proposiciones de ley. Para cada una obtuve el voto (a favor, en contra, abstención) de cada diputado, identificado por el mismo id que en la base consolidada (deputes_2017_2022.csv). Las tablas resultantes permiten cruzar posiciones de voto con grupo político y con los datos de Twitter recolectados con Zeeschuimer.
