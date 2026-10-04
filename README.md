# Enterprise IT Service Desk & Incident Resolution Agent

An enterprise-style **Agentic AI Service Desk** built with **Python, FastAPI, LangGraph, LangChain, Ollama/Qwen3, RAG, Qdrant, PostgreSQL, Redis/RQ, JWT authentication, RBAC, and React**.

The system receives an employee's IT request, classifies the intent, routes it to a specialized agent, uses tools or company knowledge when required, pauses for human approval for sensitive actions, and records activity through persistent storage and audit logs.

## Key Capabilities

* Agentic intent classification and routing
* Specialized IT service agents
* VPN status checking
* Authentication server checking
* Password-reset workflow
* Ticket creation, lookup, and status updates
* Human-in-the-loop approval for sensitive operations
* Retrieval-Augmented Generation (RAG)
* Qdrant vector search
* Local LLM inference using Ollama and Qwen3
* PostgreSQL persistence
* Conversation memory
* Redis + RQ background jobs
* JWT authentication
* Role-Based Access Control (RBAC)
* Structured application logging
* Audit trail
* Retry/error handling
* React-based dynamic dashboard
* Docker Compose deployment
* Automated pytest tests
* Agent evaluation suite

---

## Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │ Dashboard / Chat /      │
                    │ Tickets                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI API       │
                    │ Auth / Agent / Tickets  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   LangGraph Supervisor  │
                    │ Intent Classification   │
                    │ Routing + HITL          │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
       Specialized Agents       RAG Agent       General Agent
              │                  │
              ▼                  ▼
          IT Tools          Qdrant + Embeddings
              │                  │
              └──────────┬───────┘
                         ▼
                ┌──────────────────┐
                │   PostgreSQL     │
                │ Tickets / Users  │
                │ Audit / Memory   │
                └──────────────────┘

                ┌──────────────────┐
                │ Redis + RQ       │
                │ Background Jobs  │
                └──────────────────┘
```

---

## Agentic Workflow

```text
User Request
     │
     ▼
FastAPI
     │
     ▼
LangGraph Supervisor
     │
     ├── VPN ───────────────► VPN Agent ─────► VPN Tool
     │
     ├── AUTHENTICATION ────► Authentication Agent
     │                                      └─► Server Tool
     │
     ├── PASSWORD ──────────► Password Agent
     │                                      └─► Approval
     │
     ├── CREATE_TICKET ─────► Ticket Agent ─► Approval ─► PostgreSQL
     │
     ├── LOOKUP_TICKET ─────► Ticket Lookup ─► PostgreSQL
     │
     ├── UPDATE_TICKET ─────► Ticket Update ─► Approval ─► PostgreSQL
     │
     ├── KNOWLEDGE ─────────► RAG Agent ────► Qdrant ─► Qwen3
     │
     └── OTHER ─────────────► General Agent ─► Qwen3
```

---

## Specialized Agents

### VPN Agent

Handles current VPN service-status requests and invokes the VPN status tool.

### Authentication Agent

Checks the authentication server status.

### Password Agent

Handles the password-reset workflow and requires human approval before proceeding.

### Ticket Agent

Creates IT service desk tickets in PostgreSQL after human approval.

### Ticket Lookup Agent

Retrieves an existing ticket using its ticket ID.

### Ticket Update Agent

Updates ticket status and requires human approval.

### RAG Agent

Retrieves relevant information from the company IT knowledge base using vector similarity search and generates a grounded response with the local LLM.

### General Agent

Handles general IT questions that do not require a company-specific workflow or knowledge-base retrieval.

---

## RAG Pipeline

```text
Company Knowledge Base
        │
        ▼
Sentence Transformer Embeddings
        │
        ▼
Qdrant Vector Store
        │
        ▼
Similarity Search
        │
        ▼
Relevant Knowledge Chunks
        │
        ▼
Qwen3 via Ollama
        │
        ▼
Grounded Answer + Sources
```

Knowledge source:

```text
data/it_support.txt
```

The RAG agent also incorporates relevant conversation context when constructing the retrieval query and generation prompt.

---

## Human-in-the-Loop

Sensitive actions do not execute immediately.

Examples:

* Password reset
* Ticket creation
* Ticket status update

Workflow:

```text
User Request
     │
     ▼
Supervisor
     │
     ▼
Sensitive Action Detected
     │
     ▼
Approval Required
     │
     ▼
Human Approval
     │
     ▼
Tool Execution
     │
     ▼
Result + Audit Log
```

---

## Technology Stack

| Layer               | Technology              |
| ------------------- | ----------------------- |
| Frontend            | React + Vite            |
| Backend             | FastAPI                 |
| Agent Orchestration | LangGraph               |
| LLM Framework       | LangChain               |
| Local LLM           | Ollama + Qwen3          |
| Embeddings          | Sentence Transformers   |
| Vector Database     | Qdrant                  |
| Database            | PostgreSQL              |
| Background Jobs     | Redis + RQ              |
| Authentication      | JWT                     |
| Authorization       | RBAC                    |
| Testing             | Pytest                  |
| Containerization    | Docker + Docker Compose |
| Language            | Python 3.11             |

---

## Authentication & RBAC

Supported roles:

```text
EMPLOYEE
IT_SUPPORT
ADMIN
```

Protected functionality includes:

* User identity
* Agent requests
* Ticket access
* Ticket status updates
* Audit logs

Administrative/support operations are protected using role-based authorization.

---

## Background Processing

Redis and RQ are used for asynchronous agent processing.

```text
FastAPI
   │
   ▼
Redis Queue
   │
   ▼
RQ Worker
   │
   ▼
LangGraph Agent
   │
   ▼
Result + PostgreSQL Audit
```

Queue:

```text
agent_tasks
```

---

## Persistence

PostgreSQL stores:

```text
tickets
users
conversation_messages
agent_audit_logs
```

Conversation history allows the system to retain context across requests using a thread ID.

---

## Resilience

The application includes retry handling for agent operations.

```text
Operation
   │
   ├── Attempt 1
   │
   ├── Failure → Retry
   │
   └── Attempt 2
          │
          ├── Success
          └── Failure → Error Handling
```

Structured application logging is enabled for backend and worker processes.

---

## API Endpoints

### Authentication

```text
POST /auth/login
POST /auth/token
GET  /auth/me
```

### Agent

```text
POST /agent/chat
POST /agent/approve
POST /agent/jobs
GET  /agent/jobs/{job_id}
```

### Tickets

```text
GET /tickets
```

### Audit

```text
GET /audit-logs
```

### Conversations

```text
GET /conversations/{thread_id}
```

### Health

```text
GET /health
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

## Evaluation

The project includes an agent evaluation suite containing **17 test cases** across the supported intent categories.

```text
Total Tests: 17
Correct:     16
Accuracy:    94.12%
```

Evaluation categories:

```text
VPN
AUTHENTICATION
PASSWORD
CREATE_TICKET
LOOKUP_TICKET
UPDATE_TICKET
KNOWLEDGE
OTHER
```

---

## Automated Tests

The automated pytest suite currently passes:

```text
9 passed
```

Run:

```cmd
pytest
```

---

## Project Structure

```text
Enterprise_IT_Service_Desk_Agent/
│
├── app/
│   ├── agents/
│   │   ├── authentication_agent.py
│   │   ├── general_agent.py
│   │   ├── password_agent.py
│   │   ├── rag_agent.py
│   │   ├── ticket_agent.py
│   │   ├── ticket_lookup_agent.py
│   │   ├── ticket_update_agent.py
│   │   └── vpn_agent.py
│   │
│   ├── jobs/
│   │   ├── queue.py
│   │   └── tasks.py
│   │
│   ├── tools/
│   │   ├── server_tools.py
│   │   ├── ticket_tools.py
│   │   └── vpn_tools.py
│   │
│   ├── api.py
│   ├── auth.py
│   ├── database.py
│   ├── logging_config.py
│   ├── memory.py
│   ├── resilience.py
│   ├── supervisor.py
│   ├── worker.py
│   └── create_user.py
│
├── data/
│   └── it_support.txt
│
├── evaluation/
│   ├── agent_test_cases.py
│   └── evaluate_agent.py
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       └── main.jsx
│
├── tests/
│
├── qdrant_data/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Local Setup

### 1. Clone the project

```bash
git clone <your-repository-url>
cd Enterprise_IT_Service_Desk_Agent
```

### 2. Create virtual environment

Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/service_desk
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=YOUR_SECRET_KEY
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD
OLLAMA_BASE_URL=http://localhost:11434
```

Never commit `.env` or real credentials to Git.

### 5. Start Ollama

Make sure Ollama is running and Qwen3 is available:

```cmd
ollama run qwen3:8b
```

### 6. Start the backend

```cmd
cd app
python -m uvicorn api:api --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 7. Start the RQ worker

Open another terminal:

```cmd
cd app
python worker.py
```

### 8. Start the frontend

```cmd
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Docker Setup

Build:

```cmd
docker compose build
```

Start:

```cmd
docker compose up -d
```

Check services:

```cmd
docker compose ps
```

Expected services:

```text
service_desk_backend
service_desk_postgres
service_desk_redis
service_desk_worker
```

Stop:

```cmd
docker compose down
```

---

## Security Notes

For production deployment:

* Use a strong randomly generated JWT secret.
* Rotate development credentials before deployment.
* Store secrets using a proper secret-management solution.
* Use HTTPS.
* Restrict database access.
* Configure production CORS.
* Avoid exposing PostgreSQL and Redis publicly.
* Use least-privilege database users.
* Add production-grade monitoring and alerting.

---

## What This Project Demonstrates

This is an **end-to-end Agentic AI system**, not just an LLM chatbot.

```text
LLM
│
├── Prompt Engineering
├── Intent Classification
├── Agent Routing
├── Tool Calling
├── RAG
├── Vector Search
├── Conversation Memory
├── Human-in-the-Loop
├── LangGraph State Management
├── Background Processing
├── Authentication
├── RBAC
├── Auditability
├── Retry Handling
├── API Development
├── Frontend Integration
├── Testing
├── Evaluation
└── Dockerization
```

The architecture demonstrates how Agentic AI can be combined with enterprise application patterns such as **security, persistence, asynchronous processing, human approval, auditability, retrieval, and API-driven workflows**