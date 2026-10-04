from ollama import chat
from tool_registry import TOOL_REGISTRY


tools = [
    {
        "type": "function",
        "function": {
            "name": "check_vpn_status",
            "description": "Check whether the company VPN server is operational.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_server_status",
            "description": "Check whether the company authentication server is operational.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


messages = [
    {
        "role": "user",
        "content": "Is the company's authentication server working?"
    }
]


response = chat(
    model="qwen3:8b",
    messages=messages,
    tools=tools
)


if response.message.tool_calls:

    for tool_call in response.message.tool_calls:

        tool_name = tool_call.function.name

        tool_function = TOOL_REGISTRY.get(tool_name)

        if tool_function:
            result = tool_function()

            messages.append(response.message)

            messages.append(
                {
                    "role": "tool",
                    "content": result
                }
            )

            final_response = chat(
                model="qwen3:8b",
                messages=messages,
                tools=tools
            )

            print(final_response.message.content)

else:
    print(response.message.content)