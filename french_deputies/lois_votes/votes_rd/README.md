# votes_rd — dónde guardé los datos brutos de votaciones (AN 2017–2022)

Yo usé esta carpeta como **caja** para todo lo que bajé de la Asamblea antes de generar mis tablas finales en **`processed/`**. Así no mezclo ZIPs gigantes con los CSV que abro en Stata o Python todos los días.

- **Raíz de `votes_rd/`:** los ZIP que descargué (`Scrutins_XV.json.zip`, `Dossiers_Legislatifs_XV.json.zip`), si no los ignoré en Git por tamaño.
- **`json/`:** después de descomprimir Scrutins, la AN me dejó **un JSON por scrutin** (`VTANR5L15V*.json`); mi `build_laws_and_votes.py` los lee **todos**. El ZIP de Dossiers aporta sobre todo material para el paso de textos oficiales (`build_leyes_texte_oficial.py`), no es obligatorio solo para armar la tabla de votos.
- **`processed/`:** acá escribí yo los CSV que salen de `build_laws_and_votes.py` (y el otro script si lo corrí).

La explicación completa del flujo (qué es un scrutin, qué columnas tienen los CSV, comandos) la escribí en **`../README_LOIS_VOTES.md`** para tenerla en un solo lugar.
