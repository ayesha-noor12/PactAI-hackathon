from fastapi import Header, HTTPException


def get_current_user_email(x_user_email: str | None = Header(default=None)) -> str:
    """
    Identifies which account is making this request. The frontend sends this
    automatically on every call once someone's logged in (see src/lib/api.js).

    IMPORTANT: this is NOT real authentication — it trusts whatever email the client
    sends, with no password or token verified per-request. That matches the rest of
    the current auth system (login/signup return no token either). This is enough to
    stop accounts from seeing each other's data for a hackathon demo; before this
    handles real users, replace it with proper JWT-based auth issued at login and
    verified here instead of just trusted.
    """
    if not x_user_email:
        raise HTTPException(
            status_code=401,
            detail="Missing user identity — make sure you're logged in.",
        )
    return x_user_email