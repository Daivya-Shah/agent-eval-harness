from sqlalchemy.orm import Session

from app.models import ActivityEvent, ActivityEventType


def log_activity(
    db: Session,
    *,
    issue_id: int,
    event_type: ActivityEventType,
    old_value: str | None = None,
    new_value: str | None = None,
) -> ActivityEvent:
    event = ActivityEvent(
        issue_id=issue_id,
        event_type=event_type,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(event)
    return event
