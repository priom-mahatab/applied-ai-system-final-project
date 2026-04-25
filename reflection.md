# 🎧 Model Card: VibeFinder RAG — Music Recommender

---

## 1. Model Name

**VibeFinder RAG 1.0**

---

## 2. Intended Use

This system suggests the top 5 songs from a 50-song catalog based on a natural language description of what the user wants to listen to. It is designed for classroom exploration of RAG pipelines and local AI inference — not for deployment to real production users. It assumes users can express their taste in plain English, and that the catalog is small enough that retrieval quality can be evaluated by inspection.

---

## 3. How the Model Works

The user types a free-text query like *"something chill for late night coding"*. Two things happen in parallel. First, a local language model (llama3.2 via Ollama) reads the query and extracts structured preferences: the closest matching genre, mood, and an energy level between 0 and 1. Second, a local embedding model (nomic-embed-text via Ollama) converts the query into a vector — a list of numbers that captures its semantic meaning.

The vector is compared against pre-computed vectors for all 50 songs stored in ChromaDB, a local vector database. The 10 most similar songs are retrieved. Those 10 candidates are then re-ranked using the original VibeFinder 1.0 scoring rules: genre match earns 2 points, mood match earns 3 points, and energy closeness earns up to 2 points. The top 5 are shown to the user with plain-English explanations of why each song ranked highly.

---

## 4. Data

The catalog contains 50 songs in `data/songs.csv`. It covers 15 genres including pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, classical, reggae, metal, folk, techno, r&b, and country. Moods represented include happy, chill, intense, focused, moody, relaxed, confident, reflective, uplifting, aggressive, nostalgic, euphoric, romantic, and hopeful.

The original 18 songs from VibeFinder 1.0 are preserved. 32 new songs were added to improve catalog depth, with particular attention to underrepresented moods like reflective, euphoric, and romantic. No songs were removed. The catalog skews toward Western, English-language music and does not represent global genres. Whose taste it reflects depends entirely on the curator — in this case, a classroom project with no real user research behind it.

---

## 5. Strengths

The system handles natural language queries that would completely fail in the original exact-match system. Queries like *"music that feels like a rainy Sunday morning"* or *"something nostalgic and acoustic"* now return sensible results because semantic retrieval bridges the gap between how users describe music and how the catalog labels it. The two-stage pipeline — semantic retrieval followed by rule-based reranking — also preserves explainability: every recommendation comes with a reason.

---

## 6. Limitations and Bias

The small catalog is the primary limitation. With only 50 songs, recommendations for niche genres like classical or reggae repeat the same 2–3 songs regardless of query variation. The exact-label reranker still awards zero points for near-misses, so a song labeled "moody" gets no mood points for a user who asked for "melancholy." The embedding model was trained on general text, not music-specific data, which may reduce retrieval quality for highly technical musical descriptions. High-energy songs (particularly Gym Hero and Crimson Tide) can dominate rankings across diverse queries because energy closeness is weighted generously.

---

## 7. Evaluation

Seventeen unit tests were written covering the embedder, vector store, retriever, and query parser. All 17 pass without a live Ollama instance. Two integration tests verify live round-trips with real Ollama models.

Manual evaluation was also performed across the query types below:

| Query type | Result |
|---|---|
| Clear genre + mood ("chill lofi") | Accurate, consistent top results |
| High energy workout | Correct retrieval, good variety |
| Vague mood ("rainy Sunday") | Reasonable folk/ambient results |
| Genre not in catalog ("K-pop") | Falls back to closest semantic match |
| Conflicting signals ("aggressive classical") | Mixed results, expected behavior |

The biggest surprise during evaluation was how often a single high-energy song dominated rankings in the original system. The RAG retrieval step reduced this by diversifying the candidate pool before reranking.

---

## 8. Future Work

The most impactful next improvement would be expanding the catalog to 500+ songs with more global genre coverage. A music-specific embedding model (such as one trained on Last.fm or Spotify audio features) would improve retrieval quality over the general-purpose `nomic-embed-text`. Adding diversity constraints to the reranker — for example, capping results at two songs per artist — would reduce repetition in the top 5. Supporting multi-turn conversation ("show me something more upbeat than that") would make the system feel more like a real assistant.

---

## 9. AI Collaboration Reflection

### What I learned about recommender systems

Building this project showed that recommendation quality depends as much on pipeline design as on model quality. The original VibeFinder had correct scoring logic but was brittle because it relied on exact text matching. Adding RAG didn't replace the scoring logic — it wrapped it in a more forgiving retrieval layer. The result is a system that is both more flexible for users and more reliable under varied input.

### Something unexpected

The hardest technical challenge was not the AI components — it was testing code that had Streamlit woven into it. `app.py` runs UI code at import time, which made `parse_query` nearly impossible to test in isolation. The fix was to move `parse_query` into its own module. That architectural decision — driven entirely by testability — turned out to be good design practice regardless of testing. Functions with no framework dependencies are easier to reuse, debug, and reason about.

### One instance where AI collaboration was helpful

When the ChromaDB `collection.get()` call started returning a tuple instead of a dict, Claude correctly identified this as a version compatibility issue and suggested using `collection.count()` instead — a simpler, version-safe alternative. That diagnosis was accurate and resolved the issue immediately without needing to read ChromaDB release notes.

### One instance where AI collaboration was flawed

Claude's approach to testing `parse_query` was persistently wrong for several iterations. The initial strategy was to import `app.py` inside the test and manually stub out every Streamlit attribute it accessed. Each fix revealed another missing stub — `st.header`, then `st.columns` unpacking, then the embedder being called during import. Claude kept patching the same broken approach rather than recognizing that the root cause was structural: `parse_query` should not have been defined inside a Streamlit file in the first place. A more experienced engineering instinct would have flagged this earlier. The correct fix only emerged after significant back-and-forth, and it required a human to ask the right question — *"can you just regenerate the test file?"* — which broke the iteration loop and led to the architectural solution.

### How this changed how I think about AI and problem-solving

AI tools are most valuable when they handle the mechanical parts of software — boilerplate, syntax, standard patterns — and leave architectural judgment to the human. The testing failures in this project were a good example: Claude could write test code fluently but repeatedly missed the structural signal that the code under test was the problem. Knowing when to trust an AI suggestion and when to question it is itself a skill that this project helped develop.