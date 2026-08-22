# Capturas de Zeeschuimer

## Propósito

Almacena los exports **`*.ndjson`** generados por Zeeschuimer. Estos archivos **no** se versionan en GitHub tal cual, porque suelen superar el límite de 100 MB por archivo.

## Cómo se usa

1. Al terminar una captura, dejar el `.ndjson` en esta carpeta.
2. Desde **`french_deputies/`**, ejecutar:

   ```bash
   python3 twitter_zeeschuimer/scripts/merge_zeeschuimer_with_deputies.py
   ```

## Cómo se enlaza con el resto

Lo que se versiona o comparte es la salida en **`twitter_zeeschuimer/processed/`** (CSVs con el texto ya unido a los diputados).
