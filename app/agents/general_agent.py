import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama


load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


llm = ChatOllama(
    model="qwen3:8b",
    base_url=OLLAMA_BASE_URL
)


def general_agent(question: str):

    prompt = f"""
You are an Enterprise IT Service Desk Assistant.

Answer the user's question clearly and professionally.

Do not invent company-specific policies, systems, credentials,
or procedures.

If the question requires company-specific information that you
do not have, clearly say that you do not have that information.

User question:
{question}
"""

    response = llm.invoke(prompt)

    return {
        "agent": "general_agent",
        "tool_result": response.content
    }