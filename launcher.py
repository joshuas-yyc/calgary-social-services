"""
Entry point for the packaged Calgary Social Services app.
Run directly in dev: python launcher.py
Run as built exe:   double-click Calgary-Services (or Calgary-Services.exe)
"""
import sys
import os
import threading
import webbrowser
import time
import socket

BUNDLED = getattr(sys, "frozen", False)


def _setup_paths():
    if BUNDLED:
        # One-dir: the exe and bundled resources sit in the same folder
        base = os.path.dirname(sys.executable)
        os.chdir(base)
        # Store the database in a user-writable location so it persists across updates
        data_dir = os.path.join(os.path.expanduser("~"), ".calgary-services")
        os.makedirs(data_dir, exist_ok=True)
        os.environ["CALGARY_DATA_DIR"] = data_dir


def find_free_port(preferred: int = 8787) -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", preferred))
        return preferred
    except OSError:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def open_browser(url: str, delay: float = 1.5) -> None:
    time.sleep(delay)
    webbrowser.open(url)


if __name__ == "__main__":
    _setup_paths()

    from app.database import init_db, DB_PATH

    first_run = not DB_PATH.exists()
    init_db()

    if first_run:
        print("First launch — loading Calgary services data...")
        from seed_real import seed
        from enrich_data import enrich
        seed()
        enrich()
        print("Data loaded.\n")

    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    print(f"  Calgary Social Services is running at {url}")
    print("  Close this window to stop the app.\n")

    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    import uvicorn
    from app.main import app as fastapi_app

    uvicorn.run(fastapi_app, host="127.0.0.1", port=port, log_level="warning")
