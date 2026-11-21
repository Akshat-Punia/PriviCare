"""
PriviCare — Healthcare PII Anonymization & Doctor Clinical Intelligence Suite.

FastAPI Application Entry Point providing:
- Doctor-exclusive portal with patient management & historical report analysis
- Scoped PII Anonymization & Local Cryptographic Vault
- Local RAG-Powered Clinical Question & Answering
- Real-time Patient Chat Review for Clinicians
- Embedded Single-Page Desktop Application Interface
"""

import os
import sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from auth.router import router as auth_router
from routes.upload import router as upload_router
from routes.chat import router as chat_router
from routes.privacy import router as privacy_router
from routes.clinical import router as clinical_router
try:
    from routes.audit import router as audit_router
except ImportError:
    audit_router = None
from web_ui import get_app_html

app = FastAPI(
    title="PriviCare — Doctor Clinical Intelligence & Secure RAG Suite",
    description="Doctor-exclusive clinical intelligence portal with zero-leakage PII anonymization, "
                "historical patient report analysis, and privacy-preserving clinical RAG.",
    version="2.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(privacy_router)
app.include_router(clinical_router)
if audit_router is not None:
    app.include_router(audit_router)

# ---------------------------------------------------------------------------
# Static Assets (PriviCare Logos & Icons)
# ---------------------------------------------------------------------------
import sys
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
    if not os.path.isdir(_ASSETS_DIR):
        _ASSETS_DIR = os.path.join(sys._MEIPASS, "backend", "assets")
else:
    _ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))

if os.path.isdir(_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=_ASSETS_DIR), name="assets")


# ---------------------------------------------------------------------------
# Health-check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["health"])
def health_check() -> dict:
    """API health-check endpoint."""
    return {
        "status": "healthy",
        "service": "PriviCare Clinical Intelligence RAG API",
        "version": "2.0.0",
    }


# ---------------------------------------------------------------------------
# Web UI Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["ui"])
@app.get("/login", response_class=HTMLResponse, tags=["ui"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["ui"])
@app.get("/dashboard/{subpath:path}", response_class=HTMLResponse, tags=["ui"])
def serve_ui():
    """Serve embedded PriviCare Doctor Clinical Suite."""
    return HTMLResponse(content=get_app_html())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
