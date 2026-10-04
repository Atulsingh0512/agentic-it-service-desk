from tools.vpn_tools import check_vpn_status
from tools.server_tools import check_server_status


TOOL_REGISTRY = {
    "check_vpn_status": check_vpn_status,
    "check_server_status": check_server_status
}