import re

from tools.ticket_tools import get_ticket


def ticket_lookup_agent(question: str):
    match = re.search(r"\b\d+\b", question)

    if not match:
        return {
            "agent": "ticket_lookup_agent",
            "tool_result": "Please provide a valid ticket ID."
        }

    ticket_id = int(match.group())

    result = get_ticket.invoke(
        {
            "ticket_id": ticket_id
        }
    )

    return {
        "agent": "ticket_lookup_agent",
        "tool_result": result
    }