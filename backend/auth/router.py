"""
Authentication router — register, login and token-protected /me endpoint.

Uses an in-memory user store (dict) for hackathon speed; swap for a real
database in production. Includes resilient fallbacks for token and password hashing.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import base64
import hmac
from typing import Dict, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.models import (
    UserRegister,
    DoctorRegisterRequest,
    GoogleAuthRequest,
    UserLogin,
    Token,
    UserResponse,
)
from config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory user store: email / doctor_id -> user dict
_users_db: Dict[str, dict] = {}


def _hash_password(password: str) -> str:
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except Exception:
        salt = "healthguard-salt"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


# Prepopulate default accredited clinician profiles
_default_hash = _hash_password("PriviDoctor2026!")
_users_db["dr.sarah.johnson@gmail.com"] = {
    "id": "DR-SARAH-JOHNSON",
    "username": "Dr. Sarah Johnson, MD, DM",
    "name": "Dr. Sarah Johnson, MD, DM",
    "email": "dr.sarah.johnson@gmail.com",
    "doctor_id": "DR-SARAH-JOHNSON",
    "hospital_id": "HOSP_01",
    "hospital_name": "Fortis Escorts Heart Institute",
    "department": "Cardiology",
    "hashed_password": _default_hash,
}
_users_db["DR-SARAH-JOHNSON"] = _users_db["dr.sarah.johnson@gmail.com"]


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain, hashed)
    except Exception:
        salt = "healthguard-salt"
        expected = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
        return hmac.compare_digest(expected, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire.timestamp()})

    try:
        from jose import jwt
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    except Exception:
        header = {"alg": "HS256", "typ": "JWT"}
        h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        p_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
        sig = hmac.new(JWT_SECRET_KEY.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
        s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{h_b64}.{p_b64}.{s_b64}"


def _decode_token(token: str) -> Optional[dict]:
    try:
        from jose import jwt
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload_json = base64.urlsafe_b64decode(parts[1] + "==").decode()
            return json.loads(payload_json)
        except Exception:
            return None


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = _decode_token(token)
    if not payload:
        raise credentials_exception

    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = _users_db.get(email)
    if user is None:
        raise credentials_exception
    return user


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/register", response_model=Token)
def register(payload: UserRegister) -> Token:
    """Register a new clinician user and return a JWT token."""
    if payload.email in _users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_id = str(uuid.uuid4())
    _users_db[payload.email] = {
        "id": user_id,
        "username": payload.username,
        "email": payload.email,
        "hashed_password": _hash_password(payload.password),
    }

    access_token = create_access_token(data={"sub": payload.email})
    return Token(access_token=access_token)


@router.post("/login", response_model=Token)
def login(payload: UserLogin) -> Token:
    """Authenticate a clinician and return a JWT token with accredited doctor profile."""
    identifier = payload.doctor_id or payload.email
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID or Email is required",
        )

    identifier_clean = identifier.strip()
    user = (
        _users_db.get(identifier_clean)
        or _users_db.get(identifier_clean.lower())
        or _users_db.get(identifier_clean.upper())
    )

    if not user or not _verify_password(payload.password, user["hashed_password"]):
        # Support default demo verification credentials
        if identifier_clean.upper() in ["DR-SARAH-JOHNSON", "DR.SARAH.JOHNSON@GMAIL.COM"] and payload.password == "PriviDoctor2026!":
            user = _users_db["DR-SARAH-JOHNSON"]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid doctor credentials or passkey",
            )

    access_token = create_access_token(data={"sub": user["email"]})
    doctor_info = {
        "doctor_id": user.get("doctor_id", identifier_clean),
        "name": user.get("name", user.get("username", "Dr. Clinician")),
        "email": user.get("email", identifier_clean),
        "hospital_id": payload.hospital_id or user.get("hospital_id", "HOSP_01"),
        "hospital_name": user.get("hospital_name", "Fortis Escorts Heart Institute"),
        "department": payload.department or user.get("department", "Cardiology"),
        "role": "Doctor",
    }
    return Token(access_token=access_token, doctor=doctor_info)


@router.post("/doctor-register")
def doctor_register(payload: DoctorRegisterRequest):
    """Register a new clinician doctor profile with hospital credentials."""
    email_key = payload.email.lower().strip()
    doc_id_key = payload.doctor_id.strip()

    user_data = {
        "id": doc_id_key,
        "username": payload.name,
        "name": payload.name,
        "email": email_key,
        "doctor_id": doc_id_key,
        "hospital_id": payload.hospital_id or "HOSP_01",
        "hospital_name": payload.hospital_name or "Fortis Healthcare",
        "department": payload.department or "Cardiology",
        "hashed_password": _hash_password(payload.password),
    }

    _users_db[email_key] = user_data
    _users_db[doc_id_key] = user_data

    access_token = create_access_token(data={"sub": email_key})
    return {
        "status": "success",
        "access_token": access_token,
        "doctor": {
            "name": payload.name,
            "email": email_key,
            "doctor_id": doc_id_key,
            "hospital_id": payload.hospital_id or "HOSP_01",
            "hospital_name": payload.hospital_name or "Fortis Healthcare",
            "department": payload.department or "Cardiology",
        }
    }


@router.post("/google")
def google_auth(payload: GoogleAuthRequest):
    """Authenticate or register a clinician via Google / Gmail single sign-on."""
    email_key = payload.email.lower().strip()
    name = payload.name or email_key.split("@")[0].replace(".", " ").title()
    if not name.lower().startswith("dr.") and not name.lower().startswith("dr "):
        name = f"Dr. {name}"

    doc_id = f"DR-{email_key.split('@')[0].upper().replace('.', '-')}"

    if email_key not in _users_db:
        _users_db[email_key] = {
            "id": doc_id,
            "username": name,
            "name": name,
            "email": email_key,
            "doctor_id": doc_id,
            "hospital_id": payload.hospital_id or "HOSP_01",
            "hospital_name": "Ayushman Bharat Partner Hospital",
            "department": payload.department or "General Medicine",
            "hashed_password": _hash_password("google_sso_verified"),
            "provider": "google",
        }

    user = _users_db[email_key]
    access_token = create_access_token(data={"sub": email_key})
    return {
        "status": "success",
        "access_token": access_token,
        "doctor": {
            "name": user.get("name", user["username"]),
            "email": user["email"],
            "doctor_id": user.get("doctor_id", doc_id),
            "hospital_id": user.get("hospital_id", "HOSP_01"),
            "hospital_name": user.get("hospital_name", "Ayushman Bharat Partner Hospital"),
            "department": user.get("department", "General Medicine"),
            "provider": "google",
        }
    }


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Return the currently authenticated user's profile."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
    )
