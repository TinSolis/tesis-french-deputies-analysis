# Captura de Twitter de los diputados con Zeeschuimer

En esta carpeta explico cómo obtuve los tweets de las cuentas de los diputados para la tesis. Uso **Zeeschuimer**: es una extensión de navegador (Firefox) del [Digital Methods Initiative](https://github.com/digitalmethodsinitiative/zeeschuimer) que captura el tráfico que recibe el navegador mientras navego —no es una API: yo voy guardando lo que veo al hacer scroll en cada perfil. Después proceso todo con scripts y me quedo con el texto de los tweets, que es lo que me interesa para el análisis de la *Propuesta_Memoria.pdf*.

---

## Qué hago: cuenta por cuenta, de forma estandarizada

Voy **cuenta por cuenta**. Para cada diputado con Twitter:

1. Abro la URL del perfil (ej. `https://twitter.com/fionalazaar`). Las cuentas las busco en `datos_diputados/processed/deputes_2017_2022.csv` (campo `twitter_handle`).
2. Activo la captura de Zeeschuimer para X/Twitter.
3. Uso un **autoscroller en Firefox** (p. ej. [FoxScroller](https://addons.mozilla.org/en-US/firefox/addon/foxscroller/)) y lo dejo scrollear unos **15 minutos**. Eso suele dar del orden de **~400 tweets por cuenta**.
4. Exporto a ndjson y guardo el archivo en `zeeschuimer/captures/`.
5. Luego proceso todos los ndjson con un script que cruza cada tweet con el CSV de diputados y extrae el texto; ese texto es lo que uso después para la tesis.

Así tengo un volumen comparable por cuenta y evito decidir a mano cuándo parar en cada una.

---

## Estructura que uso

```
francia_deputies/
├── datos_diputados/processed/deputes_2017_2022.csv   # Lista de diputados (con twitter_handle, etc.)
├── zeeschuimer/
│   ├── README.md
│   ├── captures/                     # Exports ndjson de Zeeschuimer
│   ├── processed/                    # Salida: tweets con diputado y texto
│   └── scripts/
│       ├── generate_twitter_url_list.py
│       └── merge_zeeschuimer_with_deputies.py
```

- **Lista de cuentas:** sale de `datos_diputados/processed/deputes_2017_2022.csv` (quien tiene `twitter_handle`); voy abriendo cada perfil desde ahí.
- **captures/:** cada ndjson es una sesión (una cuenta o un lote); los nombro por fecha o por handle.
- **processed/:** el script lee todos los ndjson, cruza por autor (twitter_handle) con el CSV de diputados y escribe CSVs con cada tweet y las columnas del diputado; de ahí me quedo sobre todo con el **texto** para el análisis de la tesis.

---

## Pasos que seguí

### 1. Lista de cuentas

Uso directamente `datos_diputados/processed/deputes_2017_2022.csv`: filtro por quienes tienen `twitter_handle` y voy abriendo cada perfil (ej. `https://twitter.com/<handle>`). Opcionalmente el script `generate_twitter_url_list.py` puede generar una lista de URLs desde ese CSV si se quiere.

### 2. Instalación de Zeeschuimer

Instalé la extensión en Firefox desde los [releases de Zeeschuimer](https://github.com/digitalmethodsinitiative/zeeschuimer/releases) y activé la captura para X/Twitter. Guía oficial: [Zeeschuimer y 4CAT](https://zeeschuimer.4cat.nl/).

### 3. Captura por cuenta

Para cada diputado con Twitter: abro el perfil, refresco (Ctrl+F5), activo Zeeschuimer, pongo el autoscroller y lo dejo ~15 min (~400 tweets), luego exporto a ndjson y guardo en `captures/`. El ndjson incluye el autor de cada tweet, así que después el script puede asignar cada tweet al diputado correcto aunque en un mismo archivo haya varias cuentas.

### 4. Unificar y cruzar con diputados

Cuando tengo ndjson en `captures/`:

```bash
python3 zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py
```

El script lee todos los `.ndjson`, extrae texto y metadatos de cada tweet, cruza el handle del autor con `deputes_2017_2022.csv` y escribe en `processed/` (p. ej. `tweets_with_deputies.csv`, `tweets_text_only.csv`). A partir de ahí trabajo con el **texto** de los tweets para lo que planteo en la *Propuesta_Memoria.pdf*.

---

## Resumen

| Qué | Cómo lo hice |
|-----|----------------|
| Lista de diputados con Twitter | `datos_diputados/processed/deputes_2017_2022.csv` |
| Captura | Cuenta por cuenta: autoscroller ~15 min (~400 tweets), export ndjson a `captures/` |
| Procesar | `merge_zeeschuimer_with_deputies.py` → `processed/*.csv` |
| Para la tesis | Uso el texto de los tweets a partir de esos CSV; ver *Propuesta_Memoria.pdf* en la raíz del repo. |
