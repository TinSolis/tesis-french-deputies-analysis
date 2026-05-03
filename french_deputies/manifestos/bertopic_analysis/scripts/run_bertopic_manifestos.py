"""
BERTopic analysis on French party manifestos (2017 election).
Identifies central themes and key ideological words per party.

Input:  ../../../manifestos/processed/manifesto_texts.csv
        ../../../manifestos/processed/manifesto_full_texts.csv
Output: ../results/  (CSV tables + interactive HTML visualizations)
"""

import os
import re
import sys
import warnings
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
DATA_DIR = SCRIPT_DIR.parents[1] / "processed"

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
    "france", "français", "française", "pays", "république",
]


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[^\w\sàâäéèêëïîôùûüÿçœæ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    print("=" * 60)
    print("BERTopic — Analyse des manifestes électoraux (2017)")
    print("=" * 60)

    # ── Load data ──
    sentences_path = DATA_DIR / "manifesto_texts.csv"
    full_path = DATA_DIR / "manifesto_full_texts.csv"

    if not sentences_path.exists():
        print(f"❌ {sentences_path} not found.")
        sys.exit(1)

    print(f"\n📂 Loading sentence-level data from {sentences_path.name} ...")
    df_sentences = pd.read_csv(sentences_path)
    print(f"   Total sentences: {len(df_sentences):,}")

    # Load party mapping from full texts file
    party_map = {}
    if full_path.exists():
        df_full = pd.read_csv(full_path)
        party_map = dict(zip(df_full["manifesto_id"], df_full["party_abbrev"]))

    df_sentences["party"] = df_sentences["manifesto_id"].map(party_map).fillna("Unknown")
    df_sentences["clean_text"] = df_sentences["text"].apply(clean_text)
    df_sentences = df_sentences[df_sentences["clean_text"].str.len() > 20].copy()
    print(f"   After cleaning (>20 chars): {len(df_sentences):,}")

    docs = df_sentences["clean_text"].tolist()
    parties = df_sentences["party"].tolist()

    # ── BERTopic ──
    print("\n🔧 Configuring BERTopic ...")
    from bertopic import BERTopic
    from bertopic.representation import KeyBERTInspired
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    vectorizer = CountVectorizer(
        stop_words=FRENCH_STOPWORDS,
        min_df=3,
        ngram_range=(1, 2),
    )

    representation_model = KeyBERTInspired()

    topic_model = BERTopic(
        language="multilingual",
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        representation_model=representation_model,
        min_topic_size=10,
        nr_topics="auto",
        verbose=True,
    )

    print("\n🚀 Fitting BERTopic ...")
    topics, probs = topic_model.fit_transform(docs)

    # ── Save results ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(RESULTS_DIR / "topic_info.csv", index=False)
    print(f"\n📊 Found {len(topic_info) - 1} topics (excl. outliers)")
    print(topic_info.head(20).to_string())

    rows = []
    for tid in topic_info["Topic"]:
        if tid == -1:
            continue
        for word, score in topic_model.get_topic(tid):
            rows.append({"topic": tid, "word": word, "score": round(score, 5)})
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "top_words_per_topic.csv", index=False)

    doc_info = topic_model.get_document_info(docs)
    doc_info["party"] = parties
    doc_info.to_csv(RESULTS_DIR / "document_topics.csv", index=False)

    # Topics per party
    topics_per_class = topic_model.topics_per_class(docs, classes=parties)
    topics_per_class.to_csv(RESULTS_DIR / "topics_per_party.csv", index=False)

    # ── Global word frequency ──
    from collections import Counter
    all_words = " ".join(docs).lower().split()
    filtered = [w for w in all_words if w not in FRENCH_STOPWORDS and len(w) > 2]
    freq = Counter(filtered).most_common(200)
    pd.DataFrame(freq, columns=["word", "count"]).to_csv(
        RESULTS_DIR / "global_word_frequency.csv", index=False
    )

    # ── Per-party word frequency ──
    party_freqs = []
    for party in sorted(set(parties)):
        party_docs = [d for d, p in zip(docs, parties) if p == party]
        words = " ".join(party_docs).lower().split()
        filt = [w for w in words if w not in FRENCH_STOPWORDS and len(w) > 2]
        for word, count in Counter(filt).most_common(50):
            party_freqs.append({"party": party, "word": word, "count": count})
    pd.DataFrame(party_freqs).to_csv(
        RESULTS_DIR / "word_frequency_per_party.csv", index=False
    )

    # ── Visualizations ──
    print("\n📈 Generating visualizations ...")
    try:
        fig = topic_model.visualize_barchart(top_n_topics=15, n_words=10)
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

    try:
        fig = topic_model.visualize_topics_per_class(
            topics_per_class, top_n_topics=10
        )
        fig.write_html(str(RESULTS_DIR / "viz_topics_per_party.html"))
    except Exception as e:
        print(f"   Topics per party skipped: {e}")

    print(f"\n✅ All results saved to {RESULTS_DIR}")
    print("   Includes per-party word frequencies for comparative analysis")


if __name__ == "__main__":
    main()
