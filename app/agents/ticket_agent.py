from tools.ticket_tools import create_ticket


def ticket_agent(question: str, category: str):
    title = f"{category} support request"

    result = create_ticket.invoke(
        {
            "title": title,
            "description": question,
            "category": category
        }
    )

    return {
        "agent": "ticket_agent",
        "tool_result": result
    }