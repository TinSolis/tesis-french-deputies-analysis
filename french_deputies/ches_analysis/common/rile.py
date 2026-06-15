"""
Calculo del indice RILE (Right-Left) de MARPOR a partir de codigos de categoria.

RILE (Laver & Budge, 1992) es el indice izquierda-derecha estandar del Manifesto
Project. Se calcula como la diferencia entre el porcentaje de quasi-frases en 13
categorias "de derecha" y 13 categorias "de izquierda", sobre el total de frases
codificadas del partido:

    RILE = Σ(% categorias derecha) − Σ(% categorias izquierda)

Escala teorica: −100 (extrema izquierda) .. +100 (extrema derecha). En la practica
los partidos caen en ~[−45, +45].

Este modulo opera sobre una serie de codigos MARPOR de 3 digitos (str o int), sin
importar de donde vengan: del `cmp_code` humano o del `top1_code` predicho por
manifestoberta. Asi el mismo RILE se aplica a ambos y son comparables.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

# Categorias canonicas del indice RILE (Manifesto Project / Laver-Budge)
RIGHT_CODES = {
    "104",  # Military: Positive
    "201",  # Freedom and Human Rights
    "203",  # Constitutionalism: Positive
    "305",  # Political Authority
    "401",  # Free Market Economy
    "402",  # Incentives
    "407",  # Protectionism: Negative
    "414",  # Economic Orthodoxy
    "505",  # Welfare State Limitation
    "601",  # National Way of Life: Positive
    "603",  # Traditional Morality: Positive
    "605",  # Law and Order: Positive
    "606",  # Civic Mindedness: Positive
}

LEFT_CODES = {
    "103",  # Anti-Imperialism
    "105",  # Military: Negative
    "106",  # Peace
    "107",  # Internationalism: Positive
    "202",  # Democracy
    "403",  # Market Regulation
    "404",  # Economic Planning
    "406",  # Protectionism: Positive
    "412",  # Controlled Economy
    "413",  # Nationalisation
    "504",  # Welfare State Expansion
    "506",  # Education Expansion
    "701",  # Labour Groups: Positive
}


def normalize_code(code) -> str | None:
    """
    Normaliza un codigo MARPOR a su string de 3 digitos.

    Tolera:
      - ints / floats ('305', 305, 305.0)
      - subcategorias H5 con punto decimal ('606.1' -> '606')
      - prefijo 'per' ('per504' -> '504')
      - headers / vacios / NaN -> None
    """
    if code is None:
        return None
    s = str(code).strip().lower()
    if not s or s in {"nan", "none", "h", "0", "000"}:
        return None
    if s.startswith("per"):
        s = s[3:]
    if "." in s:                      # 606.1 -> 606  (colapsa subcategorias)
        s = s.split(".")[0]
    if not s or not s[0].isdigit():
        return None
    return s


def compute_rile(codes: Iterable) -> tuple[float, int]:
    """
    Calcula RILE sobre un iterable de codigos MARPOR.

    Devuelve (rile, n_coded) donde n_coded es la cantidad de codigos validos
    usados como denominador. Los codigos no clasificables (headers, NaN) se
    descartan y no cuentan en el denominador.

    El porcentaje de cada categoria se toma sobre n_coded (todas las frases
    codificadas), no solo sobre las RILE, siguiendo la definicion estandar.
    """
    counts = Counter()
    n_coded = 0
    for c in codes:
        nc = normalize_code(c)
        if nc is None:
            continue
        counts[nc] += 1
        n_coded += 1
    if n_coded == 0:
        return float("nan"), 0
    right = sum(counts[c] for c in RIGHT_CODES)
    left = sum(counts[c] for c in LEFT_CODES)
    rile = (right - left) / n_coded * 100.0
    return rile, n_coded
