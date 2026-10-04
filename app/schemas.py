from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):

    title: str = Field(
        min_length=1
    )

    description: str = Field(
        min_length=1
    )

    category: str = Field(
        min_length=1
    )


class TicketCreateResponse(BaseModel):

    message: str
    ticket_id: int


class TicketStatusUpdateRequest(BaseModel):

    status: str = Field(
        min_length=1
    )


class AgentRequest(BaseModel):

    message: str = Field(
        min_length=1
    )

    thread_id: str = Field(
        default="api-user-001"
    )


class ApprovalRequest(BaseModel):

    thread_id: str

    approved: bool


class AgentResponse(BaseModel):

    thread_id: str

    status: str

    intent: str | None = None

    agent: str | None = None

    result: str | None = None

    sources: list = []

    approval: dict | None = None


class LoginRequest(BaseModel):

    username: str = Field(
        min_length=1
    )

    password: str = Field(
        min_length=1
    )


class TokenResponse(BaseModel):

    access_token: str

    token_type: str

    username: str

    role: str