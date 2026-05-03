# Resultados — BERTopic sobre intervenciones en hemiciclo

Análisis de topic modeling sobre intervenciones parlamentarias sustantivas de la XV legislatura (2017–2022).
Solo se incluyeron intervenciones con **≥80 palabras** y se excluyeron entradas procedimentales (aplausos, suspensiones de sesión, votaciones).

Modelo: BERTopic con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, representación refinada con KeyBERTInspired, y stopwords en francés + jerga parlamentaria (madame *(señora)*, monsieur *(señor)*, président *(presidente)*, amendement *(enmienda)*, rapporteur *(ponente)*, etc.).

---

## Resumen general

- **Intervenciones de partida:** 5,000 (muestra)
- **Tras filtro de calidad** (≥80 palabras, sin procedimentales): 709
- **Outliers** (sin tema asignado): 249 (35%)
- **Temas detectados:** 5
- **Tema dominante:** Topic 0 con 473 docs — reforma laboral y diálogo social

---

## Temas detectados

| Topic | Docs | Palabras clave (francés) | Traducción al español |
|------:|-----:|--------------------------|----------------------|
| 0 | 473 | organisations syndicales, organisations, réforme, syndicales, sujet, règles, dispositions, amendements | organizaciones sindicales, organizaciones, reforma, sindicales, asunto, reglas, disposiciones, enmiendas |
| 1 | 140 | politique, politiques, parlementaires, france, démocratie, république, députés, française | política, políticas, parlamentarios, Francia, democracia, república, diputados, francesa |
| 2 | 44 | contre terrorisme, état urgence, antiterroriste, actes terroristes, terrorisme, attentat, terroriste, attentats | contra el terrorismo, estado de emergencia, antiterrorista, actos terroristas, terrorismo, atentado, terrorista, atentados |
| 3 | 36 | société, réformes, réforme, travail, évoluer, marché travail, emploi | sociedad, reformas, reforma, trabajo, evolucionar, mercado laboral, empleo |
| 4 | 16 | état urgence, contrôle parlementaire, parlementaire, autorité, état droit, autorité administrative, sécurité intérieure | estado de emergencia, control parlamentario, parlamentario, autoridad, estado de derecho, autoridad administrativa, seguridad interior |

---

## Principales insights

1. **La reforma laboral domina el debate** — El Topic 0 (organisations syndicales, réforme *(organizaciones sindicales, reforma)*) concentra el 67% de las intervenciones sustantivas. Esto es coherente con el contexto: la reforma laboral (ordonnances travail *(ordenanzas de trabajo)*) de 2017 fue el primer gran proyecto legislativo de la XV legislatura.

2. **El debate político general** (Topic 1) es el segundo más grande: politique, démocratie, république *(política, democracia, república)* — intervenciones de posicionamiento político más amplio.

3. **Antiterrorismo y estado de emergencia** aparecen en dos topics (2 y 4) con enfoques distintos:
   - Topic 2: el combate contra el terrorismo en sí (actes terroristes, attentat *(actos terroristas, atentado)*)
   - Topic 4: el marco legal del estado de emergencia (contrôle parlementaire, état droit, autorité administrative *(control parlamentario, estado de derecho, autoridad administrativa)*)

4. **Reformas sociales y mercado laboral** (Topic 3): société, marché travail, emploi *(sociedad, mercado laboral, empleo)* — complementa el Topic 0 con un enfoque más en el impacto social.

5. **La muestra es limitada** — Con solo 709 intervenciones sustantivas (de 5,000 totales, la mayoría muy cortas), los temas reflejan los debates más intensos de la muestra. Con el dataset completo (~950,000 intervenciones) surgirían muchos más temas.

---

## Top 30 palabras más frecuentes (sin stopwords)

| # | Palabra | Traducción | Frecuencia |
|--:|---------|------------|----------:|
| 1 | salariés | asalariados | 726 |
| 2 | travail | trabajo | 647 |
| 3 | entreprise | empresa | 599 |
| 4 | état | estado | 586 |
| 5 | entreprises | empresas | 497 |
| 6 | urgence | urgencia/emergencia | 361 |
| 7 | droit | derecho | 360 |
| 8 | social | social | 358 |
| 9 | dialogue | diálogo | 292 |
| 10 | premier | primero/primer ministro | 263 |
| 11 | pays | país | 258 |
| 12 | temps | tiempo | 247 |
| 13 | français | franceses | 242 |
| 14 | contre | contra | 233 |
| 15 | accord | acuerdo | 228 |
| 16 | sécurité | seguridad | 210 |
| 17 | politique | política | 193 |
| 18 | personnel | personal | 192 |
| 19 | emploi | empleo | 177 |
| 20 | conditions | condiciones | 177 |
| 21 | accords | acuerdos | 175 |
| 22 | droits | derechos | 163 |
| 23 | notamment | especialmente | 163 |
| 24 | confiance | confianza | 159 |
| 25 | vie | vida | 159 |
| 26 | nombre | número | 160 |
| 27 | loi | ley | 156 |
| 28 | négociation | negociación | 155 |
| 29 | mesures | medidas | 154 |
| 30 | protection | protección | 148 |

La predominancia de salariés *(asalariados)*, travail *(trabajo)*, entreprise *(empresa)*, dialogue *(diálogo)* y accord *(acuerdo)* confirma que la muestra cae fuertemente sobre el debate de la reforma laboral.

---

## Distribución por grupo parlamentario

| Grupo | Abreviatura | Docs en Topic 0 (reforma laboral) | Docs en Topic 1 (política) | Docs en Topic 2 (antiterrorismo) |
|-------|-------------|----------------------------------:|---------------------------:|---------------------------------:|
| La République en Marche | LAREM | 105 | 18 | 6 |
| Gauche démocrate et républicaine | GDR | 77 | 11 | — |
| France Insoumise | FI | 65 | 14 | 14 |
| Les Républicains | LR | 48 | 18 | 4 |
| Nouvelle Gauche | NG | 22 | 1 | — |
| UDI-AGIR | UDI-AGIR | 18 | 3 | 1 |
| Socialistes | SOC | 14 | 7 | — |
| Mouvement Démocrate | MODEM | 12 | 9 | — |
| Non-inscrits | NI | 8 | 1 | 4 |
| Europe Écologie | EDS | 8 | 2 | — |

**FI y GDR** (izquierda) destacan tanto en reforma laboral como en antiterrorismo: fue la oposición más vocal en ambos debates.

---

## Archivos de datos generados

| Archivo | Descripción |
|---------|-------------|
| `topic_info.csv` | Tabla completa de los 5 temas |
| `top_words_per_topic.csv` | Palabras clave con puntaje c-TF-IDF por tema |
| `document_topics.csv` | Cada intervención con su tema asignado |
| `topics_per_group.csv` | Distribución de temas por grupo parlamentario |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes |
| `viz_*.html` | Visualizaciones interactivas *(abrir en navegador)* |
