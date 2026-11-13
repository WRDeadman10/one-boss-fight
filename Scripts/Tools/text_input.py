"""BP-26..30 (X-2305): text-input decoding for line-oriented readers (logs, Markdown), with an explicit policy.

`read_text_input(path, errors="strict")` returns the decoded text with universal newlines, exactly like
`Path.read_text(encoding="utf-8")`, except that:
  * a leading UTF-8 BOM is stripped (never meaningful content, and it breaks first-line `^###` style matches);
  * UTF-16 input (an FF FE / FE FF byte-order mark, or NUL bytes within the first 4 KiB) always fails closed with a named
    TextInputError: decoding it as UTF-8 would silently produce garbage under errors="replace";
  * errors="strict" (the default) turns invalid UTF-8 into a named TextInputError giving the byte offset;
  * errors="replace" keeps the former lenient behaviour for invalid bytes and is only for readers whose inputs are
    third-party logs (documented per call site in BP_26_30_BOM_JSON_READS.md).
Unreadable files raise TextInputError naming the path. TextInputError subclasses ValueError.
"""
from __future__ import annotations

from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"
UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")


class TextInputError(ValueError):
    """Unreadable, UTF-16, or (strict mode) invalid UTF-8 text input; the message names the file."""


def read_text_input(path: Path, errors: str = "strict") -> str:
    if errors not in ("strict", "replace"):
        raise ValueError(f"unsupported errors policy: {errors!r}")
    path = Path(path)
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise TextInputError(f"{path}: cannot read input ({error.__class__.__name__}: {error})") from error
    if raw.startswith(UTF16_BOMS) or b"\x00" in raw[:4096]:
        raise TextInputError(f"{path}: UTF-16 or binary input is not supported; re-save it as UTF-8")
    if raw.startswith(UTF8_BOM):
        raw = raw[len(UTF8_BOM):]
    try:
        text = raw.decode("utf-8", errors=errors)
    except UnicodeDecodeError as error:
        raise TextInputError(f"{path}: invalid UTF-8 at byte {error.start}") from error
    return text.replace("\r\n", "\n").replace("\r", "\n")  # universal newlines, as Path.read_text does
