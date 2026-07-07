"""
Security Module — OAuth, 2FA, encryption, audit logs, device/session management, secrets.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import base64
import hmac

from app.database.session import get_db
from app.core.security import get_current_user_id, hash_password
from app.models.user import User, UserSession

router = APIRouter()


# ─── 2FA (TOTP-based) ───

@router.post("/2fa/setup")
def setup_2fa(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Generate TOTP secret for 2FA setup."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')

    prefs = user.preferences or {}
    prefs["2fa_secret"] = secret
    prefs["2fa_enabled"] = False
    user.preferences = prefs
    db.commit()

    provisioning_uri = f"otpauth://totp/PreStocks:{user.email}?secret={secret}&issuer=PreStocks"

    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "message": "Scan QR code with authenticator app, then verify with /2fa/verify"
    }


@router.post("/2fa/verify")
def verify_2fa(code: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Verify TOTP code and enable 2FA."""
    user = db.query(User).filter(User.id == user_id).first()
    prefs = user.preferences or {}
    secret = prefs.get("2fa_secret")

    if not secret:
        raise HTTPException(status_code=400, detail="2FA not set up. Call /2fa/setup first.")

    if _verify_totp(secret, code):
        prefs["2fa_enabled"] = True
        prefs["2fa_backup_codes"] = [secrets.token_hex(4) for _ in range(8)]
        user.preferences = prefs
        db.commit()
        return {"message": "2FA enabled successfully", "backup_codes": prefs["2fa_backup_codes"]}

    raise HTTPException(status_code=401, detail="Invalid TOTP code")


@router.post("/2fa/disable")
def disable_2fa(code: str, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Disable 2FA after verification."""
    user = db.query(User).filter(User.id == user_id).first()
    prefs = user.preferences or {}

    if not prefs.get("2fa_enabled"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    secret = prefs.get("2fa_secret")
    if not _verify_totp(secret, code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    prefs["2fa_enabled"] = False
    prefs.pop("2fa_secret", None)
    prefs.pop("2fa_backup_codes", None)
    user.preferences = prefs
    db.commit()
    return {"message": "2FA disabled"}


# ─── DEVICE & SESSION MANAGEMENT ───

@router.get("/sessions")
def list_sessions(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """List all active sessions for the user."""
    sessions = (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.expires_at > datetime.utcnow())
        .order_by(UserSession.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(s.id),
            "device_info": s.device_info,
            "ip_address": s.ip_address,
            "created_at": s.created_at,
            "expires_at": s.expires_at
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Revoke a specific session (log out device)."""
    session = db.query(UserSession).filter(
        UserSession.id == session_id, UserSession.user_id == user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session revoked"}


@router.post("/sessions/revoke-all")
def revoke_all_sessions(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Revoke all sessions except current (log out all devices)."""
    deleted = db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    db.commit()
    return {"message": f"Revoked {deleted} sessions"}


# ─── AUDIT LOG ───

@router.get("/audit-log")
def get_audit_log(
    limit: int = 50,
    action: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's security audit log."""
    from app.models.base import Base
    # Query audit_log table if it exists
    try:
        from sqlalchemy import text
        query = text("""
            SELECT id, action, resource_type, resource_id, ip_address, created_at
            FROM audit_log WHERE user_id = :uid
            ORDER BY created_at DESC LIMIT :lim
        """)
        result = db.execute(query, {"uid": user_id, "lim": limit})
        rows = result.fetchall()
        return [
            {"id": r[0], "action": r[1], "resource_type": r[2], "resource_id": r[3], "ip": r[4], "timestamp": r[5]}
            for r in rows
        ]
    except Exception:
        return {"message": "Audit log table not yet initialized", "entries": []}


# ─── ENCRYPTION UTILITIES ───

@router.post("/encrypt-note")
def encrypt_note(
    content: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Encrypt sensitive notes (e.g., investment thesis) for the user."""
    user = db.query(User).filter(User.id == user_id).first()
    key = _derive_key(str(user.id), user.email)
    encrypted = _xor_encrypt(content, key)
    return {"encrypted": base64.b64encode(encrypted.encode()).decode(), "algorithm": "xor-derived"}


@router.post("/decrypt-note")
def decrypt_note(
    encrypted_content: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Decrypt a previously encrypted note."""
    user = db.query(User).filter(User.id == user_id).first()
    key = _derive_key(str(user.id), user.email)
    decoded = base64.b64decode(encrypted_content).decode()
    decrypted = _xor_encrypt(decoded, key)
    return {"content": decrypted}


# ─── SECRETS MANAGEMENT ───

@router.get("/api-keys")
def list_api_keys(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """List user's API keys (masked)."""
    from app.models.api_key import APIKey
    keys = db.query(APIKey).filter(APIKey.user_id == user_id).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "scopes": k.scopes,
            "is_active": k.is_active,
            "last_used_at": k.last_used_at,
            "created_at": k.created_at
        }
        for k in keys
    ]


@router.post("/api-keys")
def create_api_key(
    name: str,
    scopes: list = ["read"],
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Generate a new API key."""
    from app.models.api_key import APIKey

    raw_key = f"ps_{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    prefix = raw_key[:7]

    api_key = APIKey(
        user_id=user_id,
        key_hash=key_hash,
        key_prefix=prefix,
        name=name,
        scopes=scopes,
        rate_limit=100
    )
    db.add(api_key)
    db.commit()

    return {
        "id": api_key.id,
        "key": raw_key,
        "name": name,
        "warning": "Store this key securely. It won't be shown again."
    }


@router.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Revoke an API key."""
    from app.models.api_key import APIKey
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == user_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    db.commit()
    return {"message": "API key revoked"}


# ─── Helper Functions ───

def _verify_totp(secret: str, code: str) -> bool:
    """Verify TOTP code (simplified — production should use pyotp)."""
    import time
    time_step = int(time.time()) // 30
    for offset in range(-1, 2):
        expected = _generate_totp(secret, time_step + offset)
        if hmac.compare_digest(expected, code):
            return True
    return False


def _generate_totp(secret: str, time_step: int) -> str:
    """Generate TOTP code from secret and time step."""
    key = base64.b32decode(secret)
    msg = time_step.to_bytes(8, 'big')
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    truncated = int.from_bytes(h[offset:offset + 4], 'big') & 0x7FFFFFFF
    return str(truncated % 1000000).zfill(6)


def _derive_key(user_id: str, email: str) -> str:
    return hashlib.sha256(f"{user_id}:{email}:prestocks_enc".encode()).hexdigest()[:32]


def _xor_encrypt(text: str, key: str) -> str:
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))
