"""
Utilidades compartidas para correr BERTopic sobre cualquier fuente de texto
del proyecto de tesis (tweets, intervenciones, manifiestos, leyes, enmiendas).

Asi mantenemos consistencia: misma config de embeddings, mismas stopwords FR,
mismas tablas de salida, mismas visualizaciones.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


# =============================================================================
# Stop-words: base francesa + listas de dominio que se aplican segun la fuente.
# La justificacion en la tesis es que cada fuente acarrea su propio vocabulario
# de "ruido": palabras frecuentes que no aportan al topico (boilerplate legal,
# saludos del hemiciclo, restos de markup en Twitter, etc.). Limpiarlos antes
# de c-TF-IDF evita que BERTopic genere clusters dominados por forma y no por
# contenido.
# =============================================================================

FRENCH_STOPWORDS: list[str] = [
    # articulos y determinantes
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "au",
    "aux", "à", "ce", "ces", "cette", "cet", "que", "qui", "ne", "pas",
    "par", "sur", "pour", "avec", "dans", "est", "sont", "son", "sa", "ses",
    "se", "il", "elle", "ils", "elles", "nous", "vous", "on", "je",
    "tu", "leur", "leurs", "tout", "tous", "toute", "toutes", "plus",
    "mais", "ou", "où", "donc", "ni", "car", "si", "aussi", "bien",
    "comme", "même", "être", "avoir", "fait", "faire", "dit", "peut",
    "y", "a", "été", "ai", "ont", "c", "d", "l", "n", "s", "j",
    "qu", "m", "t", "très", "peu", "lors", "ça", "cela",
    "dont", "quand", "sera", "notre", "nos", "votre", "vos",
    "encore", "entre", "sans", "sous", "après", "avant", "chez",
    "depuis", "non", "oui", "alors", "chaque", "autre", "autres",
    "là", "mon", "ma", "mes", "ton", "ta", "tes",
    "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
    "premier", "première", "second", "seconde", "troisième",
]

# Boilerplate del lenguaje legal frances (codigos, decretos, mecanica de
# enmiendas). Aplica a leyes y enmiendas.
LEGAL_STOPWORDS: list[str] = [
    # Estructura del documento
    "article", "articles", "alinéa", "alinéas", "paragraphe", "paragraphes",
    "loi", "lois", "code", "codes", "décret", "décrets", "ordonnance",
    "ordonnances", "arrêté", "arrêtés", "règlement", "règlements",
    "chapitre", "chapitres", "section", "sections", "titre", "titres",
    "livre", "livres", "ligne", "lignes", "tableau", "tableaux",
    "annexe", "annexes", "préambule",
    "présente", "présent", "présentes", "présents",
    # Mecanica de enmiendas
    "modifié", "modifiée", "modifiés", "modifiées", "modifier", "modification", "modifications",
    "rédigé", "rédigée", "rédigés", "rédigées", "rédiger", "rédaction",
    "inséré", "insérée", "insérés", "insérées", "insérer", "insertion",
    "supprimé", "supprimée", "supprimés", "supprimées", "supprimer", "suppression",
    "remplacé", "remplacée", "remplacés", "remplacées", "remplacer", "remplacement",
    "abrogé", "abrogée", "abrogés", "abrogées", "abrogation",
    "compléter", "complété", "complétée", "complétés", "complétées", "complément",
    "ajouté", "ajoutée", "ajoutés", "ajoutées", "ajouter", "ajout",
    "substitué", "substituée", "substituer", "substitution",
    "rétabli", "rétablie", "rétablir",
    "rectifier", "rectification",
    "mots", "mot", "phrase", "phrases", "membre", "membres",
    # Modalidades / aplicacion
    "modalités", "modalité", "conditions", "condition",
    "fixées", "fixée", "fixé", "fixe", "fixés", "fixer",
    "déterminé", "déterminée", "déterminés", "déterminées", "déterminer",
    "définit", "définit", "défini", "définie", "définis", "définies", "définition", "définir",
    "applicable", "applicables", "applique", "appliquent", "appliquer", "application",
    "mise", "mises", "œuvre", "ouvre",
    "exécution", "exécuter", "exécuté", "exécutée",
    # Verbos dispositivos / referenciales (ruido por ubicuidad)
    "stipule", "stipulent", "dispose", "disposent", "disposition", "dispositions",
    "prévoit", "prévoient", "prévu", "prévue", "prévus", "prévues",
    "vise", "visée", "visés", "visées", "viser", "visant",
    "concerne", "concernent", "concernant", "concerné", "concernée", "concernés", "concernées",
    "relatif", "relative", "relatifs", "relatives", "relatives", "relativement",
    "tendant", "tend", "tendent",
    "considérant", "considérants",
    # Verbos modales de obligacion legal
    "doit", "doivent", "devra", "devront", "devrait",
    "peut", "peuvent", "pourra", "pourront", "pourrait",
    # Fase parlamentaria
    "examen", "examiner", "examiné", "examinée",
    "lecture", "lectures", "navette",
    "commission", "commissions",
    "adopté", "adoptée", "adoptés", "adoptées", "adopter", "adoption",
    "rejeté", "rejetée", "rejetés", "rejetées", "rejeter", "rejet",
    "voté", "votée", "votés", "votées", "voter", "vote", "votes",
    "scrutin", "scrutins",
    "promulgué", "promulguée", "promulgation",
    "publication", "publié", "publiée", "publication",
    "saisine", "saisi", "saisie", "saisir",
    "discussion", "débat", "débats",
    # Referencias internas
    "ci-dessus", "ci-dessous", "ci-après", "ci-joint", "ci-joint",
    "susvisé", "susvisée", "susvisés", "susvisées",
    "susmentionné", "susmentionnée", "susmentionnés", "susmentionnées",
    "précité", "précitée", "précités", "précitées",
    "supra", "infra", "ibid", "idem",
    "objet", "objets",
    "fin", "fins",
    # Numeracion legal francesa
    "bis", "ter", "quater", "quinquies", "sexies", "septies",
    "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
    "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°",
    # Entidades / publicacion oficial
    "république", "française", "français",
    "gouvernement", "gouvernemental", "gouvernementale",
    "ministère", "ministre", "ministres", "ministériel", "ministérielle",
    "conseil", "constitutionnel", "constitutionnelle",
    "assemblée", "nationale", "sénat", "parlement", "parlementaire",
    "exposé", "motifs", "motif",
    "nor", "jo", "jorf", "officiel", "officielle", "journal",
    # Cuantificadores y formulas frecuentes
    "alors", "ainsi", "notamment", "toutefois", "néanmoins",
    "respectivement", "lorsqu", "lorsque", "lorsqu'il", "lorsqu'elle",
    "afin", "outre", "selon", "celui", "celle", "ceux", "celles",
    "lequel", "laquelle", "lesquels", "lesquelles",
    "etc",
]

# Vocabulario procedural del hemiciclo. Aplica a intervenciones.
HEMICYCLE_STOPWORDS: list[str] = [
    "monsieur", "madame", "messieurs", "mesdames",
    "président", "présidente", "ministre", "ministres",
    "député", "députée", "députés", "députées",
    "rapporteur", "rapporteure", "rapporteurs",
    "collègue", "collègues", "cher", "chère", "chers", "chères",
    "applaudissements", "bancs", "groupe", "groupes",
    "parole", "séance", "session", "assemblée",
    "amendement", "amendements", "sous-amendement",
    "projet", "proposition", "rapport",
    "loi", "article", "alinéa",
    "merci", "voilà", "donc", "effet",
    "intervention", "interventions", "discussion", "débat", "débats",
    "vote", "votes", "scrutin", "scrutins",
    "voudrais", "souhaite", "souhaitons", "puis", "doit", "faut",
    "dire", "disons", "permettez", "permettre",
    "président séance", "président groupe", "national",
]

# Ruido tipico de Twitter. Aplica a tweets.
TWITTER_STOPWORDS: list[str] = [
    "http", "https", "co", "rt", "amp", "via", "twitter", "com",
    "fr", "www", "html", "youtube", "youtu", "facebook", "fb",
    "live", "vidéo", "video", "photo", "image", "lien",
    "today", "soir", "matin", "demain", "aujourd",
]


DEFAULT_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def run_bertopic(
    docs: Sequence[str],
    *,
    out_dir: Path,
    classes: Sequence[str] | None = None,
    class_label: str = "class",
    min_topic_size: int = 30,
    nr_topics: str | int = "auto",
    target_nr_topics: int | None = 25,
    ngram_range: tuple[int, int] = (1, 2),
    min_df: int = 5,
    extra_stopwords: Iterable[str] = (),
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
    top_n_per_topic: int = 10,
    barchart_topics: int = 15,
    cls_topics_top_n: int = 10,
) -> dict:
    """
    Si `target_nr_topics` se especifica (default 25), despues del fit_transform
    se aplica `reduce_topics` para colapsar a ese numero objetivo. Esto evita
    la fragmentacion del dato (decenas de mini-clusters poco interpretables)
    y deja una tabla de topicos manejable y comparable entre fuentes.
    """
    """
    Ajusta BERTopic sobre `docs` y guarda en `out_dir`:
      - topic_info.csv          : tabla resumen (topic id, size, name)
      - top_words_per_topic.csv : palabras + scores por topico
      - document_topics.csv     : un fila por documento, su topico y la clase
      - topics_per_<class>.csv  : frecuencia de topicos por clase (si classes)
      - global_word_frequency.csv : top-N palabras globales
      - viz_barchart.html / viz_topics_map.html / viz_heatmap.html /
        viz_hierarchy.html / viz_topics_per_<class>.html
      - summary.json            : metadata de la corrida

    Devuelve un dict con stats clave para usar en el README.
    """
    from bertopic import BERTopic
    from bertopic.representation import KeyBERTInspired
    from sentence_transformers import SentenceTransformer

    out_dir.mkdir(parents=True, exist_ok=True)
    n_docs = len(docs)
    if n_docs == 0:
        raise ValueError("No hay documentos para ajustar BERTopic.")

    stopwords = list(FRENCH_STOPWORDS) + [s.lower() for s in extra_stopwords]

    print(f"[{out_dir.name}] documentos: {n_docs:,}")
    print(f"[{out_dir.name}] modelo embeddings: {embedding_model_name}")
    print(f"[{out_dir.name}] cargando embedding model...")
    embedding_model = SentenceTransformer(embedding_model_name)

    vectorizer = CountVectorizer(
        stop_words=stopwords,
        min_df=min_df,
        ngram_range=ngram_range,
    )

    representation_model = KeyBERTInspired()

    # Si pedimos una reduccion manual a target_nr_topics, desactivamos el
    # auto-reduce interno de BERTopic. Su loop de merging recalcula c-TF-IDF
    # sobre topicos-agregados despues de cada merge; cuando el numero de
    # topicos cae por debajo de `min_df`, sklearn lanza
    # "After pruning, no terms remain". Hacemos UNA sola reduccion al final
    # (mas abajo) con un vectorizer parcheado.
    bertopic_nr_topics = None if target_nr_topics is not None else nr_topics

    topic_model = BERTopic(
        language="multilingual",
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        representation_model=representation_model,
        min_topic_size=min_topic_size,
        nr_topics=bertopic_nr_topics,
        verbose=True,
    )

    print(f"[{out_dir.name}] fit_transform... (puede tardar)")
    t0 = time.time()
    docs_list = list(docs)
    topics, _probs = topic_model.fit_transform(docs_list)
    elapsed = time.time() - t0
    print(f"[{out_dir.name}] fit_transform listo en {elapsed:.0f}s.")

    # === Reduccion post-hoc a un numero objetivo de topicos ===
    n_topics_pre = sum(1 for t in topic_model.get_topic_info()["Topic"] if t != -1)
    if target_nr_topics is not None and n_topics_pre > target_nr_topics:
        print(f"[{out_dir.name}] reduciendo de {n_topics_pre} -> {target_nr_topics} topicos...")
        # reduce_topics recomputa c-TF-IDF sobre un documento agregado por
        # topico (~target_nr_topics filas). Si el min_df original excede ese
        # numero, sklearn lanza "max_df corresponds to < documents than min_df".
        # Usamos un vectorizer con min_df=1 solo para el post-reduce; la parte
        # IDF de c-TF-IDF sigue despriorizando terminos compartidos entre topicos.
        reduce_vectorizer = CountVectorizer(
            stop_words=stopwords,
            min_df=1,
            ngram_range=ngram_range,
        )
        topic_model.vectorizer_model = reduce_vectorizer
        t0r = time.time()
        topic_model.reduce_topics(docs_list, nr_topics=target_nr_topics)
        print(f"[{out_dir.name}] reduce_topics listo en {time.time()-t0r:.0f}s.")

    # === Tabla resumen ===
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(out_dir / "topic_info.csv", index=False)
    n_topics = sum(1 for t in topic_info["Topic"] if t != -1)
    n_outliers = int((topic_info[topic_info["Topic"] == -1]["Count"]).sum()) if -1 in topic_info["Topic"].values else 0
    print(f"[{out_dir.name}] {n_topics} topicos detectados (outliers: {n_outliers})")

    # === Top palabras por topico ===
    rows = []
    for tid in topic_info["Topic"]:
        if tid == -1:
            continue
        for word, score in topic_model.get_topic(tid)[:top_n_per_topic]:
            rows.append({"topic": int(tid), "word": word, "score": round(float(score), 5)})
    pd.DataFrame(rows).to_csv(out_dir / "top_words_per_topic.csv", index=False)

    # === Documentos con su topico asignado ===
    doc_info = topic_model.get_document_info(docs_list)
    if classes is not None:
        doc_info[class_label] = list(classes)
    doc_info.to_csv(out_dir / "document_topics.csv", index=False)

    # === Topicos por clase ===
    topics_per_class = None
    if classes is not None:
        try:
            topics_per_class = topic_model.topics_per_class(docs_list, classes=list(classes))
            topics_per_class.to_csv(out_dir / f"topics_per_{class_label}.csv", index=False)
        except Exception as e:
            print(f"[{out_dir.name}] topics_per_class omitido: {e}")

    # === Frecuencia global de palabras ===
    all_words = " ".join(docs).lower().split()
    sw = set(stopwords)
    filt = [w for w in all_words if w not in sw and len(w) > 2]
    freq = Counter(filt).most_common(200)
    pd.DataFrame(freq, columns=["word", "count"]).to_csv(
        out_dir / "global_word_frequency.csv", index=False
    )

    # === Visualizaciones ===
    print(f"[{out_dir.name}] generando visualizaciones...")
    _safe_write(topic_model.visualize_barchart, out_dir / "viz_barchart.html",
                top_n_topics=barchart_topics, n_words=10)
    _safe_write(topic_model.visualize_topics, out_dir / "viz_topics_map.html")
    _safe_write(topic_model.visualize_heatmap, out_dir / "viz_heatmap.html")
    _safe_write(topic_model.visualize_hierarchy, out_dir / "viz_hierarchy.html")
    if topics_per_class is not None:
        try:
            fig = topic_model.visualize_topics_per_class(
                topics_per_class, top_n_topics=cls_topics_top_n
            )
            fig.write_html(str(out_dir / f"viz_topics_per_{class_label}.html"))
        except Exception as e:
            print(f"[{out_dir.name}] viz topics_per_class omitido: {e}")

    # === Resumen JSON ===
    summary = {
        "n_documents": n_docs,
        "n_topics_pre_reduction": int(n_topics_pre),
        "n_topics": int(n_topics),
        "target_nr_topics": target_nr_topics,
        "n_outliers": int(n_outliers),
        "elapsed_seconds": round(elapsed, 1),
        "min_topic_size": min_topic_size,
        "nr_topics": str(nr_topics),
        "ngram_range": list(ngram_range),
        "min_df": min_df,
        "embedding_model": embedding_model_name,
        "class_label": class_label if classes is not None else None,
        "top_topics_preview": [
            {
                "topic": int(r["Topic"]),
                "count": int(r["Count"]),
                "name": str(r["Name"]),
            }
            for _, r in topic_info[topic_info["Topic"] != -1].head(10).iterrows()
        ],
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"[{out_dir.name}] hecho. Resultados en {out_dir}")
    return summary


def _safe_write(fn, path: Path, **kwargs) -> None:
    try:
        fig = fn(**kwargs)
        fig.write_html(str(path))
    except Exception as e:
        print(f"  viz {path.name} omitido: {e}")
