from fastapi import HTTPException, Request
import secrets
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
SESSION_LIFE = 3 * 60 * 60
ACTIVE_SESSIONS = {}


def cleanup_expired_sessions() -> None:
    now = datetime.utcnow()
    expired_session_ids = [
        sid for sid, session in ACTIVE_SESSIONS.items()
        if session.get("exp") and session["exp"] <= now
    ]
    for sid in expired_session_ids:
        ACTIVE_SESSIONS.pop(sid, None)

def get_session(github_token: str, user_data: dict) -> str:
    cleanup_expired_sessions()
    expires_at = datetime.utcnow() + timedelta(seconds=SESSION_LIFE)
    session_id = secrets.token_urlsafe(32)

    ACTIVE_SESSIONS[session_id] = {
        "github_token": github_token,
        "user_id": user_data.get("login"),
        "exp": expires_at,
    }

    payload = {
        "sid": session_id,
        "exp": expires_at,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_access_token(request: Request) -> str:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated. Please login first.")
    
    try:
        payload = jwt.decode(session_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        session_id = payload.get("sid")
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid session. Please login again.")

        session_data = ACTIVE_SESSIONS.get(session_id)
        if not session_data:
            raise HTTPException(status_code=401, detail="Session not found. Please login again.")

        if session_data.get("exp") <= datetime.utcnow():
            ACTIVE_SESSIONS.pop(session_id, None)
            raise HTTPException(status_code=401, detail="Session expired. Please login again.")

        token = session_data.get("github_token")
        if not token:
            raise HTTPException(status_code=401, detail="No token found. Please login again.")
        return token
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid session: {str(e)}")


def end_session(session_cookie: Optional[str]) -> None:
    if not session_cookie:
        return

    try:
        payload = jwt.decode(session_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        session_id = payload.get("sid")
        if session_id:
            ACTIVE_SESSIONS.pop(session_id, None)
    except JWTError:
        # If cookie is malformed/expired, treat as already revoked.
        pass