"""
embedder.py
 
Converts songs and user queries into numeric feature vectors using Claude.
Instead of a traditional embedding model, we prompt Claude to extract
semantic features and return them as a JSON vector. This keeps the
embedding transparent and inspectable.
"""

import json
import anthropic

# Stable key order — both song and query vectors must use the same order
# so cosine similarity comparisons are valid.

FEATURE_KEYS = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave", "indie_pop",
    "hip_hop", "classical", "reggae", "metal", "folk", "techno", "rnb",
    "country", "happy", "chill", "intense", "focused", "moody", "relaxed",
    "confident", "reflective", "uplifting", "aggressive", "nostalgic",
    "euphoric", "romantic", "hopeful", "energy", "danceability",
    "acousticness", "valence",
]

_SCHEMA = """{
  "pop": float, "lofi": float, "rock": float, "ambient": float,
  "jazz": float, "synthwave": float, "indie_pop": float, "hip_hop": float,
  "classical": float, "reggae": float, "metal": float, "folk": float,
  "techno": float, "rnb": float, "country": float,
  "happy": float, "chill": float, "intense": float, "focused": float,
  "moody": float, "relaxed": float, "confident": float, "reflective": float,
  "uplifting": float, "aggressive": float, "nostalgic": float,
  "euphoric": float, "romantic": float, "hopeful": float,
  "energy": float, "danceability": float, "acousticness": float, "valence": float
}"""

SONG_SYSTEM_PROMPT = f"""You are a music feature extractor.
Given a song description, return ONLY a JSON object with exactly these keys
and float values between 0.0 and 1.0:
{_SCHEMA}
No explanation, no markdown, no extra keys. Only valid JSON."""

QUERY_SYSTEM_PROMPT = f"""You are a music taste interpreter.
Given a natural language description of what a user wants to listen to,
return ONLY a JSON object with exactly these keys and float values between
0.0 and 1.0 representing how much each trait fits the request:
{_SCHEMA}
No explanation, no markdown, no extra keys. Only valid JSON."""


def _call_claude(system_prompt: str, user_message: str) -> list[float]:
    """Call Claude and parse the returned JSON in a float vector."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4]
        raw = raw.strip()

    parsed = json.loads(raw)
    return [float(parsed.get(k, 0.0)) for k in FEATURE_KEYS]

def embed_song(song: dict) -> list[float]:
    """Convert a song dict into a feature vector via Claude."""
    description = (
        f"Genre: {song['genre']}. ",
        f"Mood: {song['mood']}. ",
        f"Energy: {song['energy']}. ",
        f"Tempo: {song['tempo_bpm']} BPM. "
        f"Valence: {song['valence']}. "
        f"Danceability: {song['danceability']}. "
        f"Acousticness: {song['acousticness']}."
    )

    return _call_claude(SONG_SYSTEM_PROMPT, description)

def embed_query(query: str) -> list[str]:
    """Convert a free-text user query into a feature vector via Claude"""
    return _call_claude(QUERY_SYSTEM_PROMPT, query)