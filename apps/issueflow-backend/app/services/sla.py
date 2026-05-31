from datetime import UTC, datetime, timedelta

from app.models import Issue, IssuePriority, IssueStatus
from app.schemas import SLAStatus

# SLA windows from issue creation (hours)
SLA_HOURS: dict[IssuePriority, int] = {
    IssuePriority.URGENT: 24,
    IssuePriority.HIGH: 72,
    IssuePriority.MEDIUM: 24 * 7,
    IssuePriority.LOW: 24 * 14,
}


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def compute_sla_status(issue: Issue, now: datetime | None = None) -> SLAStatus:
    """Compute SLA status deterministically using UTC."""
    if issue.status in (IssueStatus.RESOLVED, IssueStatus.CLOSED):
        return SLAStatus.CLOSED

    reference = _ensure_utc(now or datetime.now(UTC))
    created = _ensure_utc(issue.created_at)
    window_hours = SLA_HOURS[issue.priority]
    deadline = created + timedelta(hours=window_hours)

    if reference >= deadline:
        return SLAStatus.OVERDUE

    # At risk when within final 20% of SLA window
    elapsed = reference - created
    window = timedelta(hours=window_hours)
    if elapsed >= window * 0.8:
        return SLAStatus.AT_RISK

    return SLAStatus.HEALTHY


def attach_sla_status(issue: Issue, now: datetime | None = None) -> SLAStatus:
    return compute_sla_status(issue, now=now)
