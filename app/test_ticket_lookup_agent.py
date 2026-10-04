from agents.ticket_lookup_agent import ticket_lookup_agent


result = ticket_lookup_agent(
    "What is the status of ticket 3?"
)

print("========== TICKET LOOKUP AGENT ==========")
print(result["agent"])

print("\n========== TOOL RESULT ==========")
print(result["tool_result"])