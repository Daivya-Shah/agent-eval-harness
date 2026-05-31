"""Hidden-style eval tests — lifecycle edge cases and audit invariants."""

from datetime import datetime
from unittest.mock import patch

from evals.helpers import FIXED_NOW, advance_to, post_status


def test_blocked_to_open_and_in_progress(client, make_issue):
    issue = make_issue()
    post_status(client, issue["id"], "blocked")

    to_open = post_status(client, issue["id"], "open")
    assert to_open.status_code == 200
    assert to_open.json()["status"] == "open"

    post_status(client, issue["id"], "blocked")
    to_progress = post_status(client, issue["id"], "in_progress")
    assert to_progress.status_code == 200
    assert to_progress.json()["status"] == "in_progress"


def test_closed_issue_patch_blocked(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "closed")

    response = client.patch(f"/api/issues/{issue['id']}", json={"title": "Should fail"})
    assert response.status_code == 400
    assert "Closed issues cannot be edited" in response.json()["detail"]


def test_closed_issue_reopens_via_status_endpoint(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "closed")

    response = post_status(client, issue["id"], "open")
    assert response.status_code == 200
    assert response.json()["status"] == "open"


def test_resolved_at_set_and_cleared(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "in_progress")

    with patch("app.crud.utc_now", return_value=FIXED_NOW):
        resolved = post_status(client, issue["id"], "resolved")
    assert resolved.status_code == 200
    resolved_at = datetime.fromisoformat(resolved.json()["resolved_at"].replace("Z", "+00:00"))
    assert resolved_at == FIXED_NOW

    reopened = post_status(client, issue["id"], "open")
    assert reopened.status_code == 200
    assert reopened.json()["resolved_at"] is None


def test_repeated_same_status_is_idempotent_for_audit(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "in_progress")

    before = client.get(f"/api/issues/{issue['id']}").json()
    status_events_before = [
        e for e in before["activity_events"] if e["event_type"] == "status_change"
    ]

    repeat = post_status(client, issue["id"], "in_progress")
    assert repeat.status_code == 200

    after = client.get(f"/api/issues/{issue['id']}").json()
    status_events_after = [
        e for e in after["activity_events"] if e["event_type"] == "status_change"
    ]
    assert len(status_events_after) == len(status_events_before)


def test_invalid_transition_message_is_specific(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "closed")

    response = post_status(client, issue["id"], "resolved")
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "closed" in detail
    assert "resolved" in detail


def test_status_change_activity_contains_old_and_new(client, make_issue):
    issue = make_issue()
    post_status(client, issue["id"], "in_progress")

    detail = client.get(f"/api/issues/{issue['id']}").json()
    events = [e for e in detail["activity_events"] if e["event_type"] == "status_change"]
    assert any(e["old_value"] == "open" and e["new_value"] == "in_progress" for e in events)
