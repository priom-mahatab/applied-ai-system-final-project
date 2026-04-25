"""
vector_store.py
 
ChromaDB wrapper for the music catalog.
Songs are embedded once and persisted to data/chroma/ so subsequent
runs skip re-indexing. Call build_index() at app startup.
"""

import chromadb
from chromadb.config import Settings
from embedder import embed_song

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "songs"

def _get_collection(persist_path: str = CHROMA_PATH):
    """Return (or create) the ChromaDB collection"""
    chroma_client = chromadb.PersistentClient(
        path=persist_path,
        settings=Settings(anonymized_telemetry=False)
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection

def build_index(songs: list[dict], persist_path: str = CHROMA_PATH) -> None:
    """
    Embed all songs and store them in ChromaDB.
    Skips songs that are already indexed (idempotent).
    """
    collection = _get_collection(persist_path),
    existing = set(collection.get()["ids"])

    to_add_ids = []
    to_add_embeddings = []
    to_add_documents = []
    to_add_metadatas = []

    for song in songs:
        song_id = f"song_{song['id']}"
        if song_id in existing:
            continue

        print(f"    Indexing: {song['title']}...")
        vector = embed_song(song)

        to_add_ids.append(song_id)
        to_add_embeddings.append(vector)
        to_add_documents.append(
            f"{song['genre']} {song['mood']} energy {song['energy']}"
        )
        to_add_metadatas.append(
            {
                "id": song["id"],
                "title": song["title"],
                "artist": song["artist"],
                "genre": song["genre"],
                "mood": song["mood"],
                "energy": float(song["energy"]),
                "tempo_bpm": float(song["tempo_bpm"]),
                "valence": float(song["valence"]),
                "danceability": float(song["danceability"]),
                "acousticness": float(song["acousticness"]),
            }
        )
    
    if to_add_ids:
        collection.add(
            ids=to_add_ids,
            embeddings=to_add_embeddings,
            documents=to_add_documents,
            metadats=to_add_metadatas
        )
        print(f"    Indexed {len(to_add_ids)} new song(s).")
    else:
        print("     All songs already indexed. Skipping.")


def query_index(
        query_vector: list[float],
        top_k: int = 10,
        persist_path: str = CHROMA_PATH,
) -> list[dict]:
    """
    Find the top_k most similar songs to a query vector.
    Returns a list of song dicts reconstructed from stored metadata.
    """

    collection = _get_collection(persist_path)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["metadatas", "distances"]
    )

    songs = []
    for metadata in results["metadatas"][0]:
        songs.append(
            {
                "id": metadata["id"],
                "title": metadata["title"],
                "artist": metadata["artist"],
                "genre": metadata["genre"],
                "mood": metadata["mood"],
                "energy": metadata["energy"],
                "tempo_bpm": metadata["tempo_bpm"],
                "valence": metadata["energy"],
                "danceability": metadata["danceability"],
                "acousticness": metadata["acousticness"],
            }
        )

    return songs