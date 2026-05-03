"""
BERTopic analysis on the FULL hemicycle dataset (XV legislature, 2017-2022).
Only includes interventions linked to a deputy (deputy_id not null) with ≥80 words.

Input:  hemicycle/processed/interventions_xv_2017_2022_with_deputies.csv.gz
Output: ../results/  (overwrites previous sample-based results)
"""

import re
import sys
import warnings
from pathlib import Path
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
DATA_DIR = SCRIPT_DIR.parents[1] / "processed"

MIN_WORDS = 80

FRENCH_STOPWORDS = [
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "au",
    "aux", "à", "ce", "ces", "cette", "que", "qui", "ne", "pas", "par",
    "sur", "pour", "avec", "dans", "est", "sont", "son", "sa", "ses",
    "se", "il", "elle", "ils", "elles", "nous", "vous", "on", "je",
    "tu", "leur", "leurs", "tout", "tous", "toute", "toutes", "plus",
    "mais", "ou", "où", "donc", "ni", "car", "si", "aussi", "bien",
    "comme", "même", "être", "avoir", "fait", "faire", "dit", "peut",
    "y", "a", "été", "ai", "ont", "c", "d", "l", "n", "s", "j",
    "qu", "m", "t", "très", "peu", "lors", "ça", "cela", "cet",
    "dont", "quand", "sera", "notre", "nos", "votre", "vos",
    "encore", "entre", "sans", "sous", "après", "avant", "chez",
    "depuis", "non", "oui", "alors", "chaque", "autre", "autres",
    "là", "mon", "ma", "mes", "ton", "ta", "tes",
    "madame", "monsieur", "président", "présidente", "ministre",
    "collègues", "chers", "applaudissements", "séance", "amendement",
    "article", "alinéa", "commission", "rapport", "rapporteur",
    "assemblée", "nationale", "gouvernement", "texte", "projet",
    "loi", "discussion", "débat", "question", "groupe",
    "amendements", "adopté", "rejeté", "avis", "défavorable",
    "favorable", "parole", "orateur", "oratrice",
]

PROCEDURAL_PATTERNS = re.compile(
    r"(applaudissements|la séance.{0,10}(suspendue|reprise|ouverte|levée)"
    r"|scrutin (public|solennel)|il est procédé|est mis aux voix"
    r"|l.ordre du jour|vote par assis|résultat du scrutin)",
    re.IGNORECASE,
)


def clean_intervention(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\sàâäéèêëïîôùûüÿçœæ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_procedural(text: str) -> bool:
    return bool(PROCEDURAL_PATTERNS.search(text))


def main():
    print("=" * 70)
    print("BERTopic — Dataset COMPLETO hemiciclo (solo diputados enlazados)")
    print("=" * 70)

    compressed_path = DATA_DIR / "interventions_xv_2017_2022_with_deputies.csv.gz"
    if not compressed_path.exists():
        print(f"❌ {compressed_path} not found.")
        sys.exit(1)

    # ── Load ──
    print(f"\n📂 Loading {compressed_path.name} ...")
    cols = [
        "intervention_plain", "nb_mots", "deputy_id",
        "political_group_abbrev", "deputy_full_name", "type",
    ]
    df = pd.read_csv(compressed_path, usecols=cols)
    print(f"   Total: {len(df):,}")

    df = df[df["deputy_id"].notna()].copy()
    print(f"   Con deputy_id enlazado: {len(df):,}")

    df = df[df["nb_mots"] >= MIN_WORDS].copy()
    print(f"   Con ≥{MIN_WORDS} palabras: {len(df):,}")

    df["clean_text"] = df["intervention_plain"].apply(clean_intervention)
    procedural_mask = df["intervention_plain"].apply(is_procedural)
    df = df[~procedural_mask].copy()
    df = df[df["clean_text"].str.len() > 50].copy()
    print(f"   Tras filtro procedimental y limpieza: {len(df):,}")

    docs = df["clean_text"].tolist()
    groups = df["political_group_abbrev"].fillna("Inconnu").tolist()

    # ── BERTopic ──
    print("\n🔧 Configuring BERTopic ...")
    from bertopic import BERTopic
    from bertopic.representation import KeyBERTInspired
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    vectorizer = CountVectorizer(
        stop_words=FRENCH_STOPWORDS,
        min_df=20,
        ngram_range=(1, 2),
    )

    representation_model = KeyBERTInspired()

    topic_model = BERTopic(
        language="multilingual",
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        representation_model=representation_model,
        min_topic_size=50,
        nr_topics="auto",
        verbose=True,
    )

    print(f"\n🚀 Fitting BERTopic on {len(docs):,} documents ...")
    print("   (embedding ~140k docs will take 5-10 min, UMAP another 5-10 min)")
    topics, probs = topic_model.fit_transform(docs)

    # ── Save ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(RESULTS_DIR / "topic_info.csv", index=False)
    n_topics = len(topic_info) - 1
    print(f"\n📊 Found {n_topics} topics (excl. outliers)")
    print(topic_info.head(25).to_string())

    rows = []
    for tid in topic_info["Topic"]:
        if tid == -1:
            continue
        for word, score in topic_model.get_topic(tid):
            rows.append({"topic": tid, "word": word, "score": round(score, 5)})
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "top_words_per_topic.csv", index=False)

    doc_info = topic_model.get_document_info(docs)
    doc_info["political_group"] = groups
    doc_info.to_csv(RESULTS_DIR / "document_topics.csv", index=False)

    try:
        topics_per_class = topic_model.topics_per_class(docs, classes=groups)
        topics_per_class.to_csv(RESULTS_DIR / "topics_per_group.csv", index=False)
    except Exception as e:
        topics_per_class = None
        print(f"   Topics per group skipped: {e}")

    # ── Word frequency ──
    all_words = " ".join(docs).lower().split()
    filtered = [w for w in all_words if w not in FRENCH_STOPWORDS and len(w) > 2]
    freq = Counter(filtered).most_common(300)
    pd.DataFrame(freq, columns=["word", "count"]).to_csv(
        RESULTS_DIR / "global_word_frequency.csv", index=False
    )

    # ── Per-group word frequency (top groups) ──
    group_freqs = []
    top_groups = pd.Series(groups).value_counts().head(10).index
    for grp in top_groups:
        grp_docs = [d for d, g in zip(docs, groups) if g == grp]
        words = " ".join(grp_docs).lower().split()
        filt = [w for w in words if w not in FRENCH_STOPWORDS and len(w) > 2]
        for word, count in Counter(filt).most_common(50):
            group_freqs.append({"group": grp, "word": word, "count": count})
    pd.DataFrame(group_freqs).to_csv(
        RESULTS_DIR / "word_frequency_per_group.csv", index=False
    )

    # ── Visualizations ──
    print("\n📈 Generating visualizations ...")
    try:
        fig = topic_model.visualize_barchart(top_n_topics=20, n_words=10)
        fig.write_html(str(RESULTS_DIR / "viz_barchart.html"))
    except Exception as e:
        print(f"   Barchart skipped: {e}")

    try:
        fig = topic_model.visualize_topics()
        fig.write_html(str(RESULTS_DIR / "viz_topics_map.html"))
    except Exception as e:
        print(f"   Topic map skipped: {e}")

    try:
        fig = topic_model.visualize_heatmap()
        fig.write_html(str(RESULTS_DIR / "viz_heatmap.html"))
    except Exception as e:
        print(f"   Heatmap skipped: {e}")

    try:
        fig = topic_model.visualize_hierarchy()
        fig.write_html(str(RESULTS_DIR / "viz_hierarchy.html"))
    except Exception as e:
        print(f"   Hierarchy skipped: {e}")

    if topics_per_class is not None:
        try:
            fig = topic_model.visualize_topics_per_class(
                topics_per_class, top_n_topics=15
            )
            fig.write_html(str(RESULTS_DIR / "viz_topics_per_group.html"))
        except Exception as e:
            print(f"   Topics per group viz skipped: {e}")

    print(f"\n✅ Done — {n_topics} topics from {len(docs):,} interventions")
    print(f"   Results in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
