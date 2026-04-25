"""
retriever.py
 
Ties the embedder and vector store together.
Takes a raw natural language query, embeds it, and returns
candidate songs from ChromaDB for the reranker to score.
"""

from embedder import embed_query
from vector_store import query_index

def retrieve(query: str, top_k: int = 10) -> list[dict]:
    """
    Embed a natural language query and fetch the top_k
    most semantically similar songs from the vector store.

    Args:
        query: Free-text user input, e.g. "something chill for late night coding".
        top_k: Number of candidates to retrieve before reranking.

    Returns:
        List of song dicts ordered by vector similarity (closest first)
    """

    query_vector = embed_query(query)
    candidates = query_index(query_vector, top_k=top_k)
    return candidates

    
