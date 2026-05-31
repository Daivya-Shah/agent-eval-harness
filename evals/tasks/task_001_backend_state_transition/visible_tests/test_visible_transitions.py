"""Visible eval tests — basic status transition happy paths."""

from evals.helpers import advance_to, post_status


def test_open_to_in_progress(client, make_issue):
    issue = make_issue()
    response = post_status(client, issue["id"], "in_progress")
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_in_progress_to_resolved(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "in_progress")
    response = post_status(client, issue["id"], "resolved")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "resolved"
    assert body["resolved_at"] is not None


def test_resolved_to_closed(client, make_issue):
    issue = make_issue()
    advance_to(client, issue["id"], "resolved")
    response = post_status(client, issue["id"], "closed")
    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_invalid_open_to_closed_returns_400(client, make_issue):
    issue = make_issue()
    response = post_status(client, issue["id"], "closed")
    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["detail"]
