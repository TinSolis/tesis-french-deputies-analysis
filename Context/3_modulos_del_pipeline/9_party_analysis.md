# Contexto de la carpeta: `french_deputies/party_analysis/`

> **Módulo central de la tesis.** Es el punto de convergencia de todas las fuentes (manifiestos, tweets, hemiciclo, leyes, enmiendas) y donde se producen los **tres análisis** que articulan el arco argumental: agenda **declarada** (lo que el partido dice), agenda **revelada** (lo que el partido vota) y su **cruce** (¿votan lo que dicen?). Este documento es exhaustivo a propósito: está pensado como guía de redacción del capítulo principal.

---

## Propósito

El módulo extrae **insights a nivel de partido** a partir de las clasificaciones MARPOR producidas por `manifestoberta_analysis/`. La pregunta deliberadamente **no** es *dónde se ubica* cada partido en el eje izquierda-derecha —eso es frágil con RILE y se valida aparte en `ches_analysis/`— sino:

1. **¿De qué habla cada partido?** Su énfasis temático / "firma" (agenda **declarada**).
2. **¿Qué políticas apoya o rechaza al votar?** (agenda **revelada**).
3. **¿Coincide lo que dice con lo que vota?** (el cruce, aporte central).

Se trabaja sobre la **distribución completa de los 7 dominios y las 56 categorías MARPOR**, no sobre un índice colapsado: esto describe el énfasis observado sin sufrir el problema de dirección que rompe a RILE (la categoría 305 "Autoridad Política" cuenta igual al que ataca que al que defiende al gobierno).

### Las dos formas de atribuir texto a un partido

| Familia | Corpus | Cómo se atribuye | Señal medida |
|---|---|---|---|
| **Texto producido** | `manifestos/`, `tweets/`, `interventions/` | el partido (o sus diputados) **escribe** el texto | **énfasis** (*salience*): de qué habla → agenda **declarada** |
| **Texto votado** | `lois/`, `amendements/` | la ley/enmienda no tiene autor partidario; el partido revela preferencia **votando** | **soporte por tema**: qué apoya/rechaza → agenda **revelada** |

---

## Archivos importantes

### Núcleo reutilizable (`common/`)

**`common/families.py`** — **fuente única de verdad** del override de la familia analítica **`FN`** (Front National / RN). Los diputados FN/RN de la XV legislatura no formaron grupo (necesitaban ≥15 escaños) y figuran como `NI` en los datos. Define:
- `FN_DEPUTY_IDS`: el set de **11 `deputy_id`** (electos 2017 + suplentes + Emmanuelle Ménard) que se reagrupan como `FN`.
- `apply_fn_override(df, party_col, id_col)`: reasigna a `FN` **solo** esas 11 filas; **no convierte todo `NI`** (el resto queda residual) y es no-op si el corpus no trae `deputy_id` (manifiestos). Tanto `analysis.py` como `votes.py` importan de aquí: **no hay listas de ids duplicadas**.

**`common/analysis.py`** — motor de **énfasis temático**. Contiene:
- `DOMAIN_NAMES`: los 7 dominios MARPOR (1 External Relations, 2 Freedom & Democracy, 3 Political System, 4 Economy, 5 Welfare & QoL, 6 Fabric of Society, 7 Social Groups).
- `GROUP_LABEL`: consolida grupos parlamentarios (XV legislatura) en familias políticas legibles (`LAREM/LREM`→LREM, `DEM/MODEM`→MoDem, `LR/LC`→LR, `FI`→LFI, `GDR`→GDR-PCF, `SOC/NG`→PS, `UDI_I/UDI-I/UDI-AGIR/UDI-A-I/AGIR-E`→UDI-Agir, `LT`→LT, `EDS`→EDS, `NI`→NI). Tras este mapeo, `load_preds` aplica `apply_fn_override` por `deputy_id` (tweets/hemiciclo) para separar `FN` del residuo `NI`.
- `load_preds` (carga, normaliza partido, filtra dominios 1–7 y partidos con < `min_docs`), `domain_distribution` (crosstab % por fila), `category_distribution`, `distinctiveness` (sobre/sub-énfasis vs. promedio del corpus, top-6 over/under en pp), `concentration` (entropía normalizada / *evenness*).
- `plot_domain_heatmap` (partido × 7 dominios, % con `YlOrRd`) y `plot_signature_heatmap` (16 categorías de mayor varianza entre partidos, **z-score** con `RdBu_r`).
- `run(...)`: orquesta y escribe los 4 CSV + `summary.json` + 2 heatmaps por corpus.

**`common/votes.py`** — motor de **voto**. Contiene:
- `load_deputy_party` (deputy_id → familia vía `GROUP_LABEL`, **luego override `FN` por `deputy_id`** de `families.py`), `party_stance` (Pour/Contre por partido×scrutin, filtro `MIN_EXPRESSED=3`, calcula `support_rate` y `rice`).
- `scrutin_domain_counts` (composición de dominios del texto), `weighted_domain_support` (soporte ponderado por contenido: `Σ(n_{s,d}·support_{p,s}) / Σ n_{s,d}`), `overall_support_and_cohesion` (soporte global + **índice Rice** ponderado), `relative_support` (soporte por tema − soporte global), `supported_vs_opposed_agenda` (distribución de dominios de lo que apoya vs. rechaza, umbral 0.5).
- `plot_domain_support_heatmap` (soporte relativo, divergente `RdBu`) y `plot_support_cohesion` (scatter soporte×cohesión).
- `run(...)`: escribe 4 CSV + `summary.json` + 2 figuras.

### Agenda declarada — un `run.py` por corpus (todos invocan `analysis.run`)

| Carpeta | Entrada (`manifestoberta_analysis/.../predictions.csv`) | Columna de partido | `min_docs` |
|---|---|---|---|
| `manifestos/run.py` | `manifestos/results/predictions.csv` | `party_abbrev` | 30 |
| `tweets/run.py` | `tweets/results/predictions.csv` | `political_group_abbrev` (→`GROUP_LABEL`) | 1000 |
| `interventions/run.py` | `interventions/results/predictions.csv` | `political_group_abbrev` (→`GROUP_LABEL`) | 1000 |

Salidas en cada `results/`: `party_domain_distribution.csv`, `party_category_distribution.csv`, `distinctive_categories.csv`, `agenda_concentration.csv`, `summary.json`, `heatmap_party_domain.png`, `heatmap_party_signature.png`, `run.log`.

### Agenda revelada — un `run.py` por corpus (ambos invocan `votes.run`)

| Carpeta | Predictions | Votos (`lois_votes/votes_rd/processed/`) | Diputados |
|---|---|---|---|
| `lois/run.py` | `lois/results/predictions.csv` | `votos_por_diputado.csv` | `datos_diputados/data/deputes_an_rd.csv` |
| `amendements/run.py` | `amendements/results/predictions.csv` | `votos_amendements_por_diputado.csv` | idem |

Salidas: `party_domain_support.csv`, `party_domain_support_relative.csv`, `party_cohesion.csv`, `supported_vs_opposed_agenda.csv`, `summary.json`, `heatmap_domain_support.png`, `scatter_support_cohesion.png`, `run.log`.

### Análisis transversales (los tres "capítulos")

| Script | Documento de prosa | Rol |
|---|---|---|
| `cross_channel/build.py` | `cross_channel/01_canal_cambia_agenda.md` | **Análisis 1** — ¿habla igual en programa, Twitter y hemiciclo? |
| `agenda_revelada/build.py` | `agenda_revelada/02_voto_dos_capas.md` | **Análisis 2** — ¿el voto revela tema o solo posición? |
| `declarado_vs_revelado/build.py` | `declarado_vs_revelado/03_declarado_vs_revelado.md` | **Análisis 3** — ¿votan lo que dicen? |

> Los tres `.md` (`01_`, `02_`, `03_`) son **redacciones de capítulo casi finales**: contienen prosa, tablas, frases-síntesis y caveats listos para la memoria.

---

## Flujo / lógica principal

```
manifestoberta_analysis/{manifestos,tweets,interventions,lois,amendements}/results/predictions.csv
   +  lois_votes/votes_rd/processed/votos_por_diputado.csv
   +  lois_votes/votes_rd/processed/votos_amendements_por_diputado.csv
   +  datos_diputados/data/deputes_an_rd.csv
         │
         ├── DECLARADA: manifestos/ tweets/ interventions/ run.py  → common/analysis.py
         │       → party_domain_distribution.csv, party_category_distribution.csv, ...
         │
         ├── REVELADA: lois/ amendements/ run.py  → common/votes.py
         │       → party_domain_support[_relative].csv, party_cohesion.csv, ...
         │
         ├── cross_channel/build.py     (Análisis 1; lee las predictions directamente)
         ├── agenda_revelada/build.py   (Análisis 2; lee predictions + votos + diputados)
         └── declarado_vs_revelado/build.py (Análisis 3; lee los results/ de los 4 corpus + scipy)
```

**Orden de ejecución obligatorio:** primero los 5 `run.py` por corpus, luego los 3 `build.py`. `cross_channel` y `agenda_revelada` leen también directamente las `predictions.csv` de ManifestoBERTa; `declarado_vs_revelado` consume los `results/*.csv` ya calculados (`party_domain_distribution.csv` de los 3 canales declarados + `party_domain_support_relative.csv` de enmiendas).

> **Nota:** los `run.py` de `lois/`/`amendements/` y `agenda_revelada/build.py` usan **los mismos** archivos de votos (`votos_por_diputado.csv`, `votos_amendements_por_diputado.csv`) y el mismo `deputes_an_rd.csv` — el dataset es consistente entre el cálculo por-corpus y el transversal.

---

## Metodología (detallada)

### A. Agenda declarada — énfasis temático (`common/analysis.py`)

- **Distribución por dominio/categoría:** `pd.crosstab` normalizado por fila → % de quasi-frases de cada partido en cada dominio/categoría.
- **Distintividad (la "firma"):** `%_partido − promedio_del_corpus`, en puntos porcentuales. Es comparable **entre partidos dentro de un canal**, no entre canales. Se reportan las 6 categorías más sobre-enfatizadas (`over`) y las 6 más sub-enfatizadas (`under`).
- **Concentración de agenda:** entropía de Shannon normalizada (*evenness* = `H / log₂k`, con `H = −Σ p·log₂p` sobre las categorías). Baja = monotemático; alta = agenda diversa.
- **Heatmap de firma:** se eligen las 16 categorías con **mayor varianza entre partidos** y se grafican en **z-score por columna** (rojo = sobre-enfatiza).
- **Consolidación de partidos** (`GROUP_LABEL` + override `FN`): tweets/hemiciclo traen `political_group_abbrev`; se mapea a familia y luego se aplica el override por `deputy_id` que separa **`FN`** (11 diputados) del residuo **`NI`** (heterogéneo, **no proxy de FN/RN**). **Filtros mínimos (sin cambios al incorporar FN):** 1.000 frases por familia en tweets/hemiciclo; 30 en manifiestos.

### B. Agenda revelada — voto (`common/votes.py`)

- **Soporte global:** `%Pour = Pour / (Pour+Contre)` sobre votos **expresados** (las abstenciones y no-votantes quedan fuera del denominador).
- **Cohesión (índice Rice):** `|Pour−Contre| / (Pour+Contre)`, promediado ponderando por nº de votos. 1 = unanimidad de bloque.
- **Soporte por tema:** ponderado por la composición MARPOR del texto del scrutin: `Σ_s(n_{s,d}·support_{p,s}) / Σ_s n_{s,d}`.
- **Soporte relativo:** `soporte_por_tema[p,d] − soporte_global[p]`. Aísla la señal temática del efecto gobierno/oposición.
- **Filtro:** un scrutin entra al cálculo de un partido solo si **≥3** de sus diputados expresan voto (`MIN_EXPRESSED=3`).
- **Precisión conceptual crítica:** "soporte relativo negativo" ≠ "vota en contra". Mide apoyo *por debajo de la propia base* del partido, no apoyo absoluto. (Ej.: la izquierda apoya *Fabric of Society* relativo −16/−22 pp pero en absoluto sigue aprobando 60–69%.)

### C. Análisis 1 — cross-channel (`cross_channel/build.py`)

Sobre los **7 partidos presentes en los 3 canales** (LFI, PS, PCF=GDR-PCF, MoDem, LREM, LR, **FN**):
- **Shift bruto:** distancia euclídea media (pp) del perfil de dominios entre los 3 canales. Confunde estrategia del partido con efecto estructural del canal.
- **Shift específico:** lo mismo sobre la **firma centrada** (perfil − promedio del canal sobre los 7 partidos) → descuenta el efecto canal, aísla la estrategia.
- **Reducción por centrado** = bruto − específico (aproximación descriptiva del efecto canal, no descomposición aditiva exacta).
- **Persistencia de firma (Opción A):** correlación de los vectores-firma de categorías entre pares de canales (`corr_man_twe`, `corr_man_hem`, `corr_twe_hem`, `mean_corr`).
- **Overlap (Opción B):** categorías-firma (top-6) que reaparecen en ≥2 canales.
- **IC95 por bootstrap:** 2.000 remuestreos multinomiales de quasi-frases (semilla 7). Crítico por los manifiestos chicos (PCF 39, PS 79 frases).
- **Métrica única:** distancia **euclídea en pp** (no Jensen-Shannon) por interpretabilidad directa.

### D. Análisis 2 — voto en dos capas (`agenda_revelada/build.py`)

- **Descomposición de R² ponderado** sobre la unidad `partido×scrutin` (outcome = %Pour ponderado por nº de votos), 4 modelos anidados:
  - **bloque** (mayoría LREM+MoDem vs. oposición),
  - **partido** (11 familias, incluida FN),
  - **partido+dominio** (aditivo, vía WLS con dummies y `np.linalg.lstsq`),
  - **partido×dominio** (interacción, medias de celda).
  Se compara **capacidad explicativa** (R²), no p-values (con cientos de miles de votos casi todo es "significativo").
- **Bootstrap por scrutin (clúster):** 1.000 réplicas (semilla 11) remuestreando *scrutins* con reemplazo → IC95 y **estabilidad de signo** del soporte relativo.
- **Chequeo de leverage:** nº de scrutins por dominio y, además, en cuántas **leyes distintas** se reparten las enmiendas de cada dominio (descarta que un clivaje venga de un único debate).
- **Definición de bloque:** Gobierno = LREM + MoDem; el resto oposición (UDI-Agir, aliado intermitente, queda en oposición → probablemente *subestima* el R² del bloque).

### E. Análisis 3 — declarado vs. revelado (`declarado_vs_revelado/build.py`)

- Las dos señales viven en unidades distintas (declarada = salience no signada; revelada = soporte signado) → **no se restan**; se comparan como **firmas relativas centradas** y vía **correlación** (invariante a escala).
- **Resultado central — tipología por celda** (signo declarado × signo revelado):
  - (+,+) **énfasis respaldado**, (+,−) **énfasis no respaldado**, (−,+) **apoyo no enfatizado**, (−,−) **baja prioridad y menor apoyo relativo**.
  - Robustez con **zona neutra ±1 pp** (`BAND=1.0`): 0% de inversiones de cuadrante; los casos chicos solo pasan a "neutro".
- Correlación por partido sobre **6 dominios** (se excluye *External Relations* por bajo leverage), reportada **con IC bootstrap de dominios** (2.000, semilla 13) para mostrar su **fragilidad**, no para concluir. Se acompaña de Spearman y una variante re-centrada por dominio.
- **Pooled por canal**, en dos versiones: "todos" (7 partidos en manifiesto, 11 en tweets/hemiciclo) y el set comparable común (hoy **7**, incluida FN; el tag interno "6p" es histórico y la columna `n_parties=7` es la fuente de verdad), re-centrado para comparación justa entre canales.
- **Cobertura:** manifiesto vs. voto = **7 partidos** (manifiesto indexado por partido electoral 2017 — FN tiene manifiesto propio; voto por grupo parlamentario); tweets/hemiciclo vs. voto = hasta **11**. `NI` **no** entra al cruce del manifiesto (no es partido electoral 2017) y queda como residuo.

**Herramientas:** `pandas`, `numpy`, `scipy.stats` (`pearsonr`, `spearmanr`), `matplotlib`. **Sin GPU ni modelos nuevos:** todo es agregación + estadística sobre las predicciones ya existentes de ManifestoBERTa.

---

## Información útil para la tesis

| Sección de la memoria | Qué aporta este módulo |
|---|---|
| **Metodología** | Definición de todas las métricas (énfasis, distintividad, evenness, Rice, soporte global/por tema/relativo, shift bruto/específico, persistencia, descomposición R², tipología); decisiones de consolidación de partidos, filtros y bloque. |
| **Implementación** | `common/analysis.py` y `common/votes.py` como librerías reutilizables; arquitectura por corpus + transversales; bootstrap multinomial y por clúster; WLS con dummies. |
| **Experimentos / Resultados** | Los **tres análisis** son el cuerpo de resultados; los `.md` (`01_`/`02_`/`03_`) ya son prosa de capítulo con tablas y figuras. |
| **Discusión** | Identidad vs. estrategia (LFI vs. LREM); clivaje **cultural > económico**; coherencia dicho-hecho débil pero localizada en banderas identitarias; el voto como dos capas (posicional + ideológica). |
| **Anexos** | Tablas por partido y canal, heatmaps, descomposición R², CSVs de soporte/cohesión/leverage, deep-dives por partido en `01_`, casos canónicos en `03_`. |

---

## Resultados, decisiones o detalles relevantes (con cifras exactas)

### Cobertura de datos
- **Manifiestos:** 3.801 quasi-frases, 10 partidos (EELV, FN, LFI, LR, LREM, MoDem, PCF, PRG, PS, UDI) — FN ya estaba como partido electoral; no hay `NI` en manifiestos.
- **Tweets:** 224.056 quasi-frases, **11 familias** (FN 3.491 docs separado de NI 2.822).
- **Hemiciclo:** 338.192 quasi-frases, **11 familias** (FN 5.808 docs separado de NI 1.542).
- **Leyes:** 335 scrutins con texto y votos (**2.129** unidades partido×scrutin). **Enmiendas:** 2.575 scrutins (**13.116** unidades). Join 100% entre votos↔diputado y scrutin↔texto. FN entra con n=95 scrutins (leyes) y n=319 (enmiendas) tras `MIN_EXPRESSED=3`.

### Hallazgo transversal — el canal define la agenda
Dominio dominante: manifiestos → **Welfare & QoL** (programa social/económico); tweets y hemiciclo → **Political System** (meta-política: gobierno, autoridad, instituciones). Pero la **firma distintiva persiste** entre canales (issue ownership).

### Análisis 1 — firmas y shift (`agenda_shift.csv`, `signature_persistence.csv`, `summary.json`)
**Firma más distintiva por partido (manifiestos, pp sobre el corpus):** PCF 305 Autoridad +17.1 (*ruido de muestra, 39 frases*), EELV 501 Medio Ambiente +8.0, PS 504 Bienestar +7.5, FN 601 Modo de Vida Nacional +5.5, MoDem 506 Educación +5.4, LREM 303 Eficiencia Gubernamental +5.1, PRG 108 UE +5.0, LFI 107 Internacionalismo +5.0, LR/UDI 305 +2.6 (**LR y UDI idénticos** en este corpus).

**Firma en tweets:** LFI 305 +9.9, **FN 305 +9.5**, EDS 501 +9.2, NI (residual) 605 Ley y Orden +4.3, GDR-PCF 504 +3.7, UDI-Agir 104 Militar +3.1, MoDem 107 +2.7, LR 502 Cultura +2.3.
**Firma en hemiciclo:** LR 305 +7.8 (el mayor), **FN 605 Ley y Orden +7.8**, MoDem/PS 305 +5.7, NI (residual) 504 Bienestar +5.7, LT 501 +5.2, LFI 305 +3.3, GDR-PCF 701 Trabajadores +3.1, LREM 303 +3.1.

**Shift (efecto canal vs. estrategia):** el centrado reduce el shift ~13–16 pp para todos (el efecto canal es estructural). Específico (recalibrado con FN): **FN 17.5** (IC [15.9, 20.7] = el **mayor reorganizador estimable**, sin solapar con el resto) → **LFI 12.1** (sigue siendo reorganización importante, pero ya no el extremo) → **LREM 7.4** (IC [6.2, 10.6], identidad gerencial estable). MoDem 11.3, PS 10.8, LR 9.1 (intermedios, IC solapados, **no se rankean**). **PCF no estimable** (shift específico 19.7 pero IC [14.3, 27.9] por las 39 frases). FN bruto 31.0, efecto canal 13.5.

**Persistencia de firma (mean_corr, recalibrada):** LREM 0.412 > LFI 0.172 > PCF 0.156 > **FN 0.148** > PS 0.108 ≈ MoDem 0.108 > LR 0.107. Salvo LREM, todas quedan comprimidas en una banda baja (0.11–0.17): **el orden interno no es interpretable con confianza**. **Overlap** (categorías-firma en ≥2 canales): LREM 5, LR 5, LFI/PCF 4, **FN 3** (601, 605 en 3 canales; 608 en 2), PS/MoDem 3. La persistencia media de FN es baja porque **Twitter funciona como outlier** (lo arrastra a 305), pero su manifiesto y hemiciclo se parecen mucho (corr 0.68) y su núcleo 601/605 reaparece en los 3 canales — persistencia y overlap miden cosas distintas.

**Monotemático/diversificado (evenness):** manifiestos PCF más monotemático / LFI más diverso; tweets **FN** más monotemático (megáfono 305) / MoDem más diverso; hemiciclo **NI** (residual) más monotemático / UDI-Agir más diverso.

### Análisis 2 — el voto en dos capas (`variance_decomposition.csv`, `support_lois_vs_amend.csv`, `party_cohesion.csv`, `domain_leverage.csv`)

**El eje se invierte leyes↔enmiendas (% Pour):**

| Partido | Leyes | Enmiendas |
|---|---:|---:|
| LREM | 99.1 | 15.7 |
| MoDem | 98.7 | 22.4 |
| UDI-Agir | 86.3 | 51.9 |
| EDS | 77.2 | 36.3 |
| LT | 54.0 | 71.4 |
| NI (residual) | 52.6 | 83.0 |
| LR | 45.9 | 70.9 |
| PS | 36.7 | 82.7 |
| **FN** | **27.1** | **73.4** |
| GDR-PCF | 18.7 | 87.0 |
| LFI | 11.5 | 83.7 |

El gobierno aprueba leyes y bloquea enmiendas; la oposición al revés (las enmiendas son intentos de la oposición de modificar el texto del gobierno). **FN** entra como oposición (no está en `GOV={LREM, MoDem}`): apoyo bajo a leyes (27.1%, de los más bajos del arco) y alto a enmiendas (73.4%). El `NI` residual queda más arriba (52.6/83.0), confirmando que es un agregado mixto y no un bloque opositor homogéneo.

**Descomposición de R² ponderado** (incluir FN solo **recalibra**, no cambia la conclusión):

| Corpus | bloque | partido | +dominio | partido×dominio | Δ partido vs bloque | Δ dominio |
|---|---:|---:|---:|---:|---:|---:|
| **Leyes** | 0.467 | 0.573 | 0.577 | 0.593 | +0.106 | +0.020 |
| **Enmiendas** | 0.331 | 0.350 | 0.355 | 0.361 | +0.019 | +0.010 |

Lectura: en leyes el binario mayoría/oposición ya explica el 47%; el partido fino suma +10 pp (oposición no monolítica) y el tema casi nada. En enmiendas todo explica menos y el partido casi no agrega sobre el bloque (+2 pp): la lógica posicional se afloja. **El tema como dominio dominante no añade varianza** (≈+1 pp) → la versión cruda "enmiendas = más temáticas en varianza" **no se sostiene**.

**Clivaje cultural (soporte relativo, `enmiendas_relative_support_ci.csv`, bootstrap por scrutin):**
- *Fabric of Society* — la izquierda apoya **de menos**: PS −21.9 (IC [−29.7,−14.2], estab. signo 1.00), GDR-PCF −17.5 (1.00), LFI −15.9 (1.00), EDS −14.9 (0.995); la derecha/centro de más: UDI-Agir +7.7 (IC roza 0), MoDem +3.3. **FN no es distintivo** aquí (−1.0, estab. 0.54).
- *Freedom & Democracy* — espejo: la derecha apoya **de menos** (LR −19.1 estab. 1.00 y **FN −19.2 estab. 1.00**: el polo derecho lo forman LR y FN) y la izquierda de más (LFI +7.0 estab. 0.999, GDR-PCF +4.4, PS +4.2). **Antes este polo aparecía atribuido a `NI` (−19.9) porque incluía a FN; el `NI` residual cae a −3.6 (no robusto).**
- *Welfare & QoL* — único soporte relativo positivo robusto de FN: **+14.0** (IC [+8.4, +19.8], estab. 1.00, apoyo absoluto 87.4%).
- *Economy* polariza **menos** (signos mezclados: EDS +23.6, LT +9.7 arriba; LFI −6.4, LR −5.3 abajo). FN aparece −24.9 pero con **IC ancho [−54.4, +7.0] → no interpretable**.
- El clivaje **sobrevive al bootstrap** y se reparte en >50 leyes distintas (Fabric of Society en 53, Freedom & Democracy en 54; ninguna ley aporta >17%).

**Leverage por dominio (descarta artefactos):** en enmiendas Welfare & QoL 1.107 scrutins, Economy 423, Freedom & Democracy 266, Political System 264, Fabric of Society 253, Social Groups 246, **External Relations solo 16** → **se descarta de la interpretación** (en leyes solo 5; valores enormes de soporte relativo no interpretables, p.ej. EDS +41.5, LT +28.6, UDI-Agir +20.3). **FN no tiene cobertura estimable en External Relations** y tampoco se interpreta ahí.

**Cohesión (índice Rice) — valida el agrupamiento:**
- *Leyes:* LFI 0.998 (el más disciplinado), GDR-PCF 0.987, LREM 0.983, MoDem 0.975, PS 0.967, **FN 0.955**, LR 0.915, EDS 0.891, UDI-Agir 0.815, LT 0.742, **`NI` (residual) 0.495 (el menos cohesionado)**.
- *Enmiendas:* LFI 0.997, GDR-PCF 0.991, **FN 0.987**, PS 0.958, LREM 0.943, LR 0.916, MoDem 0.885, EDS 0.859, **NI (residual) 0.798**, LT 0.769, UDI-Agir 0.735.
**FN vota como bloque cohesionado pese a su tamaño** (11 diputados); separar FN deja al `NI` residual aún más heterogéneo (Rice 0.495 en leyes), lo que justifica empíricamente tratarlo como agregado, no partido. LT y UDI-Agir también son agregados.

### Análisis 3 — declarado vs. revelado (`coherence_by_party_channel.csv`, `quadrant_typology_manifesto.csv`, `pooled_coherence.csv`, `summary.json`)

**Coherencia por partido (manifiesto vs. enmiendas, 6 dominios) — débil e inestable:**

| Partido | Pearson | Spearman | Pearson re-centrado | IC95 (bootstrap dominios) |
|---|---:|---:|---:|---|
| LFI | 0.49 | 0.31 | 0.47 | [−0.65, 0.99] |
| LREM | 0.43 | 0.38 | −0.10 | [−0.46, 0.97] |
| LR | 0.39 | 0.26 | 0.42 | [−0.86, 1.00] |
| PS * | 0.31 | 0.09 | 0.07 | [−0.85, 0.92] |
| PCF * | 0.05 | −0.14 | 0.21 | [−0.97, 0.85] |
| MoDem | −0.01 | −0.14 | −0.17 | [−0.81, 0.99] |
| FN | −0.20 | −0.09 | −0.00 | [−0.90, 0.75] |

`*` manifiesto de muestra chica (PCF 39, PS 79; FN tiene 274, suficiente). Los IC cubren casi [−1,+1] para **todos** (incluida FN) → **no se puede rankear** ni leer el coeficiente como juicio normativo de "coherencia"; el aporte es **tipológico**, no correlacional.

**Pooled por canal (comparación justa a 7 partidos comparables, incluida FN, sin External Relations):** manifiesto 0.08, tweets 0.08, hemiciclo 0.16 → **parejos y débiles**. La aparente ventaja del hemiciclo (0.29 con 11 partidos) era artefacto de cobertura. **Ningún canal anticipa el voto mejor que otro.** Incluir FN recalibra los niveles hacia abajo (su firma identitaria declarada no se respalda en el voto) pero no cambia la conclusión.

**Tipología — casos sustantivos:**
- **Énfasis respaldado (banderas afirmativas):** LFI↔Libertades (s_decl +2.1, s_rev +6.9, apoyo 90.6%), PS↔Bienestar (+13.1 / +3.6), MoDem↔Economía (+1.9 / +5.5; apoyo absoluto 27.9% pero base ~22%), eco-izquierda (EDS, LT)↔Economía/Bienestar.
- **Coherencia negativa (el patrón más limpio):** la izquierda no se apropia discursivamente de *Fabric of Society* (énfasis positivo ausente en sus 9 combinaciones partido-canal; PCF y PS lo sub-enfatizan 3/3) y lo apoya relativo menos (PCF −17.5, LFI −15.9, PS −21.9) — aunque siga aprobando 60–69% en absoluto.
- **Énfasis no respaldado:** LR↔Fabric of Society (+2.4 / −4.7, issue ownership securitario más discursivo que votado). El caso extremo es **FN**: declara firma nacional-securitaria persistente (*Fabric of Society* +9.8, 3/3 canales) pero su voto en ese dominio **no es distintivo** (−1.0); revela *Welfare & QoL* (+14.0) que no enfatiza; y *Freedom & Democracy* queda baja-prioridad-y-menor-apoyo (s_decl −1.8, s_rev −19.2). Es **gap entre capas observables**, no incoherencia normativa.
- **Sustitución clave respecto de la corrida sin FN:** el caso "NI↔Libertades como confrontación (−19.8)" **era FN**; el `NI` residual no es polo del clivaje (−3.6, no robusto). `NI` deja de usarse como proxy de RN/FN.
- **Robustez:** con zona neutra ±1 pp **0% de celdas invierten cuadrante**; **24%** del manifiesto (**43%** de todos los canales) pasan a neutro.

---

## Archivos de salida (inventario completo, para citar en anexos)

**Por corpus declarado** (`manifestos/`, `tweets/`, `interventions/` → `results/`):
`party_domain_distribution.csv` · `party_category_distribution.csv` · `distinctive_categories.csv` · `agenda_concentration.csv` · `summary.json` · `heatmap_party_domain.png` · `heatmap_party_signature.png` · `run.log`.

**Por corpus revelado** (`lois/`, `amendements/` → `results/`):
`party_domain_support.csv` · `party_domain_support_relative.csv` · `party_cohesion.csv` · `supported_vs_opposed_agenda.csv` · `summary.json` · `heatmap_domain_support.png` · `scatter_support_cohesion.png` · `run.log`.

**`cross_channel/results/`:** `domain_by_party_channel.csv` · `agenda_shift.csv` · `signature_persistence.csv` · `signature_overlap.csv` · `top_distinctive_by_channel.csv` · `heatmap_party_channel_domain.png` · `shift_gross_vs_specific.png` · `run.log`.

**`agenda_revelada/results/`:** `variance_decomposition.csv` · `support_lois_vs_amend.csv` · `enmiendas_relative_support_ci.csv` · `domain_leverage.csv` · `domain_leverage_by_law.csv` · `r2_decomposition.png` · `scatter_lois_vs_amend.png` · `summary.json` · `run.log`.

**`declarado_vs_revelado/results/`:** `coherence_by_party_channel.csv` · `declared_revealed_aligned.csv` · `quadrant_typology_manifesto.csv` · `pooled_coherence.csv` · `cross_channel_sign_stability.csv` · `fig_quadrants_manifiesto.png` · `fig_coherence_ranking.png` · `fig_coherence_by_channel.png` · `summary.json` · `run.log`.

---

## Dudas o cosas a revisar

1. **Dependencia en cadena:** todo parte de `manifestoberta_analysis/*/results/predictions.csv` (gitignored). Reproducir exige regenerar predicciones → correr los 5 `run.py` → luego los 3 `build.py`. Verificar que los CSV estén actualizados antes de citar números.
2. **"Partido" no es homogéneo entre canales:** manifiesto = texto oficial del partido (organización); tweets/hemiciclo = texto de **diputados individuales**. Cada quasi-frase pesa igual → mide *volumen comunicativo*, no agenda promedio por diputado. Conviene explicitarlo en la memoria (está en `01_` §"Quién produce el texto").
3. **Concentración por pocas voces:** en el hemiciclo de partidos chicos, el diputado más activo aporta MoDem 30%, PS 23%, PCF 16%, LFI 15% → esas columnas se leen con cautela. Ponderar por diputado quedó como robustez pendiente.
4. **Desfase temporal/organizacional:** manifiesto = campaña 2017 (partido electoral); voto = legislatura 2017–2022 (grupo parlamentario). **7 partidos** (incluida FN) casan limpio en el Análisis 3.
5. **Muestras chicas en manifiestos:** PCF (39 frases) y PS (79) → firmas indicativas, no robustas (FN tiene 274, suficiente). **LR y UDI idénticos (verificado):** comparten el mismo documento MARPOR (txt byte-idénticos, 282 frases cada uno, métricas idénticas en `party_positions.csv`); es un hecho del dataset MARPOR (mismos IDs 31626/31430), no error del proyecto → cuentan como uno.
   - **FN como familia analítica (decisión metodológica):** se construye por **11 `deputy_id`** en `common/families.py` (electos 2017 + suplentes + Ménard); **no se convierte todo `NI`** (el resto queda residual, **no proxy de FN/RN**). Caveats: base parlamentaria pequeña; **Houplain y Évrard sin tweets**; **Évrard dejó el FN en nov-2017** (atribución posterior a FN por decisión analítica); `MIN_EXPRESSED=3` limita los scrutins de FN (n=95 leyes, n=319 enmiendas); su *Economy* revelado (−24.9) y *External Relations* no se interpretan (IC ancho / sin cobertura). Soporte relativo negativo (p.ej. FN −19.2 en Libertades, apoyo absoluto 54.2%) **no es rechazo absoluto**; las correlaciones de coherencia **no son ranking normativo**; **sin causalidad** discurso↔voto.
6. **`demandeur` de enmiendas no controlado:** el voto depende también de quién propone la enmienda; el dato es texto libre (nombres, muchos vacíos) → mejora pendiente de alto valor (señalada en `02_`). El clivaje igualmente sobrevive al bootstrap y se reparte en >50 leyes.
7. **R² in-sample:** el modelo partido×dominio es saturado (medias de celda) → su R² es cota superior; la comparación válida es **entre corpus**, no el nivel absoluto.
8. **Abstenciones:** la métrica es Pour/(Pour+Contre); una robustez incluyendo abstenciones queda pendiente.
9. **Definición de bloque:** UDI-Agir (aliado intermitente) cae en oposición → probablemente subestima el R² del bloque. Decisión deliberada, conviene mencionarla.
10. **Sin causalidad:** el módulo describe alineaciones agregadas; **no** prueba cumplimiento programático ni que el discurso cause el voto. La validez del clasificador temático se sostiene en `ches_analysis/`.

---

## Resumen corto

`party_analysis/` es el **corazón analítico de la tesis**: cruza las clasificaciones MARPOR de las cinco fuentes para caracterizar a cada partido por **lo que dice** (agenda declarada: énfasis, firma, concentración) y **lo que vota** (agenda revelada: soporte global/relativo, cohesión). El **FN/RN** se incorpora como familia analítica propia (override por `deputy_id` en `common/families.py`), separado del residuo `NI`. Tres motores reutilizables (`common/families.py`, `common/analysis.py`, `common/votes.py`) alimentan tres análisis encadenados, cada uno con su prosa de capítulo casi final:
1. **El canal cambia la agenda** (efecto estructural ~13–16 pp) pero la firma persiste; **FN es el mayor reorganizador estimable** (específico 17.5, Twitter como outlier que lo lleva a 305) aunque su núcleo 601/605 reaparece en los 3 canales; LREM la mantiene (persistencia 0.412).
2. **El voto tiene dos capas:** una posicional dominante (bloque explica R²=0.47 en leyes) y un **clivaje cultural** robusto que aflora en enmiendas (izquierda −16/−22 en Fabric of Society; derecha LR/FN −19 en Freedom & Democracy), más cultural que económico. FN suma apoyo a Welfare & QoL (+14.0) pero no es distintivo en Fabric of Society.
3. **La coherencia dicho-hecho es débil pero localizada:** banderas afirmativas (LFI↔libertades, PS↔bienestar), coherencia negativa cultural de la izquierda, y énfasis no respaldado (LR; **FN**, que declara identidad nacional-securitaria no respaldada por su voto distintivo). El aporte es **tipológico**, no correlacional; el coeficiente no rankea coherencia.
Toda interpretación posicional izquierda-derecha se delega a `ches_analysis/`.

---

## Citas

- **Esquema MARPOR (7 dominios / 56 categorías):** Manifesto Project, heredado vía `manifestoberta_analysis/`.
- **Índice de cohesión Rice:** Rice, S. A. (1928), *Quantitative Methods in Politics* — implementado en `common/votes.py`.
- **Entropía / evenness:** Shannon (1948), normalizada por `log₂k` — `common/analysis.py` (`concentration`).
- **Entradas del pipeline:** `manifestoberta_analysis/{manifestos,tweets,interventions,lois,amendements}/results/predictions.csv`; `lois_votes/votes_rd/processed/votos_por_diputado.csv` y `votos_amendements_por_diputado.csv`; `datos_diputados/data/deputes_an_rd.csv`.
- **Documentación interna (prosa de capítulo):** `cross_channel/01_canal_cambia_agenda.md`, `agenda_revelada/02_voto_dos_capas.md`, `declarado_vs_revelado/03_declarado_vs_revelado.md`, `README.md`.
- **Código:** `common/analysis.py`, `common/votes.py`, los 5 `run.py`, `cross_channel/build.py`, `agenda_revelada/build.py`, `declarado_vs_revelado/build.py`.
- **Módulos relacionados:** `manifestoberta_analysis/` (clasificador supervisado), `ches_analysis/` (validación posicional externa), `lois_votes/`, `datos_diputados/`.

---

## Mapa a la memoria

**Carpeta/módulo que resume:** `french_deputies/party_analysis/` — **★ corazón analítico de la tesis.** Cruza las clasificaciones MARPOR de las 5 fuentes en **tres análisis encadenados**: agenda **declarada** (Análisis 1), agenda **revelada** por el voto (Análisis 2) y su **cruce** (Análisis 3). Los `.md` `01_`/`02_`/`03_` son **prosa de capítulo casi final**.

**A qué parte de la memoria alimenta:**

| Parte | Rol de este contexto |
|---|---|
| **Metodología** (principal) | Todas las métricas: énfasis, distintividad, *evenness*, Rice, soporte global/por tema/relativo, shift bruto/específico, persistencia, descomposición R², tipología por celda. |
| **Implementación** | `common/analysis.py` y `common/votes.py` como librerías; bootstrap multinomial y por clúster; WLS con dummies. |
| **Resultados** (cuerpo central) | Los **tres análisis** son el grueso de los resultados; reutilizar la prosa de `01_`/`02_`/`03_`. |
| **Discusión** (principal) | Identidad vs. estrategia; clivaje **cultural > económico**; coherencia dicho-hecho débil pero localizada. |
| **Anexos** | Tablas por partido/canal, heatmaps, descomposición R², CSVs de soporte/cohesión/leverage, casos canónicos. |

**Información concreta a extraer:**
- **Cobertura:** manifiestos 3.801/10 partidos; tweets 224.056/**11** familias (FN 3.491 vs NI 2.822); hemiciclo 338.192/**11** (FN 5.808 vs NI 1.542); leyes **335** scrutins (**2.129** unidades partido×scrutin); enmiendas **2.575** (**13.116** unidades). FN: n=95 leyes, n=319 enmiendas. Join 100 % votos↔diputado y scrutin↔texto.
- **Análisis 1:** el canal cambia la agenda (efecto estructural ~13–16 pp) pero la **firma persiste**; **FN es el mayor reorganizador estimable** (específico 17.5; Twitter outlier→305, pero núcleo 601/605 en los 3 canales) vs. LREM estable (persistencia 0,412).
- **Análisis 2:** el voto se **invierte** leyes↔enmiendas (LREM 99,1→15,7; LFI 11,5→83,7; FN 27,1→73,4); el bloque explica R²=0,47 en leyes; **clivaje cultural robusto** en enmiendas (izquierda −16/−22 en *Fabric of Society*; derecha **LR/FN −19** en *Freedom & Democracy*), más cultural que económico; FN suma Welfare & QoL +14,0; cohesión Rice valida el agrupamiento (FN 0,955 leyes; `NI` residual 0,495).
- **Análisis 3:** coherencia por partido **débil e inestable** (pooled **0,08–0,16**, no rankeable; FN −0,20 con IC [−0,90, 0,75]); el aporte es **tipológico** (banderas afirmativas, coherencia negativa cultural de la izquierda, énfasis no respaldado de LR y FN). Toda interpretación izquierda-derecha se delega a `ches_analysis/`.

**Figuras, tablas o métricas que contiene/menciona:**
- **Tablas:** inversión %Pour leyes↔enmiendas por partido; descomposición R² (bloque/partido/+dominio/×dominio); coherencia por partido con IC; cohesión Rice; firmas distintivas por canal; leverage por dominio.
- **Figuras:** `heatmap_party_domain.png`, `heatmap_party_signature.png`, `heatmap_domain_support.png`, `scatter_support_cohesion.png`, `shift_gross_vs_specific.png`, `r2_decomposition.png`, `fig_quadrants_manifiesto.png`. Inventario completo de salidas listado en este contexto (sección "Archivos de salida").

**Limitaciones / dudas a trasladar:**
- **"Partido" no es homogéneo entre canales** (manifiesto=organización; tweets/hemiciclo=diputados; voto=grupo) → **7 partidos** (incluida FN) casan en el Análisis 3; cada quasi-frase pesa igual (mide volumen, no promedio por diputado).
- **FN como familia analítica especial:** override por **11 `deputy_id`** (`common/families.py`), **no se convierte todo `NI`**; `NI` queda **residual** (no proxy de FN/RN). Base parlamentaria pequeña; **Houplain y Évrard sin tweets**; **Évrard dejó el FN en nov-2017** (atribución posterior con cautela); `MIN_EXPRESSED=3` limita los scrutins de FN; *Economy*/*External Relations* de FN no interpretables; soporte relativo negativo **no es rechazo absoluto**; correlaciones **no son ranking**; **sin causalidad**.
- Concentración por pocas voces en partidos chicos; muestras chicas (PCF 39, PS 79); LR=UDI; `demandeur` no controlado.
- R² del modelo saturado es cota superior (comparar **entre corpus**, no nivel absoluto); abstenciones excluidas; definición de bloque (UDI-Agir en oposición; FN en oposición); **sin causalidad**.
- Depende en cadena de `predictions.csv` (gitignored): regenerar predicciones antes de citar números.




