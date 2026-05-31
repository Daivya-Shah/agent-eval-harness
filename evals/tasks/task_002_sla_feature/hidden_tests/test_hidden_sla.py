"""Hidden-style SLA eval tests — boundaries, timezones, and invariants."""

from datetime import UTC, datetime, timedelta, timezone

from app.models import IssuePriority, IssueStatus
from app.schemas import SLAStatus
from app.services.sla import SLA_HOURS, compute_sla_status
from evals.helpers import FIXED_NOW, advance_to, make_issue_model


def test_exact_overdue_boundary():
    created = FIXED_NOW
    issue = make_issue_model(priority=IssuePriority.HIGH, created_at=created)
    deadline = created + timedelta(hours=SLA_HOURS[IssuePriority.HIGH])
    assert compute_sla_status(issue, now=deadline) == SLAStatus.OVERDUE


def test_one_second_before_overdue_not_overdue():
    created = FIXED_NOW
    issue = make_issue_model(priority=IssuePriority.URGENT, created_at=created)
    now = created + timedelta(hours=24) - timedelta(seconds=1)
    assert compute_sla_status(issue, now=now) != SLAStatus.OVERDUE


def test_at_risk_boundary_exactly_80_percent():
    created = FIXED_NOW
    issue = make_issue_model(priority=IssuePriority.MEDIUM, created_at=created)
    window = SLA_HOURS[IssuePriority.MEDIUM]
    now = created + timedelta(hours=window * 0.8)
    assert compute_sla_status(issue, now=now) == SLAStatus.AT_RISK


def test_naive_created_at_treated_as_utc():
    naive = datetime(2025, 6, 1, 0, 0, 0)
    issue = make_issue_model(priority=IssuePriority.URGENT, created_at=naive)
    now = datetime(2025, 6, 2, 0, 0, 1, tzinfo=UTC)
    assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE


def test_timezone_aware_created_at_normalized():
    est = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
    issue = make_issue_model(priority=IssuePriority.URGENT, created_at=est)
    now = est.astimezone(UTC) + timedelta(hours=24)
    assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE


def test_low_priority_14_day_window():
    created = FIXED_NOW
    issue = make_issue_model(priority=IssuePriority.LOW, created_at=created)
    assert compute_sla_status(issue, now=created + timedelta(days=14)) == SLAStatus.OVERDUE
    assert (
        compute_sla_status(issue, now=created + timedelta(days=13, hours=23))
        != SLAStatus.OVERDUE
    )


def test_closed_issue_never_overdue(client, make_issue):
    issue = make_issue(priority="urgent")
    advance_to(client, issue["id"], "closed")
    detail = client.get(f"/api/issues/{issue['id']}").json()
    assert detail["sla_status"] == "closed"

    model = make_issue_model(
        priority=IssuePriority.URGENT,
        status=IssueStatus.CLOSED,
        created_at=FIXED_NOW - timedelta(days=30),
    )
    assert compute_sla_status(model, now=FIXED_NOW) == SLAStatus.CLOSED
