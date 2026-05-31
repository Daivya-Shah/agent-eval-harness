from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from app.models import ActivityEventType, IssueStatus
from tests.helpers import FIXED_NOW, advance_issue_to, set_issue_status


class TestValidTransitions:
    def test_open_to_in_progress(self, client, make_issue):
        issue = make_issue()
        updated = set_issue_status(client, issue["id"], "in_progress")
        assert updated["status"] == "in_progress"

    def test_in_progress_to_resolved(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "in_progress")
        with patch("app.crud.utc_now", return_value=FIXED_NOW):
            updated = set_issue_status(client, issue["id"], "resolved")
        assert updated["status"] == "resolved"
        assert updated["resolved_at"] is not None

    def test_resolved_to_closed(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "resolved")
        updated = set_issue_status(client, issue["id"], "closed")
        assert updated["status"] == "closed"

    def test_blocked_to_open(self, client, make_issue):
        issue = make_issue()
        set_issue_status(client, issue["id"], "blocked")
        updated = set_issue_status(client, issue["id"], "open")
        assert updated["status"] == "open"

    def test_blocked_to_in_progress(self, client, make_issue):
        issue = make_issue()
        set_issue_status(client, issue["id"], "blocked")
        updated = set_issue_status(client, issue["id"], "in_progress")
        assert updated["status"] == "in_progress"


class TestInvalidTransitions:
    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            ("open", "resolved"),
            ("open", "closed"),
            ("in_progress", "closed"),
            ("closed", "resolved"),
            ("closed", "in_progress"),
            ("resolved", "in_progress"),
        ],
    )
    def test_invalid_transition_returns_400(self, client, make_issue, from_status, to_status):
        issue = make_issue()
        if from_status != "open":
            advance_issue_to(client, issue["id"], from_status)

        response = client.post(
            f"/api/issues/{issue['id']}/status",
            json={"status": to_status},
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert from_status in detail
        assert to_status in detail
        assert "Invalid status transition" in detail


class TestClosedIssueEditing:
    def test_closed_issue_cannot_be_edited(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "closed")

        response = client.patch(
            f"/api/issues/{issue['id']}",
            json={"title": "Should not apply"},
        )
        assert response.status_code == 400
        assert "Closed issues cannot be edited" in response.json()["detail"]

    def test_closed_issue_can_be_reopened_via_status_endpoint(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "closed")

        reopened = set_issue_status(client, issue["id"], "open")
        assert reopened["status"] == "open"

        patch_response = client.patch(
            f"/api/issues/{issue['id']}",
            json={"title": "Edited after reopen"},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["title"] == "Edited after reopen"


class TestResolvedAt:
    def test_resolved_at_set_when_resolved(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "in_progress")

        with patch("app.crud.utc_now", return_value=FIXED_NOW):
            updated = set_issue_status(client, issue["id"], "resolved")

        assert updated["resolved_at"] is not None
        resolved_at = datetime.fromisoformat(updated["resolved_at"].replace("Z", "+00:00"))
        assert resolved_at == FIXED_NOW

    def test_resolved_at_cleared_on_reopen_from_resolved(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "resolved")
        assert client.get(f"/api/issues/{issue['id']}").json()["resolved_at"] is not None

        reopened = set_issue_status(client, issue["id"], "open")
        assert reopened["resolved_at"] is None

    def test_resolved_at_cleared_on_reopen_from_closed(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "closed")

        reopened = set_issue_status(client, issue["id"], "open")
        assert reopened["resolved_at"] is None


class TestRepeatedTransitions:
    def test_idempotent_status_does_not_duplicate_activity(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "in_progress")

        before = client.get(f"/api/issues/{issue['id']}").json()
        status_events_before = [
            e for e in before["activity_events"] if e["event_type"] == "status_change"
        ]

        set_issue_status(client, issue["id"], "in_progress")

        after = client.get(f"/api/issues/{issue['id']}").json()
        status_events_after = [
            e for e in after["activity_events"] if e["event_type"] == "status_change"
        ]
        assert len(status_events_after) == len(status_events_before)


class TestActivityEvents:
    def test_status_change_creates_activity_event(self, client, make_issue):
        issue = make_issue()
        set_issue_status(client, issue["id"], "in_progress")

        detail = client.get(f"/api/issues/{issue['id']}").json()
        status_events = [
            e
            for e in detail["activity_events"]
            if e["event_type"] == ActivityEventType.STATUS_CHANGE.value
        ]
        assert any(e["old_value"] == "open" and e["new_value"] == "in_progress" for e in status_events)
