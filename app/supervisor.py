import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt

from agents.authentication_agent import authentication_agent
from agents.general_agent import general_agent
from agents.password_agent import password_agent
from agents.rag_agent import rag_agent
from agents.ticket_agent import ticket_agent
from agents.ticket_lookup_agent import ticket_lookup_agent
from agents.ticket_update_agent import ticket_update_agent
from agents.vpn_agent import vpn_agent

from resilience import retry_operation


load_dotenv()


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)


llm = ChatOllama(
    model="qwen3:8b",
    base_url=OLLAMA_BASE_URL
)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    conversation_context: str
    intent: str
    agent: str
    tool_result: str
    category: str
    approved: bool
    sources: list


def execute_agent(
    agent_function,
    question,
    *args
):
    try:

        return retry_operation(
            lambda: agent_function(
                question,
                *args
            ),
            max_attempts=2,
            delay_seconds=1
        )

    except Exception as error:

        return {
            "agent": "system",
            "tool_result": (
                "I'm sorry, but I couldn't complete "
                "your request because an internal "
                "service is currently unavailable."
            ),
            "error": str(error),
            "sources": []
        }


def supervisor_node(state: State):

    question = state["messages"][-1].content

    conversation_context = state.get(
        "conversation_context",
        ""
    )

    prompt = f"""
You are the supervisor of an Enterprise IT Service Desk Agent.

Classify the user's CURRENT request into exactly ONE category.

Available categories:

VPN
AUTHENTICATION
PASSWORD
CREATE_TICKET
LOOKUP_TICKET
UPDATE_TICKET
KNOWLEDGE
OTHER

Classification rules:

VPN:
Use VPN only when the user is reporting an actual VPN problem
or asking the system to check or diagnose the current VPN service.

Examples:
- My VPN is not connecting
- Check the VPN status
- VPN is down
- My company VPN is not working

KNOWLEDGE:
Use KNOWLEDGE when the user is asking for instructions,
explanation, troubleshooting steps, policy information,
or general guidance that should be answered from the
company knowledge base.

Examples:
- What should I do if my VPN is not connecting?
- How can I troubleshoot a VPN problem?
- What are the steps for fixing a VPN connection?
- What should I do if VPN keeps disconnecting?

Important distinction:

If the user is reporting a current problem and wants the
system to check the service, use VPN.

If the user is asking how to solve, troubleshoot, or understand
the problem, use KNOWLEDGE.

AUTHENTICATION:
Problems related to authentication or login.

PASSWORD:
Password reset requests.

CREATE_TICKET:
The user wants to create, raise, open, or submit a support ticket.

LOOKUP_TICKET:
The user wants the status or details of an existing ticket.

UPDATE_TICKET:
The user wants to change an existing ticket status.

OTHER:
Anything else.

Previous conversation context:

{conversation_context}

CURRENT USER REQUEST:

{question}

Use the previous conversation only to understand references
such as "it", "that issue", "the previous problem", or
"what should I do next".

Classify the CURRENT request.

Return ONLY the category name.
"""

    try:

        response = retry_operation(
            lambda: llm.invoke(prompt),
            max_attempts=2,
            delay_seconds=1
        )

        intent = response.content.strip().upper()

    except Exception:

        return {
            "intent": "OTHER"
        }

    valid_intents = [
        "VPN",
        "AUTHENTICATION",
        "PASSWORD",
        "CREATE_TICKET",
        "LOOKUP_TICKET",
        "UPDATE_TICKET",
        "KNOWLEDGE",
        "OTHER",
    ]

    if intent not in valid_intents:
        intent = "OTHER"

    return {
        "intent": intent
    }


def approval_node(state: State):

    intent = state["intent"]

    question = state["messages"][-1].content

    if intent == "CREATE_TICKET":

        approval = interrupt(
            {
                "action": "CREATE_TICKET",
                "message": (
                    "The agent wants to create an IT support ticket."
                ),
                "request": question,
                "question": "Approve ticket creation?"
            }
        )

    elif intent == "PASSWORD":

        approval = interrupt(
            {
                "action": "RESET_PASSWORD",
                "message": (
                    "The agent wants to start the password reset process."
                ),
                "request": question,
                "question": "Approve password reset?"
            }
        )

    elif intent == "UPDATE_TICKET":

        approval = interrupt(
            {
                "action": "UPDATE_TICKET",
                "message": (
                    "The agent wants to change the status of an IT ticket."
                ),
                "request": question,
                "question": "Approve ticket status update?"
            }
        )

    else:

        approval = False

    return {
        "approved": bool(approval)
    }


def vpn_node(state: State):

    result = execute_agent(
        vpn_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def authentication_node(state: State):

    result = execute_agent(
        authentication_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def password_node(state: State):

    result = execute_agent(
        password_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def create_ticket_node(state: State):

    question = state["messages"][-1].content

    prompt = f"""
Identify the main IT issue category from this request.

Return ONLY one of:

VPN
AUTHENTICATION
PASSWORD
OTHER

User request:

{question}
"""

    try:

        response = retry_operation(
            lambda: llm.invoke(prompt),
            max_attempts=2,
            delay_seconds=1
        )

        category = response.content.strip().upper()

    except Exception:

        category = "OTHER"

    valid_categories = [
        "VPN",
        "AUTHENTICATION",
        "PASSWORD",
        "OTHER",
    ]

    if category not in valid_categories:
        category = "OTHER"

    result = execute_agent(
        ticket_agent,
        question,
        category
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "category": category,
        "sources": result.get("sources", [])
    }


def lookup_ticket_node(state: State):

    result = execute_agent(
        ticket_lookup_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def update_ticket_node(state: State):

    result = execute_agent(
        ticket_update_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def rag_node(state: State):

    question = state["messages"][-1].content

    conversation_context = state.get(
        "conversation_context",
        ""
    )

    try:

        result = retry_operation(
            lambda: rag_agent(
                question,
                conversation_context
            ),
            max_attempts=2,
            delay_seconds=1
        )

    except Exception:

        return {
            "agent": "system",
            "tool_result": (
                "I'm sorry, but I couldn't access "
                "the company knowledge base right now."
            ),
            "sources": []
        }

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def other_node(state: State):

    result = execute_agent(
        general_agent,
        state["messages"][-1].content
    )

    return {
        "agent": result["agent"],
        "tool_result": result["tool_result"],
        "sources": result.get("sources", [])
    }


def cancel_node(state: State):

    return {
        "agent": "system",
        "tool_result": "Action cancelled by user.",
        "sources": []
    }


def route_intent(state: State):

    intent = state["intent"]

    routes = {
        "VPN": "vpn",
        "AUTHENTICATION": "authentication",
        "PASSWORD": "approval",
        "CREATE_TICKET": "approval",
        "LOOKUP_TICKET": "lookup_ticket",
        "UPDATE_TICKET": "approval",
        "KNOWLEDGE": "rag",
        "OTHER": "other",
    }

    return routes.get(
        intent,
        "other"
    )


def route_approval(state: State):

    if not state.get("approved", False):

        return "cancel"

    routes = {
        "CREATE_TICKET": "create_ticket",
        "PASSWORD": "password",
        "UPDATE_TICKET": "update_ticket",
    }

    return routes.get(
        state["intent"],
        "cancel"
    )


graph = StateGraph(State)


graph.add_node(
    "supervisor",
    supervisor_node
)

graph.add_node(
    "approval",
    approval_node
)

graph.add_node(
    "vpn",
    vpn_node
)

graph.add_node(
    "authentication",
    authentication_node
)

graph.add_node(
    "password",
    password_node
)

graph.add_node(
    "create_ticket",
    create_ticket_node
)

graph.add_node(
    "lookup_ticket",
    lookup_ticket_node
)

graph.add_node(
    "update_ticket",
    update_ticket_node
)

graph.add_node(
    "rag",
    rag_node
)

graph.add_node(
    "other",
    other_node
)

graph.add_node(
    "cancel",
    cancel_node
)


graph.add_edge(
    START,
    "supervisor"
)


graph.add_conditional_edges(
    "supervisor",
    route_intent,
    {
        "vpn": "vpn",
        "authentication": "authentication",
        "approval": "approval",
        "lookup_ticket": "lookup_ticket",
        "rag": "rag",
        "other": "other",
    }
)


graph.add_conditional_edges(
    "approval",
    route_approval,
    {
        "create_ticket": "create_ticket",
        "password": "password",
        "update_ticket": "update_ticket",
        "cancel": "cancel",
    }
)


graph.add_edge(
    "vpn",
    END
)

graph.add_edge(
    "authentication",
    END
)

graph.add_edge(
    "password",
    END
)

graph.add_edge(
    "create_ticket",
    END
)

graph.add_edge(
    "lookup_ticket",
    END
)

graph.add_edge(
    "update_ticket",
    END
)

graph.add_edge(
    "rag",
    END
)

graph.add_edge(
    "other",
    END
)

graph.add_edge(
    "cancel",
    END
)


memory = MemorySaver()


app = graph.compile(
    checkpointer=memory
)


def run_cli():

    config = {
        "configurable": {
            "thread_id": "employee-cli"
        }
    }

    question = input(
        "\nEnter your IT request: "
    )

    response = app.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ],
            "conversation_context": ""
        },
        config=config
    )

    if "__interrupt__" in response:

        interrupt_data = (
            response["__interrupt__"][0].value
        )

        print(
            "\n========== APPROVAL REQUIRED =========="
        )

        print("\nAction:")
        print(interrupt_data["action"])

        print("\nMessage:")
        print(interrupt_data["message"])

        print("\nRequest:")
        print(interrupt_data["request"])

        print("\nQuestion:")
        print(interrupt_data["question"])

        approval = input(
            "\nApprove? (yes/no): "
        ).strip().lower()

        final_response = app.invoke(
            Command(
                resume=approval == "yes"
            ),
            config=config
        )

        print(
            "\n========== FINAL RESPONSE =========="
        )

        print("\nIntent:")
        print(final_response.get("intent"))

        print("\nAgent:")
        print(final_response.get("agent"))

        print("\nResult:")
        print(final_response.get("tool_result"))

    else:

        print(
            "\n========== RESPONSE =========="
        )

        print("\nIntent:")
        print(response.get("intent"))

        print("\nAgent:")
        print(response.get("agent"))

        print("\nResult:")
        print(response.get("tool_result"))

        sources = response.get(
            "sources",
            []
        )

        if sources:

            print("\nSources:")

            for source in sources:
                print(source)


if __name__ == "__main__":
    run_cli()