from fastapi import APIRouter, HTTPException, Depends

from app.agent.session_manager import session_manager
from app.api.routes.deps import get_current_user_email

router = APIRouter()


@router.get("/sessions")
def list_sessions(user_email: str = Depends(get_current_user_email)):
    return session_manager.list_sessions(owner_email=user_email)


@router.get("/sessions/{session_id}")
def get_session(session_id: str, user_email: str = Depends(get_current_user_email)):

    if not session_manager.exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    try:
        memory = session_manager.get(session_id, owner_email=user_email)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return {
        "session_id": session_id,
        "stage": memory.stage,
        "messages": memory.messages,
        "project_type": memory.requirements.project_type,
        "proposal_id": memory.proposal_id,
        "agreed_price": memory.agreed_price,
        "agreed_timeline": memory.agreed_timeline,
    }