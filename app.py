import streamlit as st
import pandas as pd
import os
from datetime import datetime
from recommender import load_resources, get_recommendations

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="Husky Resource Navigator",
    page_icon="🐾",
    layout="centered"
)

# ── Load data once and cache it ──────────────────────────
def load_data():
    return load_resources()

df = load_data()

# ── Logging helpers ───────────────────────────────────────
SEARCH_LOG = "data/search_log.csv"
FEEDBACK_LOG = "data/feedback.csv"

def log_search(query, results):
    top_result = results[0]["resource_name"] if results else "No match"
    categories = ", ".join(set(r["category"] for r in results)) if results else "None"
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "top_result": top_result,
        "categories_returned": categories,
        "num_results": len(results) if results else 0
    }
    log_df = pd.DataFrame([row])
    if os.path.exists(SEARCH_LOG):
        log_df.to_csv(SEARCH_LOG, mode="a", header=False, index=False)
    else:
        log_df.to_csv(SEARCH_LOG, mode="w", header=True, index=False)

def log_feedback(query, resource_name, helpful):
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "resource_name": resource_name,
        "helpful": helpful
    }
    log_df = pd.DataFrame([row])
    if os.path.exists(FEEDBACK_LOG):
        log_df.to_csv(FEEDBACK_LOG, mode="a", header=False, index=False)
    else:
        log_df.to_csv(FEEDBACK_LOG, mode="w", header=True, index=False)

# ── UI ────────────────────────────────────────────────────
st.title("🐾 Husky Resource Navigator")
st.subheader("UConn Stamford Student Support Finder")
st.write("Tell us what you're going through and we'll point you to the right resource.")

query = st.text_area(
    label="What do you need help with?",
    placeholder="Example: I'm really stressed about finals and can't focus...",
    height=100
)

search_clicked = st.button("Find Resources", type="primary")

# ── Results ───────────────────────────────────────────────
if search_clicked:
    if not query.strip():
        st.warning("Please enter what you need help with.")
    else:
        results = get_recommendations(query, df)

        if results is None:
            st.error("We couldn't find a strong match. Try describing your situation differently.")
        else:
            log_search(query, results)
            st.success(f"Found {len(results)} resource(s) for you:")
            st.divider()

            for i, r in enumerate(results):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {i+1}. {r['resource_name']}")
                        st.caption(f"📂 {r['category']}")
                        st.write(r["description"])
                        st.markdown(f"🌐 [Visit Website]({r['website']})")
                        st.markdown(f"✉️ {r['contact']}")
                        st.markdown(f"👤 *Eligibility: {r['eligibility']}*")
                    with col2:
                        st.metric("Match Score", f"{int(r['score'] * 100)}%")

                    st.write("Was this helpful?")
                    col_yes, col_no, _ = st.columns([1, 1, 4])
                    with col_yes:
                        if st.button("👍 Yes", key=f"yes_{i}"):
                            log_feedback(query, r["resource_name"], True)
                            st.success("Thanks!")
                    with col_no:
                        if st.button("👎 No", key=f"no_{i}"):
                            log_feedback(query, r["resource_name"], False)
                            st.info("Thanks for the feedback.")

                    st.divider()