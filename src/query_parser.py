"""
query_parser.py

Extracts structured music preferences (genre, mood, energy) from a
natural language query using Ollama's chat API.

Kept in its own module so it can be imported and tested independently
of app.py and Streamlit.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """You are a music preference extractor.
Given a natural language music query, return ONLY a JSON object with these keys:
- "genre": the closest matching genre from this list: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, classical, reggae, metal, folk, techno, r&b, country. Pick the single best match or empty string if unclear.
- "mood": the closest matching mood from this list: happy, chill, intense, focused, moody, relaxed, confident, reflective, uplifting, aggressive, nostalgic, euphoric, romantic, hopeful. Pick the single best match or empty string if unclear.
- "energy": a float between 0.0 and 1.0 representing the desired energy level. 0.0 is very calm, 1.0 is very intense.
No explanation, no markdown. Only valid JSON."""


def parse_query(query: str) -> dict:
    """
    Use Ollama to extract structured preferences from a natural language query.
    Returns a dict with keys: genre, mood, energy (float 0-1).
    Falls back to safe defaults if parsing fails.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                "stream": False,
            },
            timeout=15,
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"].strip()

        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)
        return {
            "genre": str(parsed.get("genre", "")).strip().lower(),
            "mood": str(parsed.get("mood", "")).strip().lower(),
            "energy": float(parsed.get("energy", 0.5)),
        }

    except Exception:
        # Safe fallback — retrieval still works, reranking uses energy only
        return {"genre": "", "mood": "", "energy": 0.5}