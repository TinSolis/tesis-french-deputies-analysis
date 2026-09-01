# Contexto de la carpeta: `french_deputies/ches_analysis/`

## Propósito

Este módulo realiza la **validación externa** del pipeline de clasificación temática del proyecto. Estima la posición **izquierda–derecha (RILE)** de cada partido a partir de las predicciones MARPOR (de `manifestoberta_analysis/`) sobre los manifiestos 2017 y la correlaciona contra un **benchmark independiente**: el **Chapel Hill Expert Survey (CHES) 2019**, encuesta de ~420 politólogos. Responde: *¿las posiciones que estimo desde texto coinciden con dónde los expertos ubican a los partidos?* Es la pieza que aporta **evidencia de validez** al método antes de usarlo a nivel diputado.

---

## Archivos importantes

### Núcleo (`common/`)

| Archivo | Función |
|---------|---------|
| `common/rile.py` | Cálculo del índice RILE (Laver & Budge, 1992): define los 13+13 códigos canónicos derecha/izquierda, `normalize_code()` y `compute_rile()`. |
| `common/ches.py` | Carga CHES Francia (`country == 6`), mapeo `ABBREV_TO_CHES`, `correlate()` (Pearson + Spearman), `scatter_rile_vs_ches()`. |

### Datos

| Archivo | Contenido |
|---------|-----------|
| `data/CHES2019V3.csv` | CHES 2019 oficial (descargado de chesdata.eu); columnas `lrgen`, `lrecon`, `galtan` por partido. **Versionado**. |

### Pipeline y salidas

| Archivo | Rol |
|---------|-----|
| `manifestos/run.py` | Orquesta: RILE modelo/humano/oficial por partido, empareja con CHES, correlaciona en 3 capas + diagnósticos, exporta. |
| `manifestos/results/party_rile.csv` | RILE por partido (modelo, humano, oficial) + emparejamiento CHES. |
| `manifestos/results/rile_vs_ches.csv` | Solo partidos con CHES (`lrgen`/`lrecon`/`galtan`). |
| `manifestos/results/correlations.json` | Las 3 capas + diagnósticos (ρ, r, p, n). |
| `manifestos/results/scatter_rile_vs_ches.png` | Scatter etiquetado por partido con tendencia. |

> A diferencia de `bertopic_analysis/` y `manifestoberta_analysis/`, aquí los `results/` están **versionados** (archivos pequeños).

---

## Flujo / lógica principal

```
manifestoberta_analysis/manifestos/results/predictions.csv
   (top1_code modelo + cmp_code humano por quasi-frase)
         │
         ▼
manifestos/run.py
         ├── rile_per_party(top1_code) → rile_model
         ├── rile_per_party(cmp_code)  → rile_human
         ├── party_positions.csv       → rile_official (sanity check)
         ├── data/CHES2019V3.csv        → lrgen (vía ABBREV_TO_CHES)
         └── correlate() × 3 capas + diagnósticos
                  │
                  ▼
   party_rile.csv · rile_vs_ches.csv · correlations.json · scatter_rile_vs_ches.png
```

**Entradas:** `predictions.csv` (de ManifestoBERTa), `party_positions.csv` (de `manifestos/`), `CHES2019V3.csv` (local).

**Salida clave:** `correlations.json` con las tres capas de validación.

---

## Metodología

Enfoque de **validación de constructo** mediante correlación con un gold standard externo. No hay ML aquí: es agregación + estadística.

| Etapa | Técnica | Detalle |
|-------|---------|---------|
| **1. RILE por partido** | `compute_rile()` | Cuenta quasi-frases por categoría; `RILE = Σ%(derecha) − Σ%(izquierda)` sobre n codificadas. Escala ≈ −45..+45. |
| **2. Triple cálculo** | mismas frases, dos fuentes | `rile_model` (top1_code), `rile_human` (cmp_code), `rile_official` (MARPOR publicado). Separa error del modelo vs. error del método. |
| **3. Emparejamiento CHES** | `ABBREV_TO_CHES` | FN→RN; PRG y UDI **no** están en CHES 2019 (quedan fuera de correlación). |
| **4. Correlación** | `scipy` Pearson + Spearman | n chico (~8–10): Spearman (orden) es la métrica honesta. |
| **5. Visualización** | matplotlib | Scatter con línea de tendencia. |

**Las tres capas de validación:**

| Capa | Compara | Pregunta | n |
|------|---------|----------|---|
| **A** | `rile_model` vs `rile_human` | ¿el modelo reproduce la codificación humana al agregar? | 10 |
| **B** | `rile_model` vs CHES `lrgen` | **validación externa** | 8 |
| **Techo** | `rile_human` vs CHES `lrgen` | ¿cuánto coinciden dos gold standards? | 8 |

**Diagnósticos adicionales:** vs `lrecon` (eje económico), excluyendo RN, y restringido a partidos con **≥100 quasi-frases** (umbral de fiabilidad MARPOR).

**Criterios de evaluación:** coeficiente de correlación (ρ, r), p-value, n; comparación contra rango de literatura MARPOR-vs-CHES (~0,6–0,8).

**Supuestos / limitaciones de ingeniería:**
- RILE es índice **posicional 1-D, frágil y ciego a la dirección** (305 *Autoridad Política* cuenta igual ataque que defensa del gobierno).
- Solo se valida sobre **manifiestos** (único canal con `cmp_code` humano); no se extiende a tweets/hemiciclo a propósito.
- n muy chico (8–10 partidos): correlaciones sensibles a outliers (PCF con 39 frases).
- CHES mide *posición percibida*; RILE mide *énfasis temático* → no coinciden al 100 %.

**Dependencias:** `pandas`, `scipy`, `matplotlib`, `numpy`.

---

## Información útil para la tesis

| Sección | Qué aporta |
|---------|------------|
| **Metodología — validación** | Diseño de validación externa con CHES; cálculo de RILE; tres capas. |
| **Resultados** | Correlaciones (A 0,79 / B 0,38→0,89 / techo 0,76); tabla RILE por partido; scatter. |
| **Discusión** | Limitaciones de RILE con derecha radical y centristas; sensibilidad al tamaño de muestra. |
| **Validez del método** | Frase clave: con ≥100 frases, ρ≈0,89 con CHES, en rango de la codificación humana. |
| **Anexos** | Códigos RILE derecha/izquierda; mapeo partido→CHES; `correlations.json`. |

---

## Resultados, decisiones o detalles relevantes

**Correlaciones (`README.md` / `correlations.json`):**

| Comparación | Spearman ρ | Pearson r | n |
|-------------|-----------:|----------:|--:|
| A) modelo vs humano | **0,79** | 0,85 | 10 |
| B) modelo vs CHES (externo) | **0,38** | 0,42 | 8 |
| Techo) humano vs CHES | **0,76** | 0,75 | 8 |
| diag. modelo vs CHES `lrecon` | 0,57 | 0,43 | 8 |
| diag. modelo vs CHES (sin RN) | 0,36 | 0,37 | 7 |
| diag. **modelo vs CHES (≥100 frases)** | **0,89** | 0,72 | 6 |

**Lecturas clave:**
- **Cálculo correcto:** techo humano vs CHES ρ=0,76, en el rango de literatura (~0,6–0,8).
- **El modelo reproduce al humano** al agregar por partido (ρ=0,79) pese a accuracy por-frase ~58 % (los errores se cancelan).
- **Validación externa fuerte con suficiente texto:** ρ sube de 0,38 (n=8, arrastrado por PCF) a **0,89** restringiendo a ≥100 frases.

**Outliers estructurales (no bugs):**
- **FN/RN:** RILE lo centra (−6 modelo, +1,7 humano) vs. CHES 9,75 — limitación clásica de RILE con derecha radical (enfatiza welfare 504, "de izquierda").
- **MoDem/LREM:** centristas que enfatizan welfare → RILE los corre a la izquierda.
- **PCF:** único error claramente del modelo, por muestra mínima (39 frases).

**Decisiones técnicas:**
- Validación deliberadamente **limitada a manifiestos** (techo humano disponible).
- RILE solo como validación del pipeline; el análisis cross-canal de la tesis usa **énfasis temático** (distribuciones MARPOR), no posición.

---

## Dudas o cosas a revisar

1. **Dependencia de `predictions.csv`:** los `results/` de `manifestoberta_analysis/` están gitignored; para reproducir hay que regenerar primero ese CSV.
2. **n pequeño:** todas las correlaciones se basan en 6–10 partidos; reportar siempre el n y preferir Spearman en la memoria.
3. **`rile_official` incompleto:** el CSV oficial tiene `partyabbrev` vacío para LFI y LR; el script los completa por nombre (`name_to_abbrev`) — verificar que el emparejamiento es correcto.
4. **Versión CHES:** se usa CHES **2019** vs. manifiestos **2017**; hay desfase temporal de 2 años (asumido razonable, pero conviene mencionarlo).
5. **`galtan`/`lrecon`:** se cargan pero solo `lrecon` entra como diagnóstico; documentar si `galtan` se usará.
6. **«lo sugirió Franziska»** en README: referencia interna informal, quitar de la redacción final de la memoria.

---

## Resumen corto

`ches_analysis/` valida el pipeline MARPOR del proyecto contra un benchmark externo de expertos (**CHES 2019**). Calcula **RILE** por partido desde las predicciones de ManifestoBERTa sobre los manifiestos y lo correlaciona con `lrgen` en tres capas. Resultado central: con ≥100 quasi-frases por partido, el RILE estimado correlaciona **ρ≈0,89** con CHES — en el rango de la codificación humana de MARPOR. Es la **evidencia de validez** del método; se limita a manifiestos por diseño (único canal con ground truth humano).

---

## Citas

- **CHES 2019:** Bakker, R., Hooghe, L., Jolly, S., Marks, G., Polk, J., Rovny, J., Steenbergen, M., & Vachudova, M. A. (2020). *2019 Chapel Hill Expert Survey (CHES)*. [chesdata.eu](https://www.chesdata.eu/). Trend file: Jolly et al. (2022), *Electoral Studies*, [doi:10.1016/j.electstud.2021.102420](https://doi.org/10.1016/j.electstud.2021.102420).
- **RILE:** Laver, M. & Budge, I. (1992) — índice izquierda-derecha estándar MARPOR; implementación en `common/rile.py`.
- **Entradas del pipeline:** `manifestoberta_analysis/manifestos/results/predictions.csv`, `manifestos/processed/party_positions.csv`.
- **Documentación interna:** `french_deputies/ches_analysis/README.md`, `common/rile.py`, `common/ches.py`, `manifestos/run.py`.
- **Módulos relacionados:** `french_deputies/manifestoberta_analysis/`, `french_deputies/manifestos/`, `french_deputies/party_analysis/`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/ches_analysis/` — **validación externa** del pipeline: estima RILE por partido desde las predicciones MARPOR sobre los manifiestos y lo correlaciona con el **Chapel Hill Expert Survey (CHES) 2019**. Es la **evidencia de validez** del método. Acotado por diseño: solo manifiestos (único canal con `cmp_code`).

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Revisión de literatura** | CHES como benchmark de expertos; RILE (Laver & Budge, 1992) y sus límites. |
| **Metodología** | Diseño de validación externa; cálculo de RILE; las **tres capas** (A/B/techo). |
| **Validación** (principal) | El capítulo/sección de validación se apoya casi enteramente aquí. |
| **Resultados** | Correlaciones por capa; tabla RILE por partido; scatter. |
| **Discusión** | Límites de RILE con derecha radical y centristas; sensibilidad al n. |
| **Anexos** | Códigos RILE 13+13; mapeo partido→CHES; `correlations.json`. |

**Información concreta a extraer:**
- **Frase clave de validez:** con **≥100 quasi-frases** por partido, RILE estimado correlaciona **ρ≈0,89** con CHES — en el rango de la codificación humana.
- El modelo **reproduce al humano** al agregar (ρ=0,79) pese a accuracy por-frase ~58 % (los errores se cancelan); techo humano vs. CHES ρ=0,76 (cálculo correcto).
- Preferir **Spearman** (n=6–10); RILE se usa **solo para validar**, no para el análisis cross-canal (que va por énfasis).

**Figuras, tablas o métricas que contiene/menciona:**
- **Tabla de correlaciones** (A 0,79 / B 0,38→**0,89** con ≥100 frases / techo 0,76 + diagnósticos `lrecon`, sin RN).
- **`scatter_rile_vs_ches.png`** (figura **versionada** y citable). Aquí los `results/` **sí** están en Git.

**Limitaciones / dudas a trasladar:**
- RILE es **posicional 1-D, frágil y ciego a la dirección**; FN/RN y centristas (MoDem/LREM) son outliers estructurales (no bugs); PCF arrastra B por sus 39 frases.
- Desfase temporal **CHES 2019 vs. manifiestos 2017** (asumido razonable); PRG y UDI no están en CHES.
- Depende de `predictions.csv` (gitignored) → regenerar antes de reproducir; quitar referencias internas informales del README.
