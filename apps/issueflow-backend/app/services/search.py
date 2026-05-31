from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Issue, IssuePriority, IssueStatus
from app.schemas import IssueFilterParams


def apply_issue_filters(db: Session, filters: IssueFilterParams) -> tuple[list[Issue], int]:
    stmt = select(Issue).options(joinedload(Issue.assignee))

    if filters.status is not None:
        stmt = stmt.where(Issue.status == filters.status)
    if filters.priority is not None:
        stmt = stmt.where(Issue.priority == filters.priority)
    if filters.assignee_id is not None:
        stmt = stmt.where(Issue.assignee_id == filters.assignee_id)
    if filters.q:
        term = f"%{filters.q.strip()}%"
        stmt = stmt.where(
            or_(
                Issue.title.ilike(term),
                Issue.description.ilike(term),
            )
        )

    stmt = stmt.order_by(Issue.updated_at.desc())
    issues = list(db.scalars(stmt).unique().all())
    return issues, len(issues)
