# BERTopic — análisis temático del corpus de diputados franceses (XV legislatura)

Este módulo agrupa por tema cinco corpus distintos producidos por —o sobre— los diputados de la XV legislatura francesa (2017-2022): tweets, intervenciones en el hemiciclo, leyes, enmiendas y manifiestos electorales. Sobre cada corpus se ejecuta el mismo pipeline de BERTopic con stop-words ajustadas al dominio, y se genera un conjunto comparable de tablas y visualizaciones en `<fuente>/results/`.

El objetivo es triangular la agenda parlamentaria desde distintas superficies discursivas (campaña vs. trabajo legislativo vs. comunicación pública) mediante una representación temática consistente entre fuentes.

## Corpus de entrada

| Fuente | Archivo de origen | Periodo | Filtro de largo | Docs finales |
|---|---|---|---|---|
| `manifestos` | `french_deputies/manifestos/processed/manifesto_texts.csv` (+ `manifesto_full_texts.csv` para mapeo de partido) | Elección 2017 | **sin filtro de largo** (quasi-frases pre-segmentadas por MARPOR; solo se descartan vacías) | 3 801 |
| `amendements` | `french_deputies/lois_votes/votes_rd/processed/amendements_votos_con_texto.csv` | XV legis. | enmiendas con `match_confianza` alta/media y texto concatenado (`dispositif + expose_sommaire`) >= 10 palabras | 2 575 |
| `lois` | `french_deputies/lois_votes/votes_rd/processed/leyes_texto_oficial.csv` | XV legis. | párrafos del texto promulgado >= 10 palabras (solo leyes con `texto_confianza == "alta"`) | 23 267 |
| `tweets` | `french_deputies/twitter_zeeschuimer/processed/tweets_text_only.csv` | mar/2017-2025 | tweets >= 10 palabras tras limpieza (urls, menciones, hashtags) | 222 644 |
| `interventions` | `french_deputies/hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz` | 2017-2022 | intervenciones >= 10 palabras, con `deputy_id` y no procedurales | 338 192 |

El origen completo de cada corpus se documenta en sus respectivos módulos del proyecto. Aquí solo importa que los textos llegan ya procesados desde su carpeta y que BERTopic se aplica con la política de filtrado y stop-words descrita en cada `run.py`.

### Política de filtrado (resumen por fuente)

La regla general del módulo es **>= 10 palabras** en todas las fuentes, salvo manifiestos, cuya unidad nativa son las *quasi-sentences* pre-segmentadas.

- **Manifestos**. **Sin filtro de largo**. Los manifiestos vienen pre-segmentados en *quasi-sentences* por los anotadores del Manifesto Project (MARPOR), la unidad nativa de codificación del esquema. Filtrar por largo equivaldría a descartar texto ya validado por expertos como codificable, y además sub-representaría al PCF (39 quasi-frases en total, de estilo telegráfico). Solo se descartan filas con texto vacío o nulo. Sin stop-words de dominio.
- **Amendements**. **>= 10 palabras** sobre el texto concatenado `dispositif + expose_sommaire`, además de exigir `match_confianza` alta/media entre el número de scrutin y el texto de la enmienda. La distribución del corpus tiene mediana ~206 palabras, así que el filtro no descarta enmiendas sustantivas: corta ~5% formado mayormente por filas donde ambos campos del CSV vienen vacíos (NaN) y la concatenación produce un texto basura ("nan nan") que en versiones anteriores formaba un tópico espurio. Stop-words: `LEGAL_STOPWORDS`.
- **Lois**. Cada ley es un texto largo (cientos o miles de palabras); para que BERTopic descubra tópicos significativos se la parte en **párrafos** y se filtran los párrafos con **< 10 palabras** (descarta encabezados, referencias huérfanas y fragmentos de tabla). Solo se usan leyes con `texto_confianza == "alta"`. Stop-words: `LEGAL_STOPWORDS`.
- **Tweets**. Limpieza previa: se eliminan urls y menciones `@`, se "abren" los hashtags y se normalizan puntuación y espacios. Luego se filtran los tweets con **< 10 palabras** (descarta puro emoji, urls residuales o reactivos cortos tipo "merci!"). Stop-words: `TWITTER_STOPWORDS`.
- **Interventions**. Solo intervenciones enlazadas a un diputado de la cohorte (`deputy_id` no nulo), con **>= 10 palabras** (descarta interjecciones del hemiciclo tipo "Tres bien!", "Mme la Presidente."). Los patrones procedurales adicionales (apertura/cierre de sesión, anuncios de scrutin, "la parole est a", "je mets aux voix") se descartan vía regex. Stop-words: `HEMICYCLE_STOPWORDS`.

## Pipeline (4 pasos, idéntico para todas las fuentes)

1. **Embedding**. Cada documento se mapea a un vector de 384 dimensiones con `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers). Es un modelo multilingüe, para no perder la semántica del francés.
2. **Reducción dimensional (UMAP)**. De 384-D a 5-D conservando la geometría local. Sin este paso, el clustering en alta dimensión funciona mal.
3. **Clustering (HDBSCAN)**. Cada cluster densamente conectado es un tópico. Los puntos no asignados van a `-1` (outliers). De aquí salen entre 28 y 173 tópicos crudos según la fuente.
4. **Etiquetado por c-TF-IDF**. Para nombrar cada tópico, BERTopic concatena todos sus documentos en un "documento gigante" y calcula TF-IDF tratando a cada tópico como un documento. Las palabras con score alto son las que aparecen mucho dentro del tópico y poco en los demás: ese es el "significado" del tópico que se ve en `top_words_per_topic.csv`. Adicionalmente se aplica `KeyBERTInspired` como representation model para refinar los términos.

### Reducción a 25 tópicos

HDBSCAN no impone un número objetivo de tópicos. Para que las cinco fuentes sean comparables (y para que las tablas sean interpretables), cada corrida termina con una **reducción aglomerativa post-fit** hacia un objetivo de 25 tópicos:

- Calcula la similitud coseno entre los vectores c-TF-IDF de cada par de tópicos.
- Fusiona el par más similar (los documentos del menos frecuente se unen al más cercano) y recalcula c-TF-IDF.
- Repite hasta llegar a 25 tópicos (o menos, si el corpus no soporta tantos clusters distintos).

En la práctica, las 5 corridas convergen en 24 tópicos finales más el bucket `-1` de outliers.

### Stop-words

`common/bertopic_runner.py` define cuatro listas que se aplican según la fuente, sumadas a una base francesa genérica (artículos, pronombres, modales, numerales, etc.):

- `FRENCH_STOPWORDS` (siempre)
- `LEGAL_STOPWORDS` (lois, amendements): vocabulario legal/parlamentario procedural — estructura del documento (`article`, `alinea`, `chapitre`), mecánica de enmiendas (`modifie`, `redige`, `insere`, `supprime`), modalidades (`fixe`, `applicable`, `determine`), verbos dispositivos (`stipule`, `dispose`, `prevoit`, `vise`, `relatif`), modales de obligación legal (`doit`, `peut`, `pourra`), referencias internas (`ci-dessus`, `susvise`, `precite`, `supra`), numeración legal francesa (`bis`, `ter`, `quater`, romanos `i-x`, `1°-9°`), entidades republicanas (`republique`, `gouvernement`, `assemblee`, `senat`), publicación oficial (`expose`, `motifs`, `JORF`) y conectores formulaicos (`notamment`, `toutefois`, `lequel`).
- `HEMICYCLE_STOPWORDS` (interventions): saludos del hemiciclo (`monsieur le president`, `madame la ministre`, `cher collegue`), nombres de roles (`rapporteur`, `depute`), `applaudissements`, mecánica de votos (`scrutin`, `vote`, `amendement`).
- `TWITTER_STOPWORDS` (tweets): ruido web (`http`, `https`, `co`, `rt`, `via`, `twitter`, `youtube`, `lien`, etc).

## Configuración por fuente

Parámetros expuestos en cada `<fuente>/run.py`:

| Fuente | `min_topic_size` | `min_df` | `ngram_range` | `target_nr_topics` | Clase agrupadora |
|---|---|---|---|---|---|
| manifestos | 15 | 3 | (1, 2) | 25 | `party` |
| amendements | 20 | 5 | (1, 2) | 25 | `ley` |
| lois | 50 | 10 | (1, 2) | 25 | `dossier` |
| tweets | 100 | 30 | (1, 2) | 25 | `political_group` |
| interventions | 150 | 50 | (1, 2) | 25 | `political_group` |

- **`min_topic_size`**: corte mínimo de HDBSCAN para considerar un cluster. Sube con el tamaño del corpus para que no aparezcan micro-tópicos triviales.
- **`min_df`**: en el `CountVectorizer` que alimenta a c-TF-IDF, un término debe aparecer en al menos N documentos para ser considerado vocabulario. Sube con el tamaño del corpus.
- **`ngram_range`**: unigramas y bigramas. Los bigramas captan terminología compuesta (`assurance chomage`, `transition energetique`, `loi orientation agricole`).
- **`target_nr_topics`**: número objetivo final, idéntico para todas las fuentes con el fin de hacerlas comparables.

### Detalle de la corrida (registrado en cada `summary.json`)

| Fuente | Docs | Topicos crudos (HDBSCAN) | Topicos finales | Outliers (-1) | Tiempo (s) |
|---|---:|---:|---:|---:|---:|
| manifestos | 3 801 | 51 | 24 | 1 169 | 19 |
| amendements | 2 575 | 27 | 24 | 656 | 33 |
| lois | 23 267 | 126 | 24 | 8 833 | 96 |
| tweets | 222 644 | 173 | 24 | 105 894 | 407 |
| interventions | 338 192 | 156 | 24 | 165 439 | 2 355 |

Todas las corridas usan el mismo embedder (`paraphrase-multilingual-MiniLM-L12-v2`) y la misma estrategia de reducción. Los tiempos son sobre CPU (Mac M-series).

## Qué se genera en `<fuente>/results/`

Cada corrida produce el mismo conjunto de archivos:

| Archivo | Qué contiene |
|---|---|
| `topic_info.csv` | Una fila por tópico: `Topic`, `Count`, `Name`, `Representation` (top palabras), `Representative_Docs` (3 documentos ejemplares). |
| `top_words_per_topic.csv` | Tabla larga: `topic, word, score` con las top 10 palabras de cada tópico y su peso c-TF-IDF. |
| `document_topics.csv` | Una fila por documento: texto, tópico asignado, probabilidad y la clase agrupadora (`party`, `political_group`, `ley`, `dossier`). |
| `topics_per_<class>.csv` | Frecuencia de tópicos por clase. Útil para ver la distribución temática por partido o por dossier. |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes del corpus tras limpieza y stop-words. Sanity check del preprocesamiento. |
| `summary.json` | Metadata de la corrida (n_documents, parámetros, top 10 tópicos preview, tiempo). |
| `run.log` | stdout completo de la corrida (BERTopic + warnings + timestamps). |
| `viz_barchart.html` | Top 15 tópicos con sus términos más representativos. |
| `viz_topics_map.html` | Mapa 2D de tópicos (proyección UMAP de los embeddings de cada tópico). |
| `viz_heatmap.html` | Matriz de similitud entre tópicos. |
| `viz_hierarchy.html` | Dendrograma jerárquico de la agrupación de tópicos. |
| `viz_topics_per_<class>.html` | Heatmap de prevalencia por clase. |

Los HTML son auto-contenidos (Plotly inline) y se abren con doble clic.

## Resultados

A continuación se listan las 24 categorías finales por fuente, ordenadas por tamaño. La columna "tema" es lectura humana; las palabras crudas están en `top_words_per_topic.csv`.

### Manifestos (3 801 párrafos, 24 tópicos, 1 169 outliers)

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 436 | Francia / Europa / proyecto nacional | france, europe, françaises, européens, européenne |
| 1 | 304 | Constitución y reforma institucional | parlement, constitution, législative, parlementaire, démocratie |
| 2 | 284 | Educación / sistema escolar | enseignement, pédagogiques, système scolaire, supérieur, écoles |
| 3 | 226 | Fiscalidad / jubilaciones | évasion fiscale, petites retraites, pensions, impôt revenu |
| 4 | 178 | Servicios públicos y territorio | services publics, fonctions publiques, aménagement territoire |
| 5 | 164 | Trabajo / derechos del asalariado | droits salariés, contrat travail, employeur, heures supplémentaires |
| 6 | 163 | Familia / asignaciones / salud familiar | allocations familiales, quotient familial, maisons santé |
| 7 | 125 | Agricultura ecológica / PAC | agriculture écologique, politique agricole, agriculture biologique |
| 8 | 94 | Energías renovables / transición | énergies renouvelables, éolien, transition énergétique |
| 9 | 79 | Soberanía digital / numérique | numérique, souveraineté numérique, révolution numérique |
| 10 | 78 | Economía social y solidaria | économie sociale, sociale solidaire, utilité sociale |
| 11 | 76 | Crítica política / república / outre-mer | défi politique, ruine économique, démagogique, république |
| 12 | 74 | Igualdad mujeres-hombres | égalité femmes, droits femmes, libertés femmes |
| 13 | 53 | Marítimo / outre-mer | océans, économie mer, ports français, maritime |
| 14 | 51 | Asilo e inmigración | demandes asile, droit asile, immigration, migrants |
| 15 | 41 | Pleno empleo / poder adquisitivo (slogan-y) | agir pouvoir, contrat, plein-emploi, laïcité |
| 16 | 36 | Lucha contra el terrorismo | contre terrorisme, antiterroriste, terroristes djihadistes |
| 17 | 36 | Justicia / prisiones / penas | peines plancher, prison, places prison, recidiviste |
| 18 | 32 | Lemas de campaña (texto programático) | gagnerons, sommes prêts, sommes capables |
| 19 | 28 | "Aucune fatalite" / lemas | aucune fatalité, ruralite, vie rien |
| 20 | 21 | Energía nuclear / disuasión | nucléaire, dissuasion nucléaire, mix énergétique |
| 21 | 20 | Reducción del empleo público | supprimerons emplois publics, réduirons nombre |
| 22 | 17 | TPE-PME | tpe, plan tpe, tpe pme, simplification |
| 23 | 16 | Deporte | sport, fédérations sportives, pratique sportive |

### Amendements (2 575 enmiendas, 24 tópicos, 656 outliers)

Esta tabla corresponde a la corrida con el filtro `>= 10 palabras` y el manejo correcto de NaN en la concatenación `dispositif + expose_sommaire`. La versión anterior tenía un tópico espurio "nan nan" (138 docs) que aquí ya no aparece; la temática sustantiva queda mejor resuelta: el bloque sanitario/salud se desdobla en tres tópicos distintos (salud-acceso, crisis sanitaria/estado de urgencia, COVID-vacunación).

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 222 | Fiscalidad / impuestos | impôts amendement, général impôts, fiscale, impôt, taxe additionnelle |
| 1 | 187 | Vivienda / construcción | logement, logements, construction habitation, logements sociaux, immobilier |
| 2 | 153 | Procedimiento penal / prisión | ans emprisonnement, procédure pénale, peines, pénale, emprisonnement |
| 3 | 119 | Derecho del trabajo / representación asalariados | administrateurs salariés, représentant salariés, employeurs, salarié |
| 4 | 114 | Reforma de jubilaciones | réformes retraites, système retraites, régime retraite, retraite universel |
| 5 | 111 | Alimentación / pesca / rural | denrées alimentaires, rural pêche, pêche maritime, produits agricoles |
| 6 | 99 | Educación / autoridad parental | autorité parentale, matière éducation, pédagogiques, établissements enseignement |
| 7 | 88 | Salud / médicos / acceso a cuidados | médecins généralistes, santé publique, professionnels santé, assurance maladie |
| 8 | 82 | Carta del medio ambiente | charte environnement, environnementale, protection environnement |
| 9 | 73 | Financiamiento / presupuesto | financements, budgétaire, financement, budget, euros crédits |
| 10 | 64 | Inmigración / extranjeros / asilo | immigration intégration, immigration, migrants, étrangers droit, droit asile |
| 11 | 63 | Mandato / forma del amendement (boilerplate) | amendement groupe, amendement propose, mandat député |
| 12 | 62 | Lemas políticos / represión | répression institutionnalisé, projet demandons, dévastateur amendement |
| 13 | 61 | Pedidos de informe (mecanismos parlamentarios) | rapport évalue, rapport évaluant, demande rapport, rapport information |
| 14 | 59 | Mecanismo "souligner/justifier" (fórmula) | texte amendement, amendement souligner, solennellement amendement, amendement justifie |
| 15 | 59 | Reforma constitucional | inscrire constitution, 24 constitution, suffrages exprimés, élections législatives |
| 16 | 58 | Mecanismo "suivants/sauf" (fórmula) | texte suivants, suivants sauf, deuxième, sauf accord |
| 17 | 48 | Crisis sanitaria / estado de urgencia | crise sanitaire, juillet 2022, urgence sanitaire, mai 2021, état urgence |
| 18 | 48 | COVID-19 / vacunación | covid 19, résultat sérologique, schéma vaccinal, virus, couverture vaccinale |
| 19 | 41 | Transportes públicos | 1115 transports, transports publics, transport ferroviaire, transport routier |
| 20 | 31 | Discriminación / federaciones deportivas | contre discriminations, er constitution, société mentionnée, fédérations sportives |
| 21 | 30 | Libertades digitales / neutralidad de la red | libertés numériques, privée numérique, neutralité internet, liberté expression |
| 22 | 24 | Reciclaje de plásticos | recyclage bouteilles, bouteilles plastique, bouteilles consommées, plastique usage |
| 23 | 23 | Prestaciones sociales / handicap | prestations familiales, compensation handicap, bénéficiaires, justice sociale |

### Lois (23 267 artículos, 24 tópicos, 8 833 outliers)

El tópico 0 sigue siendo dominante (~36% del corpus) por la fórmula recurrente "le rapport mentionne les mesures..." que sobrevive a las stop-words. Los tópicos 7, 10 y 16 son boilerplate residual (cifras, tablas, nomenclatura). El resto sí captura temática sustantiva.

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 8 349 | Boilerplate de informes (residual) | rapport, mentionnés, mentionné, mesures |
| 1 | 1 201 | Fiscalidad intercomunal / colectividades territoriales | intercommunale fiscalité, public coopération, collectivités territoriales |
| 2 | 815 | Educación / formación profesional | enseignement, formation professionnelle, éducation, apprentis |
| 3 | 648 | Política de desarrollo / solidaridad mundial | politique développement, développement solidaire, inégalités mondiales |
| 4 | 565 | Déficit / crisis / proyección presupuestaria | déficit, crise, 2020, 2024 |
| 5 | 275 | Renovación energética / construcción / vivienda | rénovation énergétique, construction habitation, production énergie |
| 6 | 265 | Ley PACTE 2019 | 2019 croissance, transformation entreprises, croissance transformation |
| 7 | 265 | Boilerplate fiscal (residual) | mentionnée 2e, réfaction mentionnée, engagements exprimés |
| 8 | 245 | Fiscalidad / tasa profesional | taxe professionnelle, fiscalité, etat profit |
| 9 | 238 | Elecciones / electoral | élections partielles, élections, électoral |
| 10 | 235 | Cifras y montos (residual) | colonne montant, 23 162, suivantes 000 |
| 11 | 210 | Promulgación presidencial (fórmula) | président promulgue, visa président |
| 12 | 177 | Financiamiento / contribuciones / dependencia | 000 contribution, financement, dépenses solde |
| 13 | 171 | Asilo y derecho de los refugiados | demande asile, droit asile, protection réfugiés |
| 14 | 164 | Especialidades farmacéuticas / salud | spécialité pharmaceutique, prescription, chargés santé |
| 15 | 122 | Autopistas y rutas | autoroutes, autoroutes routes, voies transférées |
| 16 | 74 | Cifras presupuestarias (residual) | montant arrondi, conjoncturel mesures |
| 17 | 70 | Asiento del impuesto / imposición | assiette impôt, imposition cas, droits organisme |
| 18 | 66 | Outre-mer / Pacífico | futuna, polynésie wallis, futuna, art 765 |
| 19 | 59 | Pensión de reversión / jubilación | retraite cas, pension réversion, retraite obligatoire |
| 20 | 57 | "France Services" / red de servicios | france services, services public, maisons services |
| 21 | 57 | Asociaciones / federaciones deportivas | sport statuts, association sportive, fédération sportive |
| 22 | 54 | Capacidad eléctrica (kw) | 000 kw, 750 kw, 500 kw |
| 23 | 52 | Controles aduaneros / argent liquide | argent liquide, contrôles argent, européen |

### Tweets (222 644 tweets, 24 tópicos, 105 894 outliers)

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 15 662 | Guerra de Ucrania / Rusia | ukrainien, ukraine, peuple ukrainien, russie, guerre |
| 1 | 15 444 | Reuniones públicas / agenda local | réunion, assemblée nationale, rencontre, citoyens |
| 2 | 11 501 | Macron / presidencia | emmanuel macron, macron, françois bayrou, président |
| 3 | 11 104 | Juegos Olímpicos / deporte | jeux olympiques, olympique, champions, athlètes |
| 4 | 9 462 | Francia / France insoumise / elecciones europeas | france insoumise, françaises, élections européennes |
| 5 | 7 320 | Reforma de jubilaciones | réforme retraites, pensions, retraités, sécurité sociale |
| 6 | 6 190 | Fin de vida / cuidados paliativos / eutanasia | soins palliatifs, aide mourir, palliatifs, euthanasie |
| 7 | 5 855 | Mundo agrícola / Salon de l'Agriculture | monde agricole, soutien agriculteurs, salon agriculture |
| 8 | 5 853 | Policía / inseguridad / acoso | contre harcèlement, policiers, police, violence |
| 9 | 5 472 | Política energética / transición / nuclear | politique énergétique, transition énergétique, énergies renouvelables |
| 10 | 4 945 | Condolencias / homenajes / fallecimientos | sincères condoléances, hommage victimes, immense tristesse |
| 11 | 4 292 | Crisis de la vivienda | crise logement, logements sociaux, immobilier |
| 12 | 4 227 | Redes sociales / cybersecurite / 2024-2030 | 2024 2030, cybersécurité, interdiction réseaux sociaux |
| 13 | 3 053 | Derechos de las mujeres / 8M | droits femmes, féministes, égalité femmes, women |
| 14 | 1 849 | Vacunación COVID-19 | vaccinationcovid, campagne vaccination, stratégie vaccinale |
| 15 | 1 024 | Saludos de fin de año | belle année, bonne année, joyeux noël |
| 16 | 969 | Anuncios de invitaciones a medios | invité serai, 8h30 invité, serai invité |
| 17 | 847 | Bomberos | hommage pompiers, pompiers volontaires, sapeurs pompiers |
| 18 | 574 | Venezuela / Maduro | peuple vénézuélien, venezuela, débarrassé dictature |
| 19 | 370 | China / diplomacia | ambassadeur chine, china, régime chinois |
| 20 | 324 | Iglesia católica / pope | pape américain, nouveau pape, pontificat |
| 21 | 175 | Autismo (sensibilización) | sensibilisation autisme, semaine autisme, personnes autistes |
| 22 | 134 | Afganistán / talibanes | situation afghanistan, kaboul afghanistan, afghanes talibans |
| 23 | 104 | Cannabis / despenalización | cannabis dépénalisation, légaliser cannabis, légalisation cannabis |

Visualización adicional `viz_topics_per_political_group.html`: prevalencia temática por grupo parlamentario (LAREM, FI, LR, RN/NI, MODEM, EDS, GDR, SOC, etc.).

### Interventions (338 192 intervenciones, 24 tópicos, 165 439 outliers)

Es el corpus más grande y el único que toma horas (~40 min en CPU M-series). Los tópicos 0, 1, 9, 11 y 17 son procedural-residual (fórmula de votos, llamadas al reglamento, "renvoyée prochaine", etc.). El resto sí captura temática sustantiva del trabajo legislativo.

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 40 135 | Discurso político genérico (procedural-residual) | parlementaire, parlementaires, parce, politique |
| 1 | 31 080 | Comisión / avis / saisie (procedural-residual) | républicains demande, commission suis, avis commission |
| 2 | 24 483 | Unión Europea / Europa | union européenne, europe, européens, gouvernement |
| 3 | 22 754 | Reforma / presupuesto / gobierno | réforme, gouvernement, budget, politique |
| 4 | 15 125 | Sistema de salud / sanitario | système santé, urgence sanitaire, professionnels santé |
| 5 | 8 128 | Educación / escuela | directeurs école, scolaires, écoles |
| 6 | 3 493 | Desempleo / asuransa-chomage | chômage, chômeurs, demandeurs emploi, assurance chômage |
| 7 | 3 482 | Transporte ferroviario | ferroviaires, ferroviaire, transports |
| 8 | 3 455 | Derechos de las mujeres / igualdad | droits femmes, égalité femmes, sages femmes, sexistes |
| 9 | 3 046 | Resultados de votos (procedural-residual) | nombre votants, suffrages exprimés |
| 10 | 2 713 | Agua / agencias del agua | agences eau, gestion eau, accès eau, eau assainissement |
| 11 | 2 685 | "Renvoyée a la prochaine seance" (procedural) | prochaine, renvoyée prochaine, prochaine demande |
| 12 | 2 547 | Medios / audiovisual público | médias, journalistes, audiovisuel public |
| 13 | 2 047 | Deporte / asociaciones deportivas | associations sportives, ministère sports, clubs sportifs |
| 14 | 1 538 | Notre-Dame / patrimonio | restauration cathédrale, cathédrale dame, église |
| 15 | 1 122 | Política exterior / Siria / Argelia | syrie, algérie, affaires étrangères, armées |
| 16 | 1 094 | Bioética / embriones | embryon humain, souches embryonnaires, lois bioéthique |
| 17 | 1 040 | Llamadas al reglamento (procedural) | rappels règlement, rappel règlement, règles |
| 18 | 940 | Maltrato animal / protección animal | maltraitance animale, animal compagnie, protection animale |
| 19 | 595 | Lengua / lenguas regionales | langue république, langues régionales, langue régionale |
| 20 | 543 | Constitucional / artículos / poursuivi | articles constitutionnelle, poursuivi articles |
| 21 | 294 | COVID / mascarillas | acheter masques, masque obligatoire, porter masque |
| 22 | 253 | Cifras / "milliards d'euros" (residual) | milliards euros, million euros |
| 23 | 161 | Mención personal a Caroline Fiat (residual) | caroline fiat, fiat caroline |

Visualización adicional `viz_topics_per_political_group.html`: prevalencia temática por grupo parlamentario.

## Reproducir las corridas

Cada fuente tiene su `run.py` autocontenido. Las dependencias están en `requirements.txt`.

Activar el entorno (usa el Python del sistema con pip user-install) y correr cualquier fuente:

```bash
cd french_deputies/bertopic_analysis
python3 -u manifestos/run.py    2>&1 | tee manifestos/results/run.log
python3 -u amendements/run.py   2>&1 | tee amendements/results/run.log
python3 -u lois/run.py          2>&1 | tee lois/results/run.log
python3 -u tweets/run.py        2>&1 | tee tweets/results/run.log
python3 -u interventions/run.py 2>&1 | tee interventions/results/run.log
```

Tiempos aproximados en CPU M-series:

- manifestos: ~30 s
- amendements: ~30 s
- lois: ~2 min
- tweets: ~7 min
- interventions: ~40 min

`-u` fuerza la salida unbuffered (así `tee` muestra el avance en vivo). No hace falta `nohup` ni `&`: si necesitas cerrar la terminal, usa `screen`/`tmux`.

## Notas sobre el runner

El núcleo está en `common/bertopic_runner.py`. Dos detalles importantes que cambiaron en esta versión y que conviene tener presentes si se reentrenan los modelos:

1. **`nr_topics="auto"` está desactivado a nivel BERTopic cuando hay `target_nr_topics`.** El auto-reduce iterativo de BERTopic recalcula c-TF-IDF después de cada merge sobre tópicos agregados, y si en alguna iteración el número de tópicos cae por debajo del `min_df` configurado (`30` para tweets, `50` para interventions), sklearn lanza `After pruning, no terms remain` o `max_df < min_df`. La estrategia actual es: dejar que HDBSCAN saque sus tópicos crudos (~150-180), saltarse el auto-reduce interno y bajar a 25 con una única reducción manual al final.

2. **Vectorizer parcheado durante la reducción final.** En la fase de `reduce_topics`, BERTopic recomputa c-TF-IDF sobre un documento agregado por tópico. Para que un `min_df=30` o `50` no rompa cuando solo hay 25 tópicos, el runner intercambia momentáneamente el `CountVectorizer` por uno con `min_df=1`. La parte IDF de c-TF-IDF sigue despriorizando términos compartidos entre tópicos, así que los términos finales no quedan ruidosos.

El resto (UMAP, HDBSCAN, KeyBERT representation, visualizaciones, exportación) es estándar.

## Limitaciones conocidas

- **Outliers altos**. Tweets e interventions tienen ~48% de docs en `-1`. Es esperable: HDBSCAN es estricto y el corpus tiene mucho discurso ad-hoc. Para reducirlos habría que bajar `min_topic_size`, pero entonces crece la cantidad de micro-tópicos.
- **Tópicos residuales en lois e interventions**. La estructura formularia de los textos legales y procedurales del hemiciclo deja tópicos que, aun con stop-words extendidas, se llenan de boilerplate. Están listados explícitamente arriba para que el lector los descarte.
- **Determinismo limitado**. UMAP y HDBSCAN usan semilla por defecto; las corridas son razonablemente reproducibles, pero pueden variar +/- algunos tópicos crudos entre ejecuciones. La reducción final a 25 estabiliza la salida.
- **`paraphrase-multilingual-MiniLM-L12-v2`** es un modelo chico (118 MB) elegido por velocidad. Modelos más grandes (p. ej. `xlm-roberta-base` o `LaBSE`) probablemente captarían mejor los matices ideológicos, a costa de varias horas más de embedding.

## Estructura del módulo

```
bertopic_analysis/
├── README.md                       # este archivo
├── requirements.txt                # bertopic, sentence-transformers, umap-learn, hdbscan, plotly, pandas
├── common/
│   ├── __init__.py
│   └── bertopic_runner.py          # pipeline reutilizable (run_bertopic)
├── manifestos/
│   ├── run.py                      # carga manifestos_clean.csv y llama a run_bertopic
│   └── results/                    # outputs (24 tópicos, ver arriba)
├── amendements/
│   ├── run.py                      # carga amendements_votos_con_texto.csv
│   └── results/                    # outputs
├── lois/
│   ├── run.py                      # carga articles_lois_xv.csv.gz
│   └── results/                    # outputs
├── tweets/
│   ├── run.py                      # carga tweets_text_only.csv (con limpieza de tweets)
│   └── results/                    # outputs
└── interventions/
    ├── run.py                      # carga interventions_xv_2017_2022_with_deputies.csv.gz
    └── results/                    # outputs
```

Cada `run.py` es un script corto que carga el CSV de la fuente, aplica el filtrado específico (palabras mínimas, regex procedural, etc.), arma la lista de `docs` y la lista de `classes`, y delega en `common.bertopic_runner.run_bertopic(...)` con los parámetros propios de la fuente.

