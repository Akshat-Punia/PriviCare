#!/usr/bin/env python3
"""
ocr_engine.py — Extracted Standalone OCR & Document Ingestion Engine
Derived from Vexis-Law ingestion pipeline (`backend/ingestion/extract_pdf.py`).

Capabilities:
1. Native Text Extraction (PyMuPDF / Fast pass for digitally generated PDFs).
2. Tesseract C++ OCR Engine invocation for scanned PDFs and photos (PNG, JPG, TIFF, etc.).
3. Indian Script Support: English + Hindi (Devanagari) with automatic script fallback.
4. Preprocessing: EXIF orientation correction, illumination flattening (shadow removal),
   Otsu binarization, deskewing, and confidence scoring.
5. Standalone Execution: Auto-detects bundled Vexis Tesseract C++ and Ingestion binaries,
   with fallback to system Python libraries.

Usage:
    python ocr_engine.py <document_path> [--raw]
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Paths to bundled binaries inside Vexis-Law repository
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent / "Vexis-Law-main"
BUNDLED_BIN_DIR = PROJECT_ROOT / "src-tauri" / "bin"
WINDOWS_INGESTION_EXE = BUNDLED_BIN_DIR / "ingestion-x86_64-pc-windows-msvc.exe"
TESSERACT_EXE = BUNDLED_BIN_DIR / "tesseract" / "tesseract.exe"
TESSDATA_DIR = BUNDLED_BIN_DIR / "tesseract" / "tessdata"


def get_tesseract_path() -> str | None:
    """Find tesseract binary: environment variable, bundled binary, or system PATH."""
    env_cmd = os.getenv("TESSERACT_CMD")
    if env_cmd and os.path.exists(env_cmd):
        return env_cmd
    if TESSERACT_EXE.exists():
        return str(TESSERACT_EXE)
    import shutil
    sys_cmd = shutil.which("tesseract")
    if sys_cmd:
        return sys_cmd
    return None


def get_tessdata_prefix() -> str | None:
    """Find tessdata directory: environment variable or bundled directory."""
    env_data = os.getenv("TESSDATA_PREFIX")
    if env_data and os.path.exists(env_data):
        return env_data
    if TESSDATA_DIR.exists():
        return str(TESSDATA_DIR)
    return None


def extract_document(file_path: str, langs: str = "eng+hin") -> dict:
    """
    Extract text from a PDF, image, or text file.
    Returns:
        {
            "extracted_text": str,
            "pages": int,
            "native_pages": int,
            "ocr_pages": int,
            "engine": str,
            "warnings": list[str],
            "low_confidence_pages": list[dict]
        }
    """
    path = Path(file_path).resolve()
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    # If it's a plain text file, read directly
    if path.suffix.lower() in {".txt", ".md", ".json", ".log"}:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return {
                "extracted_text": content,
                "pages": 1,
                "native_pages": 1,
                "ocr_pages": 0,
                "engine": "plain_text",
                "warnings": [],
                "low_confidence_pages": []
            }
        except Exception as e:
            return {"error": f"Failed to read text file: {e}"}

    # Method 1: Use the bundled standalone compiled binary if present on Windows
    if os.name == "nt" and WINDOWS_INGESTION_EXE.exists():
        env = os.environ.copy()
        tess_cmd = get_tesseract_path()
        tess_data = get_tessdata_prefix()
        if tess_cmd:
            env["TESSERACT_CMD"] = tess_cmd
        if tess_data:
            env["TESSDATA_PREFIX"] = tess_data
        env["OCR_LANGS"] = langs

        try:
            res = subprocess.run(
                [str(WINDOWS_INGESTION_EXE), str(path)],
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            if res.returncode == 0 and res.stdout.strip():
                try:
                    return json.loads(res.stdout.strip())
                except json.JSONDecodeError:
                    return {
                        "extracted_text": res.stdout,
                        "pages": 1,
                        "native_pages": 0,
                        "ocr_pages": 1,
                        "engine": "bundled_ingestion_cli",
                        "warnings": [],
                        "low_confidence_pages": []
                    }
        except Exception as e:
            pass  # Fall through to python implementation

    # Method 2: Execute python extraction sidecar directly
    python_sidecar = PROJECT_ROOT / "backend" / "ingestion" / "extract_pdf.py"
    if python_sidecar.exists():
        env = os.environ.copy()
        tess_cmd = get_tesseract_path()
        tess_data = get_tessdata_prefix()
        if tess_cmd:
            env["TESSERACT_CMD"] = tess_cmd
        if tess_data:
            env["TESSDATA_PREFIX"] = tess_data
        env["OCR_LANGS"] = langs

        try:
            res = subprocess.run(
                [sys.executable, str(python_sidecar), str(path)],
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            if res.stdout.strip():
                try:
                    return json.loads(res.stdout.strip())
                except json.JSONDecodeError:
                    return {"extracted_text": res.stdout, "engine": "python_sidecar", "warnings": []}
        except Exception as e:
            return {"error": f"Extraction subprocess failed: {e}"}

    # Method 3: Direct Tesseract invocation for images
    tess_cmd = get_tesseract_path()
    tess_data = get_tessdata_prefix()
    if tess_cmd and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
        cmd = [tess_cmd, str(path), "stdout", "-l", langs]
        if tess_data:
            cmd.extend(["--tessdata-dir", tess_data])
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                return {
                    "extracted_text": res.stdout,
                    "pages": 1,
                    "native_pages": 0,
                    "ocr_pages": 1,
                    "engine": "tesseract_direct",
                    "warnings": [],
                    "low_confidence_pages": []
                }
        except Exception as e:
            return {"error": f"Direct Tesseract OCR failed: {e}"}

    return {"error": "No suitable extraction or OCR engine could be invoked."}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {Path(sys.argv[0]).name} <file_path> [--raw]")
        sys.exit(1)

    file_path = sys.argv[1]
    raw_mode = "--raw" in sys.argv

    result = extract_document(file_path)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if raw_mode:
        print(result.get("extracted_text", ""))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
