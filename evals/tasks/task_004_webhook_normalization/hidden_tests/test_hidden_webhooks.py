"""Hidden-style webhook eval tests — validation, dates, assignees, logging."""

from sqlalchemy import select

from app.models import ActivityEventType, WebhookIngestLog
from app.schemas import WebhookIssuePayload
from app.services.webhook_normalizer import WebhookNormalizationError, normalize_webhook_payload


def test_missing_title_rejected(client):
    response = client.post("/api/webhooks/issues", json={"external_id": "hid-1", "priority": "P0"})
    assert response.status_code == 400
    assert "title" in response.json()["detail"].lower()


def test_ambiguous_priority_rejected(client):
    response = client.post(
        "/api/webhooks/issues",
        json={"external_id": "hid-2", "title": "T", "priority": "critical"},
    )
    assert response.status_code == 400
    assert "priority" in response.json()["detail"].lower()


def test_unknown_assignee_rejected(client):
    response = client.post(
        "/api/webhooks/issues",
        json={
            "external_id": "hid-3",
            "title": "T",
            "assignee_email": "missing@nowhere.test",
        },
    )
    assert response.status_code == 400
    assert "assignee" in response.json()["detail"].lower()


def test_invalid_date_rejected(client):
    response = client.post(
        "/api/webhooks/issues",
        json={"external_id": "hid-4", "title": "T", "due_at": "not-a-date"},
    )
    assert response.status_code == 400
    assert "due date" in response.json()["detail"].lower()


def test_assignee_by_numeric_id(client, make_user):
    user = make_user(email="assignee-id@test.dev", name="Assignee Id")
    response = client.post(
        "/api/webhooks/issues",
        json={"external_id": "hid-5", "title": "T", "assignee": user["id"]},
    )
    assert response.status_code == 201
    assert response.json()["issue"]["assignee_id"] == user["id"]


def test_multiple_date_formats(client):
    for idx, due in enumerate(["2025-12-01T10:00:00Z", "2025-12-01", "2025/12/01"]):
        response = client.post(
            "/api/webhooks/issues",
            json={"external_id": f"hid-date-{idx}", "title": "T", "due_at": due},
        )
        assert response.status_code == 201
        assert response.json()["issue"]["due_at"] is not None


def test_low_confidence_missing_priority_logged(client, db_session):
    response = client.post(
        "/api/webhooks/issues",
        json={"external_id": "hid-lowconf", "title": "No priority"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["confidence"] == "low"

    db_session.expire_all()
    logs = list(db_session.scalars(select(WebhookIngestLog)).all())
    assert any(l.external_id == "hid-lowconf" and l.confidence == "low" for l in logs)


def test_idempotent_duplicate_does_not_spam_activity(client, make_user):
    payload = {"external_id": "hid-idem", "title": "Idempotent", "priority": "high"}
    first = client.post("/api/webhooks/issues", json=payload)
    second = client.post("/api/webhooks/issues", json=payload)
    issue_id = first.json()["issue"]["id"]

    detail = client.get(f"/api/issues/{issue_id}").json()
    webhook_events = [
        e for e in detail["activity_events"] if e["event_type"] == ActivityEventType.WEBHOOK_INGESTED.value
    ]
    assert len(webhook_events) == 1
    assert second.json()["created"] is False


def test_normalizer_accepts_all_title_aliases(db_session):
    for field, value in [("title", "A"), ("issueTitle", "B"), ("summary", "C")]:
        normalized = normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(**{"external_id": f"norm-{field}", field: value}),
        )
        assert normalized.title == value


def test_normalizer_rejects_ambiguous_priority_unit(db_session):
    try:
        normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(external_id="x", title="T", priority="P9"),
        )
        raise AssertionError("expected WebhookNormalizationError")
    except WebhookNormalizationError as exc:
        assert "priority" in str(exc).lower()
