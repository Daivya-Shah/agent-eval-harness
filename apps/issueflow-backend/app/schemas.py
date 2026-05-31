from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models import ActivityEventType, IssuePriority, IssueStatus


class SLAStatus(str, Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    OVERDUE = "overdue"
    CLOSED = "closed"


# --- User ---


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# --- Comment ---


class CommentCreate(BaseModel):
    author_id: int
    body: str = Field(min_length=1)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    issue_id: int
    author_id: int
    body: str
    created_at: datetime
    author: UserRead | None = None


# --- Activity ---


class ActivityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    issue_id: int
    event_type: ActivityEventType
    old_value: str | None
    new_value: str | None
    created_at: datetime


# --- Issue ---


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: int | None = None
    due_at: datetime | None = None


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    priority: IssuePriority | None = None
    assignee_id: int | None = None
    due_at: datetime | None = None


class IssueStatusUpdate(BaseModel):
    status: IssueStatus


class IssueAssigneeUpdate(BaseModel):
    assignee_id: int | None = None


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime
    due_at: datetime | None
    resolved_at: datetime | None
    sla_status: SLAStatus | None = None
    assignee: UserRead | None = None


class IssueDetail(IssueRead):
    comments: list[CommentRead] = []
    activity_events: list[ActivityEventRead] = []


class IssueListResponse(BaseModel):
    items: list[IssueRead]
    total: int


# --- Search / filter ---


class IssueFilterParams(BaseModel):
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    assignee_id: int | None = None
    q: str | None = None


# --- Webhook ---


class WebhookIssuePayload(BaseModel):
    """Raw webhook payload; fields are intentionally loose for normalization."""

    model_config = ConfigDict(extra="allow")

    external_id: str | None = None
    id: str | int | None = None
    title: str | None = None
    issueTitle: str | None = None
    summary: str | None = None
    description: str | None = None
    body: str | None = None
    details: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    assignee_email: str | None = None
    assignee: str | int | None = None
    due_at: str | None = None
    due_date: str | None = None
    dueDate: str | None = None


class NormalizedIssuePayload(BaseModel):
    external_id: str
    title: str
    description: str | None = None
    priority: IssuePriority
    assignee_id: int | None = None
    due_at: datetime | None = None
    confidence: str = "high"
    notes: list[str] = []


class WebhookIngestResponse(BaseModel):
    issue: IssueRead
    created: bool
    confidence: str
    notes: list[str] = []
