# Análisis 1 — El canal cambia la agenda

> **¿Un partido habla igual en su manifiesto, en Twitter y en el hemiciclo?**

Este es el primero de los tres ejes de la tesis. La idea: un partido no tiene *una* agenda, sino que la **mezcla temática de lo que dice depende del canal donde lo observes**. Acá lo medimos partido por partido, a fondo.

## Qué se compara y cómo

Los tres canales de **agenda declarada** (texto que el partido *produce*), clasificados por manifestoberta sobre las 56 categorías / 7 dominios MARPOR:

| Canal | Qué es | Volumen |
|---|---|---|
| **manifiesto** | programa electoral 2017 | ~3.800 quasi-frases |
| **tweets** | comunicación de los diputados en Twitter | ~224.000 |
| **hemiciclo** | intervenciones en el Parlamento | ~338.000 |

Se comparan los **6 partidos presentes en los tres canales**: LFI, PCF, PS, MoDem, LREM, LR (PCF = grupo GDR-PCF en tweets/hemiciclo). EELV, RN y otros solo aparecen en manifiestos o no son aislables como grupo, así que quedan fuera de esta comparación.

> **Quién produce el texto (precisión importante).** Los tres canales no son el mismo tipo de actor: el **manifiesto** lo produce el partido como organización (texto oficial), mientras que **tweets** y **hemiciclo** los producen sus **diputados** individuales. Es decir, la agenda declarada mezcla texto oficial del partido con texto de sus representantes parlamentarios. No es un problema —ambos son "lo que el partido comunica"— pero conviene tenerlo explícito.

Para cada partido medimos cuatro cosas:
- **(a) Distribución por dominio** en cada canal, y **categorías más distintivas** (su firma centrada por el promedio del canal).
- **(b) Shift bruto:** distancia euclídea media (en pp) de su perfil de dominios entre los tres canales. Mide el cambio *total*, pero **confunde la estrategia del partido con el efecto estructural del canal** (todos los partidos son arrastrados hacia *Political System* en tweets/hemiciclo).
- **(c) Shift específico del partido:** lo mismo pero sobre la **firma centrada** (desviación respecto del promedio del canal). Descuenta ese efecto estructural → aísla cuánto cambia la *identidad relativa* del partido.
- **(d) Persistencia de firma:** correlación de los vectores-firma (categorías centradas) entre pares de canales. Alta = el partido sobre-enfatiza temas parecidos donde sea.

> **Nota de método.** (i) *Una sola métrica:* usamos **distancia euclídea en puntos porcentuales** en todo el análisis (no Jensen-Shannon), porque es directamente interpretable —"cambió 14 pp"— en vez de un índice abstracto entre 0 y 1. (ii) *Baseline:* el "promedio del canal" para centrar la firma se calcula **solo con los 6 partidos comparables** (LFI, PCF, PS, MoDem, LREM, LR), no con todos los partidos del corpus, para que los tres canales tengan una referencia homogénea. (iii) *Bootstrap:* los índices de shift llevan **IC95 por bootstrap** (2.000 remuestreos multinomiales de las quasi-frases), clave porque los manifiestos de PCF (39 frases) y PS (79) son chicos.

## El patrón general

![Énfasis por dominio, partido × canal](results/heatmap_party_channel_domain.png)

Salta a la vista en la figura, y es el hallazgo de fondo:

- **El manifiesto es programático:** domina **Welfare & QoL** (políticas sociales) y **Economy**. Es donde el partido despliega su oferta sustantiva.
- **Twitter y el hemiciclo son meta-política:** domina **Political System** (gobierno, autoridad, instituciones, corrupción). En Twitter de forma extrema; en el hemiciclo, casi igual.

Dicho fuerte: **no existe "la agenda" de un partido en abstracto; la agenda depende mucho del canal.** Un mismo partido, observado en su programa o en su Twitter, parece hablar de mundos distintos.

### Cuánto cambia cada partido: bruto vs. específico

La clave: separar el cambio que es **estructural del canal** (común a todos) del que es **estrategia propia del partido**.

| Partido | shift bruto (pp) | shift específico (pp) | reducción por centrado | IC95 específico |
|---|---:|---:|---:|---|
| **LFI** | 27.5 | **14.4** | 13.0 | [13.0, 16.7] |
| MoDem | 27.1 | 10.5 | 16.6 | [8.9, 13.6] |
| PS | 27.2 | 10.0 | 17.2 | [6.7, 17.2] |
| LR | 22.9 | 7.0 | 15.9 | [5.7, 10.6] |
| **LREM** | 19.4 | **5.7** | 13.6 | [4.5, 9.2] |
| PCF* | 17.1 | 19.6* | −2.5 | [14.1, 27.8] |

![Shift bruto vs específico](results/shift_gross_vs_specific.png)

> La columna **"reducción por centrado"** es `bruto − específico`: cuánto baja el shift al quitar el promedio del canal. Es una **aproximación descriptiva del efecto canal**, no una descomposición aditiva exacta (son distancias, no componentes que se sumen limpiamente) — de hecho en PCF da negativa, justamente porque su manifiesto ruidoso aleja su firma centrada más que su perfil bruto. Léase como indicación, no como contabilidad.

Lo que dice:

- **El grueso del cambio es estructural del canal, no estrategia.** El centrado reduce el shift en **13–17 pp** para todos: el desplazamiento hacia *Political System* en tweets/hemiciclo le pasa a todos los partidos. El shift bruto **sobreestima** cuánto "cambia de agenda" cada uno.
- **Los extremos son lo robusto.** Descontado el canal, **LFI está claramente arriba** (14.4 pp, IC estrecho) y **LREM claramente abajo** (5.7 pp): oposición vs. partido presidencial, un contraste que sobrevive a los intervalos.
- **El medio es eso, medio.** PS, MoDem y LR (≈7–10 pp) son casos intermedios cuyos IC se solapan; **no conviene leer su orden exacto** como una jerarquía. Lo que sí se ve: MoDem tenía un shift bruto alto (27.1) que era casi todo canal (16.6), así que su cambio propio es moderado.
- **PCF* no se interpreta.** Su IC es enorme (`[14.1, 27.8]`) por las 39 frases del manifiesto: su shift **no es estimable con confianza**, así que queda fuera del ranking. El bootstrap deja eso a la vista.

### Persistencia de la firma (medida, no solo interpretada)

¿La firma de cada partido se conserva entre canales? Correlación de los vectores-firma (categorías centradas) entre canales — alta = sobre-enfatiza temas parecidos donde sea:

| Partido | corr. media entre canales | lectura |
|---|---:|---|
| **LREM** | **0.56** | firma muy persistente (gestión/tecnología/Europa en todos lados) |
| LR | 0.32 | persistente (nación, autoridad, ruralidad) |
| MoDem | 0.21 | media (Europa/democracia reaparecen) |
| PS | 0.18 | baja (bienestar en programa, fiscalización en hemiciclo) |
| PCF | 0.12 | manifiesto descorrelaciona; tweets↔hemiciclo sí alinean (0.65) |
| **LFI** | **0.02** | firma **casi no correlaciona** entre canales |

Complemento (overlap, Opción B): categorías-firma que reaparecen en ≥2 canales — LREM 6, LR 5, el resto 4. En LFI las que persisten son sus temas sociales (igualdad, educación, medio ambiente), pero su *Autoridad Política* (+10pp) es **exclusiva de Twitter**: por eso su correlación global se desploma aunque conserve un núcleo social.

**Lo importante:** *todos los partidos son arrastrados por el canal hacia la meta-política, pero algunos conservan mucho mejor su firma relativa que otros.* LREM mantiene una identidad temática estable; LFI la **reorganiza** por completo según el canal. Ese es el eje *identidad vs. estrategia* que el Análisis 3 lleva al voto.

---

# Deep dive por partido

Para cada partido: su perfil de dominios en los tres canales y las categorías que lo definen en cada uno. Orden ideológico, de izquierda a derecha.

## LFI — La France Insoumise (el caso extremo)

Shift específico **14.4 pp** (el más alto) y persistencia de firma **0.02** (la más baja): es el partido que más cambia su identidad relativa según dónde habla.

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| Welfare & QoL | 31 | 23 | 26 |
| Economy | 21 | 5 | 9 |
| External Relations | 13 | 7 | 3 |
| **Political System** | **6** | **41** | **32** |
| Freedom & Democracy | 9 | 9 | 13 |

**Categorías marca por canal:**
- **manifiesto:** 107 Internacionalismo (+5.0), 501 Medio Ambiente (+2.5), 403 Regulación de Mercado (+2.0), 416 Anti-crecimiento (+1.6).
- **tweets:** 305 Autoridad Política (**+10.2**), 503 Igualdad (+2.3), 506 Educación (+2.2), 304 Corrupción Política (+1.0).
- **hemiciclo:** 305 Autoridad Política (+3.3), 503 Igualdad (+1.8), 701 Trabajadores (+1.7), 201 Libertades y DDHH (+1.4).

**Lectura:** en su **programa**, LFI es una izquierda **internacionalista y ecosocialista** (Europa/exterior 13%, regulación, decrecimiento). En **Twitter** ese contenido casi desaparece: Political System salta de 6% a **41%** y su marca pasa a ser *Autoridad Política* + *Corrupción* — puro **megáfono anti-gobierno**. El **hemiciclo** es un punto intermedio: sigue confrontando al poder (305) pero recupera sustancia social (igualdad, trabajadores, derechos humanos). LFI ilustra el hallazgo como ningún otro: **su identidad programática y su identidad comunicativa son casi opuestas.**

## PCF — Partido Comunista / grupo GDR (no estimable con confianza)

**Caveat fuerte:** su manifiesto tiene solo **39 quasi-frases**. El bootstrap le da un IC enorme en el shift específico (`[14.1, 27.8]`), así que **no se puede afirmar que sea estable ni inestable**. Lo que sí es robusto: entre **tweets y hemiciclo** (los dos canales con datos suficientes) su firma correlaciona alto (0.65) — ahí su ADN obrero sí es consistente; el manifiesto es el que no es fiable.

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| Welfare & QoL | 13 | 27 | 27 |
| Political System | 23 | 32 | 31 |
| Social Groups | 21 | 8 | 9 |

**Categorías marca por canal:**
- **manifiesto:** 305 Autoridad (+17.1), 701 Trabajadores (+11.2), 202 Democracia (+4.8), 413 Nacionalizaciones (+4.3) — *muestra mínima, leer con cautela*.
- **tweets:** 504 Estado de Bienestar (+3.5), 701 Trabajadores (+2.1), 503 Igualdad (+1.3), 106 Paz (+0.6).
- **hemiciclo:** 701 Trabajadores (+2.9), 504 Estado de Bienestar (+2.6), 503 Igualdad (+1.8).

**Lectura:** dejando de lado el manifiesto (ruidoso, 39 frases), el PCF muestra un **ADN obrero consistente entre tweets y hemiciclo**: *Trabajadores* (701) e *Igualdad/Bienestar* reaparecen en ambos (correlación de firma 0.65). No afirmamos que sea "el más estable" del conjunto —su shift no es estimable por la muestra del manifiesto—, pero en los canales con datos suficientes su identidad temática se sostiene.

## PS — Partido Socialista

Shift específico 10.0 pp (IC ancho `[6.7, 17.2]` por las 79 frases del manifiesto); persistencia 0.18.

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| **Welfare & QoL** | **43** | 28 | 24 |
| Economy | 16 | 8 | 10 |
| Political System | 8 | 30 | 39 |

**Categorías marca por canal:**
- **manifiesto:** 504 Estado de Bienestar (**+7.5**), 605 Ley y Orden (+4.1), 701 Trabajadores (+2.1), 501 Medio Ambiente (+2.1).
- **tweets:** 504 Estado de Bienestar (+2.3), 502 Cultura (+1.2), 503 Igualdad (+0.7).
- **hemiciclo:** 305 Autoridad (+5.7), 303 Eficiencia Gubernamental (+0.7), 301 Federalismo (+0.4).

**Lectura:** el PS es **socialdemocracia de manual**: el bienestar es **43%** de su programa, el dominante más alto de todos los partidos en cualquier canal. Pero en el hemiciclo el bienestar cede ante *Political System* (39%) y su marca pasa a ser *Autoridad* (+5.7): el canal institucional lo arrastra al rol de oposición fiscalizadora. El bienestar es su identidad declarada; la fiscalización, su rol parlamentario.

## MoDem — Mouvement Démocrate (el europeísta)

Shift específico 10.5 pp (de un bruto de 27.1: **casi todo era efecto canal**); persistencia 0.21.

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| Welfare & QoL | 33 | 22 | 20 |
| Economy | 20 | 9 | 10 |
| **External Relations** | 10 | **17** | 3 |
| Political System | 10 | 28 | 40 |
| Freedom & Democracy | 10 | 8 | 14 |

**Categorías marca por canal:**
- **manifiesto:** 506 Educación (+5.4), 202 Democracia (+3.5), 606 Civismo (+2.0), 107 Internacionalismo (+1.7).
- **tweets:** 107 Internacionalismo (+2.5), 104 Militar+ (+2.0), 108 Unión Europea (+1.9), 106 Paz (+1.0).
- **hemiciclo:** 305 Autoridad (+5.7), 202 Democracia (+2.5), 303 Eficiencia Gubernamental (+1.8).

**Lectura:** MoDem usa **Twitter para marcar su nicho europeísta/internacionalista** — es el partido con más *External Relations* en tweets (17%), con Europa (108), internacionalismo y paz como marca. Es justo lo que lo diferencia de su socio de gobierno LREM. En el **hemiciclo**, en cambio, se confunde con el bloque gubernamental (Political System 40%, eficiencia, autoridad). Europa es su seña de comunicación; la gestión, su rol institucional.

## LREM — La République en Marche (el más coherente)

Shift específico **5.7 pp** (el más bajo) y persistencia de firma **0.56** (la más alta): el partido de gobierno, el de identidad temática más estable entre canales.

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| Welfare & QoL | 33 | 25 | 22 |
| Economy | 18 | 11 | 11 |
| Political System | 15 | 29 | 36 |

**Categorías marca por canal:**
- **manifiesto:** 303 Eficiencia Gubernamental (+5.1), 503 Igualdad (+3.0), 304 Anti-corrupción (+1.6), 411 Tecnología/Infraestructura (+1.5).
- **tweets:** 411 Tecnología/Infraestructura (+1.4), 108 Unión Europea (+0.7), 402 Incentivos (+0.6).
- **hemiciclo:** 303 Eficiencia Gubernamental (+2.9), 305 Autoridad (+2.5), 604 Moral Tradicional− (+0.6).

**Lectura:** LREM es el partido **más estable entre canales**. Su marca —*Eficiencia Gubernamental* (303)— reaparece en programa y hemiciclo, acompañada de modernización (tecnología, incentivos) y anti-corrupción (el "vie publique" macronista de 2017). Tiene poca identidad temática "ideológica" y mucha **lógica gerencial del Ejecutivo**: como ya gobierna, su mensaje no cambia tanto según el canal. (Esto se conecta con el Análisis 3: LREM aparece coherente con la agenda del gobierno.)

## LR — Les Républicains

Shift específico 7.0 pp; persistencia 0.32 (segunda más alta).

| Dominio (%) | manifiesto | tweets | hemiciclo |
|---|---:|---:|---:|
| Welfare & QoL | 28 | 24 | 19 |
| **Fabric of Society** | **17** | 15 | 10 |
| **Social Groups** | **16** | 7 | 6 |
| **Political System** | 14 | 33 | **41** |

**Categorías marca por canal:**
- **manifiesto:** 305 Autoridad (+2.6), 706 Grupos Demográficos (+2.5), 601 Modo de Vida Nacional (+2.4), 701 Trabajadores (+1.8).
- **tweets:** 502 Cultura (+2.2), 601 Modo de Vida Nacional (+1.4), 411 Tecnología (+1.3), 703 Agricultura (+1.1).
- **hemiciclo:** 305 Autoridad (**+7.8**), 303 Eficiencia Gubernamental (+1.3), 202 Democracia (+0.9), 604 Moral Tradicional− (+0.7).

**Lectura:** LR muestra su **identidad cultural/nacional** en programa y Twitter: *Modo de Vida Nacional* (601) aparece en ambos, junto a cultura y ruralidad/agricultura. Pero en el **hemiciclo** su agenda cultural se diluye y su marca pasa a ser *Autoridad Política* (**+7.8, el mayor de todos**): es la oposición de derecha en su rol más puro de fiscalización del Ejecutivo. Su agenda identitaria es más de comunicación; en el Parlamento prima el rol opositor.

---

# Síntesis del Análisis 1

1. **El canal define la mezcla temática, y ese efecto es estructural.** Manifiesto = agenda *programática* (bienestar, economía); Twitter y hemiciclo = agenda *meta-política* (gobierno, autoridad). El efecto canal pesa **13–17 pp** para todos los partidos: no es estrategia, es el género del texto.
2. **Descontado el canal, los extremos son lo robusto: LFI reorganiza más su firma; LREM, partido presidencial, la mantiene.** El shift *específico* va de LFI (14.4 pp, persistencia 0.02) a LREM (5.7 pp, persistencia 0.56), y ese contraste sobrevive a los intervalos. PS, MoDem y LR quedan en el medio con IC solapados —**no se fuerza un orden exacto entre ellos**— y PCF no se interpreta por su manifiesto chico. No es "gobierno vs oposición" en bloque: MoDem, también del gobierno, marca perfil propio (europeísta). La lectura precisa: *los partidos de oposición, en especial LFI, usan Twitter y el hemiciclo para activar una agenda de fiscalización del poder.*
3. **Cada partido conserva un núcleo de firma que reaparece entre canales — su identidad:** PCF→trabajadores (en tweets/hemiciclo), PS→bienestar, MoDem→Europa, LREM→gestión, LR→nación, LFI→temas sociales. Medido por overlap de categorías-firma (LREM 6, LR 5, resto 4).
4. **Y hay temas que solo activa en un canal — su estrategia comunicativa:** el caso nítido es LFI, cuyo +10pp de *Autoridad Política* es exclusivo de Twitter; por eso su firma global casi no correlaciona entre canales (0.02) aunque conserve un núcleo social.

> **Frase fuerte:** *No existe "la agenda" de un partido: hay una agenda programática en el manifiesto, una comunicativa en Twitter y una institucional en el hemiciclo. Buena parte del cambio entre ellas es efecto del canal (común a todos); el residuo específico de cada partido, ya medido y con intervalos, separa lo que es **identidad ideológica** (persiste: LREM) de lo que es **estrategia de comunicación** (se reorganiza: LFI).* Esa distinción es lo que el Análisis 3 llevará al terreno del voto.

## Caveats

- **n=6 partidos** (los presentes en los tres canales). EELV, RN/FN y otros quedan fuera: solo están en manifiestos o no son aislables como grupo parlamentario.
- **Muestras chicas en manifiestos (PCF 39, PS 79):** sus índices de shift llevan **IC bootstrap** anchos. En particular **PCF no es estimable con confianza** (IC `[14.1, 27.8]`), así que se evita afirmar que sea el más o el menos estable. El patrón general (efecto canal grande; LFI alto / LREM bajo en shift específico) se sostiene incluso tomando con cautela esos manifiestos.
- **"Partido" no es lo mismo en cada canal:** el manifiesto es texto oficial del partido; tweets y hemiciclo son texto de sus diputados, y cada quasi-frase pesa igual (mide *volumen comunicativo*, no la *agenda promedio de un diputado*). Verificamos que **ningún partido depende de 1–2 voces**: el mínimo son 14 diputados (PCF en tweets) y el número efectivo (1/HHI) es ~9–13 para los chicos y mucho mayor para LREM/LR. La concentración aparece sobre todo en el **hemiciclo de los partidos chicos**, donde el diputado más activo aporta MoDem 30%, PS 23%, PCF 16%, LFI 15% — por eso esas columnas de hemiciclo deben leerse con algo más de cautela. Ponderar por diputado queda como robustez pendiente (no se hizo por extensión).
- El énfasis mide *salience* (cuánto se habla de algo), no postura. La validación de que el clasificador mide bien está en `ches_analysis/`.

## Reproducir

```bash
cd french_deputies/party_analysis
python3 -u cross_channel/build.py 2>&1 | tee cross_channel/results/run.log
```

Insumos: las predicciones MARPOR de `manifestoberta_analysis/{manifestos,tweets,interventions}/`. Salidas en `cross_channel/results/`:
- `domain_by_party_channel.csv` — % por dominio, (partido × canal).
- `agenda_shift.csv` — shift bruto, específico, reducción por centrado e IC bootstrap por partido.
- `signature_persistence.csv` — correlación de firma entre canales (Opción A).
- `signature_overlap.csv` — categorías-firma repetidas entre canales (Opción B).
- `top_distinctive_by_channel.csv` — top categorías-firma por (partido, canal).
- `heatmap_party_channel_domain.png` y `shift_gross_vs_specific.png`.
