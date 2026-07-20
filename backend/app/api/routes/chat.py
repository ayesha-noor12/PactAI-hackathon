from fastapi import APIRouter, HTTPException, Depends

from app.schemas.chat import ChatRequest
from app.agent.workflow import NegotiationWorkflow
from app.agent.session_manager import session_manager
from app.llm.qwen_thinking import QwenThinkingLLM
from app.api.routes.deps import get_current_user_email


router = APIRouter()

llm = QwenThinkingLLM()
workflow = NegotiationWorkflow(llm)


@router.post("/chat")
def chat(request: ChatRequest, user_email: str = Depends(get_current_user_email)):

    try:
        memory = session_manager.get(request.session_id, owner_email=user_email)

        result = workflow.process(
            request.message,
            memory
        )

        session_manager.save(request.session_id)

        return result

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )