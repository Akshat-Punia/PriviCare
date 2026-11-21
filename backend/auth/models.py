"""
Pydantic models for authentication payloads and responses.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Payload for user registration."""

    username: str
    email: str
    password: str


class DoctorRegisterRequest(BaseModel):
    """Payload for doctor registration with hospital credentials."""

    name: str
    email: str
    doctor_id: str
    hospital_name: Optional[str] = "Fortis Healthcare"
    hospital_id: Optional[str] = "HOSP_01"
    department: Optional[str] = "Cardiology"
    password: str
    compliance_confirmed: Optional[bool] = True


class GoogleAuthRequest(BaseModel):
    """Payload for Google / Gmail single sign-on."""

    email: str
    name: Optional[str] = None
    hospital_id: Optional[str] = "HOSP_01"
    department: Optional[str] = "Cardiology"
    google_token: Optional[str] = None


class UserLogin(BaseModel):
    """Payload for user and doctor login."""

    email: Optional[str] = None
    doctor_id: Optional[str] = None
    password: str
    hospital_id: Optional[str] = None
    department: Optional[str] = None


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    doctor: Optional[dict] = None


class UserResponse(BaseModel):
    """Public user representation (no password)."""

    id: str
    username: str
    email: str
