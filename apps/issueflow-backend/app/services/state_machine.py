from app.models import IssueStatus

ALLOWED_TRANSITIONS: dict[IssueStatus, set[IssueStatus]] = {
    IssueStatus.OPEN: {IssueStatus.IN_PROGRESS, IssueStatus.BLOCKED},
    IssueStatus.IN_PROGRESS: {IssueStatus.RESOLVED, IssueStatus.BLOCKED, IssueStatus.OPEN},
    IssueStatus.BLOCKED: {IssueStatus.OPEN, IssueStatus.IN_PROGRESS},
    IssueStatus.RESOLVED: {IssueStatus.CLOSED, IssueStatus.OPEN},
    IssueStatus.CLOSED: {IssueStatus.OPEN},
}


class StateTransitionError(ValueError):
    pass


def validate_transition(old_status: IssueStatus, new_status: IssueStatus) -> None:
    if old_status == new_status:
        return
    allowed = ALLOWED_TRANSITIONS.get(old_status, set())
    if new_status not in allowed:
        raise StateTransitionError(
            f"Invalid status transition from '{old_status.value}' to '{new_status.value}'."
        )


def assert_issue_editable(status: IssueStatus, *, reopen: bool = False) -> None:
    if status == IssueStatus.CLOSED and not reopen:
        raise StateTransitionError(
            "Closed issues cannot be edited unless reopened via status transition to open."
        )
