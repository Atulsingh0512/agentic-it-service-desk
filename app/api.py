import time

from fastapi import (
    Depends,
    FastAPI,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from database import (
    create_audit_log,
    get_audit_logs,
    get_connection,
    initialize_database
)

from memory import (
    get_conversation_history,
    initialize_memory_table,
    save_message
)

from schemas import (
    AgentRequest,
    AgentResponse,
    ApprovalRequest,
    LoginRequest,
    TicketCreateRequest,
    TicketCreateResponse,
    TicketStatusUpdateRequest,
    TokenResponse
)

from tools.ticket_tools import (
    create_ticket,
    get_ticket,
    update_ticket_status
)

from supervisor import app as agent_app

from langgraph.types import Command

from jobs.queue import (
    agent_queue,
    check_redis_connection
)

from rq.job import Job

from logging_config import (
    configure_logging,
    get_logger
)

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    require_roles
)


configure_logging()

logger = get_logger(
    "api"
)


initialize_database()

initialize_memory_table()


api = FastAPI(
    title="Enterprise IT Service Desk Agent",
    description="Agentic AI IT Service Desk Backend",
    version="1.0.0"
)


api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.middleware("http")
async def request_logging_middleware(
    request,
    call_next
):

    start_time = time.time()

    logger.info(
        "Request started | method=%s | path=%s",
        request.method,
        request.url.path
    )

    try:

        response = await call_next(
            request
        )

        duration = (
            time.time() - start_time
        )

        logger.info(
            "Request completed | "
            "method=%s | "
            "path=%s | "
            "status=%s | "
            "duration=%.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration
        )

        return response

    except Exception:

        logger.exception(
            "Request failed | "
            "method=%s | "
            "path=%s",
            request.method,
            request.url.path
        )

        raise


@api.get("/")
def root():

    return {
        "application":
            "Enterprise IT Service Desk Agent",
        "status":
            "running"
    }


@api.get("/health")
def health():

    connection = None

    database_status = (
        "disconnected"
    )

    redis_status = (
        "disconnected"
    )

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT 1"
            )

            cursor.fetchone()

        database_status = (
            "connected"
        )

    except Exception as error:

        logger.error(
            "Database health check failed: %s",
            error
        )

    finally:

        if connection:
            connection.close()

    try:

        if check_redis_connection():

            redis_status = (
                "connected"
            )

    except Exception as error:

        logger.error(
            "Redis health check failed: %s",
            error
        )

    overall_status = (
        "healthy"
        if (
            database_status
            == "connected"
            and
            redis_status
            == "connected"
        )
        else
        "degraded"
    )

    return {
        "status":
            overall_status,
        "database":
            database_status,
        "redis":
            redis_status
    }


@api.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest
):

    user = authenticate_user(
        request.username,
        request.password
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid username or password."
            )
        )

    token = create_access_token(
        user["username"],
        user["role"]
    )

    logger.info(
        "User authenticated | username=%s | role=%s",
        user["username"],
        user["role"]
    )

    return {
        "access_token":
            token,
        "token_type":
            "bearer",
        "username":
            user["username"],
        "role":
            user["role"]
    }


@api.post(
    "/auth/token"
)
def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail=(
                "Invalid username or password."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )

    token = create_access_token(
        user["username"],
        user["role"]
    )

    logger.info(
        "OAuth2 authentication successful | "
        "username=%s | role=%s",
        user["username"],
        user["role"]
    )

    return {
        "access_token":
            token,
        "token_type":
            "bearer"
    }


@api.get("/auth/me")
def current_user(
    user=Depends(
        get_current_user
    )
):

    return {
        "id":
            user["id"],
        "username":
            user["username"],
        "role":
            user["role"],
        "is_active":
            user["is_active"]
    }


@api.get("/tickets")
def list_tickets(
    user=Depends(
        get_current_user
    )
):

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    description,
                    category,
                    status,
                    created_at
                FROM tickets
                ORDER BY created_at DESC
                """
            )

            tickets = cursor.fetchall()

        return [
            {
                "id": ticket[0],
                "title": ticket[1],
                "description": ticket[2],
                "category": ticket[3],
                "status": ticket[4],
                "created_at":
                    ticket[5].isoformat()
            }
            for ticket in tickets
        ]

    finally:

        connection.close()


@api.get("/audit-logs")
def audit_logs(
    user=Depends(
        require_roles(
            "IT_SUPPORT",
            "ADMIN"
        )
    )
):

    return get_audit_logs()


@api.get(
    "/conversations/{thread_id}"
)
def conversation_history(
    thread_id: str,
    user=Depends(
        get_current_user
    )
):

    return {
        "thread_id":
            thread_id,
        "messages":
            get_conversation_history(
                thread_id
            )
    }


@api.post(
    "/tickets",
    response_model=TicketCreateResponse
)
def create_ticket_api(
    request: TicketCreateRequest,
    user=Depends(
        get_current_user
    )
):

    result = create_ticket.invoke(
        {
            "title":
                request.title,
            "description":
                request.description,
            "category":
                request.category
        }
    )

    ticket_id = int(
        result.split(
            "Ticket ID: "
        )[1]
    )

    return {
        "message":
            result,
        "ticket_id":
            ticket_id
    }


@api.get(
    "/tickets/{ticket_id}"
)
def get_ticket_api(
    ticket_id: int,
    user=Depends(
        get_current_user
    )
):

    result = get_ticket.invoke(
        {
            "ticket_id":
                ticket_id
        }
    )

    if "was not found" in result:

        raise HTTPException(
            status_code=404,
            detail=result
        )

    return {
        "ticket_id":
            ticket_id,
        "details":
            result
    }


@api.patch(
    "/tickets/{ticket_id}/status"
)
def update_ticket_status_api(
    ticket_id: int,
    request: TicketStatusUpdateRequest,
    user=Depends(
        require_roles(
            "IT_SUPPORT",
            "ADMIN"
        )
    )
):

    result = update_ticket_status.invoke(
        {
            "ticket_id":
                ticket_id,
            "status":
                request.status
        }
    )

    if "was not found" in result:

        raise HTTPException(
            status_code=404,
            detail=result
        )

    if "Invalid status" in result:

        raise HTTPException(
            status_code=400,
            detail=result
        )

    return {
        "ticket_id":
            ticket_id,
        "message":
            result
    }


@api.post(
    "/agent/chat",
    response_model=AgentResponse
)
def agent_chat(
    request: AgentRequest,
    user=Depends(
        get_current_user
    )
):

    logger.info(
        "Synchronous agent request | "
        "username=%s | thread_id=%s",
        user["username"],
        request.thread_id
    )

    history = get_conversation_history(
        request.thread_id,
        limit=20
    )

    conversation_context = "\n".join(
        [
            f"{message['role'].upper()}: "
            f"{message['content']}"
            for message in history
        ]
    )

    save_message(
        thread_id=request.thread_id,
        role="user",
        content=request.message
    )

    config = {
        "configurable": {
            "thread_id":
                request.thread_id
        }
    }

    response = agent_app.invoke(
        {
            "messages": [
                {
                    "role":
                        "user",
                    "content":
                        request.message
                }
            ],
            "conversation_context":
                conversation_context
        },
        config=config
    )

    if "__interrupt__" in response:

        interrupt_data = response[
            "__interrupt__"
        ][0].value

        save_message(
            thread_id=request.thread_id,
            role="assistant",
            content=interrupt_data.get(
                "message",
                "Approval required."
            )
        )

        create_audit_log(
            thread_id=request.thread_id,
            user_request=request.message,
            intent=response.get(
                "intent"
            ),
            agent=None,
            action=interrupt_data.get(
                "action"
            ),
            status="APPROVAL_REQUIRED",
            result=interrupt_data.get(
                "message"
            )
        )

        return {
            "thread_id":
                request.thread_id,
            "status":
                "approval_required",
            "intent":
                response.get(
                    "intent"
                ),
            "approval":
                interrupt_data
        }

    result = response.get(
        "tool_result",
        ""
    )

    save_message(
        thread_id=request.thread_id,
        role="assistant",
        content=result
    )

    audit_status = (
        "FAILED"
        if response.get(
            "agent"
        ) == "system"
        else
        "COMPLETED"
    )

    create_audit_log(
        thread_id=request.thread_id,
        user_request=request.message,
        intent=response.get(
            "intent"
        ),
        agent=response.get(
            "agent"
        ),
        action=None,
        status=audit_status,
        result=result
    )

    return {
        "thread_id":
            request.thread_id,
        "status":
            (
                "failed"
                if audit_status == "FAILED"
                else
                "completed"
            ),
        "intent":
            response.get(
                "intent"
            ),
        "agent":
            response.get(
                "agent"
            ),
        "result":
            result,
        "sources":
            response.get(
                "sources",
                []
            )
    }


@api.post(
    "/agent/jobs"
)
def create_agent_job(
    request: AgentRequest,
    user=Depends(
        get_current_user
    )
):

    logger.info(
        "Background agent job requested | "
        "username=%s | thread_id=%s",
        user["username"],
        request.thread_id
    )

    try:

        history = get_conversation_history(
            request.thread_id,
            limit=20
        )

        conversation_context = "\n".join(
            [
                f"{message['role'].upper()}: "
                f"{message['content']}"
                for message in history
            ]
        )

        save_message(
            thread_id=request.thread_id,
            role="user",
            content=request.message
        )

        job = agent_queue.enqueue(
            "jobs.tasks.process_agent_request",
            request.message,
            request.thread_id,
            conversation_context
        )

        create_audit_log(
            thread_id=request.thread_id,
            user_request=request.message,
            intent=None,
            agent="background_worker",
            action="QUEUE_AGENT_JOB",
            status="QUEUED",
            result=job.id
        )

        return {
            "job_id":
                job.id,
            "thread_id":
                request.thread_id,
            "status":
                "queued"
        }

    except Exception as error:

        logger.exception(
            "Unable to queue agent job"
        )

        create_audit_log(
            thread_id=request.thread_id,
            user_request=request.message,
            intent=None,
            agent="background_worker",
            action="QUEUE_AGENT_JOB",
            status="FAILED",
            result=str(error)
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to queue "
                "background agent job."
            )
        )


@api.get(
    "/agent/jobs/{job_id}"
)
def get_agent_job(
    job_id: str,
    user=Depends(
        get_current_user
    )
):

    try:

        job = Job.fetch(
            job_id,
            connection=
                agent_queue.connection
        )

    except Exception:

        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    status = job.get_status(
        refresh=True
    )

    response = {
        "job_id":
            job.id,
        "status":
            status,
        "result":
            None,
        "error":
            None
    }

    if status == "finished":

        response["result"] = (
            job.result
        )

    elif status == "failed":

        response["error"] = (
            job.exc_info
        )

    return response


@api.post(
    "/agent/approve",
    response_model=AgentResponse
)
def agent_approve(
    request: ApprovalRequest,
    user=Depends(
        get_current_user
    )
):

    config = {
        "configurable": {
            "thread_id":
                request.thread_id
        }
    }

    response = agent_app.invoke(
        Command(
            resume=request.approved
        ),
        config=config
    )

    approval_status = (
        "APPROVED"
        if request.approved
        else
        "REJECTED"
    )

    result = response.get(
        "tool_result",
        "Action cancelled by user."
    )

    save_message(
        thread_id=request.thread_id,
        role="assistant",
        content=result
    )

    create_audit_log(
        thread_id=request.thread_id,
        user_request=
            "HITL approval decision",
        intent=response.get(
            "intent"
        ),
        agent=response.get(
            "agent"
        ),
        action="HITL_APPROVAL",
        status=approval_status,
        result=result
    )

    return {
        "thread_id":
            request.thread_id,
        "status":
            "completed",
        "intent":
            response.get(
                "intent"
            ),
        "agent":
            response.get(
                "agent"
            ),
        "result":
            result,
        "sources":
            response.get(
                "sources",
                []
            )
    }