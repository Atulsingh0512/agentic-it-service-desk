from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_core.tools import tool


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(path="qdrant_data")


@tool
def search_knowledge_base(query: str) -> str:
    """Search the company IT knowledge base and return relevant approved information with its source."""

    query_embedding = embedding_model.encode(query).tolist()

    results = client.query_points(
        collection_name="it_support",
        query=query_embedding,
        limit=3
    ).points

    if not results:
        return "NO_APPROVED_KNOWLEDGE_FOUND"

    context = ""

    for result in results:
        context += (
            f"Source: it_support.txt\n"
            f"Chunk ID: {result.payload['chunk_id']}\n"
            f"Content:\n{result.payload['text']}\n\n"
        )

    return context