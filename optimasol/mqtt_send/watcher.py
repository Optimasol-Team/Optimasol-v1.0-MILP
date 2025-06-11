"""
watcher.py – Monitor every decisions.txt under <clients_root> and
             call send_command(client_dir) as soon as it changes.

How to run
----------
python -m mqtt_send.watcher "C:/path/to/optimasol/clients"
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import the sender’s public entry point
from .sender import send_command


class DecisionsHandler(FileSystemEventHandler):
    """Callback invoked by watchdog on every filesystem change."""

    def on_modified(self, event):
        # Ignore directory events
        if event.is_directory:
            return

        path = Path(event.src_path)

        # Only react to files literally named decisions.txt
        if path.name.lower() != "decisions.txt":
            return

        client_dir = path.parent  # …/clients/<CLIENT_ID>

        try:
            # Trigger the MQTT send for this client
            send_command(str(client_dir))
        except Exception as exc:
            # Log but keep watcher alive
            print(f"[watcher] Error while sending for {client_dir}: {exc}")


def run_watcher(clients_root: str | Path) -> None:
    """
    Start watching <clients_root> recursively; never returns
    (Ctrl-C / SIGINT to stop).
    """
    root = Path(clients_root).resolve()
    if not root.is_dir():
        raise ValueError(f"{root} is not a directory")

    handler = DecisionsHandler()
    observer = Observer()
    observer.schedule(handler, str(root), recursive=True)
    observer.start()

    print(f"[watcher] Monitoring {root} (press Ctrl-C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


