"""
Fuente unica de verdad para la familia analitica FN (Front National / RN) en la
XV legislatura (2017-2022).

Contexto: los diputados FN/RN de la XV legislatura no formaron grupo parlamentario
propio (necesitaban >=15 escanos) y figuran como `NI` (Non inscrit) en los datos.
Para que `party_analysis` los trate como una familia politica normal -- separada
del agregado heterogeneo `NI` -- se define aqui el override por `deputy_id`.

Decision metodologica:
  - Se incluyen EXACTAMENTE los 11 `deputy_id` listados abajo como `FN`.
  - NO se convierte todo `NI` en `FN`: el resto de `NI` sigue siendo familia residual.
  - El override es por `deputy_id` (estable), no por nombre.

Caveat sobre Jose Evrard (720664): abandono el FN en noviembre de 2017 (paso a
"Les Patriotes"). Se mantiene dentro de `FN` porque forma parte de la lista
definida para este analisis; su actividad post-ruptura queda atribuida a `FN`.
Es el unico caso cuya inclusion es discutible y debe senalarse en la memoria.
"""

from __future__ import annotations

import pandas as pd

FN_LABEL = "FN"

# 11 diputados FN/RN de la XV legislatura (electos 2017 + suplentes + Menard).
FN_DEPUTY_IDS = {
    606212,  # Gilbert Collard
    720614,  # Marine Le Pen
    720822,  # Bruno Bilde
    720606,  # Ludovic Pajot
    720468,  # Sebastien Chenu
    720798,  # Louis Aliot
    719608,  # Emmanuelle Menard (electa con apoyo del FN; NI apparentee)
    719436,  # Nicolas Meizonnet (suplente de Collard)
    720610,  # Myriane Houplain (suplente de Pajot)
    720802,  # Catherine Pujol (suplente de Aliot)
    720664,  # Jose Evrard (dejo el FN en nov-2017; ver caveat en el modulo)
}


def apply_fn_override(df: pd.DataFrame, party_col: str = "party",
                      id_col: str = "deputy_id") -> pd.DataFrame:
    """Reasigna a `FN` las filas cuyo `deputy_id` esta en `FN_DEPUTY_IDS`.

    - No falla si falta `id_col` (p.ej. manifiestos, que no tienen diputado):
      en ese caso devuelve el dataframe sin cambios.
    - Convierte `deputy_id` a numerico de forma segura (ids no parseables -> NaN,
      que nunca caen en el set).
    - Solo toca las filas de los 11 ids; el resto de `NI` queda intacto.
    """
    if id_col not in df.columns or party_col not in df.columns:
        return df
    ids = pd.to_numeric(df[id_col], errors="coerce")
    mask = ids.isin(FN_DEPUTY_IDS)
    if mask.any():
        df.loc[mask, party_col] = FN_LABEL
    return df
