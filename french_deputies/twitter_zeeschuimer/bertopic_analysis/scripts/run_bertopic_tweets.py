"""
BERTopic analysis on French deputies' tweets.
Identifies central themes and key words in political Twitter discourse.

Input:  ../../../twitter_zeeschuimer/processed/tweets_text_only.csv
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
DATA_PATH = SCRIPT_DIR.parents[1] / "processed" / "tweets_text_only.csv"

MAX_DOCS = 50_000  # sample to keep runtime reasonable on a laptop

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
    "http", "https", "co", "rt", "amp", "via",
]


def clean_tweet(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)  # keep hashtag word, drop #
    text = re.sub(r"[^\w\sàâäéèêëïîôùûüÿçœæ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    print("=" * 60)
    print("BERTopic — Analyse des tweets des députés français")
    print("=" * 60)

    # ── Load data ──
    print(f"\n📂 Loading data from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Total tweets: {len(df):,}")

    df["clean_text"] = df["text"].apply(clean_tweet)
    df = df[df["clean_text"].str.len() > 30].copy()
    print(f"   After cleaning (>30 chars): {len(df):,}")

    if len(df) > MAX_DOCS:
        print(f"   Sampling {MAX_DOCS:,} tweets for performance ...")
        df = df.sample(MAX_DOCS, random_state=42)

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
        min_df=10,
        ngram_range=(1, 2),
    )

    representation_model = KeyBERTInspired()

    topic_model = BERTopic(
        language="multilingual",
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        representation_model=representation_model,
        min_topic_size=30,
        nr_topics="auto",
        verbose=True,
    )

    print("\n🚀 Fitting BERTopic (this may take several minutes) ...")
    topics, probs = topic_model.fit_transform(docs)

    # ── Save results ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Topic info table
    topic_info = topic_model.get_topic_info()
    topic_info.to_csv(RESULTS_DIR / "topic_info.csv", index=False)
    print(f"\n📊 Found {len(topic_info) - 1} topics (excl. outliers)")
    print(topic_info.head(20).to_string())

    # Top words per topic
    rows = []
    for tid in topic_info["Topic"]:
        if tid == -1:
            continue
        for word, score in topic_model.get_topic(tid):
            rows.append({"topic": tid, "word": word, "score": round(score, 5)})
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "top_words_per_topic.csv", index=False)

    # Document info
    doc_info = topic_model.get_document_info(docs)
    doc_info["political_group"] = groups
    doc_info.to_csv(RESULTS_DIR / "document_topics.csv", index=False)

    # Topics per political group
    try:
        topics_per_class = topic_model.topics_per_class(docs, classes=groups)
        topics_per_class.to_csv(RESULTS_DIR / "topics_per_group.csv", index=False)
    except Exception as e:
        topics_per_class = None
        print(f"   Topics per group skipped: {e}")

    # ── Global word frequency (outside BERTopic) ──
    from collections import Counter
    all_words = " ".join(docs).lower().split()
    filtered = [w for w in all_words if w not in FRENCH_STOPWORDS and len(w) > 2]
    freq = Counter(filtered).most_common(200)
    pd.DataFrame(freq, columns=["word", "count"]).to_csv(
        RESULTS_DIR / "global_word_frequency.csv", index=False
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

    if topics_per_class is not None:
        try:
            fig = topic_model.visualize_topics_per_class(
                topics_per_class, top_n_topics=10
            )
            fig.write_html(str(RESULTS_DIR / "viz_topics_per_group.html"))
        except Exception as e:
            print(f"   Topics per group viz skipped: {e}")

    print(f"\n✅ All results saved to {RESULTS_DIR}")
    print("   CSV files: topic_info, top_words_per_topic, document_topics,")
    print("              topics_per_group, global_word_frequency")
    print("   HTML visualizations: barchart, topics_map, heatmap, hierarchy,")
    print("                        topics_per_group")


if __name__ == "__main__":
    main()
