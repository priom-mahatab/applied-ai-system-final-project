"""
embedder.py

Converts songs and user queries into embedding vectors using Ollama
running locally. No API key or internet connection required after setup.

Requirements:
  - Ollama installed and running (`ollama serve`)
  - nomic-embed-text model pulled (`ollama pull nomic-embed-text`)
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def _embed(text: str) -> list[float]:
    """Send text to Ollama and return the embedding vector."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": EMBED_MODEL, "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


def embed_song(song: dict) -> list[float]:
    """
    Convert a song dict into an embedding vector.
    We build a natural language description so the embedding captures
    semantic meaning rather than just raw numbers.
    """
    description = (
        f"A {song['genre']} song with a {song['mood']} mood. "
        f"Energy level {song['energy']:.0%}, "
        f"tempo {song['tempo_bpm']} BPM, "
        f"danceability {song['danceability']:.0%}, "
        f"acousticness {song['acousticness']:.0%}, "
        f"valence {song['valence']:.0%}."
    )
    return _embed(description)


def embed_query(query: str) -> list[float]:
    """Convert a free-text user query into an embedding vector."""
    return _embed(query)