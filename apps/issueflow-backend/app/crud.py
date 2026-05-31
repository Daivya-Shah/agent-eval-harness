from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    ActivityEventType,
    Comment,
    Issue,
    IssueStatus,
    User,
    WebhookIngestLog,
)
from app.schemas import (
    CommentCreate,
    IssueAssigneeUpdate,
    IssueCreate,
    IssueFilterParams,
    IssueRead,
    IssueStatusUpdate,
    IssueUpdate,
    NormalizedIssuePayload,
)
from app.services.audit import log_activity
from app.services.clock import utc_now
from app.services.search import apply_issue_filters
from app.services.sla import attach_sla_status
from app.services.state_machine import (
    StateTransitionError,
    assert_issue_editable,
    validate_transition,
)

# Re-export for route handlers and tests.
__all__ = ["StateTransitionError"]


def _issue_to_read(issue: Issue) -> IssueRead:
    data = IssueRead.model_validate(issue)
    data.sla_status = attach_sla_status(issue)
    return data


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).one_or_none()


def list_users(db: Session) -> list[User]:
    stmt = select(User).order_by(User.name)
    return list(db.scalars(stmt).all())


def create_user(db: Session, *, email: str, name: str) -> User:
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_issue(db: Session, issue_id: int) -> Issue | None:
    stmt = (
        select(Issue)
        .options(
            joinedload(Issue.assignee),
            joinedload(Issue.comments).joinedload(Comment.author),
            joinedload(Issue.activity_events),
        )
        .where(Issue.id == issue_id)
    )
    return db.scalars(stmt).unique().one_or_none()


def get_issue_by_external_id(db: Session, external_id: str) -> Issue | None:
    stmt = select(Issue).where(Issue.external_id == external_id)
    return db.scalars(stmt).one_or_none()


def list_issues(db: Session, filters: IssueFilterParams) -> tuple[list[IssueRead], int]:
    issues, total = apply_issue_filters(db, filters)
    return [_issue_to_read(i) for i in issues], total


def create_issue(db: Session, data: IssueCreate) -> Issue:
    if data.assignee_id is not None and get_user(db, data.assignee_id) is None:
        raise HTTPException(status_code=400, detail=f"Unknown assignee_id: {data.assignee_id}")

    issue = Issue(
        title=data.title,
        description=data.description,
        priority=data.priority,
        assignee_id=data.assignee_id,
        due_at=data.due_at,
        status=IssueStatus.OPEN,
    )
    db.add(issue)
    db.flush()
    log_activity(
        db,
        issue_id=issue.id,
        event_type=ActivityEventType.ISSUE_CREATED,
        new_value=issue.title,
    )
    db.commit()
    db.refresh(issue)
    return issue


def update_issue(db: Session, issue: Issue, data: IssueUpdate) -> Issue:
    assert_issue_editable(issue.status)

    if data.title is not None and data.title != issue.title:
        log_activity(
            db,
            issue_id=issue.id,
            event_type=ActivityEventType.ISSUE_UPDATED,
            old_value=issue.title,
            new_value=data.title,
        )
        issue.title = data.title

    if data.description is not None and data.description != issue.description:
        issue.description = data.description

    if data.priority is not None and data.priority != issue.priority:
        log_activity(
            db,
            issue_id=issue.id,
            event_type=ActivityEventType.PRIORITY_CHANGE,
            old_value=issue.priority.value,
            new_value=data.priority.value,
        )
        issue.priority = data.priority

    if data.assignee_id is not None and data.assignee_id != issue.assignee_id:
        if get_user(db, data.assignee_id) is None:
            raise HTTPException(status_code=400, detail=f"Unknown assignee_id: {data.assignee_id}")
        log_activity(
            db,
            issue_id=issue.id,
            event_type=ActivityEventType.ASSIGNEE_CHANGE,
            old_value=str(issue.assignee_id) if issue.assignee_id else None,
            new_value=str(data.assignee_id),
        )
        issue.assignee_id = data.assignee_id

    if data.due_at is not None:
        issue.due_at = data.due_at

    issue.updated_at = utc_now()
    db.commit()
    db.refresh(issue)
    return issue


def transition_status(
    db: Session, issue: Issue, new_status: IssueStatus, *, now: datetime | None = None
) -> Issue:
    old_status = issue.status
    if old_status == new_status:
        return issue

    validate_transition(old_status, new_status)

    issue.status = new_status
    timestamp = now or utc_now()

    if new_status == IssueStatus.RESOLVED:
        issue.resolved_at = timestamp
    elif old_status in (IssueStatus.RESOLVED, IssueStatus.CLOSED) and new_status == IssueStatus.OPEN:
        issue.resolved_at = None

    log_activity(
        db,
        issue_id=issue.id,
        event_type=ActivityEventType.STATUS_CHANGE,
        old_value=old_status.value,
        new_value=new_status.value,
    )
    issue.updated_at = timestamp
    db.commit()
    db.refresh(issue)
    return issue


def update_issue_status(db: Session, issue: Issue, data: IssueStatusUpdate) -> Issue:
    try:
        return transition_status(db, issue, data.status)
    except StateTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def update_issue_assignee(db: Session, issue: Issue, data: IssueAssigneeUpdate) -> Issue:
    assert_issue_editable(issue.status)

    if data.assignee_id is not None and get_user(db, data.assignee_id) is None:
        raise HTTPException(status_code=400, detail=f"Unknown assignee_id: {data.assignee_id}")

    old = str(issue.assignee_id) if issue.assignee_id else None
    new = str(data.assignee_id) if data.assignee_id else None
    if old != new:
        log_activity(
            db,
            issue_id=issue.id,
            event_type=ActivityEventType.ASSIGNEE_CHANGE,
            old_value=old,
            new_value=new,
        )
        issue.assignee_id = data.assignee_id
        issue.updated_at = utc_now()
        db.commit()
        db.refresh(issue)
    return issue


def add_comment(db: Session, issue: Issue, data: CommentCreate) -> Comment:
    assert_issue_editable(issue.status)

    if get_user(db, data.author_id) is None:
        raise HTTPException(status_code=400, detail=f"Unknown author_id: {data.author_id}")

    comment = Comment(issue_id=issue.id, author_id=data.author_id, body=data.body)
    db.add(comment)
    db.flush()
    log_activity(
        db,
        issue_id=issue.id,
        event_type=ActivityEventType.COMMENT_ADDED,
        new_value=data.body[:200],
    )
    issue.updated_at = utc_now()
    db.commit()
    db.refresh(comment)
    return comment


def ingest_webhook_issue(
    db: Session, normalized: NormalizedIssuePayload, *, source: str = "default"
) -> tuple[Issue, bool]:
    existing = get_issue_by_external_id(db, normalized.external_id)
    if existing:
        return existing, False

    issue = Issue(
        external_id=normalized.external_id,
        title=normalized.title,
        description=normalized.description,
        priority=normalized.priority,
        assignee_id=normalized.assignee_id,
        due_at=normalized.due_at,
        status=IssueStatus.OPEN,
    )
    db.add(issue)
    db.flush()
    log_activity(
        db,
        issue_id=issue.id,
        event_type=ActivityEventType.WEBHOOK_INGESTED,
        new_value=normalized.external_id,
    )

    if normalized.confidence == "low" or normalized.notes:
        db.add(
            WebhookIngestLog(
                external_id=normalized.external_id,
                source=source,
                confidence=normalized.confidence,
                notes="; ".join(normalized.notes) if normalized.notes else None,
            )
        )

    db.commit()
    db.refresh(issue)
    return issue, True
