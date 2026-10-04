from tools.vpn_tools import check_vpn_status


def vpn_agent(question: str):
    result = check_vpn_status.invoke({})

    return {
        "agent": "vpn_agent",
        "tool_result": result
    }