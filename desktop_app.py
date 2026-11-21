"""
PriviCare — Desktop Application Launcher.

Runs the PriviCare Doctor Clinical Intelligence & Secure RAG Suite locally
in a native Windows desktop window (via Microsoft Edge WebView2 / pywebview)
directly on the user's HDD/SSD without opening external Google Chrome.
"""

import os
import sys

# Ensure sys.stdout and sys.stderr are never None in PyInstaller windowed mode (console=False)
if sys.stdout is None:
    try:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass
if sys.stderr is None:
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass

import time
import socket
import logging
import tempfile
import threading
import traceback
import urllib.request
import webbrowser

# ---------------------------------------------------------------------------
# Storage Directory Setup with Graceful Fallbacks
# ---------------------------------------------------------------------------
def _init_storage():
    """Find or create a writable local storage directory on SSD/HDD."""
    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "PriviCare"),
        os.path.join(os.path.expanduser("~"), ".privicare"),
        os.path.join(tempfile.gettempdir(), "PriviCare"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            data_p = os.path.join(candidate, "data")
            lance_p = os.path.join(candidate, "lancedb")
            os.makedirs(data_p, exist_ok=True)
            os.makedirs(lance_p, exist_ok=True)
            test_f = os.path.join(candidate, ".write_test")
            with open(test_f, "w") as f:
                f.write("ok")
            os.remove(test_f)
            return candidate
        except Exception:
            continue

    fallback = os.path.join(tempfile.gettempdir(), "PriviCare")
    os.makedirs(os.path.join(fallback, "data"), exist_ok=True)
    os.makedirs(os.path.join(fallback, "lancedb"), exist_ok=True)
    return fallback

_STORAGE_DIR = _init_storage()
os.environ["PRIVICARE_DATA_DIR"] = os.path.join(_STORAGE_DIR, "data")

# Configure persistent file logging for troubleshooting
_LOG_FILE = os.path.join(_STORAGE_DIR, "privicare_app.log")
logging.basicConfig(
    filename=_LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
logging.info("PriviCare starting up. Storage directory: %s", _STORAGE_DIR)

# ---------------------------------------------------------------------------
# Python Path & Bundle Detection
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

backend_dir = os.path.join(bundle_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if bundle_dir not in sys.path:
    sys.path.insert(0, bundle_dir)

# Import FastAPI app
try:
    from main import app
    logging.info("Successfully imported FastAPI main.app")
except Exception as e:
    logging.critical("Failed to import main.app: %s\n%s", e, traceback.format_exc())
    app = None

# ---------------------------------------------------------------------------
# Port Discovery & Server Management
# ---------------------------------------------------------------------------
def find_available_port(start_port=8000, max_attempts=25):
    """Find a guaranteed-free local TCP port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port

_server_instance = None
_server_error = None

def run_api_server(port):
    """Run uvicorn inside dedicated asyncio loop in background thread."""
    global _server_instance, _server_error
    try:
        import uvicorn
        import asyncio

        # Each thread requires its own asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=port,
            log_config=None,  # CRITICAL: prevents uvicorn from failing when sys.stdout has no isatty
            access_log=False,
        )
        _server_instance = uvicorn.Server(config)
        logging.info("Starting uvicorn server on 127.0.0.1:%d", port)
        loop.run_until_complete(_server_instance.serve())
    except Exception as e:
        _server_error = str(e)
        logging.critical("Uvicorn server crashed: %s\n%s", e, traceback.format_exc())

def wait_for_server(url, timeout=25.0):
    """Actively poll /api/health until server is confirmed responding with 200 OK."""
    health_url = f"{url}/api/health"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(
                health_url,
                headers={"User-Agent": "PriviCare-Desktop-Probe"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    logging.info("Server health confirmed at %s in %.2fs", url, time.time() - start_time)
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    logging.warning("Server health check timed out after %.2fs", timeout)
    return False

# ---------------------------------------------------------------------------
# Main Launcher
# ---------------------------------------------------------------------------
def main():
    if app is None:
        logging.critical("Cannot start: FastAPI app failed to import.")
        return

    # 1. Discover free port
    port = find_available_port(8000)
    url = f"http://127.0.0.1:{port}"
    logging.info("Selected local endpoint: %s", url)

    # 2. Start server thread
    server_thread = threading.Thread(target=run_api_server, args=(port,), daemon=True)
    server_thread.start()

    # 3. Actively wait until the server is UP before opening WebView
    server_ready = wait_for_server(url, timeout=20.0)
    if not server_ready:
        logging.error("Server did not respond in time. Attempting window launch anyway.")

    # 4. Resolve icon path
    icon_candidates = [
        os.path.join(bundle_dir, "assets", "icon.ico"),
        os.path.join(bundle_dir, "backend", "assets", "icon.ico"),
        os.path.join(_STORAGE_DIR, "icon.ico"),
    ]
    icon_path = next((p for p in icon_candidates if os.path.exists(p)), None)

    # 5. Launch native Windows desktop app window (pywebview with Edge WebView2)
    native_window_success = False
    try:
        import webview
        logging.info("Initializing Edge WebView2 window for %s", url)
        window = webview.create_window(
            title="PriviCare — Doctor Clinical Intelligence & Secure RAG Suite",
            url=url,
            width=1380,
            height=880,
            resizable=True,
            min_size=(1024, 700),
            confirm_close=False,
        )
        native_window_success = True
        logging.info("Starting webview event loop (gui=edgechromium)")
        webview.start(gui="edgechromium", icon=icon_path)
    except Exception as e:
        logging.warning("WebView2 desktop window unavailable (%s). Falling back to browser.", e)
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass

    # 6. Clean shutdown
    logging.info("PriviCare desktop window closed. Shutting down server.")
    if _server_instance:
        _server_instance.should_exit = True
    sys.exit(0)


if __name__ == "__main__":
    main()
