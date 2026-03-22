# votes_rd — datos votaciones AN (2017-2022)

- **Raíz de `votes_rd/`**: ZIP descargados (`Scrutins_XV.json.zip`, `Dossiers_Legislatifs_XV.json.zip`).
- **`json/`**: tras descomprimir Scrutins, la AN publica **un JSON por scrutin** (`VTANR5L15V*.json`); el script `build_laws_and_votes.py` los lee todos. El ZIP de Dossiers añade `json/document/` (textos); no hace falta para el build de votos.
- **`processed/`**: CSV generados por `build_laws_and_votes.py`.

Ver `../README_LOIS_VOTES.md`.
