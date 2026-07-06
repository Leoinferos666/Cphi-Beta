import subprocess
import sys
import os
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))

subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ],
    cwd=ROOT
)

time.sleep(3)

webbrowser.open("http://localhost:8501")