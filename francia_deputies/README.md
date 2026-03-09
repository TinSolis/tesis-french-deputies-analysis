# Francia – diputados 2017-2022

En esta carpeta dejo los datos y scripts con los que trabajo la 15ª legislatura francesa: la lista de diputados (Assemblée nationale + Twitter), la captura de sus timelines con Zeeschuimer y las leyes/votos. Todo esto forma parte del trabajo empírico de la tesis (ver *Propuesta_Memoria.pdf* en la raíz del repo).

En la raíz de **francia_deputies** solo están este README y **ESTRUCTURA.md**; el resto está organizado en subcarpetas.

---

## Subcarpetas


| Carpeta              | Qué hice                                                                                                                                                                                                                                                                                                    |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **datos_diputados/** | Armé el CSV consolidado de diputados: fuentes Twitter (twitter-parlementaires) y AN (open data 15e), scripts de limpieza y merge. La salida que uso en todo lo demás es **processed/deputes_2017_2022.csv**. Detalle en **datos_diputados/README.md**.                                                      |
| **zeeschuimer/**     | Capturo tweets de las cuentas de los diputados con Zeeschuimer (cuenta por cuenta, ~15 min de scroll por cuenta, ~400 tweets). Los scripts generan la lista de URLs y luego unifican los ndjson con el CSV de diputados; me quedo con el texto para el análisis. Ver **zeeschuimer/README.md**. |
| **lois_votes/**      | Uso los open data de la AN (Scrutins XV y Dossiers législatifs) para unas 50 leyes y el voto de cada diputado (a favor/en contra); cruzo con deputes_2017_2022 para análisis de valores. Ver **lois_votes/README_LOIS_VOTES.md**.                                                                           |


---

## Orden en que lo hice / cómo reproducir

1. **datos_diputados:** seguí el flujo del README de esa carpeta (twitter raw → build twitter → fetch AN → merge) hasta tener **deputes_2017_2022.csv** en `datos_diputados/processed/`.
2. **zeeschuimer:** generé la lista de URLs, fui capturando cuenta por cuenta con Zeeschuimer y luego ejecuté el merge (ver su README).
3. **lois_votes:** descargué Scrutins y Dossiers, ejecuté build_laws_and_votes (ver su README).

**Índice detallado de archivos:** **[ESTRUCTURA.md](ESTRUCTURA.md)**.