# Resultados — BERTopic sobre manifiestos electorales (2017)

Análisis de topic modeling sobre los manifiestos de los partidos franceses para las elecciones legislativas 2017, codificados por el Manifesto Project (MARPOR) a nivel de quasi-sentence *(cuasi-oración)*.

Modelo: BERTopic con embeddings `paraphrase-multilingual-MiniLM-L12-v2`, representación refinada con KeyBERTInspired, y stopwords en francés + términos genéricos de país (france, français, française, pays, république *(Francia, franceses, francesa, país, república)*).

---

## Resumen general

- **Quasi-sentences analizadas:** 3,715 (de 3,801, tras filtro >20 caracteres)
- **Outliers** (sin tema asignado): 1,124 (30%)
- **Temas detectados:** 37
- **Partidos representados:** EELV, FN, LFI, LR, LREM, MoDem, PCF, PRG, PS, UDI

---

## Temas detectados

| Topic | Docs | Palabras clave (francés) | Traducción al español |
|------:|-----:|--------------------------|----------------------|
| 0 | 595 | politiques publiques, parlement, services publics, gouvernement, citoyens, démocratie | políticas públicas, parlamento, servicios públicos, gobierno, ciudadanos, democracia |
| 1 | 242 | salariés, salarié, contrat travail, emploi, travailleurs, entreprises | asalariados, asalariado, contrato de trabajo, empleo, trabajadores, empresas |
| 2 | 188 | union européenne, europe, européens, niveau européen, euro, démocratique | unión europea, Europa, europeos, a nivel europeo, euro, democrático |
| 3 | 167 | enseignement supérieur, éducation, scolaires, écoles, universités, lycées | educación superior, educación, escolares, escuelas, universidades, liceos |
| 4 | 159 | europe, libertés, majorité, droite centre, identité nationale, conquête | Europa, libertades, mayoría, derecha centro, identidad nacional, conquista |
| 5 | 127 | agriculture, agricole, écologique, environnement, produire | agricultura, agrícola, ecológico, medio ambiente, producir |
| 6 | 125 | évasion fiscale, fiscalité, impôts, taxation, crédit impôt | evasión fiscal, fiscalidad, impuestos, tributación, crédito fiscal |
| 7 | 101 | politique santé, santé, professionnels santé, soins, hôpitaux, prévention | política de salud, salud, profesionales de salud, cuidados, hospitales, prevención |
| 8 | 78 | hommes femmes, égalité réelle, discriminations, égalité | hombres mujeres, igualdad real, discriminaciones, igualdad |
| 9 | 77 | faut changer, approche, enjeux, confiance, agir, responsabilité | hay que cambiar, enfoque, desafíos, confianza, actuar, responsabilidad |
| 10 | 55 | numériques, numérique, technologique, internet, plateformes, réseaux | digitales, digital, tecnológico, internet, plataformas, redes |
| 11 | 50 | immigration, asile, condamnés, demandeurs | inmigración, asilo, condenados, solicitantes |
| 12 | 46 | océans, économie mer, maritime, ultra marins, pêcheurs | océanos, economía marítima, marítimo, ultramarinos, pescadores |
| 13 | 45 | langue, étrangères, culturel, internationaux | lengua, extranjeras, cultural, internacionales |
| 14 | 44 | modèle social, justice sociale, protection sociale, partenaires sociaux | modelo social, justicia social, protección social, interlocutores sociales |
| 15 | 41 | petites retraites, retraite, durée vie, âge, seuil pauvreté | pensiones pequeñas, jubilación, esperanza de vida, edad, umbral de pobreza |
| 16 | 38 | vie, laïcité, mise place, établir | vida, laicidad, puesta en marcha, establecer |
| 17 | 37 | énergies renouvelables, transition énergétique, précarité énergétique | energías renovables, transición energética, precariedad energética |
| 18 | 34 | quotient familial, familles, famille, adoption, parents, aides sociales | cociente familiar, familias, familia, adopción, padres, ayudas sociales |
| 19 | 34 | aucune, rien, aucun, pourtant | ninguna, nada, ningún, sin embargo |
| 20 | 33 | culture, culturel, création, patrimoine | cultura, cultural, creación, patrimonio |
| 21 | 33 | contre terrorisme, terrorisme, sécurité intérieure, surveillance, menace | contra el terrorismo, terrorismo, seguridad interior, vigilancia, amenaza |
| 22 | 27 | mobilité, transports, transport, infrastructures, télétravail | movilidad, transportes, transporte, infraestructuras, teletrabajo |
| 23 | 24 | temps travail, temps partiel, travailler, durée | tiempo de trabajo, tiempo parcial, trabajar, duración |
| 24 | 20 | public, télévision, audiovisuel, service public, interdire | público, televisión, audiovisual, servicio público, prohibir |
| 25 | 19 | nucléaire, politique environnementale, énergies renouvelables, gaz effet | nuclear, política medioambiental, energías renovables, gas de efecto |
| 26 | 17 | déficits, déficit, évasion fiscale, budgétaire, budget | déficits, déficit, evasión fiscal, presupuestario, presupuesto |
| 27 | 17 | handicap, situation handicap, santé, accès emploi | discapacidad, situación de discapacidad, salud, acceso al empleo |
| 28 | 16 | sport, équipe, défendre, professionnel | deporte, equipo, defender, profesional |
| 29 | 16 | jeunesse, jeunes, politiques publiques, 18 ans, avenir | juventud, jóvenes, políticas públicas, 18 años, futuro |
| 30 | 15 | réduire, supprimerons, diminuerons, baisserons, baisse | reducir, suprimiremos, disminuiremos, bajaremos, baja |
| 31 | 14 | tpe, tpe pme, petites entreprises, financement, administratif | microempresas, pymes, pequeñas empresas, financiamiento, administrativo |
| 32 | 14 | énergies renouvelables, précarité énergétique, gaz effet, 2030 | energías renovables, precariedad energética, gas de efecto, 2030 |
| 33 | 12 | sécurité sociale, retraites, impôts, crédit impôt | seguridad social, jubilaciones, impuestos, crédito fiscal |
| 34 | 11 | taxation, politique prévention, addictions, sanctions, libertés | tributación, política de prevención, adicciones, sanciones, libertades |
| 35 | 10 | souffrance travail, contre chômage, maladies professionnelles | sufrimiento laboral, contra el desempleo, enfermedades profesionales |
| 36 | 10 | pauvreté, centaines milliers, millions, 500 euros | pobreza, cientos de miles, millones, 500 euros |

---

## Principales insights

1. **Gobernanza y servicios públicos** es el tema más grande (Topic 0, 595 docs): politiques publiques, parlement, services publics, citoyens *(políticas públicas, parlamento, servicios públicos, ciudadanos)*. Es el marco general de las propuestas de todos los partidos.

2. **Empleo y relaciones laborales** (Topics 1 y 23, ~266 docs): salariés, contrat travail, emploi, temps travail *(asalariados, contrato de trabajo, empleo, tiempo de trabajo)*. Es el segundo eje temático más importante.

3. **Europa** tiene dos caras en los manifiestos:
   - Topic 2: visión europeísta — union européenne, européens, démocratique *(unión europea, europeos, democrático)*
   - Topic 4: visión identitaria/soberanista — libertés, identité nationale, droite centre *(libertades, identidad nacional, derecha centro)*

4. **Educación** (Topic 3, 167 docs): enseignement supérieur, éducation, écoles, universités *(educación superior, educación, escuelas, universidades)* — tema sustantivo y transversal.

5. **Agricultura y ecología** (Topics 5, 17, 25, 32, ~207 docs sumados): agriculture, écologique, énergies renouvelables, transition énergétique, nucléaire *(agricultura, ecológico, energías renovables, transición energética, nuclear)*. La dimensión ambiental es fuerte.

6. **Fiscalidad** (Topics 6 y 26, 142 docs): évasion fiscale, impôts, déficits, budgétaire *(evasión fiscal, impuestos, déficits, presupuestario)*.

7. **Salud** (Topic 7): politique santé, hôpitaux, prévention *(política de salud, hospitales, prevención)*.

8. **Igualdad de género** (Topic 8): hommes femmes, égalité réelle, discriminations *(hombres mujeres, igualdad real, discriminaciones)*.

9. **Inmigración y asilo** (Topic 11): immigration, asile, demandeurs *(inmigración, asilo, solicitantes)*.

---

## Palabras clave por partido (top 5 cada uno)

| Partido | Top 5 palabras (francés) | Traducción |
|---------|--------------------------|------------|
| **EELV** (ecologistas) | contre *(contra)*, vive *(viva)*, renforcer *(reforzar)*, lutter *(luchar)*, vie *(vida)* | Lucha, combate, vida — discurso de militancia ecologista |
| **FN** (extrema derecha) | contre *(contra)*, afin *(a fin de)*, ans *(años)*, créer *(crear)*, état *(estado)* | Estado, soberanía, oposición |
| **LFI** (izquierda radical) | mesures *(medidas)*, proposons *(proponemos)*, réaliser *(realizar)*, suivantes *(siguientes)*, contre *(contra)* | Programa muy estructurado ("proponemos realizar las siguientes medidas") |
| **LR** (derecha) | voulons *(queremos)*, travail *(trabajo)*, politique *(política)*, devons *(debemos)*, contrat *(contrato)* | Voluntarismo, trabajo, contrato social |
| **LREM** (centro/macronismo) | travail *(trabajo)*, seront *(serán)*, euros, créerons *(crearemos)*, europe *(Europa)* | Promesas concretas, Europa, inversión |
| **MoDem** (centro) | créer *(crear)*, politique *(política)*, nationale *(nacional)*, vie *(vida)*, loi *(ley)* | Creación, legislación |
| **PCF** (comunistas) | contre *(contra)*, humain *(humano)*, macron | Oposición, humanismo |
| **PRG** (radicales) | doit *(debe)*, politique *(política)*, moyens *(medios)*, entreprises *(empresas)*, entreprise *(empresa)* | Deber, medios, empresas |
| **PS** (socialistas) | 000 *(cifras)*, loi *(ley)*, défendre *(defender)*, sociale *(social)*, transition *(transición)* | Cifras concretas, defensa social |
| **UDI** (centro-derecha) | voulons *(queremos)*, travail *(trabajo)*, politique *(política)*, devons *(debemos)*, contrat *(contrato)* | Idéntico a LR (compartían manifiesto) |

**Observación clave:** LR y UDI comparten las mismas top-5 palabras — esto confirma que presentaron un manifiesto conjunto para las legislativas 2017.

---

## Temas dominantes por partido

| Partido | Topic principal | Segundo tema | Tercer tema |
|---------|----------------|-------------|-------------|
| **LFI** | T0 — gobernanza (181 docs) | T1 — empleo (72) | T5 — agricultura (59) |
| **PRG** | T0 — gobernanza (113) | T2 — UE europeísta (57) | T1 — empleo (42) |
| **MoDem** | T0 — gobernanza (88) | T3 — educación (46) | T2 — UE europeísta (25) |
| **LREM** | T0 — gobernanza (53) | T1 — empleo (26) | T9 — cambio/confianza (23) |
| **FN** | T0 — gobernanza (41) | T6 — fiscalidad (21) | T1 — empleo (17) |
| **EELV** | T0 — gobernanza (36) | T1 — empleo (16) | T4 — identidad/libertades (16) |
| **LR/UDI** | T0 — gobernanza (32–33) | T4 — identidad/libertades (25) | T1 — empleo (15–16) |
| **PCF** | T0 — gobernanza (10) | T1 — empleo (6) | T2 — UE (2) |
| **PS** | T0 — gobernanza (8) | T1 — empleo (7) | T2 — UE (5) |

**LFI domina en volumen** (manifiesto muy extenso, "L'Avenir en commun" *(El futuro en común)*). **FN destaca en fiscalidad** (évasion fiscale, impôts *(evasión fiscal, impuestos)*). **MoDem** es el que más destaca en **educación**. **LR/UDI y FN** comparten el foco en **identidad y libertades** (Topic 4).

---

## Top 30 palabras más frecuentes (sin stopwords, todos los partidos)

| # | Palabra | Traducción | Frecuencia |
|--:|---------|------------|----------:|
| 1 | doit | debe | 196 |
| 2 | contre | contra | 184 |
| 3 | politique | política | 165 |
| 4 | travail | trabajo | 140 |
| 5 | entreprises | empresas | 138 |
| 6 | mesures | medidas | 123 |
| 7 | vie | vida | 119 |
| 8 | ans | años | 118 |
| 9 | droit | derecho | 117 |
| 10 | créer | crear | 112 |
| 11 | sociale | social | 104 |
| 12 | plan | plan | 95 |
| 13 | sécurité | seguridad | 94 |
| 14 | mettre | poner/implementar | 92 |
| 15 | emploi | empleo | 92 |
| 16 | publique | pública | 90 |
| 17 | loi | ley | 90 |
| 18 | entreprise | empresa | 90 |
| 19 | état | estado | 89 |
| 20 | santé | salud | 89 |
| 21 | proposons | proponemos | 89 |
| 22 | europe | Europa | 87 |
| 23 | publics | públicos | 87 |
| 24 | moyens | medios | 82 |
| 25 | développement | desarrollo | 78 |
| 26 | droits | derechos | 78 |
| 27 | salariés | asalariados | 77 |
| 28 | renforcer | reforzar | 75 |
| 29 | garantir | garantizar | 74 |
| 30 | femmes | mujeres | 71 |

---

## Archivos de datos generados

| Archivo | Descripción |
|---------|-------------|
| `topic_info.csv` | Tabla completa de los 37 temas |
| `top_words_per_topic.csv` | Palabras clave con puntaje c-TF-IDF por tema |
| `document_topics.csv` | Cada quasi-sentence *(cuasi-oración)* con su tema y partido |
| `topics_per_party.csv` | Distribución de temas por partido |
| `global_word_frequency.csv` | Top 200 palabras más frecuentes |
| `word_frequency_per_party.csv` | Top 50 palabras por partido |
| `viz_*.html` | Visualizaciones interactivas *(abrir en navegador)* |
