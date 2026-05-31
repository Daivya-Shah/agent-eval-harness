from tests.helpers import advance_issue_to, set_issue_status


class TestIssueFilters:
    def test_filter_by_status(self, client, make_issue):
        make_issue(title="Open item")
        blocked = make_issue(title="Blocked item")
        set_issue_status(client, blocked["id"], "blocked")

        response = client.get("/api/issues?status=blocked")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == blocked["id"]

    def test_filter_by_priority(self, client, make_issue):
        make_issue(title="Low priority", priority="low")
        urgent = make_issue(title="Urgent priority", priority="urgent")

        response = client.get("/api/issues?priority=urgent")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == urgent["id"]

    def test_filter_by_assignee(self, client, make_user, make_issue):
        alice = make_user(email="alice@filter.test", name="Alice")
        bob = make_user(email="bob@filter.test", name="Bob")
        assigned = make_issue(title="Alice task", assignee_id=alice["id"])
        make_issue(title="Bob task", assignee_id=bob["id"])

        response = client.get(f"/api/issues?assignee_id={alice['id']}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == assigned["id"]

    def test_keyword_search_title(self, client, make_issue):
        match = make_issue(title="UniqueAlphaKeyword in title")
        make_issue(title="Unrelated issue")

        response = client.get("/api/issues?q=UniqueAlphaKeyword")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == match["id"]

    def test_keyword_search_description(self, client, make_issue):
        match = make_issue(title="Issue A", description="Contains BetaSearchToken here")
        make_issue(title="Issue B", description="Nothing relevant")

        response = client.get("/api/issues?q=BetaSearchToken")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == match["id"]

    def test_combined_filters(self, client, make_user, make_issue):
        user = make_user(email="combo@filter.test", name="Combo User")
        target = make_issue(
            title="Combo match token",
            description="combo desc",
            priority="high",
            assignee_id=user["id"],
        )
        make_issue(title="Combo match token", priority="low", assignee_id=user["id"])
        other = make_issue(title="Other", priority="high", assignee_id=user["id"])
        set_issue_status(client, other["id"], "in_progress")
        set_issue_status(client, target["id"], "in_progress")

        response = client.get(
            f"/api/issues?status=in_progress&priority=high&assignee_id={user['id']}&q=Combo"
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["id"] == target["id"]

    def test_empty_results_not_error(self, client):
        response = client.get("/api/issues?q=__no_match_expected__")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 0
        assert payload["items"] == []
