# Captura de Twitter de los diputados con Zeeschuimer

## Propósito

Documenta cómo se obtuvieron los tweets de las cuentas de los diputados para la tesis. La captura se hace con **Zeeschuimer**, una extensión de navegador (Firefox) del [Digital Methods Initiative](https://github.com/digitalmethodsinitiative/zeeschuimer) que registra el tráfico que recibe el navegador durante la navegación. No es una API: se guarda lo que se muestra al hacer scroll en cada perfil. Luego los datos se procesan con scripts para quedarse con el texto de los tweets, que es el insumo principal del análisis de la memoria (ver `memoria/`; propuesta original en `memoria/propuesta/`).

---

## Qué contiene

```
french_deputies/
├── datos_diputados/processed/deputes_2017_2022.csv   # Lista de diputados (con twitter_handle, etc.)
├── twitter_zeeschuimer/
│   ├── README.md
│   ├── captures/                     # Exports ndjson de Zeeschuimer
│   ├── processed/                    # Salida: tweets con diputado y texto
│   └── scripts/
│       ├── generate_twitter_url_list.py
│       └── merge_zeeschuimer_with_deputies.py
```

- **captures/:** cada ndjson es una sesión (una cuenta o un lote); se nombran por fecha o por handle.
- **processed/:** el script lee todos los ndjson, cruza por autor (`twitter_handle`) con el CSV de diputados y escribe CSVs con cada tweet y las columnas del diputado. De esa salida se usa sobre todo el **texto** para el análisis.

---

## Metodología: cuenta por cuenta, de forma estandarizada

Se procede **cuenta por cuenta**. Para cada diputado con Twitter:

1. Abrir la URL del perfil (ej. `https://twitter.com/fionalazaar`). Las cuentas están en `datos_diputados/processed/deputes_2017_2022.csv` (campo `twitter_handle`).
2. Activar la captura de Zeeschuimer para X/Twitter.
3. Usar un **autoscroller en Firefox** (p. ej. [FoxScroller](https://addons.mozilla.org/en-US/firefox/addon/foxscroller/)) durante unos **15 minutos**, lo que suele dar del orden de **~400 tweets por cuenta**.
4. Exportar a ndjson y guardar el archivo en `captures/`.
5. Procesar todos los ndjson con un script que cruza cada tweet con el CSV de diputados y extrae el texto.

Este procedimiento asegura un volumen comparable por cuenta y evita decidir manualmente cuándo detener la captura de cada una.

---

## Cómo reproducir

### 1. Lista de cuentas

Se usa directamente `datos_diputados/processed/deputes_2017_2022.csv`: se filtra por quienes tienen `twitter_handle` y se abre cada perfil (ej. `https://twitter.com/<handle>`). Opcionalmente, el script `generate_twitter_url_list.py` genera una lista de URLs a partir de ese CSV.

### 2. Instalación de Zeeschuimer

Instalar la extensión en Firefox desde los [releases de Zeeschuimer](https://github.com/digitalmethodsinitiative/zeeschuimer/releases) y activar la captura para X/Twitter. Guía oficial: [Zeeschuimer y 4CAT](https://zeeschuimer.4cat.nl/).

### 3. Captura por cuenta

Para cada diputado con Twitter: abrir el perfil, refrescar (Ctrl+F5), activar Zeeschuimer, poner el autoscroller y dejarlo ~15 min (~400 tweets), luego exportar a ndjson y guardar en `captures/`. El ndjson incluye el autor de cada tweet, de modo que el script puede asignar cada tweet al diputado correcto aunque en un mismo archivo haya varias cuentas.

### 4. Unificar y cruzar con diputados

Con los ndjson en `captures/`, ejecutar:

```bash
python3 twitter_zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py
```

El script lee todos los `.ndjson`, extrae texto y metadatos de cada tweet, cruza el handle del autor con `deputes_2017_2022.csv` y escribe en `processed/` (p. ej. `tweets_with_deputies.csv`, `tweets_text_only.csv`). A partir de ahí se trabaja con el **texto** de los tweets.

---

## Cómo se enlaza con el resto

| Qué | Cómo se hizo |
|-----|----------------|
| Lista de diputados con Twitter | `datos_diputados/processed/deputes_2017_2022.csv` |
| Captura | Cuenta por cuenta: autoscroller ~15 min (~400 tweets), export ndjson a `captures/` |
| Procesar | `merge_zeeschuimer_with_deputies.py` → `processed/*.csv` |
| Para la tesis | Se usa el texto de los tweets a partir de esos CSV; ver la memoria en `memoria/`. |
