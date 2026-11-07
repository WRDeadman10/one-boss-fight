"""Run the Scripts/Tools unittest suite and enforce its wall-time budget."""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAX_SECONDS = 20.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    args = parser.parse_args()
    if not math.isfinite(args.max_seconds) or args.max_seconds <= 0:
        parser.error("--max-seconds must be finite and positive")

    command = [sys.executable, "-m", "unittest", "discover", "-s", "Scripts/Tools"]
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, check=False)
    elapsed = time.monotonic() - started
    print("OFFLINE_SUITE elapsed_seconds=%.3f limit_seconds=%.3f" % (elapsed, args.max_seconds), flush=True)
    if result.returncode != 0:
        return result.returncode
    if elapsed >= args.max_seconds:
        print("OFFLINE_SUITE_TIMING FAIL: elapsed time reached or exceeded the limit", file=sys.stderr)
        return 2
    print("OFFLINE_SUITE_TIMING PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
