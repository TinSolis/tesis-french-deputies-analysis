# Referencias

Papers, modelos y recursos que sostienen este trabajo, con un resumen muy breve de qué son y cómo los pienso usar en la tesis. Organizados por rol: (1) métodos y modelos que uso, (2) benchmarks externos para validación, (3) literatura teórica que enmarca las preguntas, (4) antecedentes en grafos de conocimiento parlamentario.

---

## 1. Métodos y modelos que uso

### MARPOR / Manifesto Project (esquema de codificación)
> Volkens, A., Bara, J., Budge, I., et al. *The Manifesto Project Dataset / Coding Handbook (mp v5)*. WZB Berlin. <https://manifestoproject.wzb.eu/coding_schemes/mp_v5>

- **Qué es.** La taxonomía estándar de la ciencia política comparada desde 1979 para clasificar contenido programático de partidos: 56 categorías agrupadas en 7 dominios. Para temas controversiales el posicionamiento está incorporado en la categoría (pares positive/negative).
- **Cómo lo uso.** Es el esquema de etiquetas de toda la clasificación supervisada. Todo el análisis de "qué tema y en qué dirección" se expresa en estas 56 categorías + 7 dominios.

### ManifestoBERTa (modelo de clasificación)
> Burst, T., Lehmann, P., Franzmann, S., et al. (2024). *manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1*. Manifesto Project. <https://huggingface.co/manifesto-project/manifestoberta-xlm-roberta-56policy-topics-sentence-2024-1-1>

- **Qué es.** Un `xlm-roberta-large` fine-tuneado sobre ~1.7 M quasi-oraciones del Manifesto Corpus (38 idiomas) anotadas a mano. Clasifica texto en las 56 categorías MARPOR.
- **Cómo lo uso.** Es el clasificador supervisado del proyecto (`manifestoberta_analysis/`). Lo aplico a los 5 corpus y valido su accuracy contra el ground truth humano de MARPOR sobre los manifiestos.

### BERTopic (topic modeling no supervisado)
> Grootendorst, M. (2022). *BERTopic: Neural topic modeling with a class-based TF-IDF procedure*. arXiv:2203.05794. <https://arxiv.org/abs/2203.05794>

- **Qué es.** Pipeline de topic modeling: embeddings → reducción dimensional (UMAP) → clustering (HDBSCAN) → representación de tópicos con c-TF-IDF.
- **Cómo lo uso.** Es el método exploratorio (`bertopic_analysis/`): descubre qué temáticas emergen de cada corpus sin esquema previo, como contraparte data-driven de ManifestoBERTa.

### Sentence-Transformers (embeddings multilingües)
> Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP. arXiv:1908.10084. <https://arxiv.org/abs/1908.10084>

- **Qué es.** El método detrás de `paraphrase-multilingual-MiniLM-L12-v2`, que mapea cada documento a un vector de 384 dimensiones conservando semántica multilingüe.
- **Cómo lo uso.** Genera los embeddings que alimentan a BERTopic. Modelo multilingüe para no perder la semántica del francés.

### KG-Gen (extracción de grafos de conocimiento)
> Mo, B., Yu, K., Kazdan, J., Cabezas, J., Mpala, P., Yu, L., Cundy, C., Kanatsoulis, C., & Koyejo, S. (2025). *KGGen: Extracting Knowledge Graphs from Plain Text with Language Models*. NeurIPS 2025. arXiv:2502.09956. <https://arxiv.org/abs/2502.09956>

- **Qué es.** Extractor de triples (sujeto, predicado, objeto) basado en LLMs, con un paso de clustering de entidades para reducir duplicados.
- **Cómo lo uso.** Lo probé sobre una muestra acotada de intervenciones (`kg-gen/`). Queda documentado como referencia experimental: los tiempos con modelos locales gratuitos lo hacen inviable sobre el corpus completo, así que no entra al pipeline principal.

---

## 2. Benchmarks externos para validación

### RILE (Right-Left score de MARPOR)
> Laver, M., & Budge, I. (1992). *Party Policy and Government Coalitions*. Palgrave Macmillan. (Índice RILE estándar del Manifesto Project.)

- **Qué es.** Un índice izquierda-derecha que se calcula sumando/restando familias de categorías MARPOR.
- **Cómo lo pienso usar.** Como referencia descriptiva para ubicar a los partidos en un eje izquierda-derecha. **Caveat (lo señaló Franziska):** RILE se construye con las mismas categorías MARPOR, así que correlacionar contra él no es validación *plenamente externa*, sino más bien de consistencia interna. Conviene presentarlo así y no sobrevenderlo.

### CHES — Chapel Hill Expert Survey
> Rovny, J., Polk, J., Bakker, R., Hooghe, L., Jolly, S., Marks, G., Steenbergen, M., & Vachudova, M. A. (2025). *The 2024 Chapel Hill Expert Survey on political party positioning in Europe: Twenty-five years of party positional data*. Electoral Studies 97. <https://doi.org/10.1016/j.electstud.2025.102981> — datos en <https://www.chesdata.eu/>

- **Qué es.** Encuesta de expertos sobre las posiciones de los partidos europeos (ideología, política, integración europea, etc.), con waves desde 1999.
- **Cómo lo pienso usar.** Como benchmark **genuinamente externo** (mecanismo distinto a MARPOR) contra el cual contrastar las posiciones que estimo de los partidos. Es la validación independiente que sugirió Franziska. **Caveat:** las posiciones de expertos pueden diferir de la comunicación real de los partidos.

---

## 3. Literatura teórica que enmarca las preguntas

### Comunicación de partidos por canal (Ivanusch 2024)
> Ivanusch, C. (2024). *Where do parties talk about what? Party issue salience across communication channels*. West European Politics. <https://doi.org/10.1080/01402382.2024.2322234>

- **Qué es.** Estudia cómo los partidos ajustan su agenda temática según el canal (discursos parlamentarios, comunicados, tweets de cuentas oficiales vs. de miembros individuales), usando BERT sobre Alemania, Austria y Suiza. Encuentra que la *salience* de cada tema depende de las características del canal (centralizado vs. descentralizado, pre-estructurado vs. libre).
- **Cómo lo pienso usar.** Es el marco teórico directo de mi comparación entre canales: justifica por qué un diputado dice cosas distintas en el manifiesto, el hemiciclo y Twitter. Lo recomendó Franziska.

### Disciplina y cohesión partidaria (línea de literatura)
> Líneas a revisar (confirmar cita exacta al citar): p. ej. Sieberer, U. (2006). *Party unity in parliamentary democracies: A comparative analysis*. Journal of Legislative Studies; Carey, J. M. (2007). *Competing Principals, Political Institutions, and Party Unity in Legislative Voting*. American Journal of Political Science.

- **Qué es.** Literatura sobre por qué y cuándo los diputados votan con su partido, y cómo se mide la cohesión/disciplina.
- **Cómo lo pienso usar.** Para enmarcar la parte de "¿qué diputados se desvían de la línea de su partido y en qué temas?" usando los votos nominales cruzados con las clasificaciones MARPOR. Franziska mencionó esta línea sin una cita puntual; estas son entradas canónicas para empezar a buscar.

---

## 4. Antecedentes en grafos de conocimiento parlamentario

### ParliamentSampo (Hyvönen et al. 2023)
> Hyvönen, E., et al. (2023). *Publishing and Using Parliamentary Linked Data on the Semantic Web: ParliamentSampo System for the Parliament of Finland*. Semantic Web Journal.

- **Qué es.** Sistema de datos enlazados (linked data) sobre el parlamento finlandés.
- **Cómo lo uso.** Antecedente que cito en `kg-gen/` para situar la idea de representar actividad parlamentaria como grafo.

### PAKT (Plenz et al. 2024)
> Plenz, M., et al. (2024). *PAKT: Perspectivized Argumentation Knowledge Graph and Tool for Deliberation Analysis*. arXiv:2404.10570. <https://arxiv.org/abs/2404.10570>

- **Qué es.** Grafo de conocimiento de argumentación perspectivizada para analizar deliberación.
- **Cómo lo uso.** Antecedente del módulo KG-Gen: muestra trabajo previo en grafos de argumentación sobre texto político.

---

> Nota: las citas de la sección 3 (cohesión partidaria) están marcadas para confirmar el formato exacto al momento de citarlas en el informe. El resto tiene DOI / URL verificados.
