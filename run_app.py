"""
Digital DNA Desktop Application Launcher.
Run directly from root: python run_app.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.desktop.main import main

if __name__ == "__main__":
    main()
