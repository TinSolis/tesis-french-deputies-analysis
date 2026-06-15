"""
Utilidades compartidas para validar las estimaciones MARPOR del proyecto contra
el Chapel Hill Expert Survey (CHES) 2019.

CHES es una encuesta de expertos sobre las posiciones de los partidos europeos.
A diferencia de RILE (que se calcula con las mismas categorias MARPOR), CHES es
una fuente *externa* e independiente: sirve como benchmark para responder si
nuestras posiciones estimadas desde texto coinciden con el consenso de expertos.

Escala de `lrgen`: 0 (extrema izquierda) .. 10 (extrema derecha).
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

FRANCE_COUNTRY_CODE = 6  # codigo de Francia en CHES

# Mapeo: abreviatura de partido del proyecto -> nombre del partido en CHES 2019.
# CHES 2019 (Francia) cubre: FI, PCF, PS, EELV, MoDem, LREM, LR, RN, DLF.
# PRG y UDI NO estan en CHES 2019 -> quedan fuera de la correlacion (None).
ABBREV_TO_CHES = {
    "LFI": "FI",       # La France Insoumise
    "FI": "FI",
    "PCF": "PCF",      # Parti Communiste Francais
    "PS": "PS",        # Parti Socialiste
    "EELV": "EELV",    # Europe Ecologie - Les Verts
    "MoDem": "MoDem",  # Mouvement Democrate
    "MODEM": "MoDem",
    "LREM": "LREM",    # La Republique en Marche
    "LAREM": "LREM",
    "LR": "LR",        # Les Republicains
    "FN": "RN",        # Front National -> renombrado Rassemblement National en 2018
    "RN": "RN",
    "PRG": None,       # Parti Radical de Gauche - no esta en CHES 2019
    "UDI": None,       # Union des Democrates et Independants - no esta en CHES 2019
}


def load_ches_france(csv_path: Path) -> pd.DataFrame:
    """Carga el CSV oficial de CHES 2019 y filtra los partidos franceses."""
    df = pd.read_csv(csv_path)
    fr = df[df["country"] == FRANCE_COUNTRY_CODE].copy()
    cols = ["party", "party_id", "lrgen", "lrecon", "galtan"]
    fr = fr[cols].rename(columns={"party": "ches_party"})
    return fr.reset_index(drop=True)


def correlate(x: pd.Series, y: pd.Series) -> dict:
    """
    Pearson + Spearman entre dos series alineadas (mismas filas).

    Devuelve coeficientes, p-values y n. Pensado para n chico (~8-10 partidos),
    por eso Spearman (orden) suele ser la metrica mas honesta.
    """
    from scipy.stats import pearsonr, spearmanr

    pair = pd.DataFrame({"x": x, "y": y}).dropna()
    n = len(pair)
    out = {"n": int(n)}
    if n >= 3:
        pr, pp = pearsonr(pair["x"], pair["y"])
        sr, sp = spearmanr(pair["x"], pair["y"])
        out.update({
            "pearson_r": round(float(pr), 4),
            "pearson_p": round(float(pp), 4),
            "spearman_rho": round(float(sr), 4),
            "spearman_p": round(float(sp), 4),
        })
    else:
        out.update({"pearson_r": None, "pearson_p": None,
                    "spearman_rho": None, "spearman_p": None})
    return out


def scatter_rile_vs_ches(df: pd.DataFrame, *, x_col: str, y_col: str,
                         label_col: str, title: str, out_png: Path,
                         corr: dict | None = None) -> None:
    """Scatter etiquetado por partido, con linea de tendencia."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    d = df.dropna(subset=[x_col, y_col]).copy()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(d[x_col], d[y_col], s=70, color="#1565c0", zorder=3)
    for _, r in d.iterrows():
        ax.annotate(str(r[label_col]), (r[x_col], r[y_col]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    # linea de tendencia
    if len(d) >= 2:
        m, b = np.polyfit(d[x_col], d[y_col], 1)
        xs = np.linspace(d[x_col].min(), d[x_col].max(), 50)
        ax.plot(xs, m * xs + b, "--", color="#b0bec5", zorder=2)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    sub = ""
    if corr and corr.get("spearman_rho") is not None:
        sub = (f"\nSpearman ρ={corr['spearman_rho']}  "
               f"Pearson r={corr['pearson_r']}  n={corr['n']}")
    ax.set_title(title + sub, fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches="tight")
    plt.close(fig)


def dump_json(obj: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
