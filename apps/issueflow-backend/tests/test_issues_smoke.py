def test_create_and_list_issues(client):
    user_resp = client.post(
        "/api/users",
        json={"email": "dev@issueflow.dev", "name": "Dev User"},
    )
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    create_resp = client.post(
        "/api/issues",
        json={
            "title": "Test issue",
            "description": "Created from smoke test",
            "priority": "high",
            "assignee_id": user_id,
        },
    )
    assert create_resp.status_code == 201
    issue = create_resp.json()
    assert issue["title"] == "Test issue"
    assert issue["status"] == "open"
    assert issue["sla_status"] == "healthy"

    list_resp = client.get("/api/issues?priority=high")
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == issue["id"]
