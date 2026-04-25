"""
test_rag_pipeline.py

Tests for the RAG pipeline components:
  - embedder.py
  - vector_store.py
  - retriever.py
  - query_parser.py

Run unit tests only (no Ollama needed):
    pytest -m "not integration"

Run integration tests (requires `ollama serve` + nomic-embed-text + llama3.2):
    pytest -m integration
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ── Shared fixtures ───────────────────────────────────────────────────────────

SAMPLE_SONGS = [
    {
        "id": 1, "title": "Sunrise City", "artist": "Neon Echo",
        "genre": "pop", "mood": "happy", "energy": 0.82,
        "tempo_bpm": 118.0, "valence": 0.84, "danceability": 0.79, "acousticness": 0.18,
    },
    {
        "id": 2, "title": "Midnight Coding", "artist": "LoRoom",
        "genre": "lofi", "mood": "chill", "energy": 0.42,
        "tempo_bpm": 78.0, "valence": 0.56, "danceability": 0.62, "acousticness": 0.71,
    },
    {
        "id": 3, "title": "Storm Runner", "artist": "Voltline",
        "genre": "rock", "mood": "intense", "energy": 0.91,
        "tempo_bpm": 152.0, "valence": 0.48, "danceability": 0.66, "acousticness": 0.10,
    },
]

FAKE_VECTOR = [0.1] * 768  # nomic-embed-text produces 768-dim vectors


# ══════════════════════════════════════════════════════════════════════════════
# EMBEDDER TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestEmbedder:

    @patch("embedder.requests.post")
    def test_embed_song_returns_list_of_floats(self, mock_post):
        """embed_song should return a non-empty list of floats."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": FAKE_VECTOR},
        )
        from embedder import embed_song
        result = embed_song(SAMPLE_SONGS[0])

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(v, float) for v in result)

    @patch("embedder.requests.post")
    def test_embed_query_returns_list_of_floats(self, mock_post):
        """embed_query should return a non-empty list of floats."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": FAKE_VECTOR},
        )
        from embedder import embed_query
        result = embed_query("chill lofi for studying")

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(v, float) for v in result)

    @patch("embedder.requests.post")
    def test_embed_song_calls_ollama_with_description(self, mock_post):
        """embed_song should build a natural language description and POST it."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"embedding": FAKE_VECTOR},
        )
        from embedder import embed_song
        embed_song(SAMPLE_SONGS[0])

        call_args = mock_post.call_args
        payload = call_args.kwargs.get("json") or call_args.args[1]
        assert "pop" in payload["prompt"].lower() or "happy" in payload["prompt"].lower()

    @patch("embedder.requests.post", side_effect=Exception("Ollama not running"))
    def test_embed_song_raises_on_ollama_failure(self, mock_post):
        """embed_song should propagate exceptions when Ollama is unreachable."""
        from embedder import embed_song
        with pytest.raises(Exception, match="Ollama not running"):
            embed_song(SAMPLE_SONGS[0])


# ══════════════════════════════════════════════════════════════════════════════
# VECTOR STORE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestVectorStore:

    @patch("vector_store.embed_song", return_value=FAKE_VECTOR)
    def test_build_index_adds_all_songs(self, mock_embed, tmp_path):
        """build_index should add all songs to the collection."""
        from vector_store import build_index, _get_collection
        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        collection = _get_collection(persist_path=str(tmp_path))
        assert collection.count() == len(SAMPLE_SONGS)

    @patch("vector_store.embed_song", return_value=FAKE_VECTOR)
    def test_build_index_is_idempotent(self, mock_embed, tmp_path):
        """Calling build_index twice should not duplicate songs."""
        from vector_store import build_index, _get_collection
        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        collection = _get_collection(persist_path=str(tmp_path))
        assert collection.count() == len(SAMPLE_SONGS)

    @patch("vector_store.embed_song", return_value=FAKE_VECTOR)
    def test_query_index_returns_song_dicts(self, mock_embed, tmp_path):
        """query_index should return a list of dicts with expected song keys."""
        from vector_store import build_index, query_index
        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        results = query_index(FAKE_VECTOR, top_k=2, persist_path=str(tmp_path))
        assert isinstance(results, list)
        assert len(results) <= 2
        for song in results:
            for key in ("title", "genre", "mood", "energy"):
                assert key in song

    @patch("vector_store.embed_song", return_value=FAKE_VECTOR)
    def test_query_index_respects_top_k(self, mock_embed, tmp_path):
        """query_index should return at most top_k results."""
        from vector_store import build_index, query_index
        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        results = query_index(FAKE_VECTOR, top_k=2, persist_path=str(tmp_path))
        assert len(results) <= 2


# ══════════════════════════════════════════════════════════════════════════════
# RETRIEVER TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestRetriever:

    @patch("retriever.embed_query", return_value=FAKE_VECTOR)
    @patch("retriever.query_index", return_value=SAMPLE_SONGS[:2])
    def test_retrieve_returns_list_of_dicts(self, mock_index, mock_embed):
        """retrieve() should return a list of song dicts."""
        from retriever import retrieve
        results = retrieve("chill lofi for late night coding", top_k=2)
        assert isinstance(results, list)
        assert len(results) == 2

    @patch("retriever.embed_query", return_value=FAKE_VECTOR)
    @patch("retriever.query_index", return_value=SAMPLE_SONGS)
    def test_retrieve_calls_embed_query(self, mock_index, mock_embed):
        """retrieve() should call embed_query with the raw query string."""
        from retriever import retrieve
        retrieve("something energetic")
        mock_embed.assert_called_once_with("something energetic")

    @patch("retriever.embed_query", return_value=FAKE_VECTOR)
    @patch("retriever.query_index", return_value=SAMPLE_SONGS)
    def test_retrieve_passes_top_k_to_index(self, mock_index, mock_embed):
        """retrieve() should forward top_k to query_index."""
        from retriever import retrieve
        retrieve("happy pop", top_k=7)
        mock_index.assert_called_once_with(FAKE_VECTOR, top_k=7)


# ══════════════════════════════════════════════════════════════════════════════
# PARSE_QUERY TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestParseQuery:
    """
    Tests for query_parser.parse_query().

    parse_query lives in its own module (query_parser.py) with no Streamlit
    dependency, so these tests import it directly — no app.py gymnastics needed.
    """

    @patch("query_parser.requests.post")
    def test_parse_query_returns_required_keys(self, mock_post):
        """parse_query should always return genre, mood, and energy keys."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "message": {"content": '{"genre": "lofi", "mood": "chill", "energy": 0.35}'}
            },
        )
        from query_parser import parse_query
        result = parse_query("chill lofi for late night coding")

        assert "genre" in result
        assert "mood" in result
        assert "energy" in result

    @patch("query_parser.requests.post")
    def test_parse_query_energy_is_float(self, mock_post):
        """parse_query should return energy as a float."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "message": {"content": '{"genre": "pop", "mood": "happy", "energy": 0.85}'}
            },
        )
        from query_parser import parse_query
        result = parse_query("upbeat happy pop")

        assert isinstance(result["energy"], float)

    @patch("query_parser.requests.post", side_effect=Exception("Ollama down"))
    def test_parse_query_falls_back_on_error(self, mock_post):
        """parse_query should return safe defaults if Ollama is unreachable."""
        from query_parser import parse_query
        result = parse_query("some query")

        assert result["genre"] == ""
        assert result["mood"] == ""
        assert result["energy"] == 0.5

    @patch("query_parser.requests.post")
    def test_parse_query_lowercases_genre_and_mood(self, mock_post):
        """parse_query should normalize genre and mood to lowercase."""
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "message": {"content": '{"genre": "LoFi", "mood": "Chill", "energy": 0.4}'}
            },
        )
        from query_parser import parse_query
        result = parse_query("chill lofi vibes")

        assert result["genre"] == "lofi"
        assert result["mood"] == "chill"


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS (require live Ollama)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestIntegration:

    def test_embed_query_live(self):
        """Live: embed_query returns a real vector from Ollama."""
        from embedder import embed_query
        result = embed_query("chill lofi music for studying")
        assert isinstance(result, list)
        assert len(result) == 768

    def test_retrieve_live(self, tmp_path):
        """Live: full retrieve pipeline returns song dicts from a tmp index."""
        from vector_store import build_index, query_index
        from embedder import embed_query

        build_index(SAMPLE_SONGS, persist_path=str(tmp_path))
        query_vector = embed_query("something chill and relaxing")
        results = query_index(query_vector, top_k=2, persist_path=str(tmp_path))

        assert isinstance(results, list)
        assert len(results) >= 1
        for song in results:
            assert "title" in song
            assert "genre" in song