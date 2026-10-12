import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_resources():
    df = pd.read_csv("data/resources.csv")
    df.columns = df.columns.str.strip()
    print("Columns found:", df.columns.tolist())  # debug line
    print("Shape:", df.shape)                      # debug line
    return df

def build_corpus(df):
    df = df.copy()
    df["corpus"] = df["description"].fillna("") + " " + df["keywords"].fillna("")
    return df

def get_recommendations(query, df, top_n=3):
    df = build_corpus(df)
    corpus = df["corpus"].tolist()
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = scores.argsort()[::-1][:top_n]

    results = []
    for i in top_indices:
        results.append({
            "resource_name": df.iloc[i]["resource_name"],
            "category": df.iloc[i]["category"],
            "description": df.iloc[i]["description"],
            "website": df.iloc[i]["website"],
            "contact": df.iloc[i]["contact"],
            "eligibility": df.iloc[i]["eligibility"],
            "score": round(float(scores[i]), 3)
        })

    results = [r for r in results if r["score"] > 0.05]

    if not results:
        return None

    return results