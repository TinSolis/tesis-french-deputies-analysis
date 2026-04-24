# Leyes y votos (Assemblée nationale, XVe législature 2017–2022)

Yo armé este bloque para la tesis porque necesitaba **dos cosas enlazables entre sí**: (1) **qué se votó** en la Asamblea en la misma legislatura que estudio (2017–2022) y (2) **cómo votó cada diputado** en esas votaciones. Todo sale de los **datos abiertos** de la Asamblea (licencia ouverte). El marco general de la investigación está en *Propuesta_Memoria.pdf* (raíz del repo).

---

## La idea en una frase (para que quede claro)

La Asamblea publica cada **votación nominal** (“scrutin”) como un registro con fecha, título y la posición de cada diputado (a favor, en contra, abstención, no votó). Yo **no** descargo “la ley” como PDF desde aquí por defecto: primero construyo la tabla de **votos por persona y por votación**; después, si quiero, enriquezco con **enlace al texto oficial** (JORF / Légifrance) usando los expedientes legislativos (“dossiers”).

**Scrutin** = una votación concreta (un momento en el tiempo). **Un mismo proyecto de ley** puede tener **varios** scrutins (lecturas, artículos, adopción final). Por eso mi tabla de leyes tiene **una fila por scrutin**, no necesariamente “una fila = una ley en sentido coloquial”.

---

## Qué bajé yo y dónde lo guardé

| Fuente (open data) | Para qué la uso | Dónde la dejo |
|--------------------|-----------------|---------------|
| **Scrutins XV** | Lista de votaciones + voto de cada diputado | ZIP en `votes_rd/`, luego muchos JSON en `votes_rd/json/` (un archivo por scrutin) |
| **Dossiers législatifs XV** | Metadatos del expediente (título, tramitación…); sirve para enlazar scrutin → dossier → texto promulgado | ZIP en `votes_rd/`, JSON bajo `votes_rd/json/` |

Enlaces oficiales:

- [Scrutins 15e](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/scrutins)
- [Dossiers législatifs 15e](https://data.assemblee-nationale.fr/archives-anterieures/archives-15e/dossiers-legislatifs)

ZIP directos (por si descargo a mano):

- Scrutins: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/scrutins/Scrutins_XV.json.zip`
- Dossiers: `https://data.assemblee-nationale.fr/static/openData/repository/15/loi/dossiers_legislatifs/Dossiers_Legislatifs_XV.json.zip`

**Nota que a mí me confundía al principio:** el ZIP de Scrutins **no** me deja un solo archivo gigante `Scrutins_XV.json` con todo adentro; al descomprimir, la AN reparte **un JSON por scrutin** (`VTANR5L15V*.json`). Mi script `build_laws_and_votes.py` **recorre todos** esos archivos, no busca un único JSON con otro nombre.

---

## Qué archivos generé yo y para qué los uso

Todo lo que considero “salida de análisis” lo dejé en **`votes_rd/processed/`**.

| Archivo | Qué es (en mis palabras) |
|---------|-------------------------|
| **`leyes_votadas_2017_2022.csv`** | Una fila por **scrutin** que yo clasifiqué como adopción de texto legislativo (proyecto o propuesta de ley, ley orgánica, ratificación vinculada a ley, etc.) y cuya fecha cae en el rango de la XVe legislatura que definí (aprox. **27/06/2017** a **21/06/2022**). Columnas típicas: identificador del scrutin, título, fecha, referencia al dossier si la extraje. |
| **`votos_por_diputado.csv`** | **Todos** los diputados que figuran en esos scrutins: una fila por par (diputado, scrutin) con el **voto** (Pour / Contre / Abstention / NonVotant). |
| **`votos_por_diputado_cohorte.csv`** | Lo mismo que el anterior, pero **filtrado** a los `id` que yo tengo en `datos_diputados/processed/deputes_2017_2022.csv` (la cohorte que uso en Twitter y en el resto de la tesis). Es el archivo que suelo cruzar con el resto de mis datos. |
| **`leyes_texto_oficial.csv`** | Lo genero con un script aparte: por scrutin (o ley votada) intento acercar **NOR**, URL Légifrance y, si yo pegé textos en `votes_rd/textes_lois/`, la columna **`texto_oficial`**. |

---

## Cómo lo reproduzco yo (orden fijo)

Desde la carpeta **`francia_deputies/`**:

```bash
# Paso 1 — Descargar los ZIP y descomprimirlos en votes_rd/
python3 lois_votes/scripts/download_an_scrutins_and_dossiers.py
```

Si `requests` no me instala (red corporativa, etc.), descargo los dos ZIP a mano, los pongo en `lois_votes/votes_rd/` y descomprimo hasta tener la carpeta `json/` con los `VTANR5L15V*.json`.

```bash
# Paso 2 — Armar las tablas de leyes filtradas y votos
python3 lois_votes/scripts/build_laws_and_votes.py
```

Opción que usé a veces para depurar: `--sin-filtro-fechas` incluye scrutins fuera del rango de fechas (no lo usaría para el análisis final sin revisar).

```bash
# Paso 3 (opcional) — Enlazar con dossiers y NOR / Légifrance; rellenar texto si tengo .txt en textes_lois/
python3 lois_votes/scripts/build_leyes_texte_oficial.py
```

La **primera** vez que corro el paso 3, el script indexa muchos dossiers y puede tardar; guarda caché en `votes_rd/.dossier_index_cache.pkl` para las siguientes corridas.

---

## Cómo enlazo esto con mis diputados

En **`deputes_2017_2022.csv`**, la columna **`id`** es el mismo identificador numérico que uso como **`deputy_id`** en los CSV de votos (en la fuente AN los actores suelen venir como `PA…`; yo trabajo con el número sin el prefijo para hacer el JOIN con mi CSV).

---

## Qué hace exactamente cada script (para leer el código sin perderse)

1. **`download_an_scrutins_and_dossiers.py`**  
   Yo lo escribí para no tener que acordarme de las URLs: baja los ZIP y los descomprime donde el build los espera.

2. **`build_laws_and_votes.py`**  
   Lee todos los JSON de scrutin, **filtra** por tipo de votación (adopción de texto legislativo, según reglas que están en el propio script) y por ventana de fechas de la legislatura, y escribe los tres CSV principales en `processed/`.

3. **`build_leyes_texte_oficial.py`**  
   Cruza mis leyes votadas con los JSON de dossier (emparejamiento por título; hay columnas de calidad del match para revisar a mano si algo queda raro), busca el acto de **promulgación** (PROM-PUB) para sacar NOR y URL al Journal officiel / Légifrance. **No** confío en un scraper masivo de Légifrance porque a menudo bloquea; si quiero el texto completo en el CSV, yo lo pongo en archivos `.txt` bajo `votes_rd/textes_lois/` y el script los incorpora.

---

## Lo que le aclaré a mi comisión (metodología en dos líneas)

- Mi unidad de observación en la tabla de “leyes” es el **scrutin de adopción** (o el conjunto de scrutins que cumplan mi filtro), no “el código civil entero” como un solo evento.
- Si necesito **una sola fila por ley** en sentido jurídico, tengo que **agrupar** por expediente o elegir el scrutin final según el criterio que defina en el capítulo de métodos.

Si algo de esto no queda claro en una lectura, prefiero que me lo marquen en la defensa y lo preciso en el cuerpo de la memoria; este README es mi hoja de ruta para mí mismo y para quien revise el repo.
