from datetime import UTC, datetime

from dateutil import parser as date_parser
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IssuePriority, User
from app.schemas import NormalizedIssuePayload, WebhookIssuePayload

PRIORITY_ALIASES: dict[str, IssuePriority] = {
    "p0": IssuePriority.URGENT,
    "p1": IssuePriority.HIGH,
    "p2": IssuePriority.MEDIUM,
    "p3": IssuePriority.LOW,
    "urgent": IssuePriority.URGENT,
    "high": IssuePriority.HIGH,
    "medium": IssuePriority.MEDIUM,
    "low": IssuePriority.LOW,
}


class WebhookNormalizationError(ValueError):
    pass


def _first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _parse_priority(raw: str | None) -> tuple[IssuePriority, list[str]]:
    notes: list[str] = []
    if raw is None or not str(raw).strip():
        return IssuePriority.MEDIUM, ["priority missing; defaulted to medium"]

    key = str(raw).strip().lower()
    if key not in PRIORITY_ALIASES:
        raise WebhookNormalizationError(
            f"Ambiguous or unknown priority '{raw}'. Expected P0-P3 or urgent/high/medium/low."
        )
    return PRIORITY_ALIASES[key], notes


def _parse_due_date(raw: str | None) -> tuple[datetime | None, list[str]]:
    if raw is None or not str(raw).strip():
        return None, []
    try:
        parsed = date_parser.parse(str(raw).strip())
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC), []
    except (ValueError, TypeError) as exc:
        raise WebhookNormalizationError(f"Invalid due date format: {raw}") from exc


def _resolve_assignee(
    db: Session,
    *,
    assignee_id: int | None,
    assignee_email: str | None,
    assignee: str | int | None,
) -> tuple[int | None, list[str]]:
    notes: list[str] = []

    if assignee_id is not None:
        user = db.get(User, assignee_id)
        if user is None:
            raise WebhookNormalizationError(f"Unknown assignee_id: {assignee_id}")
        return assignee_id, notes

    email = assignee_email
    if email is None and assignee is not None and isinstance(assignee, str) and "@" in assignee:
        email = assignee

    if email:
        user = db.scalars(select(User).where(User.email == email)).one_or_none()
        if user is None:
            raise WebhookNormalizationError(f"Unknown assignee email: {email}")
        return user.id, notes

    if assignee is not None and isinstance(assignee, int):
        user = db.get(User, assignee)
        if user is None:
            raise WebhookNormalizationError(f"Unknown assignee id: {assignee}")
        return assignee, notes

    if assignee is not None:
        notes.append(f"Could not resolve assignee '{assignee}'; leaving unassigned")

    return None, notes


def normalize_webhook_payload(
    db: Session, payload: WebhookIssuePayload
) -> NormalizedIssuePayload:
    notes: list[str] = []
    confidence = "high"

    external_id = _first_non_empty(
        payload.external_id,
        str(payload.id) if payload.id is not None else None,
    )
    if not external_id:
        raise WebhookNormalizationError("Missing required field: external_id (or id)")

    title = _first_non_empty(payload.title, payload.issueTitle, payload.summary)
    if not title:
        raise WebhookNormalizationError(
            "Missing required field: title (accepts title, issueTitle, or summary)"
        )

    description = _first_non_empty(payload.description, payload.body, payload.details)

    priority, priority_notes = _parse_priority(payload.priority)
    notes.extend(priority_notes)
    if priority_notes:
        confidence = "low"

    due_raw = _first_non_empty(payload.due_at, payload.due_date, payload.dueDate)
    due_at, due_notes = _parse_due_date(due_raw)
    notes.extend(due_notes)

    assignee_id, assignee_notes = _resolve_assignee(
        db,
        assignee_id=payload.assignee_id,
        assignee_email=payload.assignee_email,
        assignee=payload.assignee,
    )
    notes.extend(assignee_notes)
    if assignee_notes:
        confidence = "low"

    return NormalizedIssuePayload(
        external_id=external_id,
        title=title,
        description=description,
        priority=priority,
        assignee_id=assignee_id,
        due_at=due_at,
        confidence=confidence,
        notes=notes,
    )
