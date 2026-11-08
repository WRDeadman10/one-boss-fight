"""Fail if Development-only presentation or package-stamp strings ship."""
import sys
from pathlib import Path

TOKENS = ("rpg.Art.Tier2", "BuildStamp.txt", "DEVELOPMENT BUILD")


def find_tokens(data: bytes) -> list[str]:
    return [token for token in TOKENS
            if token.encode("ascii") in data or token.encode("utf-16-le") in data]


def main() -> int:
    binary = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "Saved/StagedBuilds_Shipping/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe"
    )
    if not binary.is_file():
        print(f"FAIL no Shipping executable at {binary}")
        return 1
    data = binary.read_bytes()
    hits = find_tokens(data)
    print(f"binary: {binary} ({len(data)} bytes)")
    for token in TOKENS:
        print(f"{token}: {'FOUND' if token in hits else 'absent'}")
    print("VERDICT " + ("FAIL: Development-only symbols present" if hits else "PASS: Development-only symbols absent"))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
