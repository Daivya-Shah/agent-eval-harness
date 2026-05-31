"""Visible webhook eval tests — straightforward payloads."""


def test_standard_payload_with_title_description_p1(client, make_user):
    user = make_user(email="wh-visible@test.dev", name="WH Visible")
    payload = {
        "external_id": "vis-1001",
        "title": "Standard webhook issue",
        "description": "Visible test description",
        "priority": "P1",
        "assignee_email": user["email"],
    }
    response = client.post("/api/webhooks/issues", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["created"] is True
    assert body["issue"]["title"] == "Standard webhook issue"
    assert body["issue"]["priority"] == "high"


def test_alias_payload_summary_and_body(client):
    payload = {
        "external_id": "vis-1002",
        "summary": "Summary title",
        "body": "Body description",
        "priority": "medium",
    }
    response = client.post("/api/webhooks/issues", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["issue"]["title"] == "Summary title"
    assert body["issue"]["description"] == "Body description"


def test_duplicate_external_id_returns_existing(client):
    payload = {
        "external_id": "vis-dup-1",
        "title": "Duplicate test",
        "priority": "low",
    }
    first = client.post("/api/webhooks/issues", json=payload)
    second = client.post("/api/webhooks/issues", json=payload)
    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["created"] is False
    assert second.json()["issue"]["id"] == first.json()["issue"]["id"]
