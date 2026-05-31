from datetime import UTC, datetime
from unittest.mock import patch

from app.models import Issue, IssuePriority, IssueStatus

FIXED_NOW = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)


def make_issue_model(
    *,
    priority: IssuePriority = IssuePriority.MEDIUM,
    status: IssueStatus = IssueStatus.OPEN,
    created_at: datetime,
) -> Issue:
    return Issue(
        id=1,
        title="Eval SLA issue",
        description="SLA eval helper",
        status=status,
        priority=priority,
        created_at=created_at,
        updated_at=created_at,
    )


def post_status(client, issue_id: int, status: str):
    return client.post(f"/api/issues/{issue_id}/status", json={"status": status})


def advance_to(client, issue_id: int, target: str) -> dict:
    paths = {
        "in_progress": ["in_progress"],
        "blocked": ["blocked"],
        "resolved": ["in_progress", "resolved"],
        "closed": ["in_progress", "resolved", "closed"],
    }
    issue = None
    for step in paths.get(target, []):
        response = post_status(client, issue_id, step)
        assert response.status_code == 200, response.text
        issue = response.json()
    if issue is None:
        response = client.get(f"/api/issues/{issue_id}")
        assert response.status_code == 200
        issue = response.json()
    return issue
