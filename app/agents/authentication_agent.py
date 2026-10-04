from tools.server_tools import check_server_status


def authentication_agent(question: str):
    result = check_server_status.invoke({})

    return {
        "agent": "authentication_agent",
        "tool_result": result
    }