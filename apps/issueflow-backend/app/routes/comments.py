from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import CommentCreate, CommentRead, IssueAssigneeUpdate, IssueRead
from app.services.sla import attach_sla_status

router = APIRouter(prefix="/issues", tags=["comments"])


@router.post("/{issue_id}/comments", response_model=CommentRead, status_code=201)
def add_comment(
    issue_id: int, data: CommentCreate, db: Session = Depends(get_db)
) -> CommentRead:
    issue = crud.get_issue(db, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    try:
        comment = crud.add_comment(db, issue, data)
    except crud.StateTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CommentRead.model_validate(comment)


@router.post("/{issue_id}/assignee", response_model=IssueRead)
def update_assignee(
    issue_id: int, data: IssueAssigneeUpdate, db: Session = Depends(get_db)
) -> IssueRead:
    issue = crud.get_issue(db, issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    try:
        updated = crud.update_issue_assignee(db, issue, data)
    except crud.StateTransitionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    read = IssueRead.model_validate(updated)
    read.sla_status = attach_sla_status(updated)
    return read
