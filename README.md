# 🎵 VibeFinder RAG — Music Recommender with Retrieval-Augmented Generation

> A natural language music recommendation system that understands what you *mean*, not just what you *type*.

---

## Original Project

This project extends **VibeFinder 1.0**, a content-based music recommender built in Modules 1–3. The original system scored songs from an 18-song catalog by comparing exact genre and mood labels against a structured user profile (e.g. `{"genre": "lofi", "mood": "chill", "energy": 0.38}`). While transparent and explainable, it relied on exact text matching — meaning `"hip-hop"` would fail to match `"hip hop"`, and descriptive phrases like *"music for a rainy afternoon"* were not supported at all.

---

## Title and Summary

**VibeFinder RAG** upgrades the original recommender with a full Retrieval-Augmented Generation pipeline. Instead of requiring users to fill out a structured profile, they can now describe what they want in plain English. The system interprets that description using a local Ollama language model, retrieves semantically similar songs from a ChromaDB vector store, and re-ranks them using the original scoring logic — preserving explainability while adding natural language understanding.

This matters because real music recommendation is fuzzy. People don't think in genre labels — they think in vibes, moods, and moments. This system bridges that gap without requiring a paid API or sending data to the cloud.

---

## System Architecture

```
User (Streamlit UI)
        │
        │  natural language query
        ▼
  query_parser.py
  (llama3.2 via Ollama → genre, mood, energy)
        │
        ▼
  embedder.py
  (nomic-embed-text via Ollama → vector)
        │
        ▼
  vector_store.py
  (ChromaDB cosine similarity → top 10 candidates)
        │
        ▼
  recommender.py  ← original scoring logic reused as reranker
  (score_song() → top 5 with explanations)
        │
        ▼
  Results displayed in Streamlit UI
```

The pipeline has two parallel AI steps: `query_parser.py` extracts structured preferences (genre, mood, energy) from the query for the reranker, while `embedder.py` converts the raw query into a vector for semantic retrieval. Both run locally via Ollama — no API keys, no cost, no data sent externally.

The system diagram image is available in [`/assets/system_diagram.png`](assets/system_diagram.png).

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed on your machine

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Ollama and pull the required models (one-time setup)
```bash
# In a separate terminal — keep this running
ollama serve

# Pull the embedding model (~270MB)
ollama pull nomic-embed-text

# Pull the chat model for query parsing (~2GB)
ollama pull llama3.2
```

### 5. Run the app
```bash
streamlit run src/app.py
```

The first run will index all 50 songs into ChromaDB (takes ~30 seconds). Every subsequent run loads the index instantly from `data/chroma/`.

### 6. Run the tests
```bash
# Unit tests only — no Ollama needed
pytest -m "not integration"

# Full suite including live Ollama tests
pytest -m integration
```

---

## Sample Interactions

### Example 1 — Descriptive vibe query
**Input:** `"something chill for late night coding"`

**Interpreted as:** Genre: lofi · Mood: chill · Energy: 35%

**Top results:**
1. Midnight Coding — LoRoom *(genre matches, mood matches, energy very close)*
2. Library Rain — Paper Lanterns *(genre matches, mood matches)*
3. Deep Focus — LoRoom *(genre matches, mood: focused)*

---

### Example 2 — High energy workout
**Input:** `"upbeat high energy music to work out to"`

**Interpreted as:** Genre: pop · Mood: intense · Energy: 90%

**Top results:**
1. Gym Hero — Max Pulse *(genre matches, mood matches, energy very close)*
2. Neon Circuit — Kilo Pulse *(euphoric, energy 89%)*
3. Pulse City — Kilo Pulse *(techno intense, energy 95%)*

---

### Example 3 — Mood-based, no genre specified
**Input:** `"music that feels nostalgic and acoustic, like a road trip through the countryside"`

**Interpreted as:** Genre: folk · Mood: nostalgic · Energy: 38%

**Top results:**
1. Pine Trail Letters — Willow Reed *(folk nostalgic, acousticness 91%)*
2. Ember Roads — Sunfield *(folk nostalgic, acousticness 92%)*
3. Porch Swing Summer — Willow Reed *(folk hopeful, acousticness 88%)*

---

## Design Decisions

### Why Ollama instead of a paid API?
Ollama runs fully locally — no API key, no cost, no data leaving the machine. For a classroom project this makes setup frictionless. The trade-off is that models are slower than cloud APIs and require ~2GB of local storage for `llama3.2`.

### Why two separate AI steps (embedder + query parser)?
The embedder (`nomic-embed-text`) handles semantic similarity — it finds songs that *feel* like the query. The query parser (`llama3.2`) extracts structured labels (genre, mood, energy) so the original `score_song()` logic can generate meaningful explanations. Using one model for both would sacrifice either retrieval quality or explainability.

### Why keep the original `score_song()` as the reranker?
It preserves the transparency of the original system. Every recommendation comes with a plain-English explanation of *why* it ranked highly. Replacing it with a pure neural ranker would make the system a black box.

### Why move `parse_query` into its own module?
`app.py` runs Streamlit code at import time, making it impossible to unit test functions defined inside it. Extracting `parse_query` into `query_parser.py` means it can be imported and tested independently with no Streamlit dependency.

### Trade-offs
| Decision | Benefit | Cost |
|---|---|---|
| Local Ollama | Free, private | Slower, needs setup |
| Two-stage pipeline | Explainable results | Two model calls per query |
| ChromaDB persistence | Fast after first run | Extra `data/chroma/` folder to manage |
| 50-song catalog | Richer results than original | Still small; niche genres underrepresented |

---

## Testing Summary

**17 / 17 unit tests pass** (`pytest -m "not integration"`)

| Suite | Tests | What's covered |
|---|---|---|
| TestEmbedder | 4 | Vector output shape, description building, error propagation |
| TestVectorStore | 4 | Indexing, idempotency, query shape, top_k |
| TestRetriever | 3 | Wiring, query forwarding, top_k forwarding |
| TestParseQuery | 4 | Required keys, float types, fallback on error, lowercasing |
| TestIntegration | 2 | Live Ollama round-trips (skipped in unit mode) |

**What worked well:** Mocking `requests.post` at the module level (`@patch("embedder.requests.post")`) made the embedder tests clean and fast. Using `tmp_path` for ChromaDB tests meant no real disk state was touched.

**What was hard:** Testing `parse_query` was the toughest part. Originally it lived inside `app.py`, which runs Streamlit code on import — making isolation nearly impossible. The fix was architectural: move `parse_query` to its own module so tests never need to touch `app.py`.

**What we learned:** Good testability is a design constraint, not an afterthought. If a function is hard to test, that's usually a sign it's doing too many things.

---

## Reflection

Building this project changed how I think about the gap between a model "knowing" something and a system being genuinely useful. The original recommender had perfect knowledge of its scoring rules, but it was brittle — one typo in a genre label could tank a recommendation. Adding RAG didn't just improve results; it made the system more forgiving of how humans actually communicate.

The most surprising insight was how much of the work happened *outside* the AI models. The embedder and query parser are just a few lines each — the real engineering was in the pipeline: making sure the right data flows to the right place, that errors fall back gracefully, and that the system stays testable as it grows. AI components are powerful, but they only matter if the surrounding system handles them reliably.

Running everything locally with Ollama also reframed what "AI-powered" means. A system doesn't need a cloud API to be intelligent — it needs the right model for the right job, wired together thoughtfully.

---

## Demo

> 📹 **[Loom walkthrough — add your link here]**
>
> The walkthrough shows three end-to-end queries: a chill late-night coding request, a high-energy workout query, and a vague mood-based request. Each demonstrates the interpreted preferences, retrieved candidates, and final ranked results with explanations.

Screenshots are available in the [`/assets`](assets/) folder.

---

## Project Structure

```
.
├── data/
│   ├── songs.csv              # 50-song catalog
│   └── chroma/                # ChromaDB index (auto-generated)
├── src/
│   ├── app.py                 # Streamlit UI entry point
│   ├── query_parser.py        # Natural language → structured prefs
│   ├── embedder.py            # Text → vector via Ollama
│   ├── vector_store.py        # ChromaDB index + query
│   ├── retriever.py           # Query → candidates
│   └── recommender.py        # Original scoring logic (reranker)
├── tests/
│   ├── test_recommender.py    # Original tests
│   └── test_rag_pipeline.py   # RAG pipeline tests
├── assets/
│   └── system_diagram.png     # Architecture diagram
├── model_card.md
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Requirements

```
pandas
pytest
streamlit
chromadb
requests
```

All AI inference runs locally via [Ollama](https://ollama.com). No paid API keys required.

---

## Reflection and Ethics

### Limitations and Biases

The catalog of 50 songs is the system's biggest limitation. With so few entries, underrepresented genres like classical, reggae, and ambient have only 2–3 songs each, meaning users who ask for those styles get very limited variety. The system also inherits the biases of whoever curated the catalog — the songs skew toward Western genres and English-language music, so a user asking for K-pop, Afrobeats, or Bollywood would get nothing useful back.

The `score_song()` reranker still uses exact label matching for genre and mood. While `query_parser.py` now handles fuzzy natural language input, the reranking step awards zero points for near-misses like `"melancholy"` vs `"moody"`. This means the explanation a user sees may not fully reflect why a song was retrieved semantically.

The embedding model (`nomic-embed-text`) was trained on general text, not music metadata specifically. It may not capture musical nuance as well as a purpose-built music embedding model would.

### Could this system be misused?

A music recommender has a low direct misuse risk, but a few concerns are worth noting. First, a catalog with intentional mislabeling could be used to serve unwanted content to users who trust the system's genre/mood labels. Second, if this system were scaled to real users, the query logs would reveal sensitive personal information — what someone listens to when anxious, grieving, or celebrating. That data should never be stored or sold. In this project, all inference runs locally and nothing is logged, which eliminates that risk entirely.

### What surprised us during testing

The hardest part of testing had nothing to do with the AI models — it was importing `app.py` in a test context. Because Streamlit runs UI code at module import time, any function defined inside `app.py` was nearly impossible to test in isolation. We went through several failed approaches (manual stubs, `MagicMock`, stubbing `build_index`) before realizing the right fix was architectural: move `parse_query` into its own module. That one change made four previously failing tests pass immediately. The lesson was that testability is a design property, not something you bolt on afterward.

We were also surprised by how often `Gym Hero` appeared across unrelated profiles in the original system. A song with very high energy (0.93) could stay competitive even when genre and mood didn't match, because energy closeness awards up to 2.0 points regardless of other factors. The RAG system reduced this repetition because semantic retrieval diversifies the candidate pool before reranking.

### Collaboration with AI

This project was built collaboratively with Claude (Anthropic). Claude contributed the architecture design, all five new source files (`embedder.py`, `vector_store.py`, `retriever.py`, `query_parser.py`, `app.py`), the expanded song catalog, and the full test suite.

**One instance where AI was genuinely helpful:** When we hit the `collection.get()` tuple bug in ChromaDB, Claude correctly diagnosed that newer versions of ChromaDB changed the return type of `get()` from a dict to a tuple, and suggested switching to `collection.count()` as a version-safe alternative. That diagnosis was accurate and saved significant debugging time.

**One instance where AI's suggestion was flawed:** Claude's first approach to testing `parse_query` was to import `app.py` inside the test and stub out Streamlit manually — listing every `st.*` attribute the file used. This kept failing because each fix revealed another missing stub (`st.header`, then `st.columns` unpacking, then the embedder being called during import). Claude kept patching the same broken approach rather than stepping back to question whether importing `app.py` in tests was the right strategy at all. The correct solution — extracting `parse_query` into its own file — only emerged after multiple failed iterations. A better first instinct would have been to recognize that untestable code signals a structural problem, not a mocking problem.