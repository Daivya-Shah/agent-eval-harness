from datetime import UTC, datetime

from app.models import Issue, IssuePriority, IssueStatus

FIXED_NOW = datetime(2025, 6, 15, 12, 0, 0, tzinfo=UTC)


def set_issue_status(client, issue_id: int, status: str) -> dict:
    response = client.post(f"/api/issues/{issue_id}/status", json={"status": status})
    assert response.status_code == 200, response.text
    return response.json()


def advance_issue_to(client, issue_id: int, target_status: str) -> dict:
    """Walk an issue through a valid path to the target status."""
    paths: dict[str, list[str]] = {
        "open": [],
        "in_progress": ["in_progress"],
        "blocked": ["blocked"],
        "resolved": ["in_progress", "resolved"],
        "closed": ["in_progress", "resolved", "closed"],
    }
    if target_status not in paths:
        raise ValueError(f"Unknown status: {target_status}")

    issue: dict | None = None
    for status in paths[target_status]:
        issue = set_issue_status(client, issue_id, status)
    if issue is None:
        response = client.get(f"/api/issues/{issue_id}")
        assert response.status_code == 200
        issue = response.json()
    return issue


def make_issue_model(
    *,
    priority: IssuePriority = IssuePriority.MEDIUM,
    status: IssueStatus = IssueStatus.OPEN,
    created_at: datetime,
) -> Issue:
    return Issue(
        id=1,
        title="SLA test issue",
        description="For unit tests",
        status=status,
        priority=priority,
        created_at=created_at,
        updated_at=created_at,
    )
