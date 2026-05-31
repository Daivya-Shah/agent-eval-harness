from datetime import UTC, datetime, timedelta

import pytest

from app.models import IssuePriority, IssueStatus
from app.schemas import SLAStatus
from app.services.sla import SLA_HOURS, compute_sla_status
from tests.helpers import FIXED_NOW, make_issue_model


class TestOverdueThresholds:
    @pytest.mark.parametrize(
        ("priority", "hours"),
        [
            (IssuePriority.URGENT, 24),
            (IssuePriority.HIGH, 72),
            (IssuePriority.MEDIUM, 24 * 7),
            (IssuePriority.LOW, 24 * 14),
        ],
    )
    def test_becomes_overdue_after_sla_window(self, priority, hours):
        created = FIXED_NOW
        issue = make_issue_model(priority=priority, created_at=created)
        now = created + timedelta(hours=hours)
        assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE

    @pytest.mark.parametrize(
        ("priority", "hours"),
        [
            (IssuePriority.URGENT, 24),
            (IssuePriority.HIGH, 72),
            (IssuePriority.MEDIUM, 24 * 7),
            (IssuePriority.LOW, 24 * 14),
        ],
    )
    def test_one_second_before_deadline_not_overdue(self, priority, hours):
        created = FIXED_NOW
        issue = make_issue_model(priority=priority, created_at=created)
        now = created + timedelta(hours=hours) - timedelta(seconds=1)
        assert compute_sla_status(issue, now=now) != SLAStatus.OVERDUE


class TestAtRisk:
    def test_urgent_at_risk_in_final_20_percent(self):
        created = FIXED_NOW
        issue = make_issue_model(priority=IssuePriority.URGENT, created_at=created)
        # 80% of 24h = 19.2h
        now = created + timedelta(hours=19, minutes=12, seconds=1)
        assert compute_sla_status(issue, now=now) == SLAStatus.AT_RISK

    def test_just_before_at_risk_is_healthy(self):
        created = FIXED_NOW
        issue = make_issue_model(priority=IssuePriority.URGENT, created_at=created)
        now = created + timedelta(hours=19, minutes=11, seconds=59)
        assert compute_sla_status(issue, now=now) == SLAStatus.HEALTHY


class TestHealthy:
    def test_new_issue_is_healthy(self):
        issue = make_issue_model(priority=IssuePriority.HIGH, created_at=FIXED_NOW)
        assert compute_sla_status(issue, now=FIXED_NOW) == SLAStatus.HEALTHY


class TestResolvedAndClosed:
    @pytest.mark.parametrize("status", [IssueStatus.RESOLVED, IssueStatus.CLOSED])
    def test_terminal_status_returns_closed_sla(self, status):
        created = FIXED_NOW - timedelta(days=30)
        issue = make_issue_model(priority=IssuePriority.URGENT, status=status, created_at=created)
        assert compute_sla_status(issue, now=FIXED_NOW) == SLAStatus.CLOSED


class TestTimezoneHandling:
    def test_naive_created_at_treated_as_utc(self):
        created_naive = datetime(2025, 6, 1, 0, 0, 0)
        issue = make_issue_model(priority=IssuePriority.URGENT, created_at=created_naive)
        now = datetime(2025, 6, 2, 0, 0, 1, tzinfo=UTC)
        assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE

    def test_non_utc_created_at_normalized(self):
        from datetime import timezone

        created_est = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
        issue = make_issue_model(priority=IssuePriority.URGENT, created_at=created_est)
        # 24h after created_est in UTC terms
        now = created_est.astimezone(UTC) + timedelta(hours=24)
        assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE


class TestExactBoundary:
    def test_exact_deadline_is_overdue(self):
        created = FIXED_NOW
        issue = make_issue_model(priority=IssuePriority.HIGH, created_at=created)
        now = created + timedelta(hours=SLA_HOURS[IssuePriority.HIGH])
        assert compute_sla_status(issue, now=now) == SLAStatus.OVERDUE

    def test_exact_80_percent_mark_is_at_risk(self):
        created = FIXED_NOW
        issue = make_issue_model(priority=IssuePriority.MEDIUM, created_at=created)
        window_hours = SLA_HOURS[IssuePriority.MEDIUM]
        now = created + timedelta(hours=window_hours * 0.8)
        assert compute_sla_status(issue, now=now) == SLAStatus.AT_RISK
