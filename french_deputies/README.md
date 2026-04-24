# Francia – diputados 2017-2022

En esta carpeta junto **todo el trabajo empírico** que hice para la tesis sobre la 15.ª legislatura francesa: lista de diputados (Assemblée nationale + Twitter), captura de timelines con Zeeschuimer, leyes y votos en el hemiciclo, y el procesamiento de intervenciones parlamentarias. El documento que encuadra la investigación está en la raíz del repo (*Propuesta_Memoria.pdf*).

En la raíz de **francia_deputies** dejé solo este **README** y **ESTRUCTURA.md** (índice de archivos); el resto lo separé en subcarpetas para no mezclar fuentes con salidas.

---

## Cómo organicé el proyecto

| Carpeta | Qué hice yo y para qué sirve |
|--------|------------------------------|
| **datos_diputados/** | Construí el CSV maestro de diputados a partir de Twitter (twitter-parlementaires) y de los datos abiertos de la AN 15e; limpié y fusioné todo. El archivo que uso en **todo** lo demás es **`processed/deputes_2017_2022.csv`**. Lo explico paso a paso en **datos_diputados/README.md**. |
| **zeeschuimer/** | Capturé tweets cuenta por cuenta con Zeeschuimer y luego unifiqué los exports con mi lista de diputados; me quedé con el texto para el análisis. Detalle en **zeeschuimer/README.md**. |
| **lois_votes/** | Bajé los scrutins y dossiers de la AN, generé las tablas de leyes votadas y votos por diputado (y la versión filtrada a mi cohorte). Lo cuento con cuidado en **lois_votes/README_LOIS_VOTES.md** porque es la parte más fácil de malinterpretar. |
| **hemicycle/** | Procesé las intervenciones del hemiciclo (Regards Citoyens): la fuente va en **`fuente/`**, las tablas listas en **`processed/`**; **ND15** es la legislatura que coincide con mis diputados 2017–2022. Ver **hemicycle/README.md**. |

---

## Orden en que lo fui haciendo (y cómo lo volvería a correr)

1. **datos_diputados:** seguí el flujo de su README (Twitter raw → limpieza → AN → merge) hasta tener **`deputes_2017_2022.csv`** en `datos_diputados/processed/`.
2. **zeeschuimer:** generé URLs o abrí perfiles desde el CSV, capturé con Zeeschuimer y corrí el merge (ver su README).
3. **lois_votes:** descargué Scrutins + Dossiers, ejecuté `build_laws_and_votes.py` y, cuando quise, `build_leyes_texte_oficial.py` (ver **README_LOIS_VOTES.md**).
4. **hemicycle:** puse los `*.tsv.gz` en `hemicycle/fuente/` y ejecuté `python3 hemicycle/scripts/build_interventions_with_deputies.py` (ver **hemicycle/README.md**).

**Índice detallado de archivos:** **[ESTRUCTURA.md](ESTRUCTURA.md)**.
