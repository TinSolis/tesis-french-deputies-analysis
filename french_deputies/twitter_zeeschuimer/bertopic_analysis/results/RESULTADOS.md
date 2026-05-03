# Resultados — BERTopic sobre tweets de diputados franceses

Análisis de topic modeling sobre **50,000 tweets** (muestreados de 231,890 válidos, de un total de 528,530).
Modelo: BERTopic con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, representación refinada con KeyBERTInspired, y stopwords en francés + Twitter (URLs, RT, menciones).

---

## Resumen general

- **Documentos analizados:** 50,000 tweets
- **Outliers** (sin tema asignado): 24,034 (48%) — típico en textos cortos como tweets
- **Temas detectados:** 32
- **Tema dominante:** Topic 0 con 20,514 docs — discurso político general

---

## Temas detectados

| Topic | Docs | Palabras clave (francés) | Traducción al español |
|------:|-----:|--------------------------|----------------------|
| 0 | 20,514 | politique, france, démocratie, europe, paris, française, européenne, république | política, Francia, democracia, Europa, París, francesa, europea, república |
| 1 | 1,449 | enfants, jeunes, familles, parents, jeune, société | niños, jóvenes, familias, padres, joven, sociedad |
| 2 | 1,160 | eau, environnement, durable, urgence, avenir, solutions | agua, medio ambiente, sostenible, urgencia, futuro, soluciones |
| 3 | 354 | prévention, sanitaire, santé, responsabilité, lutte contre | prevención, sanitario, salud, responsabilidad, lucha contra |
| 4 | 342 | outre mer, monde, enjeux, international, conférence | ultramar, mundo, desafíos, internacional, conferencia |
| 5 | 287 | merci, urgence, soir, salue, honneur, député | gracias, urgencia, tarde, saludo, honor, diputado |
| 6 | 239 | défense, protection, sécurité, protéger, forces, mobilisés | defensa, protección, seguridad, proteger, fuerzas, movilizados |
| 7 | 170 | nationale, nation, enjeux, proposition, gouvernement | nacional, nación, desafíos, propuesta, gobierno |
| 8 | 104 | 2026, 2025, 2022, 2024, 2021 | (fechas — agrupamiento temporal) |
| 9 | 103 | justice, peine, dignité, liberté, mort, défendre | justicia, pena, dignidad, libertad, muerte, defender |
| 10 | 101 | travail, travailler, engagé, professionnels, créer | trabajo, trabajar, comprometido, profesionales, crear |
| 11 | 94 | femmes, soutenir, soutien, santé, prévention | mujeres, apoyar, apoyo, salud, prevención |
| 12 | 88 | sanitaires, prévenir, bonne nouvelle | sanitarios, prevenir, buena noticia |
| 13 | 87 | assemblée nationale, rencontre, députée, ministre, visite | asamblea nacional, encuentro, diputada, ministro, visita |
| 14 | 79 | projet loi, proposition loi, environnement, produits | proyecto de ley, proposición de ley, medio ambiente, productos |
| 15 | 75 | coup, politiques, trump, président, europe, défendre | golpe, políticas, Trump, presidente, Europa, defender |
| 16 | 71 | environnement, préserver, protéger, rapport, essentiel | medio ambiente, preservar, proteger, informe, esencial |
| 17 | 68 | événement, écoute, montre, retrouvez | evento, escucha, muestra, encuéntrennos |
| 18 | 65 | parlement, europe, européen, européenne | parlamento, Europa, europeo, europea |
| 19 | 41 | jours, loin, mois, combat, contre | días, lejos, meses, combate, contra |
| 20 | 41 | histoire, cérémonie, honneur, victimes, liberté | historia, ceremonia, honor, víctimas, libertad |
| 21 | 40 | paris, france, française, visite, libération, engagement | París, Francia, francesa, visita, liberación, compromiso |
| 22 | 40 | saint, vers, libération, respect, république | santo, hacia, liberación, respeto, república |
| 23 | 40 | entreprises, entreprise, stratégique, industrie, développement | empresas, empresa, estratégico, industria, desarrollo |
| 24 | 39 | enfants, soutenir, inauguration, journée, familles | niños, apoyar, inauguración, jornada, familias |
| 25 | 38 | europe, européenne, avenir, assemblée nationale, stratégique | Europa, europea, futuro, asamblea nacional, estratégico |
| 26 | 37 | démocratie, unanimité, débat, lutter contre, parlementaires | democracia, unanimidad, debate, luchar contra, parlamentarios |
| 27 | 37 | prévention, étude, dangereux, débat, enquête | prevención, estudio, peligroso, debate, encuesta |
| 28 | 35 | lâche, lettre, justice, peine, menace | cobarde, carta, justicia, pena, amenaza |
| 29 | 33 | proposition, avenir, stratégique, nécessaires, politique | propuesta, futuro, estratégico, necesarios, política |
| 30 | 33 | femmes, défendre, droits, politiques, protection | mujeres, defender, derechos, políticas, protección |
| 31 | 31 | alimentaire, initiative, priorité, public, produits | alimentario, iniciativa, prioridad, público, productos |
| 32 | 31 | femmes, prévention, liberté, santé | mujeres, prevención, libertad, salud |

---

## Principales insights

1. **El discurso político general domina** — El Topic 0 (politique, france, démocratie *(política, Francia, democracia)*) absorbe el 41% de los tweets. Es esperable: Twitter político tiende a un vocabulario genérico de posicionamiento.

2. **Infancia y familia** es el segundo tema más grande (Topic 1, 1,449 docs): enfants, jeunes, familles *(niños, jóvenes, familias)* — refleja un eje discursivo transversal.

3. **Medio ambiente** aparece con fuerza en varios topics (2, 14, 16): eau, environnement, durable, préserver *(agua, medio ambiente, sostenible, preservar)* — sumados representan ~1,300 tweets.

4. **Seguridad y defensa** (Topic 6): défense, protection, sécurité, forces *(defensa, protección, seguridad, fuerzas)* — tema clásico de la política francesa.

5. **Justicia y derechos** (Topics 9, 28): justice, peine, dignité, liberté *(justicia, pena, dignidad, libertad)* — discurso sobre el sistema judicial.

6. **Mujeres y derechos** cruzan varios topics (11, 30, 32): femmes, défendre, droits, égalité *(mujeres, defender, derechos, igualdad)*.

7. **Geopolítica y Europa** (Topics 15, 18, 25): parlement, europe, européen, trump *(parlamento, Europa, europeo, Trump)*.

---

## Top 30 palabras más frecuentes (sin stopwords)

| # | Palabra | Traducción | Frecuencia |
|--:|---------|------------|----------:|
| 1 | france | Francia | 4,577 |
| 2 | merci | gracias | 2,740 |
| 3 | contre | contra | 2,388 |
| 4 | ans | años | 2,100 |
| 5 | français | franceses | 2,025 |
| 6 | président | presidente | 2,002 |
| 7 | aujourd'hui | hoy | 1,992 |
| 8 | loi | ley | 1,985 |
| 9 | ministre | ministro | 1,868 |
| 10 | matin | mañana | 1,754 |
| 11 | soutien | apoyo | 1,735 |
| 12 | nationale | nacional | 1,648 |
| 13 | pays | país | 1,618 |
| 14 | politique | política | 1,538 |
| 15 | assemblée | asamblea | 1,517 |
| 16 | travail | trabajo | 1,504 |
| 17 | soir | tarde/noche | 1,490 |
| 18 | face | frente a | 1,388 |
| 19 | doit | debe | 1,382 |
| 20 | projet | proyecto | 1,349 |
| 21 | ensemble | juntos | 1,335 |
| 22 | ceux | aquellos | 1,331 |
| 23 | europe | Europa | 1,295 |
| 24 | vie | vida | 1,241 |
| 25 | république | república | 1,221 |
| 26 | gouvernement | gobierno | 1,217 |
| 27 | nouvelle | nueva | 1,138 |
| 28 | hier | ayer | 1,112 |
| 29 | faut | hay que | 1,109 |
| 30 | engagement | compromiso | 1,102 |

---

## Distribución por grupo parlamentario

Los tweets se distribuyen así entre los principales grupos de la Asamblea Nacional:

| Grupo | Abreviatura | Total tweets | Top 3 topics |
|-------|-------------|------------:|--------------|
| La République en Marche | LAREM | 25,585 | T0 (política general), T1 (infancia), T2 (medio ambiente) |
| Les Républicains | LR | 8,412 | T0, T1, T2 |
| Mouvement Démocrate | MODEM | 2,508 | T0, T1, T2 |
| Démocrate | DEM | 1,972 | T0, T1, T2 |
| Gauche démocrate et républicaine | GDR | 1,565 | T0, T2 (medio ambiente), T1 |
| Socialistes | SOC | 1,542 | T0, T1, T2 |
| France Insoumise | FI | 1,537 | T0, T1, T2 |
| Non-inscrits | NI | 1,385 | T0, T2, T3 (santé/salud) |

LAREM domina ampliamente (51% de los tweets), lo que refleja su mayoría parlamentaria en la XV legislatura.

---

## Archivos de datos generados

Los CSV y HTML que acompañan este resumen se regeneran ejecutando el script. Ver el README del directorio padre para instrucciones.

| Archivo | Descripción |
|---------|-------------|
| `topic_info.csv` | Tabla completa de los 32 temas |
| `top_words_per_topic.csv` | Palabras clave con puntaje c-TF-IDF por tema |
| `document_topics.csv` | Cada tweet con su tema asignado |
| `topics_per_group.csv` | Distribución de temas por grupo parlamentario |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes |
| `viz_barchart.html` | Gráfico de barras *(abrir en navegador)* |
| `viz_topics_map.html` | Mapa 2D de proximidad entre temas |
| `viz_heatmap.html` | Mapa de calor de similitud entre temas |
| `viz_hierarchy.html` | Dendrograma jerárquico |
| `viz_topics_per_group.html` | Temas por grupo parlamentario |
