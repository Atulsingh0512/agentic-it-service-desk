from tools.rag_tools import search_knowledge_base


result = search_knowledge_base.invoke(
    {
        "query": "My VPN is not working"
    }
)

print(result)