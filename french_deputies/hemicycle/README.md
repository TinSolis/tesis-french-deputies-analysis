# Hemiciclo — intervenciones en la Assemblée nationale

Yo concentré acá todo lo relacionado con **lo que se dice en el hemiciclo** (compte rendu / intervenciones). Lo separé de Twitter y de las votaciones en archivos distintos, pero lo dejé **enlazable** a ambos por diputado y por fecha porque eso es lo que necesito para la tesis.

La **XVe legislatura (2017–2022)** es la que coincide con mi **`datos_diputados/processed/deputes_2017_2022.csv`** y con lo que armé en **lois_votes**. En los archivos de Regards Citoyens eso es el sufijo **`ND15`**.

---

## Cómo ordené esta carpeta

| Ruta | Para qué la uso |
|------|-----------------|
| **`fuente/`** | Acá pongo los `*_ND##_interventions_hemicycle_rich.tsv.gz` que bajé de Regards Citoyens (ND13, ND14, ND15, ND16 según lo que tenga). No los versiono en Git por el peso. Si **solo** tengo ND15 en `fuente/`, mi script **no sobrescribe** el agregado de otras legislaturas (`interventions_xiii_xiv_xvi_speaker_text.csv.gz`) para no borrar trabajo previo por accidente. |
| **`processed/`** | Salidas listas para analizar (CSV o `.csv.gz`). |
| **`scripts/`** | `build_interventions_with_deputies.py` y `report_hemicycle_stats.py`. |
| **`GUIA_IDENTIFICADORES_TESIS.md`** | Me dejé anotado qué significa cada columna y cómo la cruzo con votos y Twitter. |
| **`RESUMEN_CUANTITATIVO.md`** | Números y tabla de tipos; lo **regenero** con el script de reporte cuando cambio la fuente. |

---

## Qué trae cada fila (una intervención)

- **Texto:** en las tablas completas está en **`intervention_plain`** (sin HTML).
- **Quién habla:** **`parlementaire`** en el acta; si es ND15 y el nombre matchea mi CSV, relleno las columnas **`deputy_*`**.
- **Cuándo:** **`date`**, **`seance_id`**, **`moment`**, **`timestamp`**.
- **Tema aproximado:** **`type`**, **`section`**, **`sous_section`**.
- **Rol:** **`fonction`** (presidente, ponente, etc.) — yo lo uso para filtrar protocolo vs. argumentación.
- **Citación al acta:** **`source_url`** y los campos **`cri_*`**.

Más detalle: **[GUIA_IDENTIFICADORES_TESIS.md](GUIA_IDENTIFICADORES_TESIS.md)**.

---

## Archivos que genero en `processed/`

Después de correr el build, para **ND15** me quedan:

1. **`interventions_xv_2017_2022_with_deputies.csv.gz`** — tabla completa.
2. **`interventions_xv_2017_2022_meta.csv.gz`** — lo mismo sin la columna de texto largo.
3. **`interventions_xv_2017_2022_texts.csv.gz`** — `intervention_id` + texto para NLP.
4. **`interventions_xv_sample5000.csv`** — muestra sin comprimir para mirar rápido en Excel.

Si cuando corro el build tengo también ND13, ND14 y ND16 en **`fuente/`**, se genera **`interventions_xiii_xiv_xvi_speaker_text.csv.gz`** (sin cruce a mi CSV de diputados 2017–2022).

---

## Cómo lo ejecuto yo

Desde **`francia_deputies/`**:

```bash
python3 hemicycle/scripts/build_interventions_with_deputies.py
python3 hemicycle/scripts/report_hemicycle_stats.py
```

Ejemplo mínimo en Python:

```python
import gzip, csv
path = "hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz"
with gzip.open(path, "rt", encoding="utf-8") as f:
    row = next(csv.DictReader(f))
```

---

## Resumen cuantitativo (orden de magnitud)

Los números exactos y la tabla de **`type`** los dejé en **[RESUMEN_CUANTITATIVO.md](RESUMEN_CUANTITATIVO.md)**; lo actualizo con `report_hemicycle_stats.py` cada vez que regenero las tablas.

En términos generales: en ND15 tengo del orden de **~950 000** intervenciones (turnos en el acta, no “discursos” de acto de campaña). Casi **dos tercios** las puedo enlazar a un diputado de mi lista (**`deputy_id`**), lo que cubre del orden de **650** diputados distintos (el número preciso está en el resumen). El acta separa sobre todo tramos tipo **`loi`** y **`question`**; los títulos de **`section`** me sirven como proxy de tema, no como lista de leyes numeradas.

Mis votos en **`leyes_votadas_2017_2022.csv`** son otra granularidad (una fila por scrutin de adopción en mi filtro). **No** viene un id de ley por fila en el hemiciclo: si quiero vincular discurso y ley concreta, lo tengo que razonar yo con fechas y contexto.

---

## Dónde sigo leyendo en el repo

| Necesito… | Abro… |
|-----------|--------|
| Diccionario de columnas | [GUIA_IDENTIFICADORES_TESIS.md](GUIA_IDENTIFICADORES_TESIS.md) |
| Cifras | [RESUMEN_CUANTITATIVO.md](RESUMEN_CUANTITATIVO.md) |
| Diputados | `../datos_diputados/processed/deputes_2017_2022.csv` |
| Leyes y votos | `../lois_votes/README_LOIS_VOTES.md` |
