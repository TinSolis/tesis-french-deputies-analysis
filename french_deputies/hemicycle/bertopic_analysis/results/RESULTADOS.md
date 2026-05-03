# Resultados — BERTopic sobre intervenciones en hemiciclo (dataset completo)

Análisis de topic modeling sobre **138,551 intervenciones sustantivas** de la XV legislatura (2017–2022), filtradas a diputados enlazados con `deputes_2017_2022.csv` y con ≥80 palabras.

Modelo: BERTopic con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, representación refinada con KeyBERTInspired, y stopwords en francés + jerga parlamentaria.

---

## Resumen general

- **Dataset original:** 949,718 intervenciones totales
- **Con `deputy_id` enlazado:** 661,690
- **Tras filtro sustantivo** (≥80 palabras, sin procedimentales): **138,551**
- **Outliers** (sin tema claro): 62,826 (45%)
- **Temas detectados: 80**

---

## Los 30 temas principales

| Topic | Docs | Palabras clave (francés) | Traducción al español |
|------:|-----:|--------------------------|----------------------|
| 0 | 40,704 | réforme, parlement, politique, proposition, république | reforma, parlamento, política, propuesta, república |
| 1 | 3,287 | changement climatique, transition écologique, réchauffement climatique | cambio climático, transición ecológica, calentamiento global |
| 2 | 3,278 | salariés, salarié, employeurs, travailleurs, travail, fonction publique | asalariados, empleadores, trabajadores, trabajo, función pública |
| 3 | 2,383 | logement social, logements, taxe habitation, immobilier | vivienda social, viviendas, impuesto de habitación, inmobiliario |
| 4 | 2,299 | secteur agricole, exploitations agricoles, agriculteurs, agriculture | sector agrícola, explotaciones agrícolas, agricultores, agricultura |
| 5 | 2,134 | immigration, migrants, migratoire, union européenne | inmigración, migrantes, migratorio, unión europea |
| 6 | 1,551 | vaccination, crise sanitaire, épidémie, passe sanitaire | vacunación, crisis sanitaria, epidemia, pase sanitario |
| 7 | 1,328 | transports commun, mobilité, transports, déplacements | transporte público, movilidad, transportes, desplazamientos |
| 8 | 1,293 | sport, sports, sportifs, sportive | deporte, deportes, deportistas, deportiva |
| 9 | 933 | contre terrorisme, terrorisme, terroriste, menace, attentats | contra el terrorismo, terrorismo, terrorista, amenaza, atentados |
| 10 | 849 | eaux, eau, élus locaux, service public | aguas, agua, electos locales, servicio público |
| 11 | 725 | police judiciaire, policiers, police gendarmerie | policía judicial, policías, policía y gendarmería |
| 12 | 704 | personnes handicapées, handicap, situation handicap | personas discapacitadas, discapacidad, situación de discapacidad |
| 13 | 689 | militaires, armées, militaire, armée, soldats | militares, fuerzas armadas, ejército, soldados |
| 14 | 656 | enceintes, grossesse, femmes, professionnels santé | embarazadas, embarazo, mujeres, profesionales de salud |
| 15 | 594 | aéroports, privatisation, aéroport, avions, aérien | aeropuertos, privatización, aeropuerto, aviones, aéreo |
| 16 | 550 | animale, animal, animaux, élevage, éleveurs, espèces | animal, animales, ganadería, ganaderos, especies |
| 17 | 497 | musique, audiovisuel, culturelle, médias, culture | música, audiovisual, cultural, medios, cultura |
| 18 | 495 | plastique, gaspillage, pollution, déchets, écologique | plástico, desperdicio, contaminación, residuos, ecológico |
| 19 | 462 | paris, monuments, édifice, bâtiment, historiques | París, monumentos, edificio, edificio, históricos |
| 20 | 461 | langues, français, langue, cultures, étrangères | lenguas, francés, lengua, culturas, extranjeras |
| 21 | 441 | chercheurs, scientifiques, cellules, science | investigadores, científicos, células, ciencia |
| 22 | 432 | tourisme, touristiques, touristes, vacances | turismo, turísticos, turistas, vacaciones |
| 23 | 429 | liberté expression, censure, réseaux sociaux, lutter contre | libertad de expresión, censura, redes sociales, luchar contra |
| 24 | 360 | sapeurs pompiers, pompiers, volontariat, volontaires | bomberos, voluntariado, voluntarios |
| 25 | 348 | médiatique, médias, journalistes, journaux | mediático, medios, periodistas, periódicos |
| 26 | 343 | 000 jeunes, jeunes moins, pauvreté, jeunesse, génération | miles de jóvenes, jóvenes menores, pobreza, juventud, generación |
| 27 | 303 | france, affaires étrangères, françaises, armées, alliés | Francia, asuntos exteriores, francesas, fuerzas armadas, aliados |
| 28 | 299 | médicaments, prescription, médicament, santé publique | medicamentos, prescripción, medicamento, salud pública |
| 29 | 296 | débats, parlementaire, législateur, éthiques | debates, parlamentario, legislador, éticos |

---

## Temas adicionales (30–79) — agrupados por eje temático

### Medio ambiente y energía
| Topic | Docs | Tema |
|------:|-----:|------|
| 30 | 285 | pesticides *(pesticidas)* — prohibición de pesticidas |
| 31 | 282 | nucléaire, centrales, transition énergétique *(nuclear, centrales, transición energética)* |
| 32 | 268 | forêts, changement climatique *(bosques, cambio climático)* |
| 18 | 495 | plastique, pollution, déchets *(plástico, contaminación, residuos)* |

### Educación y juventud
| Topic | Docs | Tema |
|------:|-----:|------|
| 33 | 233 | harcèlement, établissements scolaires, enseignants *(acoso, centros escolares, profesores)* |
| 47 | 142 | téléphone, scolaires, pédagogique *(teléfono, escolares, pedagógico)* — dispositivos en escuelas |
| 48 | 141 | universités, enseignement supérieur *(universidades, educación superior)* |
| 26 | 343 | jeunes, pauvreté, jeunesse *(jóvenes, pobreza, juventud)* |

### Salud
| Topic | Docs | Tema |
|------:|-----:|------|
| 34 | 221 | épidémie, pandémie, virus, coronavirus *(epidemia, pandemia, virus, coronavirus)* |
| 52 | 131 | masques, crise sanitaire *(mascarillas, crisis sanitaria)* |
| 53 | 124 | santé mentale, psychologiques *(salud mental, psicológicos)* |
| 56 | 117 | cancer, cancers, mortalité *(cáncer, mortalidad)* |
| 57 | 115 | personnes âgées, vieillissement *(personas mayores, envejecimiento)* |
| 77 | 52 | maladies, maladie, traitement *(enfermedades, enfermedad, tratamiento)* |

### Fiscalidad y economía
| Topic | Docs | Tema |
|------:|-----:|------|
| 38 | 203 | directive européenne, impôt, fiscalité *(directiva europea, impuesto, fiscalidad)* |
| 40 | 184 | alcool, taxation, fiscalité *(alcohol, tributación, fiscalidad)* |
| 51 | 138 | tabac, fiscalité, taxe *(tabaco, fiscalidad, impuesto)* |
| 59 | 100 | fiscalité, fiscale, contribuables *(fiscalidad, fiscal, contribuyentes)* |
| 72 | 71 | banques, bancaires, financière *(bancos, bancarios, financiera)* |

### Seguridad y geopolítica
| Topic | Docs | Tema |
|------:|-----:|------|
| 35 | 218 | idéologie, terrorisme, lutte contre *(ideología, terrorismo, lucha contra)* |
| 44 | 149 | israël, paix, conflit *(Israel, paz, conflicto)* |
| 64 | 93 | gendarmerie, terrorisme, forces ordre *(gendarmería, terrorismo, fuerzas del orden)* |
| 65 | 88 | russie, russes, europe *(Rusia, rusos, Europa)* |
| 74 | 65 | turquie, affaires étrangères, russie *(Turquía, asuntos exteriores, Rusia)* |

### Sociedad y derechos
| Topic | Docs | Tema |
|------:|-----:|------|
| 36 | 210 | religion, religieuses, conscience, constitution *(religión, religiosas, conciencia, constitución)* |
| 41 | 164 | mourir, décès, suicide, mort *(morir, deceso, suicidio, muerte)* — fin de vida |
| 43 | 158 | donneurs, consentement, droits *(donantes, consentimiento, derechos)* |
| 46 | 143 | libertés fondamentales, libertés publiques, droits libertés *(libertades fundamentales, libertades públicas, derechos y libertades)* |
| 54 | 123 | mariage, consentement, code civil *(matrimonio, consentimiento, código civil)* |
| 78 | 51 | contre discriminations, discriminations *(contra las discriminaciones)* |
| 79 | 50 | principes républicains, républicaine *(principios republicanos, republicana)* |

### Comercio y UE
| Topic | Docs | Tema |
|------:|-----:|------|
| 37 | 208 | libre échange, mondialisation, multinationales *(libre comercio, globalización, multinacionales)* |
| 60 | 98 | parlement européen, brexit, union européenne *(parlamento europeo, Brexit, unión europea)* |
| 67 | 85 | union européenne, canada, éleveurs *(UE, Canadá, ganaderos)* — CETA |
| 75 | 61 | publicités, marketing, consommateurs *(publicidad, marketing, consumidores)* |

---

## Principales insights

1. **El debate general domina** (Topic 0, 40,704 docs = 29%): réforme, parlement, politique *(reforma, parlamento, política)*. Es el "cajón de sastre" parlamentario.

2. **Cambio climático es el tema específico más grande** (Topic 1, 3,287 docs): changement climatique, transition écologique *(cambio climático, transición ecológica)*. Sumado a los topics 18 (plástico/contaminación), 30 (pesticidas), 31 (nuclear) y 32 (bosques), **medio ambiente totaliza ~4,800+ intervenciones** — el eje temático más importante tras el debate general.

3. **Trabajo y empleo** (Topic 2, 3,278 docs): salariés, employeurs, travailleurs *(asalariados, empleadores, trabajadores)* — confirma lo que vimos en la muestra, pero ahora como el 3er tema más grande.

4. **Vivienda** emerge como tema autónomo (Topic 3, 2,383 docs): logement social, taxe habitation *(vivienda social, impuesto de habitación)* — invisible en la muestra de 5k.

5. **Agricultura** (Topic 4, 2,299 docs) y la crisis sanitaria/COVID (Topics 6, 34, 52 = ~1,900 docs) son ejes mayores que no aparecían antes.

6. **Inmigración** (Topic 5, 2,134 docs): immigration, migrants, migratoire *(inmigración, migrantes, migratorio)* — tema polémico con peso propio.

7. **El hemiciclo refleja la vida real**: COVID (Topics 6, 34, 52), bienestar animal (T16), fin de vida (T41), teléfonos en escuelas (T47), redes sociales (T23), Brexit (T60), CETA con Canadá (T67), Rusia (T65), Turquía (T74).

8. **Temas invisibles en Twitter y manifiestos** que sí aparecen en hemiciclo: bomberos (T24), deporte (T8), turismo (T22), personas mayores (T57), salud mental (T53), bancos (T72).

---

## Top 30 palabras más frecuentes (sin stopwords)

| # | Palabra | Traducción | Frecuencia |
|--:|---------|------------|----------:|
| 1 | état | estado | 56,813 |
| 2 | avons | tenemos/hemos | 46,616 |
| 3 | france | Francia | 41,300 |
| 4 | euros | euros | 37,454 |
| 5 | faut | hay que | 36,578 |
| 6 | deux | dos | 34,370 |
| 7 | travail | trabajo | 30,116 |
| 8 | contre | contra | 28,899 |
| 9 | pays | país | 28,805 |
| 10 | notamment | especialmente | 28,659 |
| 11 | droit | derecho | 28,649 |
| 12 | ans | años | 27,933 |
| 13 | aujourd'hui | hoy | 27,901 |
| 14 | doit | debe | 27,483 |
| 15 | français | franceses | 27,180 |
| 16 | entreprises | empresas | 25,377 |
| 17 | personnes | personas | 24,158 |
| 18 | santé | salud | 24,057 |
| 19 | enfants | niños | 22,624 |
| 20 | conditions | condiciones | 22,120 |

---

## Distribución por grupo parlamentario

### Temas dominantes por grupo

| Grupo | Abreviatura | Docs total | Top temas |
|-------|-------------|----------:|-----------|
| La République en Marche | LAREM | 36,212 | T0 (reforma), T1 (clima), T2 (empleo), T4 (agricultura), T3 (vivienda) |
| Les Républicains | LR | 29,427 | T0 (reforma), T1 (clima), T4 (agricultura), T3 (vivienda), T5 (inmigración) |
| France Insoumise | FI | 17,028 | T0 (reforma), T2 (empleo), T1 (clima), T5 (inmigración), T6 (COVID) |
| Gauche démocrate et républicaine | GDR | 10,977 | T0 (reforma), T2 (empleo), T3 (vivienda), T1 (clima), T7 (transporte) |
| Socialistes | SOC | 7,078 | T0, T1 (clima), T4 (agricultura), T8 (deporte), T3 (vivienda) |
| Mouvement Démocrate | MODEM | 6,182 | T0, T1 (clima), T4 (agricultura), T3 (vivienda), T5 (inmigración) |
| Nouvelle Gauche | NG | 6,068 | T0, T3 (vivienda), T2 (empleo), T1 (clima), T5 (inmigración) |
| Non-inscrits | NI | 4,535 | T0, T5 (**inmigración destacado**), T6 (COVID), T14 (embarazo/mujeres), T11 (policía) |

**Observaciones por grupo:**
- **LAREM** (mayoría): perfil balanceado, todos los temas principales
- **LR** (derecha): agricultura e inmigración tienen más peso relativo que en LAREM
- **FI** (izquierda radical): empleo (T2) es su 2° tema, por encima de clima
- **GDR** (comunistas): empleo y vivienda por encima de clima — perfil social
- **NI** (no inscritos): inmigración es su 2° tema con 227 docs — perfil identitario
- **SOC** (socialistas): deporte (T8) aparece alto — posiblemente por proyectos de ley específicos

---

## Archivos de datos generados

| Archivo | Descripción |
|---------|-------------|
| `topic_info.csv` | Tabla completa de los 80 temas |
| `top_words_per_topic.csv` | Palabras clave con puntaje c-TF-IDF por tema |
| `document_topics.csv` | Cada intervención con su tema asignado |
| `topics_per_group.csv` | Distribución de temas por grupo parlamentario |
| `global_word_frequency.csv` | Top 300 palabras más frecuentes |
| `word_frequency_per_group.csv` | Top 50 palabras por grupo parlamentario |
| `viz_*.html` | Visualizaciones interactivas *(abrir en navegador)* |

---

*Generado con `run_bertopic_hemicycle_full.py` sobre 138,551 intervenciones de 661,690 filas enlazadas a diputados.*
