"""BO-05 / KI-167: opt-in redaction for local report tools.

Each report tool exposes `--redact`. Without it, output is byte-for-byte what the tool printed before. With it:
- `display_path` prints a repo-relative POSIX path when the file is inside the project, otherwise `<external>/<file name>`,
  so no absolute machine path (user name, drive layout) appears;
- `display_row` replaces an echoed raw source or log line with `<row redacted>`. The line number and the structured
  fields the tool derives itself are still printed;
- `install_stream_redaction()` (BO-01..05 hotfix + BO-06..09) wraps stdout/stderr so that every line a tool prints has
  absolute machine paths rewritten by `redact_text`, including diagnostics, values echoed from scripts, and JSON-escaped
  paths. Only absolute machine paths change; Unreal object paths such as `/Game/...` and parsed telemetry are kept.

Redaction is a sharing aid, not a security boundary: tokens and identifiers that a tool parses out of a log are still
printed, and an absolute path containing a space outside the project, temp and home roots is only masked up to that
space. Review the output before sharing it outside the machine.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REDACTED_ROW = "<row redacted>"


def add_redact_argument(parser, argv=None) -> None:
    """Add --redact. Call it AFTER every other option is added (the tools call it right before parse_args), because the
    early pre-scan below compares against the parser's complete option table."""
    redact_action = parser.add_argument(
        "--redact", action="store_true",
        help="print repo-relative paths (or <external>/name) and omit raw source/log rows; default output is unchanged")
    # BO-26 (+ X-2250 hotfix): argparse prints usage errors (for example "unrecognized arguments: C:\...") while parsing,
    # before the tool can call install_stream_redaction. If a token argparse will resolve to --redact is on the command
    # line, enable redaction now so those messages are masked too; the tool's redaction_scope removes it again.
    # Without the flag nothing changes. Tokens after a bare `--` are positional values and are ignored.
    tokens = list(sys.argv[1:] if argv is None else argv)
    if "--" in tokens:
        tokens = tokens[:tokens.index("--")]
    if any(_resolves_to(parser, token, redact_action) for token in tokens):
        install_stream_redaction(True)


def _resolves_to(parser, token: str, action) -> bool:
    """Mirror argparse's own long-option resolution: an exact option string, or (when allow_abbrev is on) a prefix that
    matches exactly one action. An ambiguous prefix (for example `--re` where `--require-complete-run` also exists) or a
    prefix of another option does not count."""
    if not token.startswith("--") or token == "--":
        return False
    option = token.split("=", 1)[0]
    table = parser._option_string_actions  # argparse's own option table (stable private API since Python 3.2)
    if option in table:
        return table[option] is action
    if not getattr(parser, "allow_abbrev", True):
        return False
    candidates = {id(a): a for text, a in table.items() if text.startswith("--") and text.startswith(option)}
    return len(candidates) == 1 and next(iter(candidates.values())) is action


def display_path(path, redact: bool, root: Path | None = None) -> str:
    """Return `str(path)` unchanged when not redacting; otherwise a path that carries no absolute machine location."""
    path = Path(path)
    if not redact:
        return str(path)
    resolved = path.resolve()
    for base in ([Path(root).resolve()] if root is not None else []) + [PROJECT_ROOT]:
        try:
            return resolved.relative_to(base).as_posix()
        except ValueError:
            continue
    return f"<external>/{path.name}"


def display_row(text: str, redact: bool) -> str:
    return REDACTED_ROW if redact else text


BACKSLASH = "\\"
# A path separator: a JSON-escaped backslash pair, one backslash, or a forward slash.
SEP = r"(?:\\\\|[\\/])"
# Characters that end a path token in free text.
STOP = r"""[^\s"'<>|*?,;()\[\]{}]"""


def _root_rules():
    """Project, temp and home roots, longest first; each matched raw, with forward slashes, and JSON-escaped, ignoring case."""
    rules = []
    for base, label in ((PROJECT_ROOT, ""), (Path(tempfile.gettempdir()), "<tmp>"), (Path.home(), "<home>")):
        for candidate in {str(base), str(base.resolve())}:
            for variant in {candidate, candidate.replace(BACKSLASH, "/"), candidate.replace(BACKSLASH, BACKSLASH * 2)}:
                rules.append((variant.rstrip(BACKSLASH + "/"), label))
    rules.sort(key=lambda item: len(item[0]), reverse=True)
    return [(re.compile(re.escape(text) + SEP + "?", re.IGNORECASE), label) for text, label in rules]


_ROOT_RULES = None
# BO-13: first segments that mark a POSIX *machine* path (Linux FHS, WSL/containers, macOS). Case-sensitive on purpose:
# Unreal mounts are /Game, /Engine, /Script, /Temp, /Memory, /Config and CamelCase plugin mounts, none of which is listed.
# Anything outside this list (for example /data2/...) is NOT masked; see the limits in the BO-11..15 report.
POSIX_MACHINE_ROOTS = ("home", "tmp", "var", "mnt", "opt", "root", "private", "media", "srv", "etc", "usr", "run",
                       "data", "workspace", "workspaces", "proc", "dev", "Users", "Volumes", "Applications", "Library")
# Fallback for any other absolute path: a drive path, a UNC path, or a POSIX path under a machine root.
# Unreal object paths (/Game, /Script, /Engine, plugin mounts) are deliberately NOT matched.
_ABS = re.compile(r"(?<![\w])(?:[A-Za-z]:" + SEP + STOP + "*"
                  + r"|\\\\" + STOP + "+"
                  + r"|/" + "(?:" + "|".join(POSIX_MACHINE_ROOTS) + ")/" + STOP + "*)")


def redact_text(text: str) -> str:
    """Rewrite absolute machine paths in free text. Project paths become repo-relative; temp/home roots become <tmp>/ and <home>/."""
    global _ROOT_RULES
    if _ROOT_RULES is None:
        _ROOT_RULES = _root_rules()
    for pattern, label in _ROOT_RULES:
        text = pattern.sub(lambda match, label=label: f"{label}/" if label else "", text)

    def external(match):
        token = match.group(0)
        # BO-15: a path cut at a space (for example a parsed `profile=C:\Users\First` from `C:\Users\First Last\...`)
        # is a prefix of a known root; label it as that root instead of echoing its last component (a user-name fragment).
        normalized = re.sub(r"[\\/]+", "/", token).rstrip("/").lower()
        for root_text, label in _root_prefixes():
            if root_text.startswith(normalized) and len(normalized) > 3:
                return f"{label}/" if label else "<project>/"
        parts = [part for part in re.split(r"[\\/]+", token) if part]
        return f"<external>/{parts[-1]}" if parts else "<external>"
    return _ABS.sub(external, text)


_PREFIXES = None


def _root_prefixes():
    """Normalized (forward-slash, lower-case) project/temp/home roots for the space-cut prefix check."""
    global _PREFIXES
    if _PREFIXES is None:
        out = []
        for base, label in ((PROJECT_ROOT, ""), (Path(tempfile.gettempdir()), "<tmp>"), (Path.home(), "<home>")):
            for candidate in {str(base), str(base.resolve())}:
                out.append((re.sub(r"[\\/]+", "/", candidate).rstrip("/").lower(), label))
        _PREFIXES = out
    return _PREFIXES


class _RedactingStream:
    """Line-buffered redacting wrapper (BO-12). A path split across several write() calls is redacted as a whole:
    text is held until a newline, and the held tail is redacted and written on flush() or close."""

    def __init__(self, inner):
        self._inner = inner
        self._pending = ""

    def write(self, text):
        self._pending += text
        if "\n" in self._pending:
            complete, self._pending = self._pending.rsplit("\n", 1)
            self._inner.write(redact_text(complete + "\n"))
        return len(text)

    def flush(self):
        if self._pending:
            self._inner.write(redact_text(self._pending))
            self._pending = ""
        return self._inner.flush()

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _unwrap(stream):
    if isinstance(stream, _RedactingStream):
        stream.flush()
        return stream._inner
    return stream


def install_stream_redaction(redact: bool) -> None:
    """Wrap sys.stdout and sys.stderr when --redact is set (once; repeated calls do not double-wrap).

    BO-11: `install_stream_redaction(False)` after an earlier `True` flushes and restores the original streams, so
    redaction can be toggled within one process. A call with False when nothing is wrapped is a no-op, so default
    output is unchanged. The interpreter flushes sys.stdout/sys.stderr at exit, which writes any held tail; an atexit
    hook does the same as a backstop.
    """
    if redact:
        if not isinstance(sys.stdout, _RedactingStream):
            sys.stdout = _RedactingStream(sys.stdout)
        if not isinstance(sys.stderr, _RedactingStream):
            sys.stderr = _RedactingStream(sys.stderr)
        _register_exit_flush()
    else:
        sys.stdout = _unwrap(sys.stdout)
        sys.stderr = _unwrap(sys.stderr)


def redaction_scope(main):
    """BO-18: decorator for a tool's `main`. Whatever `main` does with `install_stream_redaction`, the streams it was
    called with are restored when it returns, raises, or exits (SystemExit), so several tool mains can run in one process
    across redact on/off transitions without a stale wrapper. A wrapper installed by the caller beforehand is left alone."""
    import functools

    @functools.wraps(main)
    def scoped(*args, **kwargs):
        saved = (sys.stdout, sys.stderr)
        try:
            return main(*args, **kwargs)
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException:
            # BO-19: the default excepthook would print the traceback only AFTER the streams are restored below, unredacted.
            # While main's own redacting wrapper is active, print the traceback through it and exit with code 1, the same
            # code an uncaught exception gives. Without --redact the exception propagates unchanged.
            if isinstance(sys.stderr, _RedactingStream) and sys.stderr not in saved:
                import traceback
                traceback.print_exc(file=sys.stderr)
                raise SystemExit(1) from None
            raise
        finally:
            for stream in (sys.stdout, sys.stderr):
                if isinstance(stream, _RedactingStream) and stream not in saved:
                    stream.flush()
            sys.stdout, sys.stderr = saved
    return scoped


_EXIT_HOOK = False


def _register_exit_flush():
    global _EXIT_HOOK
    if not _EXIT_HOOK:
        import atexit

        def _flush_wrapped():
            for stream in (sys.stdout, sys.stderr):
                if isinstance(stream, _RedactingStream):
                    try:
                        stream.flush()
                    except (OSError, ValueError):
                        pass
        atexit.register(_flush_wrapped)
        _EXIT_HOOK = True
