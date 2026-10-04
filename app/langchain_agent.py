from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from tools.vpn_tools import check_vpn_status


llm = ChatOllama(
    model="qwen3:8b"
)

agent = create_agent(
    model=llm,
    tools=[check_vpn_status],
    system_prompt="You are an IT service desk assistant. Use tools when necessary to solve user problems."
)

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "My VPN is not working. Please check the VPN server status."
            }
        ]
    }
)

print(response["messages"][-1].content)