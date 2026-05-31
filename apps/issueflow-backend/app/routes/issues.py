from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import IssuePriority, IssueStatus
from app.schemas import (
    IssueCreate,
    IssueDetail,
    IssueFilterParams,
    IssueListResponse,
    IssueRead,
    IssueStatusUpdate,
    IssueUpdate,
    UserCreate,
    UserRead,
)
from app.services.sla import attach_sla_status

router = APIRouter(prefix="/issues", tags=["issues"])


def _issue_detail(issue) -> IssueDetail:
    detail = IssueDetail.model_validate(issue)
    detail.sla_status = attach_sla_status(issue)
    return detail


@router.get("", response_model=IssueListResponse)
def list_issues(
    status: IssueStatus | None = Query(default=None),
    priority: IssuePriority | None = Query(default=None),
    assignee_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> IssueListResponse:
    filters = IssueFilterParams(
        status=status, priority=priority, assignee_id=assignee_id, q=q
    )
    items, total = crud.list_issues(db, filters)
    return IssueListResponse(items=items, total=total)


@router.post("", response_model=IssueRead, status_code=201)
def create_issue(data: IssueCreate, db: Session = Depends(get_db)) -> IssueRead:
    issue = crud.create_issue(db, data)
    read = IssueRead.model_validate(issue)
    read.sla_status = attach_sla_status(issue)
    return read


@router.get("/{issue_id}", response_model=IssueDetail)
def get_issue(issue_id: int, db: Session = Depends(get_db)) -> IssueDetail:
    issue = crud.get_issue(db, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return _issue_detail(issue)


@router.patch("/{issue_id}", response_model=IssueRead)
def update_issue(
    issue_id: int, data: IssueUpdate, db: Session = Depends(get_db)
) -> IssueRead:
    issue = crud.get_issue(db, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    try:
        updated = crud.update_issue(db, issue, data)
    except crud.StateTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    read = IssueRead.model_validate(updated)
    read.sla_status = attach_sla_status(updated)
    return read


@router.post("/{issue_id}/status", response_model=IssueRead)
def update_issue_status(
    issue_id: int, data: IssueStatusUpdate, db: Session = Depends(get_db)
) -> IssueRead:
    issue = crud.get_issue(db, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    updated = crud.update_issue_status(db, issue, data)
    read = IssueRead.model_validate(updated)
    read.sla_status = attach_sla_status(updated)
    return read
