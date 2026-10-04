import re

from tools.ticket_tools import update_ticket_status


def ticket_update_agent(question: str):

    ticket_match = re.search(
        r"\bticket\s*(\d+)\b",
        question,
        re.IGNORECASE
    )

    if not ticket_match:
        return {
            "agent": "ticket_update_agent",
            "tool_result": "Please provide a valid ticket ID."
        }

    ticket_id = int(ticket_match.group(1))

    question_lower = question.lower()

    if "close" in question_lower:
        status = "CLOSED"

    elif "resolve" in question_lower:
        status = "RESOLVED"

    elif "progress" in question_lower:
        status = "IN_PROGRESS"

    elif "open" in question_lower:
        status = "OPEN"

    else:
        return {
            "agent": "ticket_update_agent",
            "tool_result": (
                "Please specify the new ticket status."
            )
        }

    result = update_ticket_status.invoke(
        {
            "ticket_id": ticket_id,
            "status": status
        }
    )

    return {
        "agent": "ticket_update_agent",
        "tool_result": result
    }