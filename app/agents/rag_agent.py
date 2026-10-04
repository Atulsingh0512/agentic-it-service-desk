import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_ollama import ChatOllama


load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


llm = ChatOllama(
    model="qwen3:8b",
    base_url=OLLAMA_BASE_URL
)


def retrieve_context(
    question: str,
    conversation_context: str = ""
):

    qdrant = QdrantClient(
        path="qdrant_data"
    )

    try:

        retrieval_query = question

        if conversation_context:

            retrieval_query = f"""
Previous conversation:

{conversation_context}

Current user question:

{question}
"""

        query_embedding = (
            embedding_model
            .encode(retrieval_query)
            .tolist()
        )

        results = qdrant.query_points(
            collection_name="it_support",
            query=query_embedding,
            limit=3
        ).points

        context = []
        sources = []

        for result in results:

            context.append(
                result.payload["text"]
            )

            sources.append(
                {
                    "source": "it_support.txt",
                    "chunk_id": result.payload["chunk_id"]
                }
            )

        return context, sources

    finally:

        qdrant.close()


def rag_agent(
    question: str,
    conversation_context: str = ""
):

    context, sources = retrieve_context(
        question,
        conversation_context
    )

    if not context:

        return {
            "agent": "rag_agent",
            "tool_result": (
                "I don't have enough information "
                "in the company knowledge base."
            ),
            "sources": []
        }

    knowledge = "\n\n".join(
        context
    )

    conversation = (
        conversation_context
        if conversation_context
        else "No previous conversation."
    )

    prompt = f"""
You are an Enterprise IT Service Desk Assistant.

Answer the user's CURRENT question using ONLY:

1. The approved company knowledge below.
2. The relevant previous conversation context.

Do not invent company-specific procedures.

If the answer cannot be supported by the
company knowledge base, say:

"I don't have enough information in the company knowledge base."

Previous conversation:

{conversation}

Approved company knowledge:

{knowledge}

Current user question:

{question}

Answer the current question directly and clearly.
"""

    response = llm.invoke(
        prompt
    )

    return {
        "agent": "rag_agent",
        "tool_result": response.content,
        "sources": sources
    }