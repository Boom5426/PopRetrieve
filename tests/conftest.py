import sys
from pathlib import Path

# put <package>/src on sys.path so `data` / `retrieval` / `utils` import as packages
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
