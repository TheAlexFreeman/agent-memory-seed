#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from memory_engine_core.engine import main as engine_main


def main() -> int:
    return engine_main()


if __name__ == "__main__":
    raise SystemExit(main())
