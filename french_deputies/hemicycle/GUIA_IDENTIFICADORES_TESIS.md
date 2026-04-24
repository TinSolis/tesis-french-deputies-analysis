# Identificadores útiles — hemiciclo (ND15 / XVe)

Yo armé esta guía para acordarme **cómo enlazo** las intervenciones del hemiciclo con el resto de mi proyecto (diputados, Twitter, votos) y para diseñar el análisis de texto sin perder de vista quién habla y cuándo.

## Archivos que me genera mi script

| Archivo | Cómo lo uso |
|--------|-------------|
| `processed/interventions_xv_2017_2022_with_deputies.csv.gz` | Tabla maestra: texto + metadatos + diputado cuando hay match. |
| `processed/interventions_xv_2017_2022_meta.csv.gz` | Igual que la maestra pero **sin** `intervention_plain`: uniones y estadísticas sin cargar todo el NLP. |
| `processed/interventions_xv_2017_2022_texts.csv.gz` | Solo `intervention_id` + texto; después hago merge con la meta por id. |
| `processed/interventions_xv_sample5000.csv` | Muestra sin comprimir para mirar en hoja de cálculo o editor. |

## Claves de fila y tiempo

| Campo | Para qué me sirve |
|--------|-------------------|
| `intervention_id` | Clave estable **dentro del export Regards Citoyens** para juntar meta + textos. |
| `seance_id` | Agrupa intervenciones de la **misma sesión** en la fuente (junto con `timestamp` para el orden). |
| `date` | Día calendario: lo pienso para acercarme a **votaciones** u otros eventos. |
| `moment` | Hora anunciada de la sesión (aprox.). |
| `timestamp` | Orden relativo dentro del compte rendu. |

## Quién habla (diputado vs. función)

| Campo | Para qué me sirve |
|--------|-------------------|
| `parlementaire` | Nombre en el acta. |
| `parlementaire_groupe` | Grupo en el **momento del acta** (puede no coincidir con mi CSV si hubo cambios de bancada). |
| `fonction` | Rol (presidente, rapporteur, ministro…): yo filtro acá ritual vs. fondo. |
| `personnalite` | A veces figura ministerial u otra personalidad. |
| `deputy_id`, `deputy_full_name`, … | Mi roster **`deputes_2017_2022.csv`** (match por nombre en ND15). Vacío si no hay match o no es alguien de mi lista. |
| `former_deputy` | Lo traigo de mi CSV de diputados. |

## Enlace con votos y diputados (misma legislatura)

| Campo | Para qué me sirve |
|--------|-------------------|
| `deputy_id` | Mismo `id` que en **`deputes_2017_2022.csv`** y en mis tablas de votos. Me permite contrastar **discurso** y **voto** en la misma persona. |
| `political_group_abbrev` / `political_group` | Grupo en mi CSV (comparo con `parlementaire_groupe` del acta si quiero). |
| `dept_num`, `district_name`, `district_num` | Territorio del mandato. |

## Enlace con Twitter (Zeeschuimer)

| Campo | Para qué me sirve |
|--------|-------------------|
| `twitter_handle`, `twitter_id` | Cruce con **`zeeschuimer/processed/`**: misma persona, registro escrito vs. hemiciclo. |

## Ancla al documento oficial

Los URLs del CRI suelen verse como `.../15/cri/<période>/<page>.asp#<ancre>`.

| Campo | Para qué me sirve |
|--------|-------------------|
| `source_url` | URL completa en assemblee-nationale.fr. |
| `cri_url_legislature_num` | `15` en la ruta. |
| `cri_session_period` | Carpeta tipo `2016-2017`. |
| `cri_page_file` | Archivo `.asp` del día / documento. |
| `cri_anchor_id` | Ancla (`P…`) para citar un punto exacto del compte rendu. |

## Estructura del debate antes del NLP

| Campo | Para qué me sirve |
|--------|-------------------|
| `type` | Tipo de tramo (ley, preguntas, etc.). |
| `section` / `sous_section` | Título de sección: **proxy de tema**. |
| `nb_mots` | Longitud del turno. |

## `intervention_plain`

Texto sin HTML: base para tópicos, sentimiento, marcos; lo comparo con tweets del mismo `deputy_id` alrededor de la misma `date` cuando armo análisis cruzados.

---

Para regenerar todo desde los `*.tsv.gz` en **`hemicycle/fuente/`**:

```bash
cd francia_deputies
python3 hemicycle/scripts/build_interventions_with_deputies.py
python3 hemicycle/scripts/report_hemicycle_stats.py
```
