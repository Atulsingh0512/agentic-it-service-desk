from langchain_core.tools import tool


@tool
def check_vpn_status():
    """Check whether the company VPN server is operational."""
    return "VPN server is operational"