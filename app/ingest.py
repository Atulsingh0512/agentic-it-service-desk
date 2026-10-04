from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


with open("data/it_support.txt", "r", encoding="utf-8") as file:
    text = file.read()


sections = text.split("\n\n")

chunks = []

for section in sections:
    section = section.strip()

    if section:
        chunks.append(section)


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(path="qdrant_data")

first_embedding = embedding_model.encode(chunks[0]).tolist()


if client.collection_exists("it_support"):
    client.delete_collection("it_support")


client.create_collection(
    collection_name="it_support",
    vectors_config=VectorParams(
        size=len(first_embedding),
        distance=Distance.COSINE
    )
)


points = []

for index, chunk in enumerate(chunks):
    embedding = embedding_model.encode(chunk).tolist()

    points.append(
        PointStruct(
            id=index,
            vector=embedding,
            payload={
                "text": chunk,
                "chunk_id": index
            }
        )
    )


client.upsert(
    collection_name="it_support",
    points=points
)


print("RAG ingestion completed.")
print("Total chunks stored:", len(chunks))

client.close()