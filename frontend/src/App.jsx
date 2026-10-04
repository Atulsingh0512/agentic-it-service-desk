import {
  Activity,
  Bot,
  CheckCircle2,
  Clock3,
  Database,
  LayoutDashboard,
  MessageSquare,
  RefreshCw,
  Send,
  Server,
  Ticket,
  XCircle
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [tickets, setTickets] = useState([]);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [approval, setApproval] = useState(null);
  const [backendStatus, setBackendStatus] = useState("checking");

  const [threadId] = useState(
    () => `frontend-${crypto.randomUUID()}`
  );

  const loadTickets = async () => {
    try {
      const response = await fetch(`${API_URL}/tickets`);

      if (!response.ok) {
        throw new Error("Unable to load tickets");
      }

      const data = await response.json();
      setTickets(data);
    } catch (error) {
      console.error("Ticket loading error:", error);
    }
  };

  const checkBackend = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      setBackendStatus("online");
    } catch {
      setBackendStatus("offline");
    }
  };

  useEffect(() => {
    loadTickets();
    checkBackend();

    const interval = setInterval(() => {
      loadTickets();
      checkBackend();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmedMessage
      }
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/agent/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: trimmedMessage,
            thread_id: threadId
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Agent request failed"
        );
      }

      if (data.status === "approval_required") {
        setApproval({
          ...data.approval,
          thread_id: threadId,
          intent: data.intent
        });

        setMessages((previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: "agent",
            content: data.approval.message,
            intent: data.intent
          }
        ]);
      } else {
        setMessages((previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: "agent",
            content: data.result,
            agent: data.agent,
            intent: data.intent,
            sources: data.sources || []
          }
        ]);

        await loadTickets();
      }
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "error",
          content: error.message
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approved) => {
    if (!approval || loading) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/agent/approve`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            thread_id: approval.thread_id,
            approved
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Approval request failed"
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "agent",
          content: data.result,
          agent: data.agent,
          intent: data.intent
        }
      ]);

      setApproval(null);

      await loadTickets();
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "error",
          content: error.message
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const refreshAll = async () => {
    await Promise.all([
      loadTickets(),
      checkBackend()
    ]);
  };

  const statistics = useMemo(() => {
    return {
      total: tickets.length,

      open: tickets.filter(
        (ticket) => ticket.status === "OPEN"
      ).length,

      inProgress: tickets.filter(
        (ticket) => ticket.status === "IN_PROGRESS"
      ).length,

      resolved: tickets.filter(
        (ticket) =>
          ticket.status === "RESOLVED" ||
          ticket.status === "CLOSED"
      ).length
    };
  }, [tickets]);

  const navigate = (page) => {
    setActivePage(page);

    if (
      page === "tickets" ||
      page === "dashboard"
    ) {
      loadTickets();
    }
  };

  return (
    <div className="app">

      <Sidebar
        activePage={activePage}
        navigate={navigate}
        backendStatus={backendStatus}
      />

      <main className="main-content">

        <TopBar
          activePage={activePage}
          refreshAll={refreshAll}
          loading={loading}
        />

        {activePage === "dashboard" && (
          <Dashboard
            statistics={statistics}
            tickets={tickets}
            navigate={navigate}
          />
        )}

        {activePage === "chat" && (
          <ChatPage
            messages={messages}
            message={message}
            setMessage={setMessage}
            sendMessage={sendMessage}
            loading={loading}
            approval={approval}
            handleApproval={handleApproval}
          />
        )}

        {activePage === "tickets" && (
          <TicketsPage
            tickets={tickets}
            loadTickets={loadTickets}
          />
        )}

      </main>

    </div>
  );
}


function Sidebar({
  activePage,
  navigate,
  backendStatus
}) {
  return (
    <aside className="sidebar">

      <div className="brand">

        <div className="brand-icon">
          <Bot size={23} />
        </div>

        <div>
          <h2>IT Service Desk</h2>
          <span>Agentic AI Platform</span>
        </div>

      </div>

      <nav className="navigation">

        <NavButton
          icon={<LayoutDashboard size={18} />}
          label="Dashboard"
          active={activePage === "dashboard"}
          onClick={() => navigate("dashboard")}
        />

        <NavButton
          icon={<MessageSquare size={18} />}
          label="AI Assistant"
          active={activePage === "chat"}
          onClick={() => navigate("chat")}
        />

        <NavButton
          icon={<Ticket size={18} />}
          label="Tickets"
          active={activePage === "tickets"}
          onClick={() => navigate("tickets")}
        />

      </nav>

      <div className="sidebar-bottom">

        <div className="system-status">

          <span
            className={`status-dot ${backendStatus}`}
          />

          <div>
            <strong>
              {backendStatus === "online"
                ? "System Online"
                : backendStatus === "offline"
                  ? "System Offline"
                  : "Checking System"}
            </strong>

            <span>
              FastAPI backend
            </span>
          </div>

        </div>

      </div>

    </aside>
  );
}


function NavButton({
  icon,
  label,
  active,
  onClick
}) {
  return (
    <button
      className={
        active
          ? "nav-button active"
          : "nav-button"
      }
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}


function TopBar({
  activePage,
  refreshAll,
  loading
}) {
  const titles = {
    dashboard: "Service Desk Dashboard",
    chat: "AI Service Desk Assistant",
    tickets: "Incident Tickets"
  };

  const subtitles = {
    dashboard:
      "Monitor enterprise IT support activity",
    chat:
      "Interact with the autonomous IT support agent",
    tickets:
      "View and monitor service desk incidents"
  };

  return (
    <header className="topbar">

      <div>
        <h1>{titles[activePage]}</h1>
        <p>{subtitles[activePage]}</p>
      </div>

      <button
        className="refresh-button"
        onClick={refreshAll}
        disabled={loading}
      >
        <RefreshCw
          size={16}
          className={loading ? "spin" : ""}
        />

        Refresh
      </button>

    </header>
  );
}


function Dashboard({
  statistics,
  tickets,
  navigate
}) {
  return (
    <section>

      <div className="stats-grid">

        <StatCard
          title="Total Tickets"
          value={statistics.total}
          icon={<Ticket size={20} />}
        />

        <StatCard
          title="Open"
          value={statistics.open}
          icon={<Clock3 size={20} />}
        />

        <StatCard
          title="In Progress"
          value={statistics.inProgress}
          icon={<Activity size={20} />}
        />

        <StatCard
          title="Resolved"
          value={statistics.resolved}
          icon={<CheckCircle2 size={20} />}
        />

      </div>

      <div className="dashboard-grid">

        <div className="panel">

          <div className="panel-header">

            <div>
              <h3>Recent Tickets</h3>
              <p>
                Live data from PostgreSQL
              </p>
            </div>

            <button
              className="text-button"
              onClick={() => navigate("tickets")}
            >
              View all
            </button>

          </div>

          {tickets.length === 0 ? (
            <EmptyState
              icon={<Database size={30} />}
              message="No tickets have been created."
            />
          ) : (
            <div className="ticket-list">

              {tickets
                .slice(0, 6)
                .map((ticket) => (
                  <TicketRow
                    key={ticket.id}
                    ticket={ticket}
                  />
                ))}

            </div>
          )}

        </div>

        <div className="panel agent-card">

          <div className="agent-card-icon">
            <Bot size={30} />
          </div>

          <h3>Enterprise AI Agent</h3>

          <p>
            Resolve IT issues, search the company
            knowledge base, manage tickets and
            perform approved actions.
          </p>

          <button
            className="primary-button"
            onClick={() => navigate("chat")}
          >
            <MessageSquare size={17} />
            Open AI Assistant
          </button>

        </div>

      </div>

      <div className="architecture-panel">

        <div className="panel-header">

          <div>
            <h3>Agentic Architecture</h3>
            <p>
              Current backend execution flow
            </p>
          </div>

          <Server size={20} />

        </div>

        <div className="architecture-flow">

          <ArchitectureNode
            icon={<MessageSquare />}
            title="User"
          />

          <Arrow />

          <ArchitectureNode
            icon={<Server />}
            title="FastAPI"
          />

          <Arrow />

          <ArchitectureNode
            icon={<Bot />}
            title="LangGraph"
          />

          <Arrow />

          <ArchitectureNode
            icon={<Database />}
            title="Tools / RAG / DB"
          />

        </div>

      </div>

    </section>
  );
}


function StatCard({
  title,
  value,
  icon
}) {
  return (
    <div className="stat-card">

      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}


function ChatPage({
  messages,
  message,
  setMessage,
  sendMessage,
  loading,
  approval,
  handleApproval
}) {
  return (
    <section className="chat-page">

      <div className="chat-container">

        <div className="chat-header">

          <div className="agent-avatar">
            <Bot size={20} />
          </div>

          <div>
            <strong>
              Enterprise IT Agent
            </strong>

            <span>
              LangGraph Supervisor
            </span>
          </div>

        </div>

        <div className="messages">

          {messages.length === 0 && (
            <div className="chat-empty">

              <div className="empty-bot-icon">
                <Bot size={40} />
              </div>

              <h3>
                How can I help?
              </h3>

              <p>
                Describe your IT issue or ask
                an enterprise IT question.
              </p>

              <div className="suggestion-list">

                <span>
                  VPN connection problem
                </span>

                <span>
                  Check my ticket
                </span>

                <span>
                  Password reset
                </span>

                <span>
                  Ask IT knowledge
                </span>

              </div>

            </div>
          )}

          {messages.map((item) => (
            <ChatMessage
              key={item.id}
              item={item}
            />
          ))}

          {loading && (
            <div className="typing-indicator">

              <span />
              <span />
              <span />

              <small>
                Agent is processing
              </small>

            </div>
          )}

        </div>

        {approval && (
          <ApprovalCard
            approval={approval}
            loading={loading}
            handleApproval={handleApproval}
          />
        )}

        <div className="chat-input">

          <input
            value={message}
            onChange={(event) =>
              setMessage(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Describe your IT issue..."
            disabled={loading}
          />

          <button
            onClick={sendMessage}
            disabled={
              loading ||
              !message.trim()
            }
          >
            <Send size={18} />
          </button>

        </div>

      </div>

    </section>
  );
}


function ChatMessage({ item }) {
  const isUser = item.role === "user";
  const isError = item.role === "error";

  return (
    <div
      className={
        isUser
          ? "chat-message user"
          : isError
            ? "chat-message error"
            : "chat-message agent"
      }
    >

      {!isUser && (
        <div className="small-agent-icon">

          {isError ? (
            <XCircle size={15} />
          ) : (
            <Bot size={15} />
          )}

        </div>
      )}

      <div className="message-bubble">

        <p>{item.content}</p>

        {(item.agent || item.intent) && (
          <div className="message-metadata">

            {item.agent && (
              <span>
                Agent: {item.agent}
              </span>
            )}

            {item.intent && (
              <span>
                Intent: {item.intent}
              </span>
            )}

          </div>
        )}

        {item.sources?.length > 0 && (
          <div className="sources">

            <strong>Sources</strong>

            {item.sources.map(
              (source, index) => (
                <span key={index}>
                  {source.source}
                  {" • "}
                  Chunk {source.chunk_id}
                </span>
              )
            )}

          </div>
        )}

      </div>

    </div>
  );
}


function ApprovalCard({
  approval,
  loading,
  handleApproval
}) {
  return (
    <div className="approval-card">

      <div className="approval-icon">
        <Clock3 size={20} />
      </div>

      <div className="approval-content">

        <strong>
          Approval Required
        </strong>

        <p>
          {approval.message}
        </p>

        <span>
          Action: {approval.action}
        </span>

      </div>

      <div className="approval-actions">

        <button
          className="approve-button"
          onClick={() =>
            handleApproval(true)
          }
          disabled={loading}
        >
          <CheckCircle2 size={16} />
          Approve
        </button>

        <button
          className="reject-button"
          onClick={() =>
            handleApproval(false)
          }
          disabled={loading}
        >
          <XCircle size={16} />
          Reject
        </button>

      </div>

    </div>
  );
}


function TicketsPage({
  tickets,
  loadTickets
}) {
  return (
    <section className="panel tickets-panel">

      <div className="panel-header">

        <div>
          <h3>All Tickets</h3>

          <p>
            Live incident data from PostgreSQL
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={loadTickets}
        >
          <RefreshCw size={15} />
          Refresh
        </button>

      </div>

      {tickets.length === 0 ? (
        <EmptyState
          icon={<Ticket size={32} />}
          message="No tickets have been created yet."
        />
      ) : (
        <div className="table-wrapper">

          <table>

            <thead>

              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Status</th>
                <th>Created</th>
              </tr>

            </thead>

            <tbody>

              {tickets.map((ticket) => (
                <tr key={ticket.id}>

                  <td className="ticket-id">
                    #{ticket.id}
                  </td>

                  <td>
                    <strong>
                      {ticket.title}
                    </strong>

                    <small>
                      {ticket.description}
                    </small>
                  </td>

                  <td>
                    {ticket.category}
                  </td>

                  <td>
                    <StatusBadge
                      status={ticket.status}
                    />
                  </td>

                  <td>
                    {formatDate(
                      ticket.created_at
                    )}
                  </td>

                </tr>
              ))}

            </tbody>

          </table>

        </div>
      )}

    </section>
  );
}


function TicketRow({ ticket }) {
  return (
    <div className="ticket-row">

      <div className="ticket-icon">
        <Ticket size={17} />
      </div>

      <div className="ticket-info">

        <strong>
          #{ticket.id} — {ticket.title}
        </strong>

        <span>
          {ticket.category}
        </span>

      </div>

      <StatusBadge
        status={ticket.status}
      />

    </div>
  );
}


function StatusBadge({ status }) {
  return (
    <span
      className={`status-badge ${status.toLowerCase()}`}
    >
      {status.replace("_", " ")}
    </span>
  );
}


function ArchitectureNode({
  icon,
  title
}) {
  return (
    <div className="architecture-node">
      {icon}
      <span>{title}</span>
    </div>
  );
}


function Arrow() {
  return (
    <div className="architecture-arrow">
      →
    </div>
  );
}


function EmptyState({
  icon,
  message
}) {
  return (
    <div className="empty-state">
      {icon}
      <p>{message}</p>
    </div>
  );
}


function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
}


export default App;