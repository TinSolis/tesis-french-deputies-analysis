# Identificadores útiles — hemiciclo (ND15 / XVe)

Esta guía documenta **cómo se enlazan** las intervenciones del hemiciclo con el resto del proyecto (diputados, Twitter, votos) y sirve de referencia para diseñar el análisis de texto sin perder de vista quién habla y cuándo.

## Archivos generados por el script

| Archivo | Uso |
|--------|-----|
| `processed/interventions_xv_2017_2022_with_deputies.csv.gz` | Tabla maestra: texto + metadatos + diputado cuando hay match. |
| `processed/interventions_xv_2017_2022_meta.csv.gz` | Igual que la maestra pero **sin** `intervention_plain`: uniones y estadísticas sin cargar todo el NLP. |
| `processed/interventions_xv_2017_2022_texts.csv.gz` | Solo `intervention_id` + texto; se une luego con la meta por id. |
| `processed/interventions_xv_sample5000.csv` | Muestra sin comprimir para inspección en hoja de cálculo o editor. |

## Claves de fila y tiempo

| Campo | Función |
|--------|---------|
| `intervention_id` | Clave estable **dentro del export de Regards Citoyens** para unir meta + textos. |
| `seance_id` | Agrupa intervenciones de la **misma sesión** en la fuente (junto con `timestamp` para el orden). |
| `date` | Día calendario; base para aproximar **votaciones** u otros eventos. |
| `moment` | Hora anunciada de la sesión (aprox.). |
| `timestamp` | Orden relativo dentro del compte rendu. |

## Quién habla (diputado vs. función)

| Campo | Función |
|--------|---------|
| `parlementaire` | Nombre en el acta. |
| `parlementaire_groupe` | Grupo en el **momento del acta** (puede no coincidir con el CSV si hubo cambios de bancada). |
| `fonction` | Rol (presidente, rapporteur, ministro…); permite filtrar ritual vs. fondo. |
| `personnalite` | En ocasiones, figura ministerial u otra personalidad. |
| `deputy_id`, `deputy_full_name`, … | Roster **`deputes_2017_2022.csv`** (match por nombre en ND15). Vacío si no hay match o si el orador no está en la lista. |
| `former_deputy` | Proviene del CSV de diputados. |

## Enlace con votos y diputados (misma legislatura)

| Campo | Función |
|--------|---------|
| `deputy_id` | Mismo `id` que en **`deputes_2017_2022.csv`** y en las tablas de votos. Permite contrastar **discurso** y **voto** en la misma persona. |
| `political_group_abbrev` / `political_group` | Grupo según el CSV (comparable con `parlementaire_groupe` del acta). |
| `dept_num`, `district_name`, `district_num` | Territorio del mandato. |

## Enlace con Twitter (Zeeschuimer)

| Campo | Función |
|--------|---------|
| `twitter_handle`, `twitter_id` | Cruce con **`twitter_zeeschuimer/processed/`**: misma persona, registro escrito vs. hemiciclo. |

## Ancla al documento oficial

Los URLs del CRI tienen la forma `.../15/cri/<période>/<page>.asp#<ancre>`.

| Campo | Función |
|--------|---------|
| `source_url` | URL completa en assemblee-nationale.fr. |
| `cri_url_legislature_num` | `15` en la ruta. |
| `cri_session_period` | Carpeta tipo `2016-2017`. |
| `cri_page_file` | Archivo `.asp` del día / documento. |
| `cri_anchor_id` | Ancla (`P…`) para citar un punto exacto del compte rendu. |

## Estructura del debate antes del NLP

| Campo | Función |
|--------|---------|
| `type` | Tipo de tramo (ley, preguntas, etc.). |
| `section` / `sous_section` | Título de sección: **proxy de tema**. |
| `nb_mots` | Longitud del turno. |

## `intervention_plain`

Texto sin HTML: base para tópicos, sentimiento y marcos. Se compara con los tweets del mismo `deputy_id` alrededor de la misma `date` en los análisis cruzados.

---

Para regenerar todo desde los `*.tsv.gz` en **`hemicycle/fuente/`**:

```bash
cd french_deputies
python3 hemicycle/scripts/build_interventions_with_deputies.py
python3 hemicycle/scripts/report_hemicycle_stats.py
```
