#!/usr/bin/env python3
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "engine"))

from memory_mcp.server import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
