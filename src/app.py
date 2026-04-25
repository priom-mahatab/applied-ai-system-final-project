"""
app.py
 
Streamlit UI for the RAG music recommender.
Run with:  streamlit run src/app.py
 
Flow:
  1. Load songs from CSV and build the ChromaDB index (once, cached).
  2. User types a natural language query.
  3. Retriever embeds the query and fetches top-10 candidates from ChromaDB.
  4. Existing score_song() reranks those 10 candidates.
  5. Top 5 results are displayed with scores and explanations.
"""

import streamlit as st
from recommender import load_songs, score_song
from retriever import retrieve
from vector_store import build_index

DATA_PATH = "data/songs.csv"

# ── Cached startup ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Building song index (first run only)...")
def startup():
    """Load songs and ensure the ChromaDB index is built. Cached across reruns"""
    songs = load_songs(DATA_PATH)
    build_index(songs)
    return songs

# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Music Recommender", page_icon="🎵", layout="centered")
st.title("🎵 Music Recommender")
st.caption("Describe what you want to listen to and we'll find your top 5 songs.")

songs = startup()

# ── Query input ─────────────────────────────────────────────────────────────
 
query = st.text_input(
    label="What are you in the mood for?",
    placeholder="e.g. something chill for late night coding, or upbeat pop to work out to",
)

col1, col2 = st.columns([1,5])
with col1:
    search = st.button("Find songs", type="primary")


# ── Results ─────────────────────────────────────────────────────────────────
if search and query.strip():
    with st.spinner("Retrieving candidates..."):
        candidates = retrieve(query.strip(), top_k=10)

    if not candidates:
        st.warning("No candidates returned from the index. Try a different query.")
    else:
        # Rerank the retrieved candidates using the existing scoring logic.
        # We pass an empty prefs dict so score_song falls back to energy-only
        # scoring — the semantic retrieval already handled genre/mood matching.
        scored = []
        for song in candidates:
            score, reasons = score_song({}, song)
            scored.append((song, score, reasons))

        scored.sort(key=lambda x: x[1], reverse=True)
        top5 = scored[:5]

        st.subheader("Top 5 recommendations")
        for rank, (song, score, reasons) in enumerate(top5, start=1):
            with st.expander(f"{rank}. {song['title']} - {song['artist']}", expanded=rank == 1):
                cols = st.columns(3)
                cols[0].metric("Genre", song["genre"].capitalize())
                cols[1].metric("Mood", song["mood"].capitalize())
                cols[2].metric("Energy", f"{song['energy']:.0%}")
 
                st.progress(float(song["energy"]), text="Energy")
                st.progress(float(song["danceability"]), text="Danceability")
                st.progress(float(song["acousticness"]), text="Acousticness")
 
                if reasons:
                    st.markdown("**Why this song:**")
                    for reason in reasons:
                        st.markdown(f"- {reason}")

elif search and not query.strip():
    st.warning("Please enter a query first.")

# ── Sidebar: catalog browser ─────────────────────────────────────────────────
 
with st.sidebar:
    st.header("Catalog")
    st.caption(f"{len(songs)} songs indexed")
    for song in songs:
        st.markdown(f"**{song['title']}** · {song['genre']} · {song['mood']}")
