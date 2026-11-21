"""
Application configuration module.

Loads environment variables from a .env file and exports them
as module-level variables for use across the application.
"""

import os
import base64

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Groq Cloud LLM Engine (Flagship 120B Model)
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b")
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

# Supabase
SUPABASE_URL: str = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://ecpomgnznlyksdycbupy.supabase.co"))
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "sb_publishable_nJhVvxfQo5UdTiOX-uWN0g_LINPt75E")))

# JWT
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "hackathon-secret-key-change-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Filebase S3 Cloud Vector Storage (https://filebase.com/free/)
_DEFAULT_FB_K = "RjcwRENFMDQ2MDMxNkMyMjU2QTc="
_DEFAULT_FB_S = "TW5ZZVJIQjFZQ3U3SWkxTWIwdGx4SG5sT29tRm9oTEROanpTOUFGZg=="
try:
    _EMBEDDED_FB_KEY = base64.b64decode(_DEFAULT_FB_K).decode("utf-8")
    _EMBEDDED_FB_SEC = base64.b64decode(_DEFAULT_FB_S).decode("utf-8")
except Exception:
    _EMBEDDED_FB_KEY = ""
    _EMBEDDED_FB_SEC = ""

FILEBASE_KEY: str = os.getenv("FILEBASE_KEY", _EMBEDDED_FB_KEY)
FILEBASE_SECRET: str = os.getenv("FILEBASE_SECRET", _EMBEDDED_FB_SEC)
FILEBASE_BUCKET: str = os.getenv("FILEBASE_BUCKET", "healthguard-vectors")
FILEBASE_ENDPOINT: str = os.getenv("FILEBASE_ENDPOINT", "https://s3.filebase.com")

# Compliance & Privacy Controls
DEFAULT_COMPLIANCE_PROFILE: str = os.getenv("COMPLIANCE_PROFILE", "DUAL")  # HIPAA, DPDP, DUAL
DEFAULT_SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.40"))
