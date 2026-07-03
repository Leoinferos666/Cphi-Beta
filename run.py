import os
import subprocess
import sys

base = os.path.dirname(os.path.abspath(__file__))

subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        os.path.join(base, "app.py"),
        "--server.headless=true"
    ]
)