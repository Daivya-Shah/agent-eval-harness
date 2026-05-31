from tests.helpers import advance_issue_to, set_issue_status


class TestIssueLifecycleRegressions:
    def test_create_issue_returns_sla_status(self, client, make_issue):
        issue = make_issue()
        assert issue["sla_status"] == "healthy"

    def test_issue_detail_includes_comments_and_activity(self, client, make_user, make_issue):
        user = make_user()
        issue = make_issue()
        client.post(
            f"/api/issues/{issue['id']}/comments",
            json={"author_id": user["id"], "body": "Regression comment"},
        )

        detail = client.get(f"/api/issues/{issue['id']}").json()
        assert len(detail["comments"]) == 1
        assert detail["comments"][0]["body"] == "Regression comment"
        assert len(detail["activity_events"]) >= 2  # created + comment

    def test_add_comment_creates_activity_event(self, client, make_user, make_issue):
        user = make_user()
        issue = make_issue()
        client.post(
            f"/api/issues/{issue['id']}/comments",
            json={"author_id": user["id"], "body": "Activity test comment"},
        )

        detail = client.get(f"/api/issues/{issue['id']}").json()
        comment_events = [
            e for e in detail["activity_events"] if e["event_type"] == "comment_added"
        ]
        assert len(comment_events) == 1
        assert "Activity test comment" in comment_events[0]["new_value"]

    def test_assign_and_unassign_create_activity_events(self, client, make_user, make_issue):
        user = make_user()
        issue = make_issue()
        client.post(
            f"/api/issues/{issue['id']}/assignee",
            json={"assignee_id": user["id"]},
        )
        client.post(
            f"/api/issues/{issue['id']}/assignee",
            json={"assignee_id": None},
        )

        detail = client.get(f"/api/issues/{issue['id']}").json()
        assignee_events = [
            e for e in detail["activity_events"] if e["event_type"] == "assignee_change"
        ]
        assert len(assignee_events) == 2
        assert assignee_events[0]["new_value"] == str(user["id"])
        assert assignee_events[1]["new_value"] is None

    def test_priority_update_creates_activity_event(self, client, make_issue):
        issue = make_issue(priority="low")
        client.patch(f"/api/issues/{issue['id']}", json={"priority": "urgent"})

        detail = client.get(f"/api/issues/{issue['id']}").json()
        priority_events = [
            e for e in detail["activity_events"] if e["event_type"] == "priority_change"
        ]
        assert len(priority_events) == 1
        assert priority_events[0]["old_value"] == "low"
        assert priority_events[0]["new_value"] == "urgent"

    def test_closed_issue_edit_blocked_but_reopen_works(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "closed")

        blocked = client.patch(f"/api/issues/{issue['id']}", json={"title": "Nope"})
        assert blocked.status_code == 400

        reopened = set_issue_status(client, issue["id"], "open")
        assert reopened["status"] == "open"

        allowed = client.patch(f"/api/issues/{issue['id']}", json={"title": "Allowed now"})
        assert allowed.status_code == 200

    def test_resolved_issue_has_closed_sla_status(self, client, make_issue):
        issue = make_issue()
        advance_issue_to(client, issue["id"], "resolved")
        detail = client.get(f"/api/issues/{issue['id']}").json()
        assert detail["sla_status"] == "closed"
