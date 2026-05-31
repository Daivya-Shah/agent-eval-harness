from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app import crud
from app.models import IssuePriority, IssueStatus
from app.schemas import IssueCreate


def seed_database(db: Session) -> None:
    """Populate demo users and issues if the database is empty."""
    if crud.list_users(db):
        return

    alice = crud.create_user(db, email="alice@issueflow.dev", name="Alice Chen")
    bob = crud.create_user(db, email="bob@issueflow.dev", name="Bob Martinez")
    carol = crud.create_user(db, email="carol@issueflow.dev", name="Carol Singh")

    now = datetime.now(UTC)

    samples = [
        IssueCreate(
            title="Login timeout on mobile Safari",
            description="Users report session expiry after 30 seconds on iOS Safari.",
            priority=IssuePriority.URGENT,
            assignee_id=alice.id,
            due_at=now + timedelta(hours=12),
        ),
        IssueCreate(
            title="Export CSV missing assignee column",
            description="CSV export omits assignee for filtered views.",
            priority=IssuePriority.HIGH,
            assignee_id=bob.id,
            due_at=now + timedelta(days=2),
        ),
        IssueCreate(
            title="Dark mode contrast on comment threads",
            description="Comment text fails WCAG AA in dark theme.",
            priority=IssuePriority.MEDIUM,
            assignee_id=carol.id,
            due_at=now + timedelta(days=5),
        ),
        IssueCreate(
            title="Webhook retries flooding logs",
            description="Duplicate webhook deliveries create noisy error logs.",
            priority=IssuePriority.LOW,
            assignee_id=None,
            due_at=now + timedelta(days=10),
        ),
    ]

    issue_ids: list[int] = []
    for sample in samples:
        issue = crud.create_issue(db, sample)
        issue_ids.append(issue.id)

    # Set varied statuses for demo data
    from app.schemas import IssueStatusUpdate

    crud.update_issue_status(
        db, crud.get_issue(db, issue_ids[0]), IssueStatusUpdate(status=IssueStatus.IN_PROGRESS)
    )
    crud.update_issue_status(
        db, crud.get_issue(db, issue_ids[1]), IssueStatusUpdate(status=IssueStatus.BLOCKED)
    )
    crud.update_issue_status(
        db, crud.get_issue(db, issue_ids[2]), IssueStatusUpdate(status=IssueStatus.RESOLVED)
    )

    # Add sample comments
    from app.schemas import CommentCreate

    crud.add_comment(
        db,
        crud.get_issue(db, issue_ids[0]),
        CommentCreate(author_id=bob.id, body="Reproduced on iOS 17.4 — investigating cookie SameSite settings."),
    )
    crud.add_comment(
        db,
        crud.get_issue(db, issue_ids[2]),
        CommentCreate(author_id=alice.id, body="Fixed contrast ratio in comment panel CSS."),
    )
