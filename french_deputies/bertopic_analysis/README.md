# BERTopic — analisis tematico del corpus de diputados franceses (XV legislatura)

Este modulo agrupa por tema cinco corpus distintos producidos por o sobre los diputados de la XV legislatura francesa (2017-2022): tweets, intervenciones en el hemiciclo, leyes, enmiendas y manifiestos electorales. Para cada uno corre la misma pipeline de BERTopic con stop-words ajustadas al dominio y deja un set comparable de tablas y visualizaciones en `<fuente>/results/`.

El objetivo es triangular el "agenda parlamentaria" desde diferentes superficies discursivas (campaña vs trabajo legislativo vs comunicacion publica) usando una representacion tematica consistente entre fuentes.

## Corpus de entrada

| Fuente | Archivo de origen | Periodo | Filtro de largo | Docs finales |
|---|---|---|---|---|
| `manifestos` | `french_deputies/manifestos/processed/manifesto_texts.csv` (+ `manifesto_full_texts.csv` para mapeo de partido) | Eleccion 2017 | **sin filtro de largo** (quasi-frases pre-segmentadas por MARPOR; solo se descartan vacias) | 3 801 |
| `amendements` | `french_deputies/lois_votes/votes_rd/processed/amendements_votos_con_texto.csv` | XV legis. | enmiendas con `match_confianza` alta/media y texto concatenado (`dispositif + expose_sommaire`) >= 10 palabras | 2 575 |
| `lois` | `french_deputies/lois_votes/votes_rd/processed/leyes_texto_oficial.csv` | XV legis. | parrafos del texto promulgado >= 10 palabras (solo leyes con `texto_confianza == "alta"`) | 23 267 |
| `tweets` | `french_deputies/twitter_zeeschuimer/processed/tweets_text_only.csv` | mar/2017-2025 | tweets >= 10 palabras tras limpieza (urls, menciones, hashtags) | 222 644 |
| `interventions` | `french_deputies/hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz` | 2017-2022 | intervenciones >= 10 palabras, con `deputy_id` y no procedurales | 338 192 |

Origen completo de cada corpus en sus respectivos modulos del proyecto. Aca solo importa que los textos llegan ya procesados desde su carpeta y BERTopic se aplica con la politica de filtrado y stop-words descrita en cada `run.py`.

### Politica de filtrado (resumen por fuente)

La regla general que sigue el modulo: **>= 10 palabras** en todas las fuentes salvo manifiestos (cuya unidad nativa son las *quasi-sentences* pre-segmentadas).

- **Manifestos**. **Sin filtro de largo**. Los manifiestos vienen pre-segmentados en *quasi-sentences* por los anotadores del Manifesto Project (MARPOR), que es la unidad nativa de codificacion del esquema. Filtrar por largo equivaldria a descartar texto ya validado por expertos como codificable, y ademas sub-representaria al PCF (39 quasi-frases en total, estilo telegrafico). Solo se descartan filas con texto vacio o nulo. Sin stop-words de dominio.
- **Amendements**. **>= 10 palabras** sobre el texto concatenado `dispositif + expose_sommaire`, ademas de exigir `match_confianza` alta/media entre el numero de scrutin y el texto de la enmienda. La distribucion del corpus tiene mediana ~206 palabras, asi que el filtro no descarta enmiendas sustantivas: corta ~5% formado mayormente por filas donde ambos campos del CSV vienen vacios (NaN) y la concatenacion produce un texto basura ("nan nan") que en versiones anteriores formaba un topico espureo. Stop-words: `LEGAL_STOPWORDS`.
- **Lois**. Cada ley es un texto largo (cientos o miles de palabras); para que BERTopic descubra topicos significativos se la parte en **parrafos** y se filtran los parrafos con **< 10 palabras** (descarta encabezados, referencias huerfanas y fragmentos de tabla). Solo se usan leyes con `texto_confianza == "alta"`. Stop-words: `LEGAL_STOPWORDS`.
- **Tweets**. Limpieza previa: se sacan urls, menciones `@`, se "abren" hashtags, se normaliza puntuacion y espacios. Luego se filtran tweets con **< 10 palabras** (descarta puro emoji, urls residuales o reactivos cortos tipo "merci!"). Stop-words: `TWITTER_STOPWORDS`.
- **Interventions**. Solo intervenciones enlazadas a un diputado de la cohorte (`deputy_id` no nulo), con **>= 10 palabras** (descarta interjecciones del hemiciclo tipo "Tres bien!", "Mme la Presidente."). Patrones procedurales adicionales (apertura/cierre de sesion, anuncios de scrutin, "la parole est a", "je mets aux voix") se descartan via regex. Stop-words: `HEMICYCLE_STOPWORDS`.

## Pipeline (4 pasos, identica para todas las fuentes)

1. **Embedding**. Cada documento se mapea a un vector de 384 dimensiones con `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers). Modelo multilingue para no perder semantica del frances.
2. **Reduccion dimensional (UMAP)**. De 384-D a 5-D conservando geometria local. Sin esto el clustering en alta dimension funciona mal.
3. **Clustering (HDBSCAN)**. Cada cluster densamente conectado = un topico. Los puntos no asignados van a `-1` (outliers). De aqui salen entre 28 y 173 topicos crudos segun la fuente.
4. **Etiquetado por c-TF-IDF**. Para nombrar cada topico, BERTopic concatena todos los docs del topico en un "documento gigante" y calcula TF-IDF tratando a cada topico como un documento. Las palabras con score alto son las que aparecen mucho dentro del topico y poco en otros: ese es el "significado" del topico que se ve en `top_words_per_topic.csv`. Adicionalmente se aplica `KeyBERTInspired` como representation model para refinar los terminos.

### Reduccion a 25 topicos

HDBSCAN no impone un numero objetivo de topicos. Para que las cinco fuentes sean comparables (y para que las tablas sean interpretables) cada corrida termina con una **reduccion aglomerativa post-fit** a un objetivo de 25 topicos:

- Calcula similitud coseno entre los vectores c-TF-IDF de cada par de topicos.
- Mergea el par mas similar (los docs del menos frecuente se fusionan al mas cercano) y recalcula c-TF-IDF.
- Repite hasta llegar a 25 topicos (o menos, si el corpus no soporta tantos clusters distintos).

En la practica, las 5 corridas convergen en 24 topicos finales + el bucket `-1` de outliers.

### Stop-words

`common/bertopic_runner.py` define cuatro listas que se aplican segun la fuente, sumadas a una base francesa generica (articulos, pronombres, modales, numerales, etc):

- `FRENCH_STOPWORDS` (siempre)
- `LEGAL_STOPWORDS` (lois, amendements): vocabulario legal/parlamentario procedural — estructura del documento (`article`, `alinea`, `chapitre`), mecanica de enmiendas (`modifie`, `redige`, `insere`, `supprime`), modalidades (`fixe`, `applicable`, `determine`), verbos dispositivos (`stipule`, `dispose`, `prevoit`, `vise`, `relatif`), modales de obligacion legal (`doit`, `peut`, `pourra`), referencias internas (`ci-dessus`, `susvise`, `precite`, `supra`), numeracion legal francesa (`bis`, `ter`, `quater`, romanos `i-x`, `1°-9°`), entidades republicanas (`republique`, `gouvernement`, `assemblee`, `senat`), publicacion oficial (`expose`, `motifs`, `JORF`) y conectores formulaicos (`notamment`, `toutefois`, `lequel`).
- `HEMICYCLE_STOPWORDS` (interventions): saludos del hemiciclo (`monsieur le president`, `madame la ministre`, `cher collegue`), nombres de roles (`rapporteur`, `depute`), `applaudissements`, mecanica de votos (`scrutin`, `vote`, `amendement`).
- `TWITTER_STOPWORDS` (tweets): ruido web (`http`, `https`, `co`, `rt`, `via`, `twitter`, `youtube`, `lien`, etc).

## Configuracion por fuente

Parametros expuestos en cada `<fuente>/run.py`:

| Fuente | `min_topic_size` | `min_df` | `ngram_range` | `target_nr_topics` | Clase agrupadora |
|---|---|---|---|---|---|
| manifestos | 15 | 3 | (1, 2) | 25 | `party` |
| amendements | 20 | 5 | (1, 2) | 25 | `ley` |
| lois | 50 | 10 | (1, 2) | 25 | `dossier` |
| tweets | 100 | 30 | (1, 2) | 25 | `political_group` |
| interventions | 150 | 50 | (1, 2) | 25 | `political_group` |

- **`min_topic_size`**: corte minimo de HDBSCAN para considerar un cluster. Sube con el tamaño del corpus para que no aparezcan micro-topicos triviales.
- **`min_df`**: en el `CountVectorizer` que alimenta a c-TF-IDF, un termino debe aparecer en al menos N documentos para ser considerado vocabulario. Sube con el tamaño del corpus.
- **`ngram_range`**: unigramas y bigramas. Los bigramas captan terminologia compuesta (`assurance chomage`, `transition energetique`, `loi orientation agricole`).
- **`target_nr_topics`**: numero objetivo final, identico para todos para hacer las fuentes comparables.

### Detalle de la corrida (registrado en cada `summary.json`)

| Fuente | Docs | Topicos crudos (HDBSCAN) | Topicos finales | Outliers (-1) | Tiempo (s) |
|---|---:|---:|---:|---:|---:|
| manifestos | 3 801 | 51 | 24 | 1 169 | 19 |
| amendements | 2 575 | 27 | 24 | 656 | 33 |
| lois | 23 267 | 126 | 24 | 8 833 | 96 |
| tweets | 222 644 | 173 | 24 | 105 894 | 407 |
| interventions | 338 192 | 156 | 24 | 165 439 | 2 355 |

Todas las corridas usan el mismo embedder (`paraphrase-multilingual-MiniLM-L12-v2`) y la misma estrategia de reduccion. Los tiempos son sobre CPU (Mac M-series).

## Que se genera en `<fuente>/results/`

Cada corrida produce el mismo set de archivos:

| Archivo | Que contiene |
|---|---|
| `topic_info.csv` | Una fila por topico: `Topic`, `Count`, `Name`, `Representation` (top palabras), `Representative_Docs` (3 documentos ejemplares). |
| `top_words_per_topic.csv` | Tabla larga: `topic, word, score` con las top 10 palabras de cada topico y su peso c-TF-IDF. |
| `document_topics.csv` | Una fila por documento: texto, topico asignado, probabilidad y la clase agrupadora (`party`, `political_group`, `ley`, `dossier`). |
| `topics_per_<class>.csv` | Frecuencia de topicos por clase. Util para ver la distribucion tematica por partido o por dossier. |
| `global_word_frequency.csv` | Top 200 palabras mas frecuentes del corpus tras limpieza y stop-words. Sanity check del preprocesamiento. |
| `summary.json` | Metadata de la corrida (n_documents, parametros, top 10 topicos preview, tiempo). |
| `run.log` | stdout completo de la corrida (BERTopic + warnings + timestamps). |
| `viz_barchart.html` | Top 15 topicos con sus terminos mas representativos. |
| `viz_topics_map.html` | Mapa 2D de topicos (proyeccion UMAP de los embeddings de cada topico). |
| `viz_heatmap.html` | Matriz de similitud entre topicos. |
| `viz_hierarchy.html` | Dendrograma jerarquico de la agrupacion de topicos. |
| `viz_topics_per_<class>.html` | Heatmap de prevalencia por clase. |

Los HTML son auto-contenidos (Plotly inline), se abren con doble click.

## Resultados

A continuacion las 24 categorias finales por fuente, ordenadas por tamaño. La columna "tema" es lectura humana; las palabras crudas estan en `top_words_per_topic.csv`.

### Manifestos (3 801 parrafos, 24 topicos, 1 169 outliers)

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 436 | Francia / Europa / proyecto nacional | france, europe, françaises, européens, européenne |
| 1 | 304 | Constitucion y reforma institucional | parlement, constitution, législative, parlementaire, démocratie |
| 2 | 284 | Educacion / sistema escolar | enseignement, pédagogiques, système scolaire, supérieur, écoles |
| 3 | 226 | Fiscalidad / jubilaciones | évasion fiscale, petites retraites, pensions, impôt revenu |
| 4 | 178 | Servicios publicos y territorio | services publics, fonctions publiques, aménagement territoire |
| 5 | 164 | Trabajo / derechos del asalariado | droits salariés, contrat travail, employeur, heures supplémentaires |
| 6 | 163 | Familia / asignaciones / salud familiar | allocations familiales, quotient familial, maisons santé |
| 7 | 125 | Agricultura ecologica / PAC | agriculture écologique, politique agricole, agriculture biologique |
| 8 | 94 | Energias renovables / transicion | énergies renouvelables, éolien, transition énergétique |
| 9 | 79 | Soberania digital / numerique | numérique, souveraineté numérique, révolution numérique |
| 10 | 78 | Economia social y solidaria | économie sociale, sociale solidaire, utilité sociale |
| 11 | 76 | Critica politica / republica / outre-mer | défi politique, ruine économique, démagogique, république |
| 12 | 74 | Igualdad mujeres-hombres | égalité femmes, droits femmes, libertés femmes |
| 13 | 53 | Maritimo / outre-mer | océans, économie mer, ports français, maritime |
| 14 | 51 | Asilo e inmigracion | demandes asile, droit asile, immigration, migrants |
| 15 | 41 | Pleno empleo / poder adquisitivo (slogan-y) | agir pouvoir, contrat, plein-emploi, laïcité |
| 16 | 36 | Lucha contra el terrorismo | contre terrorisme, antiterroriste, terroristes djihadistes |
| 17 | 36 | Justicia / prisiones / penas | peines plancher, prison, places prison, recidiviste |
| 18 | 32 | Lemas de campaña (texto programatico) | gagnerons, sommes prêts, sommes capables |
| 19 | 28 | "Aucune fatalite" / lemas | aucune fatalité, ruralite, vie rien |
| 20 | 21 | Energia nuclear / disuasion | nucléaire, dissuasion nucléaire, mix énergétique |
| 21 | 20 | Reduccion del empleo publico | supprimerons emplois publics, réduirons nombre |
| 22 | 17 | TPE-PME | tpe, plan tpe, tpe pme, simplification |
| 23 | 16 | Deporte | sport, fédérations sportives, pratique sportive |

### Amendements (2 575 enmiendas, 24 topicos, 656 outliers)

Esta tabla corresponde a la corrida con el filtro `>= 10 palabras` y el manejo correcto de NaN en la concatenacion `dispositif + expose_sommaire`. La version anterior tenia un topico espureo "nan nan" (138 docs) que aqui ya no aparece; la tematica sustantiva queda mejor resuelta: el bloque sanitario/salud se desdobla en tres topicos distintos (salud-acceso, crisis sanitaria/estado de urgencia, COVID-vacunacion).

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 222 | Fiscalidad / impuestos | impôts amendement, général impôts, fiscale, impôt, taxe additionnelle |
| 1 | 187 | Vivienda / construccion | logement, logements, construction habitation, logements sociaux, immobilier |
| 2 | 153 | Procedimiento penal / prision | ans emprisonnement, procédure pénale, peines, pénale, emprisonnement |
| 3 | 119 | Derecho del trabajo / representacion asalariados | administrateurs salariés, représentant salariés, employeurs, salarié |
| 4 | 114 | Reforma de jubilaciones | réformes retraites, système retraites, régime retraite, retraite universel |
| 5 | 111 | Alimentacion / pesca / rural | denrées alimentaires, rural pêche, pêche maritime, produits agricoles |
| 6 | 99 | Educacion / autoridad parental | autorité parentale, matière éducation, pédagogiques, établissements enseignement |
| 7 | 88 | Salud / medicos / acceso a cuidados | médecins généralistes, santé publique, professionnels santé, assurance maladie |
| 8 | 82 | Carta del medio ambiente | charte environnement, environnementale, protection environnement |
| 9 | 73 | Financiamiento / presupuesto | financements, budgétaire, financement, budget, euros crédits |
| 10 | 64 | Inmigracion / extranjeros / asilo | immigration intégration, immigration, migrants, étrangers droit, droit asile |
| 11 | 63 | Mandato / forma del amendement (boilerplate) | amendement groupe, amendement propose, mandat député |
| 12 | 62 | Lemas politicos / represion | répression institutionnalisé, projet demandons, dévastateur amendement |
| 13 | 61 | Pedidos de informe (mecanismos parlamentarios) | rapport évalue, rapport évaluant, demande rapport, rapport information |
| 14 | 59 | Mecanismo "souligner/justifier" (formula) | texte amendement, amendement souligner, solennellement amendement, amendement justifie |
| 15 | 59 | Reforma constitucional | inscrire constitution, 24 constitution, suffrages exprimés, élections législatives |
| 16 | 58 | Mecanismo "suivants/sauf" (formula) | texte suivants, suivants sauf, deuxième, sauf accord |
| 17 | 48 | Crisis sanitaria / estado de urgencia | crise sanitaire, juillet 2022, urgence sanitaire, mai 2021, état urgence |
| 18 | 48 | COVID-19 / vacunacion | covid 19, résultat sérologique, schéma vaccinal, virus, couverture vaccinale |
| 19 | 41 | Transportes publicos | 1115 transports, transports publics, transport ferroviaire, transport routier |
| 20 | 31 | Discriminacion / federaciones deportivas | contre discriminations, er constitution, société mentionnée, fédérations sportives |
| 21 | 30 | Libertades digitales / neutralidad de la red | libertés numériques, privée numérique, neutralité internet, liberté expression |
| 22 | 24 | Reciclaje de plasticos | recyclage bouteilles, bouteilles plastique, bouteilles consommées, plastique usage |
| 23 | 23 | Prestaciones sociales / handicap | prestations familiales, compensation handicap, bénéficiaires, justice sociale |

### Lois (23 267 articulos, 24 topicos, 8 833 outliers)

El topico 0 sigue siendo dominante (~36% del corpus) por la formula recurrente "le rapport mentionne les mesures..." que sobrevive las stop-words. Los topicos 7, 10, 16 son boilerplate residual (cifras, tablas, nomenclatura). El resto si captura tematica sustantiva.

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 8 349 | Boilerplate de informes (residual) | rapport, mentionnés, mentionné, mesures |
| 1 | 1 201 | Fiscalidad intercomunal / colectividades territoriales | intercommunale fiscalité, public coopération, collectivités territoriales |
| 2 | 815 | Educacion / formacion profesional | enseignement, formation professionnelle, éducation, apprentis |
| 3 | 648 | Politica de desarrollo / solidaridad mundial | politique développement, développement solidaire, inégalités mondiales |
| 4 | 565 | Deficit / crisis / proyeccion presupuestaria | déficit, crise, 2020, 2024 |
| 5 | 275 | Renovacion energetica / construccion / vivienda | rénovation énergétique, construction habitation, production énergie |
| 6 | 265 | Ley PACTE 2019 | 2019 croissance, transformation entreprises, croissance transformation |
| 7 | 265 | Boilerplate fiscal (residual) | mentionnée 2e, réfaction mentionnée, engagements exprimés |
| 8 | 245 | Fiscalidad / tasa profesional | taxe professionnelle, fiscalité, etat profit |
| 9 | 238 | Elecciones / electoral | élections partielles, élections, électoral |
| 10 | 235 | Cifras y montos (residual) | colonne montant, 23 162, suivantes 000 |
| 11 | 210 | Promulgacion presidencial (formula) | président promulgue, visa président |
| 12 | 177 | Financiamiento / contribuciones / dependencia | 000 contribution, financement, dépenses solde |
| 13 | 171 | Asilo y derecho de los refugiados | demande asile, droit asile, protection réfugiés |
| 14 | 164 | Especialidades farmaceuticas / salud | spécialité pharmaceutique, prescription, chargés santé |
| 15 | 122 | Autopistas y rutas | autoroutes, autoroutes routes, voies transférées |
| 16 | 74 | Cifras presupuestarias (residual) | montant arrondi, conjoncturel mesures |
| 17 | 70 | Asiento del impuesto / imposicion | assiette impôt, imposition cas, droits organisme |
| 18 | 66 | Outre-mer / Pacifico | futuna, polynésie wallis, futuna, art 765 |
| 19 | 59 | Pension de reversion / jubilacion | retraite cas, pension réversion, retraite obligatoire |
| 20 | 57 | "France Services" / red de servicios | france services, services public, maisons services |
| 21 | 57 | Asociaciones / federaciones deportivas | sport statuts, association sportive, fédération sportive |
| 22 | 54 | Capacidad electrica (kw) | 000 kw, 750 kw, 500 kw |
| 23 | 52 | Controles aduaneros / argent liquide | argent liquide, contrôles argent, européen |

### Tweets (222 644 tweets, 24 topicos, 105 894 outliers)

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 15 662 | Guerra de Ucrania / Rusia | ukrainien, ukraine, peuple ukrainien, russie, guerre |
| 1 | 15 444 | Reuniones publicas / agenda local | réunion, assemblée nationale, rencontre, citoyens |
| 2 | 11 501 | Macron / presidencia | emmanuel macron, macron, françois bayrou, président |
| 3 | 11 104 | Juegos Olimpicos / deporte | jeux olympiques, olympique, champions, athlètes |
| 4 | 9 462 | Francia / France insoumise / elecciones europeas | france insoumise, françaises, élections européennes |
| 5 | 7 320 | Reforma de jubilaciones | réforme retraites, pensions, retraités, sécurité sociale |
| 6 | 6 190 | Fin de vida / cuidados paliativos / eutanasia | soins palliatifs, aide mourir, palliatifs, euthanasie |
| 7 | 5 855 | Mundo agricola / Salon de l'Agriculture | monde agricole, soutien agriculteurs, salon agriculture |
| 8 | 5 853 | Policia / inseguridad / acoso | contre harcèlement, policiers, police, violence |
| 9 | 5 472 | Politica energetica / transicion / nuclear | politique énergétique, transition énergétique, énergies renouvelables |
| 10 | 4 945 | Condolencias / homenajes / fallecimientos | sincères condoléances, hommage victimes, immense tristesse |
| 11 | 4 292 | Crisis de la vivienda | crise logement, logements sociaux, immobilier |
| 12 | 4 227 | Redes sociales / cybersecurite / 2024-2030 | 2024 2030, cybersécurité, interdiction réseaux sociaux |
| 13 | 3 053 | Derechos de las mujeres / 8M | droits femmes, féministes, égalité femmes, women |
| 14 | 1 849 | Vacunacion COVID-19 | vaccinationcovid, campagne vaccination, stratégie vaccinale |
| 15 | 1 024 | Saludos de fin de año | belle année, bonne année, joyeux noël |
| 16 | 969 | Anuncios de invitaciones a medios | invité serai, 8h30 invité, serai invité |
| 17 | 847 | Bomberos | hommage pompiers, pompiers volontaires, sapeurs pompiers |
| 18 | 574 | Venezuela / Maduro | peuple vénézuélien, venezuela, débarrassé dictature |
| 19 | 370 | China / diplomacia | ambassadeur chine, china, régime chinois |
| 20 | 324 | Iglesia catolica / pope | pape américain, nouveau pape, pontificat |
| 21 | 175 | Autismo (sensibilizacion) | sensibilisation autisme, semaine autisme, personnes autistes |
| 22 | 134 | Afganistan / talibanes | situation afghanistan, kaboul afghanistan, afghanes talibans |
| 23 | 104 | Cannabis / despenalizacion | cannabis dépénalisation, légaliser cannabis, légalisation cannabis |

Visualizacion adicional `viz_topics_per_political_group.html`: prevalencia tematica por grupo parlamentario (LAREM, FI, LR, RN/NI, MODEM, EDS, GDR, SOC, etc).

### Interventions (338 192 intervenciones, 24 topicos, 165 439 outliers)

Es el corpus mas grande y el unico que toma horas (~40 min en CPU M-series). Los topicos 0, 1, 9, 11, 17 son procedural-residual (formula de votos, llamadas al reglamento, "renvoyée prochaine", etc). El resto si captura tematica sustantiva del trabajo legislativo.

| # | Docs | Tema | Top words |
|---:|---:|---|---|
| 0 | 40 135 | Discurso politico generico (procedural-residual) | parlementaire, parlementaires, parce, politique |
| 1 | 31 080 | Comision / avis / saisie (procedural-residual) | républicains demande, commission suis, avis commission |
| 2 | 24 483 | Union Europea / Europa | union européenne, europe, européens, gouvernement |
| 3 | 22 754 | Reforma / presupuesto / gobierno | réforme, gouvernement, budget, politique |
| 4 | 15 125 | Sistema de salud / sanitario | système santé, urgence sanitaire, professionnels santé |
| 5 | 8 128 | Educacion / escuela | directeurs école, scolaires, écoles |
| 6 | 3 493 | Desempleo / asuransa-chomage | chômage, chômeurs, demandeurs emploi, assurance chômage |
| 7 | 3 482 | Transporte ferroviario | ferroviaires, ferroviaire, transports |
| 8 | 3 455 | Derechos de las mujeres / igualdad | droits femmes, égalité femmes, sages femmes, sexistes |
| 9 | 3 046 | Resultados de votos (procedural-residual) | nombre votants, suffrages exprimés |
| 10 | 2 713 | Agua / agencias del agua | agences eau, gestion eau, accès eau, eau assainissement |
| 11 | 2 685 | "Renvoyée a la prochaine seance" (procedural) | prochaine, renvoyée prochaine, prochaine demande |
| 12 | 2 547 | Medios / audiovisual publico | médias, journalistes, audiovisuel public |
| 13 | 2 047 | Deporte / asociaciones deportivas | associations sportives, ministère sports, clubs sportifs |
| 14 | 1 538 | Notre-Dame / patrimonio | restauration cathédrale, cathédrale dame, église |
| 15 | 1 122 | Politica exterior / Siria / Argelia | syrie, algérie, affaires étrangères, armées |
| 16 | 1 094 | Bioetica / embriones | embryon humain, souches embryonnaires, lois bioéthique |
| 17 | 1 040 | Llamadas al reglamento (procedural) | rappels règlement, rappel règlement, règles |
| 18 | 940 | Maltrato animal / proteccion animal | maltraitance animale, animal compagnie, protection animale |
| 19 | 595 | Lengua / lenguas regionales | langue république, langues régionales, langue régionale |
| 20 | 543 | Constitucional / articulos / poursuivi | articles constitutionnelle, poursuivi articles |
| 21 | 294 | COVID / mascarillas | acheter masques, masque obligatoire, porter masque |
| 22 | 253 | Cifras / "milliards d'euros" (residual) | milliards euros, million euros |
| 23 | 161 | Mencion personal a Caroline Fiat (residual) | caroline fiat, fiat caroline |

Visualizacion adicional `viz_topics_per_political_group.html`: prevalencia tematica por grupo parlamentario.

## Reproducir las corridas

Cada fuente tiene su `run.py` autocontenido. Las dependencias estan en `requirements.txt`.

Activar entorno (usa el python del sistema con pip user-install) y correr cualquier fuente:

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

`-u` fuerza salida unbuffered (asi `tee` muestra el avance en vivo). No hace falta `nohup` ni `&`: si necesitas cerrar la terminal usa `screen`/`tmux`.

## Notas sobre el runner

El nucleo esta en `common/bertopic_runner.py`. Dos detalles importantes que cambiaron en esta version y que conviene tener presentes si se reentrenan los modelos:

1. **`nr_topics="auto"` esta desactivado a nivel BERTopic cuando hay `target_nr_topics`.** El auto-reduce iterativo de BERTopic recalcula c-TF-IDF despues de cada merge sobre topicos-agregados, y si en alguna iteracion el numero de topicos cae por debajo del `min_df` configurado (`30` para tweets, `50` para interventions), sklearn lanza `After pruning, no terms remain` o `max_df < min_df`. La estrategia ahora es: dejar que HDBSCAN saque sus topicos crudos (~150-180), saltarse el auto-reduce interno y bajar a 25 con una unica reduccion manual al final.

2. **Vectorizer parcheado durante la reduccion final.** En la fase de `reduce_topics`, BERTopic recomputa c-TF-IDF sobre un documento agregado por topico. Para que un `min_df=30` o `50` no rompa cuando solo hay 25 topicos, el runner swappea momentaneamente el `CountVectorizer` por uno con `min_df=1`. La parte IDF de c-TF-IDF sigue despriorizando terminos compartidos entre topicos, asi que los terminos finales no quedan ruidosos.

El resto (UMAP, HDBSCAN, KeyBERT representation, visualizaciones, exportacion) es estandar.

## Limitaciones conocidas

- **Outliers altos**. Tweets e interventions tienen ~48% de docs en `-1`. Es esperable: HDBSCAN es estricto y el corpus tiene mucho discurso ad-hoc. Si se quisiera reducir, habria que bajar `min_topic_size`, pero la cantidad de micro-topicos crece.
- **Topicos residuales en lois e interventions**. La estructura formularia de los textos legales y procedurales del hemiciclo deja topicos que aun con stop-words extendidas se llenan de boilerplate. Estan listados explicitamente arriba para que el lector los descarte.
- **Determinismo limitado**. UMAP y HDBSCAN tienen semilla por defecto; los runs son razonablemente reproducibles pero pueden variar +/- algunos topicos crudos entre corridas. La reduccion final a 25 estabiliza la salida.
- **`paraphrase-multilingual-MiniLM-L12-v2`** es un modelo chico (118 MB) elegido por velocidad. Modelos mas grandes (e.g. `xlm-roberta-base` o `LaBSE`) probablemente captarian mejor matices ideologicos, a costa de varias horas mas de embedding.

## Estructura del modulo

```
bertopic_analysis/
├── README.md                       # este archivo
├── requirements.txt                # bertopic, sentence-transformers, umap-learn, hdbscan, plotly, pandas
├── common/
│   ├── __init__.py
│   └── bertopic_runner.py          # pipeline reutilizable (run_bertopic)
├── manifestos/
│   ├── run.py                      # carga manifestos_clean.csv y llama a run_bertopic
│   └── results/                    # outputs (24 topicos, ver arriba)
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

Cada `run.py` es un script corto que: carga el CSV de la fuente, aplica el filtrado especifico (palabras minimas, regex procedural, etc), arma la lista de `docs` y la lista de `classes`, y delega en `common.bertopic_runner.run_bertopic(...)` con los parametros propios de la fuente.

