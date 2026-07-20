import json
import os
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STORE_FILE = os.path.join(BASE_DIR, "storage", "proposals.json")


def _load():
    if not os.path.exists(STORE_FILE):
        return []
    with open(STORE_FILE, "r") as f:
        return json.load(f)


def _save(data):
    os.makedirs(os.path.dirname(STORE_FILE), exist_ok=True)
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=2)


class ProposalStore:

    def create(self, owner_email, **fields):

        data = _load()

        record = {
            "id": str(uuid.uuid4()),
            "owner_email": owner_email,
            "status": "pending_review",
            "created_at": datetime.now().isoformat(),
            **fields,
        }

        data.append(record)
        _save(data)
        return record

    def list(self, owner_email, include_rejected: bool = False):

        data = [p for p in _load() if p.get("owner_email") == owner_email]

        if include_rejected:
            return data

        # Rejected proposals go to the "recycle bin" — hidden from the main list by
        # default, matching "if the user hits reject, put it in the recycle bin".
        return [p for p in data if p["status"] != "rejected"]

    def list_rejected(self, owner_email):
        """The recycle bin itself — only this account's rejected proposals."""
        return [
            p for p in _load()
            if p.get("owner_email") == owner_email and p["status"] == "rejected"
        ]

    def get(self, proposal_id: str, owner_email: str | None = None):
        for p in _load():
            if p["id"] == proposal_id:
                # If an owner is specified, enforce it — one account shouldn't be able
                # to view another's proposal by guessing/URL-sharing an id.
                if owner_email is not None and p.get("owner_email") != owner_email:
                    return None
                return p
        return None

    def set_status(self, proposal_id: str, status: str, owner_email: str | None = None):

        data = _load()

        for p in data:
            if p["id"] == proposal_id:
                if owner_email is not None and p.get("owner_email") != owner_email:
                    return None
                p["status"] = status
                _save(data)
                return p

        return None


proposal_store = ProposalStore()