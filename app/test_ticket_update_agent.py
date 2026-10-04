from agents.ticket_update_agent import ticket_update_agent


result = ticket_update_agent(
    "Close ticket 4."
)

print(
    "========== TICKET UPDATE AGENT =========="
)

print(
    result["agent"]
)

print(
    "\n========== TOOL RESULT =========="
)

print(
    result["tool_result"]
)