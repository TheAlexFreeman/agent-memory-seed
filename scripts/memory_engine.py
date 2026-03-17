#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "engine"))

from memory_engine_core.engine import main as engine_main  # noqa: E402


def main() -> int:
    return engine_main()


if __name__ == "__main__":
    raise SystemExit(main())
