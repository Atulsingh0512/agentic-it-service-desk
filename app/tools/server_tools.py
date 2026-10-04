from langchain_core.tools import tool


@tool
def check_server_status():
    """Check whether the company authentication server is operational."""
    return "Authentication server is operational"


@tool
def reset_password():
    """Start the approved company password reset process."""
    return "Password reset process has been initiated. The employee must complete the approved verification steps."