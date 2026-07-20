import os
import pickle
from datetime import datetime
from typing import Dict

from app.agent.conversation_memory import ConversationMemory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SESSIONS_DIR = os.path.join(BASE_DIR, "storage", "sessions")


class SessionManager:

    def __init__(self):

        os.makedirs(SESSIONS_DIR, exist_ok=True)
        self.sessions: Dict[str, ConversationMemory] = {}

    def _path(self, session_id: str) -> str:
        return os.path.join(SESSIONS_DIR, f"{session_id}.pkl")

    def exists(self, session_id: str) -> bool:
        return session_id in self.sessions or os.path.exists(self._path(session_id))

    def get(self, session_id: str, owner_email: str | None = None) -> ConversationMemory:

        if session_id in self.sessions:
            memory = self.sessions[session_id]
        else:
            path = self._path(session_id)

            if os.path.exists(path):
                with open(path, "rb") as f:
                    memory = pickle.load(f)
            else:
                memory = ConversationMemory()
                memory.session_id = session_id
                memory.owner_email = owner_email

            self.sessions[session_id] = memory

        # Ownership check — a session created by one account should never be readable
        # by another, even if they somehow ended up with the same session_id. This is
        # the actual fix for "accounts shouldn't cross each other."
        existing_owner = getattr(memory, "owner_email", None)

        if owner_email is not None and existing_owner is not None and existing_owner != owner_email:
            raise PermissionError("This session belongs to a different account.")

        # Backfill ownership on old sessions created before this field existed, or
        # sessions somehow created without an owner.
        if existing_owner is None and owner_email is not None:
            memory.owner_email = owner_email

        return memory

    def save(self, session_id: str):

        if session_id not in self.sessions:
            return

        with open(self._path(session_id), "wb") as f:
            pickle.dump(self.sessions[session_id], f)

    def list_sessions(self, owner_email: str | None = None):
        """
        Returns a summary of every saved session belonging to owner_email, newest
        first. If owner_email is None, returns nothing — this should never happen in
        practice since the route always supplies it, but failing closed (returning
        nothing) is safer than accidentally returning everyone's sessions.
        """

        if owner_email is None:
            return []

        summaries = []

        for fname in os.listdir(SESSIONS_DIR):

            if not fname.endswith(".pkl"):
                continue

            session_id = fname[:-4]
            path = os.path.join(SESSIONS_DIR, fname)

            try:
                with open(path, "rb") as f:
                    memory = pickle.load(f)
            except Exception:
                continue

            if getattr(memory, "owner_email", None) != owner_email:
                continue

            last_client_message = next(
                (m["content"] for m in reversed(memory.messages) if m["role"] == "user"),
                None,
            )

            label = memory.requirements.project_type or f"New conversation ({session_id[:8]})"

            summaries.append({
                "session_id": session_id,
                "label": label,
                "stage": memory.stage,
                "message_count": len(memory.messages),
                "last_message": last_client_message,
                "proposal_id": memory.proposal_id,
                "updated_at": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
            })

        summaries.sort(key=lambda s: s["updated_at"], reverse=True)
        return summaries


session_manager = SessionManager()