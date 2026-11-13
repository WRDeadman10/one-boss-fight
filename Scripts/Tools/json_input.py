"""BO-04 / KI-166: fail-closed JSON input loading for the small report tools.

`load_json(path, expect)` returns the parsed value, or raises `JsonInputError` with a message that names the input file.
Each tool's `main` catches it and calls `fail(error)`. That prints `ERROR <path>: <reason>` to stderr and returns exit code 2
(1 stays reserved for each tool's own "issues found" result), and nothing is printed to stdout first.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXIT_BAD_INPUT = 2


class JsonInputError(ValueError):
    """Raised for an unreadable, malformed or wrongly shaped JSON input; the message names the file."""


def load_json(path: Path, expect: type | tuple[type, ...] | None = None):
    path = Path(path)
    try:
        # BO-36: utf-8-sig accepts an optional UTF-8 BOM (Windows PowerShell's default for Out-File/Set-Content -Encoding
        # utf8). A BOM is never valid JSON content, so accepting it cannot change the meaning of a valid file.
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise JsonInputError(f"{path}: cannot read input ({error.__class__.__name__}: {error})") from error
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonInputError(f"{path}: malformed JSON at line {error.lineno} column {error.colno}: {error.msg}") from error
    except RecursionError as error:  # BO-37: pathologically deep nesting fails closed instead of tracing back
        raise JsonInputError(f"{path}: JSON nesting is too deep to parse") from error
    if expect is not None and not isinstance(value, expect):
        names = "/".join(t.__name__ for t in (expect if isinstance(expect, tuple) else (expect,)))
        raise JsonInputError(f"{path}: expected top-level {names}, found {type(value).__name__}")
    return value


def require_objects(path: Path, items, what: str) -> list:
    """Every element of `items` must be a JSON object; otherwise raise JsonInputError naming the file and index."""
    if not isinstance(items, list):
        raise JsonInputError(f"{path}: expected {what} to be a list, found {type(items).__name__}")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise JsonInputError(f"{path}: {what}[{index}] must be an object, found {type(item).__name__}")
    return items


def fail(error: JsonInputError) -> int:
    print(f"ERROR {error}", file=sys.stderr)
    return EXIT_BAD_INPUT
