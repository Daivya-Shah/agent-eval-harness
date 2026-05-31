"""Visible SLA eval tests — basic overdue/healthy/closed checks."""

from app.models import IssuePriority
from app.schemas import SLAStatus
from app.services.sla import compute_sla_status
from evals.helpers import FIXED_NOW, advance_to, make_issue_model


def test_urgent_issue_is_overdue_after_24_hours(client, make_issue):
    from datetime import timedelta

    make_issue(priority="urgent")
    model = make_issue_model(
        priority=IssuePriority.URGENT,
        created_at=FIXED_NOW - timedelta(hours=25),
    )
    assert compute_sla_status(model, now=FIXED_NOW) == SLAStatus.OVERDUE


def test_high_priority_can_be_healthy():
    from datetime import timedelta

    model = make_issue_model(
        priority=IssuePriority.HIGH,
        created_at=FIXED_NOW - timedelta(hours=1),
    )
    assert compute_sla_status(model, now=FIXED_NOW) == SLAStatus.HEALTHY


def test_resolved_issue_returns_closed_sla(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "resolved")
    detail = client.get(f"/api/issues/{issue['id']}").json()
    assert detail["sla_status"] == "closed"
