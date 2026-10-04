AGENT_TEST_CASES = [

    {
        "id": "VPN_001",
        "input":
            "My company VPN is not connecting.",
        "expected_intent":
            "VPN"
    },

    {
        "id": "VPN_002",
        "input":
            "Is the VPN server operational?",
        "expected_intent":
            "VPN"
    },

    {
        "id": "AUTH_001",
        "input":
            "I cannot log into the company system.",
        "expected_intent":
            "AUTHENTICATION"
    },

    {
        "id": "AUTH_002",
        "input":
            "The authentication server is not allowing me to login.",
        "expected_intent":
            "AUTHENTICATION"
    },

    {
        "id": "PASSWORD_001",
        "input":
            "I forgot my password and need a reset.",
        "expected_intent":
            "PASSWORD"
    },

    {
        "id": "PASSWORD_002",
        "input":
            "Please reset my company password.",
        "expected_intent":
            "PASSWORD"
    },

    {
        "id": "CREATE_TICKET_001",
        "input":
            "Create a support ticket because my laptop VPN is broken.",
        "expected_intent":
            "CREATE_TICKET"
    },

    {
        "id": "CREATE_TICKET_002",
        "input":
            "Raise an IT ticket for my login problem.",
        "expected_intent":
            "CREATE_TICKET"
    },

    {
        "id": "LOOKUP_TICKET_001",
        "input":
            "What is the status of ticket 1?",
        "expected_intent":
            "LOOKUP_TICKET"
    },

    {
        "id": "LOOKUP_TICKET_002",
        "input":
            "Show me the details of ticket 25.",
        "expected_intent":
            "LOOKUP_TICKET"
    },

    {
        "id": "UPDATE_TICKET_001",
        "input":
            "Close ticket 1.",
        "expected_intent":
            "UPDATE_TICKET"
    },

    {
        "id": "UPDATE_TICKET_002",
        "input":
            "Mark ticket 10 as resolved.",
        "expected_intent":
            "UPDATE_TICKET"
    },

    {
        "id": "KNOWLEDGE_001",
        "input":
            "What should I do if the VPN server is working but I still cannot connect?",
        "expected_intent":
            "KNOWLEDGE"
    },

    {
        "id": "KNOWLEDGE_002",
        "input":
            "What should employees do after repeated authentication failures?",
        "expected_intent":
            "KNOWLEDGE"
    },

    {
        "id": "KNOWLEDGE_003",
        "input":
            "What should I do if self-service password reset fails?",
        "expected_intent":
            "KNOWLEDGE"
    },

    {
        "id": "SECURITY_001",
        "input":
            "Should I share my authentication code with another employee?",
        "expected_intent":
            "KNOWLEDGE"
    },

    {
        "id": "OTHER_001",
        "input":
            "What is the capital of France?",
        "expected_intent":
            "OTHER"
    }

]