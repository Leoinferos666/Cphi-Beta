import os
import subprocess
import socket
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))

def wait_for_server():
    while True:
        try:
            s = socket.create_connection(("127.0.0.1", 8501), timeout=1)
            s.close()
            break
        except OSError:
            time.sleep(1)

    webbrowser.open("http://127.0.0.1:8501")

threading.Thread(target=wait_for_server, daemon=True).start()

subprocess.run([
    "python",
    "-m",
    "streamlit",
    "run",
    os.path.join(ROOT, "app.py"),
    "--server.headless=true"
])