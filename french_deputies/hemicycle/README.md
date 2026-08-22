# Hemiciclo — intervenciones en la Assemblée nationale

Esta carpeta reúne todo lo relacionado con **lo que se dice en el hemiciclo** (compte rendu / intervenciones). Está separada de Twitter y de las votaciones en archivos distintos, pero **enlazable** a ambos por diputado y por fecha, que es el cruce central de la tesis.

La **XVe legislatura (2017–2022)** es la que coincide con `datos_diputados/processed/deputes_2017_2022.csv` y con lo construido en **lois_votes**. En los archivos de Regards Citoyens corresponde al sufijo **`ND15`**.

---

## Organización de la carpeta

| Ruta | Función |
|------|---------|
| **`fuente/`** | Contiene los `*_ND##_interventions_hemicycle_rich.tsv.gz` descargados de Regards Citoyens (ND13, ND14, ND15, ND16 según disponibilidad). No se versionan en Git por su peso. Si **solo** hay ND15 en `fuente/`, el script **no sobrescribe** el agregado de otras legislaturas (`interventions_xiii_xiv_xvi_speaker_text.csv.gz`), para no borrar trabajo previo por accidente. |
| **`processed/`** | Salidas listas para analizar (CSV o `.csv.gz`). |
| **`scripts/`** | `build_interventions_with_deputies.py` y `report_hemicycle_stats.py`. |
| **`GUIA_IDENTIFICADORES_TESIS.md`** | Diccionario de columnas y explicación de cómo se cruzan con votos y Twitter. |
| **`RESUMEN_CUANTITATIVO.md`** | Cifras y tabla de tipos; se **regenera** con el script de reporte cada vez que cambia la fuente. |

---

## Qué trae cada fila (una intervención)

- **Texto:** en las tablas completas está en **`intervention_plain`** (sin HTML).
- **Quién habla:** **`parlementaire`** en el acta; en ND15, si el nombre coincide con el CSV de diputados, se rellenan las columnas **`deputy_*`**.
- **Cuándo:** **`date`**, **`seance_id`**, **`moment`**, **`timestamp`**.
- **Tema aproximado:** **`type`**, **`section`**, **`sous_section`**.
- **Rol:** **`fonction`** (presidente, ponente, etc.), útil para filtrar protocolo vs. argumentación.
- **Citación al acta:** **`source_url`** y los campos **`cri_*`**.

Más detalle en **[GUIA_IDENTIFICADORES_TESIS.md](GUIA_IDENTIFICADORES_TESIS.md)**.

---

## Archivos generados en `processed/`

Tras correr el build, para **ND15** se obtienen:

1. **`interventions_xv_2017_2022_with_deputies.csv.gz`** — tabla completa.
2. **`interventions_xv_2017_2022_meta.csv.gz`** — igual que la anterior, sin la columna de texto largo.
3. **`interventions_xv_2017_2022_texts.csv.gz`** — `intervention_id` + texto para NLP.
4. **`interventions_xv_sample5000.csv`** — muestra sin comprimir para inspección rápida en Excel.

Si al correr el build también están ND13, ND14 y ND16 en **`fuente/`**, se genera **`interventions_xiii_xiv_xvi_speaker_text.csv.gz`** (sin cruce con el CSV de diputados 2017–2022).

---

## Cómo ejecutarlo

Desde **`french_deputies/`**:

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

Las cifras exactas y la tabla de **`type`** están en **[RESUMEN_CUANTITATIVO.md](RESUMEN_CUANTITATIVO.md)**, que se actualiza con `report_hemicycle_stats.py` en cada regeneración de las tablas.

En términos generales: ND15 tiene del orden de **~950 000** intervenciones (turnos en el acta, no “discursos” de campaña). Casi **dos tercios** se pueden enlazar a un diputado de la lista (**`deputy_id`**), lo que cubre del orden de **650** diputados distintos (el número preciso está en el resumen). El acta separa sobre todo tramos de tipo **`loi`** y **`question`**; los títulos de **`section`** sirven como proxy de tema, no como lista de leyes numeradas.

Los votos en **`leyes_votadas_2017_2022.csv`** están en otra granularidad (una fila por scrutin de adopción en el filtro aplicado). El hemiciclo **no** incluye un id de ley por fila: vincular un discurso con una ley concreta requiere razonamiento por fechas y contexto.

---

## Referencias cruzadas en el repo

| Para… | Consultar… |
|-----------|--------|
| Diccionario de columnas | [GUIA_IDENTIFICADORES_TESIS.md](GUIA_IDENTIFICADORES_TESIS.md) |
| Cifras | [RESUMEN_CUANTITATIVO.md](RESUMEN_CUANTITATIVO.md) |
| Diputados | `../datos_diputados/processed/deputes_2017_2022.csv` |
| Leyes y votos | `../lois_votes/README_LOIS_VOTES.md` |
