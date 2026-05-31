from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import IssueRead, WebhookIngestResponse, WebhookIssuePayload
from app.services.sla import attach_sla_status
from app.services.webhook_normalizer import WebhookNormalizationError, normalize_webhook_payload

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/issues", response_model=WebhookIngestResponse, status_code=201)
def ingest_issue_webhook(
    payload: WebhookIssuePayload,
    db: Session = Depends(get_db),
) -> WebhookIngestResponse:
    try:
        normalized = normalize_webhook_payload(db, payload)
    except WebhookNormalizationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    issue, created = crud.ingest_webhook_issue(db, normalized)
    read = IssueRead.model_validate(issue)
    read.sla_status = attach_sla_status(issue)

    status_code_note = "created" if created else "duplicate external_id; returning existing issue"
    notes = list(normalized.notes)
    if not created:
        notes.append(status_code_note)

    return WebhookIngestResponse(
        issue=read,
        created=created,
        confidence=normalized.confidence,
        notes=notes,
    )
