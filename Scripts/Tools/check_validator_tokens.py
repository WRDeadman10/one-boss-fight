"""Check FrameworkProof UE_LOG tokens against validator and documentation indexes."""
import argparse
import re
import sys
from pathlib import Path


FRAMEWORK_LOG = re.compile(
    r'UE_LOG\s*\([^;]*?TEXT\s*\(\s*"[^"\n]*?'
    r'\[FrameworkProof\]\s*([A-Za-z_][A-Za-z0-9_]*)',
    re.DOTALL,
)
TOKEN_CELL = re.compile(r'`([A-Za-z_][A-Za-z0-9_]*)`')


def strip_cpp_comments(source):
    """Blank C++ comments while preserving strings and newlines for the token scan."""
    out = []
    i = 0
    state = "code"
    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if state == "code":
            if ch == '"':
                state = "string"
                out.append(ch)
            elif ch == "'":
                state = "char"
                out.append(ch)
            elif ch == "/" and nxt == "/":
                state = "line"
                out.extend((" ", " "))
                i += 1
            elif ch == "/" and nxt == "*":
                state = "block"
                out.extend((" ", " "))
                i += 1
            else:
                out.append(ch)
        elif state in ("string", "char"):
            out.append(ch)
            if ch == "\\" and i + 1 < len(source):
                i += 1
                out.append(source[i])
            elif (state == "string" and ch == '"') or (state == "char" and ch == "'"):
                state = "code"
        elif state == "line":
            if ch == "\n":
                out.append(ch)
                state = "code"
            else:
                out.append(" ")
        else:  # block comment
            if ch == "*" and nxt == "/":
                out.extend((" ", " "))
                i += 1
                state = "code"
            else:
                out.append("\n" if ch == "\n" else " ")
        i += 1
    return "".join(out)


def read_validator(root):
    reviews = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
    sys.path.insert(0, str(reviews))
    try:
        import validate_framework_proof_logs
    except ImportError as exc:
        raise RuntimeError("cannot import validator schemas: " + str(exc)) from exc
    return validate_framework_proof_logs.SCHEMAS


def emitted_tokens(source_dir):
    found = set()
    for path in sorted((*source_dir.rglob("*.cpp"), *source_dir.rglob("*.h"))):
        text = strip_cpp_comments(path.read_text(encoding="utf-8", errors="replace"))
        found.update(FRAMEWORK_LOG.findall(text))
    return found


def table_tokens(markdown, title=None):
    text = markdown
    if title:
        try:
            text = text.split(title, 1)[1]
        except IndexError:
            return set()
    return {
        token
        for line in text.splitlines()
        if line.startswith("|")
        for token in TOKEN_CELL.findall(line)
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[2],
                        help="project root (defaults to this script's checkout)")
    args = parser.parse_args()
    root = args.root.resolve()
    source_dir = root / "Source"
    log_tokens_path = root / "Documentation/Boss/LOG_TOKENS.md"
    if not source_dir.is_dir() or not log_tokens_path.is_file():
        parser.error("root must contain Source/ and Documentation/Boss/LOG_TOKENS.md")

    schemas = read_validator(root)
    emitted = emitted_tokens(source_dir)
    docs = log_tokens_path.read_text(encoding="utf-8")
    semantic = table_tokens(docs.split("## Emission source locations", 1)[0])
    emission = table_tokens(docs, "## Emission source locations")

    problems = []
    for label, missing in (
        ("validator schema", emitted - set(schemas)),
        ("semantic LOG_TOKENS row", emitted - semantic),
        ("emission-source LOG_TOKENS row", emitted - emission),
    ):
        if missing:
            problems.append("missing %s: %s" % (label, ", ".join(sorted(missing))))
    if problems:
        print("FrameworkProof token audit FAILED")
        for problem in problems:
            print("- " + problem)
        return 1

    schema_only = set(schemas) - emitted
    print("FrameworkProof token audit PASS: %d emitted tokens, %d schemas, semantic and source indexes complete"
          % (len(emitted), len(schemas)))
    if schema_only:
        print("Schemas without a literal source emission: " + ", ".join(sorted(schema_only)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
