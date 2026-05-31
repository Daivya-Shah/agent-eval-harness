import pytest
from sqlalchemy import select

from app.models import WebhookIngestLog
from app.schemas import WebhookIssuePayload
from app.services.webhook_normalizer import WebhookNormalizationError, normalize_webhook_payload


class TestTitleFields:
    @pytest.mark.parametrize(
        "payload",
        [
            {"external_id": "ext-1", "title": "From title"},
            {"external_id": "ext-2", "issueTitle": "From issueTitle"},
            {"external_id": "ext-3", "summary": "From summary"},
        ],
    )
    def test_accepts_title_aliases(self, db_session, payload):
        normalized = normalize_webhook_payload(db_session, WebhookIssuePayload(**payload))
        assert normalized.title in {"From title", "From issueTitle", "From summary"}


class TestDescriptionFields:
    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("description", "From description"),
            ("body", "From body"),
            ("details", "From details"),
        ],
    )
    def test_accepts_description_aliases(self, db_session, field, value):
        payload = {"external_id": "ext-desc", "title": "T", field: value}
        normalized = normalize_webhook_payload(db_session, WebhookIssuePayload(**payload))
        assert normalized.description == value


class TestPriorityMapping:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("P0", "urgent"),
            ("p1", "high"),
            ("P2", "medium"),
            ("p3", "low"),
            ("urgent", "urgent"),
            ("high", "high"),
            ("medium", "medium"),
            ("low", "low"),
        ],
    )
    def test_priority_aliases(self, db_session, raw, expected):
        normalized = normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(external_id=f"ext-{raw}", title="T", priority=raw),
        )
        assert normalized.priority.value == expected


class TestAssigneeResolution:
    def test_assignee_by_email(self, db_session, make_user_via_db):
        user = make_user_via_db(email="webhook@assignee.test", name="Webhook User")
        normalized = normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(
                external_id="ext-email",
                title="T",
                assignee_email=user.email,
            ),
        )
        assert normalized.assignee_id == user.id

    def test_assignee_by_id_field(self, db_session, make_user_via_db):
        user = make_user_via_db(email="id@assignee.test", name="Id User")
        normalized = normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(external_id="ext-id", title="T", assignee=user.id),
        )
        assert normalized.assignee_id == user.id


class TestDueDates:
    @pytest.mark.parametrize(
        "due_value",
        [
            "2025-12-01T10:00:00Z",
            "2025-12-01",
            "2025/12/01 10:00:00",
        ],
    )
    def test_multiple_date_formats(self, db_session, due_value):
        normalized = normalize_webhook_payload(
            db_session,
            WebhookIssuePayload(external_id="ext-due", title="T", due_at=due_value),
        )
        assert normalized.due_at is not None


class TestRejections:
    def test_rejects_missing_title(self, db_session):
        with pytest.raises(WebhookNormalizationError, match="Missing required field: title"):
            normalize_webhook_payload(
                db_session,
                WebhookIssuePayload(external_id="ext-no-title", description="only desc"),
            )

    def test_rejects_ambiguous_priority(self, db_session):
        with pytest.raises(WebhookNormalizationError, match="Ambiguous or unknown priority"):
            normalize_webhook_payload(
                db_session,
                WebhookIssuePayload(external_id="ext-bad-pri", title="T", priority="critical"),
            )

    def test_rejects_unknown_assignee_email(self, db_session):
        with pytest.raises(WebhookNormalizationError, match="Unknown assignee email"):
            normalize_webhook_payload(
                db_session,
                WebhookIssuePayload(
                    external_id="ext-unknown",
                    title="T",
                    assignee_email="missing@nowhere.test",
                ),
            )


class TestWebhookAPI:
    def test_ingest_and_idempotent_duplicate(self, client, make_user):
        user = make_user(email="wh@api.test", name="WH User")
        payload = {
            "external_id": "jira-1001",
            "issueTitle": "Webhook issue",
            "body": "Details from webhook",
            "priority": "P1",
            "assignee_email": user["email"],
            "due_date": "2025-12-15",
        }
        first = client.post("/api/webhooks/issues", json=payload)
        assert first.status_code == 201
        first_body = first.json()
        assert first_body["created"] is True
        assert first_body["issue"]["title"] == "Webhook issue"
        assert first_body["issue"]["priority"] == "high"

        second = client.post("/api/webhooks/issues", json=payload)
        assert second.status_code == 201
        second_body = second.json()
        assert second_body["created"] is False
        assert second_body["issue"]["id"] == first_body["issue"]["id"]

    def test_missing_priority_logs_low_confidence(self, client, db_session):
        response = client.post(
            "/api/webhooks/issues",
            json={"external_id": "low-conf-1", "title": "No priority field"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["confidence"] == "low"
        assert any("priority" in note.lower() for note in body["notes"])

        db_session.expire_all()
        logs = list(db_session.scalars(select(WebhookIngestLog)).all())
        assert any(log.external_id == "low-conf-1" and log.confidence == "low" for log in logs)

    def test_rejects_bad_payload_via_api(self, client):
        response = client.post(
            "/api/webhooks/issues",
            json={"external_id": "bad-1", "priority": "P0"},
        )
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()
