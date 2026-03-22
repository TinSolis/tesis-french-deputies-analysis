# Textos oficiales (JORF / Légifrance)

Para rellenar la columna **`texto_oficial`** en `processed/leyes_texto_oficial.csv`, coloca aquí archivos **UTF-8**:

- `{scrutin_id}.txt` — mismo `scrutin_id` que en `votos_por_diputado.csv` / `leyes_votadas_2017_2022.csv`, **o**
- `{NOR}.txt` — mismo NOR que en la columna `nor_jo` (ej. `CPAX1723900L`).

Luego ejecuta:

```bash
cd francia_deputies
python3 lois_votes/scripts/build_leyes_texte_oficial.py
```

El script copiará el contenido del `.txt` en el CSV.

**Origen del texto:** copia desde Légifrance (navegador) o usa la **API Légifrance vía PISTE** ([piste.gouv.fr](https://piste.gouv.fr)) — la web suele bloquear descargas automáticas sin navegador (Cloudflare).
