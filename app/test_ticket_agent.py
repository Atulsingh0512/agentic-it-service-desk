from agents.ticket_agent import ticket_agent


result = ticket_agent(
    "My VPN is still not working. Please create a ticket.",
    "VPN"
)

print("========== TICKET AGENT ==========")
print(result["agent"])

print("\n========== TOOL RESULT ==========")
print(result["tool_result"])