from typing import Annotated, TypedDict

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

from tools.vpn_tools import check_vpn_status
from tools.server_tools import check_server_status, reset_password


class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str
    tool_result: str
    context: str
    sources: list


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

llm = ChatOllama(
    model="qwen3:8b"
)


def detect_intent(state: State):
    question = state["messages"][-1].content

    prompt = f"""
Classify this IT support request into exactly ONE category:

VPN
AUTHENTICATION
PASSWORD
OTHER

Return ONLY the category name.

User request:
{question}
"""

    response = llm.invoke(prompt)

    intent = response.content.strip().upper()

    if intent not in ["VPN", "AUTHENTICATION", "PASSWORD", "OTHER"]:
        intent = "OTHER"

    return {
        "intent": intent
    }


def vpn_node(state: State):
    result = check_vpn_status.invoke({})

    return {
        "tool_result": result
    }


def authentication_node(state: State):
    result = check_server_status.invoke({})

    return {
        "tool_result": result
    }


def password_node(state: State):
    result = reset_password.invoke({})

    return {
        "tool_result": result
    }


def retrieve_knowledge(state: State):
    question = state["messages"][-1].content

    query_embedding = embedding_model.encode(question).tolist()

    qdrant = QdrantClient(path="qdrant_data")

    try:
        results = qdrant.query_points(
            collection_name="it_support",
            query=query_embedding,
            limit=3
        ).points
    finally:
        qdrant.close()

    context = ""
    sources = []

    for result in results:
        context += result.payload["text"] + "\n\n"

        sources.append(
            {
                "source": "it_support.txt",
                "chunk_id": result.payload["chunk_id"]
            }
        )

    return {
        "context": context,
        "sources": sources
    }


def response_node(state: State):
    prompt = f"""
You are an Enterprise IT Service Desk Assistant.

Answer the user's question using the information below.

Tool result:
{state["tool_result"]}

Approved company knowledge:
{state["context"]}

Rules:
- Use the tool result when relevant.
- Use only the approved company knowledge for troubleshooting instructions.
- Do not invent company policies or troubleshooting steps.
- Do not add information from your general knowledge.
- If the information is insufficient, clearly say so.
- Give one concise answer.

User question:
{state["messages"][-1].content}
"""

    response = llm.invoke(prompt)

    return {
        "messages": [response]
    }


def route_intent(state: State):
    if state["intent"] == "VPN":
        return "vpn"

    if state["intent"] == "AUTHENTICATION":
        return "authentication"

    if state["intent"] == "PASSWORD":
        return "password"

    return "rag"


graph = StateGraph(State)

graph.add_node("intent", detect_intent)
graph.add_node("vpn", vpn_node)
graph.add_node("authentication", authentication_node)
graph.add_node("password", password_node)
graph.add_node("rag", retrieve_knowledge)
graph.add_node("response", response_node)

graph.add_edge(START, "intent")

graph.add_conditional_edges(
    "intent",
    route_intent,
    {
        "vpn": "vpn",
        "authentication": "authentication",
        "password": "password",
        "rag": "rag"
    }
)

graph.add_edge("vpn", "rag")
graph.add_edge("authentication", "rag")
graph.add_edge("password", "rag")

graph.add_edge("rag", "response")

graph.add_edge("response", END)

app = graph.compile()


result = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="My VPN is not working. What should I do?"
            )
        ],
        "intent": "",
        "tool_result": "",
        "context": "",
        "sources": []
    }
)


print("\nDetected Intent:")
print(result["intent"])

print("\nTool Result:")
print(result["tool_result"])

print("\nFinal Answer:")
print(result["messages"][-1].content)

print("\nSources:")
for source in result["sources"]:
    print(source)