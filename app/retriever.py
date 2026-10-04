from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(path="qdrant_data")

query = "My VPN is not working"

query_embedding = embedding_model.encode(query).tolist()

results = client.query_points(
    collection_name="it_support",
    query=query_embedding,
    limit=3
).points


print("Query:", query)
print("Results found:", len(results))

for result in results:
    print("\nScore:", result.score)
    print("Chunk ID:", result.payload["chunk_id"])
    print("Content:")
    print(result.payload["text"])

client.close()