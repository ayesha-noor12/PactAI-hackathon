from fastapi import APIRouter, HTTPException, Depends

from app.agent.proposal_store import proposal_store
from app.api.routes.deps import get_current_user_email

router = APIRouter()


@router.get("/proposals")
def list_proposals(user_email: str = Depends(get_current_user_email)):
    return proposal_store.list(owner_email=user_email)


@router.get("/proposals/rejected")
def list_rejected_proposals(user_email: str = Depends(get_current_user_email)):
    return proposal_store.list_rejected(owner_email=user_email)


@router.get("/proposals/{proposal_id}")
def get_proposal(proposal_id: str, user_email: str = Depends(get_current_user_email)):
    proposal = proposal_store.get(proposal_id, owner_email=user_email)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@router.post("/proposals/{proposal_id}/accept")
def accept_proposal(proposal_id: str, user_email: str = Depends(get_current_user_email)):
    proposal = proposal_store.set_status(proposal_id, "accepted", owner_email=user_email)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str, user_email: str = Depends(get_current_user_email)):
    proposal = proposal_store.set_status(proposal_id, "rejected", owner_email=user_email)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return proposal