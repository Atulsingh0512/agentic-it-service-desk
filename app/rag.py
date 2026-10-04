from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_ollama import ChatOllama


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient(path="qdrant_data")

llm = ChatOllama(
    model="qwen3:8b"
)


def retrieve_context(query):
    query_embedding = embedding_model.encode(query).tolist()

    results = client.query_points(
        collection_name="it_support",
        query=query_embedding,
        limit=3
    ).points

    context = ""

    for result in results:
        context += result.payload["text"] + "\n\n"

    return context


question = "My VPN is not working. What should I do?"

context = retrieve_context(question)


prompt = f"""
You are an Enterprise IT Support Assistant.

Answer the user's question using only the provided company knowledge.

If the knowledge does not contain the answer, say:
"I don't have enough information in the company knowledge base."

Company knowledge:
{context}

User question:
{question}
"""


response = llm.invoke(prompt)


print("\nAnswer:")
print(response.content)