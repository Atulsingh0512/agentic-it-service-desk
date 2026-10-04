from tools.server_tools import reset_password


def password_agent(question: str):
    result = reset_password.invoke({})

    return {
        "agent": "password_agent",
        "tool_result": result
    }