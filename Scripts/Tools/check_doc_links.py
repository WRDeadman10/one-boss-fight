#!/usr/bin/env python3
"""Find broken relative Markdown links in Documentation/**/*.md."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\s*\)")
INLINE_CODE = re.compile(r"(`+).*?\1")
CPP_LAMBDA = re.compile(r"\[\]\s*\([^)]*\)")


def find_broken(root: Path) -> list[str]:
    docs = root / "Documentation"
    issues: list[str] = []
    for markdown in sorted(docs.rglob("*.md")):
        source = markdown.read_text(encoding="utf-8", errors="replace")
        in_fence = False
        for number, line in enumerate(source.splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            visible = CPP_LAMBDA.sub("", INLINE_CODE.sub("", line))
            for match in LINK.finditer(visible):
                target = unquote(match.group(1) or match.group(2) or "").strip()
                parsed = urlsplit(target)
                if not target or parsed.scheme or target.startswith("//"):
                    continue
                path = parsed.path
                if not path:  # fragment-only link
                    continue
                candidate = (markdown.parent / path).resolve() if not path.startswith("/") else (root / path.lstrip("/")).resolve()
                if not candidate.exists():
                    issues.append(f"{markdown}:{number}: broken link {target}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    issues = find_broken(args.root.resolve())
    for issue in issues:
        print(issue)
    print(f"broken_links={len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
