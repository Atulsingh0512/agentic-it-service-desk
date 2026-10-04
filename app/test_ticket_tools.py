import re

from tools.ticket_tools import (
    create_ticket,
    get_ticket,
    update_ticket_status
)


create_result = create_ticket.invoke(
    {
        "title": "VPN connection issue",
        "description": "Employee cannot connect to company VPN.",
        "category": "VPN"
    }
)

print("========== CREATE TICKET ==========")
print(create_result)


ticket_match = re.search(
    r"Ticket ID: (\d+)",
    create_result
)

if not ticket_match:
    raise ValueError(
        "Could not extract ticket ID."
    )

ticket_id = int(
    ticket_match.group(1)
)


ticket_result = get_ticket.invoke(
    {
        "ticket_id": ticket_id
    }
)

print("\n========== TICKET DETAILS ==========")
print(ticket_result)


update_result = update_ticket_status.invoke(
    {
        "ticket_id": ticket_id,
        "status": "IN_PROGRESS"
    }
)

print("\n========== UPDATE TICKET ==========")
print(update_result)


updated_ticket = get_ticket.invoke(
    {
        "ticket_id": ticket_id
    }
)

print("\n========== UPDATED TICKET ==========")
print(updated_ticket)