"""Read-only evidence verifier. Hashes/log summaries are not package acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re


class EvidenceError(ValueError):
    pass


def inside(path: Path, root: Path) -> Path:
    path, root = path.resolve(), root.resolve()
    if not path.is_relative_to(root):
        raise EvidenceError("Evidence path escapes the explicitly allowed root")
    return path


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def parse_receipt(text: str) -> list[dict]:
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # Both observed formats: SHA *path and SHA size path.
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+(?:\*(.+)|(\d+)\s+(.+))", line)
        if not match:
            raise EvidenceError(f"Unsupported receipt line {number}")
        result.append({"expected_sha256": match[1].lower(),
                       "relative_path": match[2] if match[2] is not None else match[4],
                       "expected_size": int(match[3]) if match[3] else None})
    if not result:
        raise EvidenceError("Receipt has no entries")
    return result


def verify_receipt(receipt: Path, base: Path, root: Path) -> dict:
    root = root.resolve()
    receipt, base = inside(receipt, root), inside(base, root)
    rows = parse_receipt(receipt.read_text(encoding="utf-8-sig"))
    seen, checks = set(), []
    for row in rows:
        name = row["relative_path"]
        # Receipts are relative. Refuse absolute/drive paths even inside root.
        if Path(name).is_absolute() or re.match(r"^[A-Za-z]:", name) or name.startswith(("\\", "/")):
            raise EvidenceError("Receipt entry must be relative")
        target = inside(base / name, root)
        key = str(target).casefold()
        if key in seen:
            raise EvidenceError("Duplicate canonical receipt target")
        seen.add(key)
        check = {**row, "path": str(target.relative_to(root))}
        if not target.is_file():
            check["status"] = "missing"
        else:
            check["actual_sha256"] = digest(target)
            check["actual_size"] = target.stat().st_size
            check["status"] = "verified" if (
                check["actual_sha256"] == row["expected_sha256"]
                and (row["expected_size"] is None or row["expected_size"] == check["actual_size"])
            ) else "mismatch"
        checks.append(check)
    return {"scope": "File integrity only, not source semantics/runtime acceptance",
            "receipt_sha256": digest(receipt), "entries": len(checks),
            "all_verified": all(c["status"] == "verified" for c in checks), "checks": checks}


def summarize_automation(path: Path, root: Path) -> dict:
    path = inside(path, root)
    text = path.read_text(encoding="utf-8", errors="strict")
    pairs = re.findall(r"Test Completed\. Result=\{([^}]+)\} Name=\{[^}]+\} Path=\{([^}]+)\}", text)
    counts = {}
    for state, name in pairs:
        counts[name] = counts.get(name, 0) + 1
    severities = re.findall(r"(?m)^(?:\[[^\r\n]*?\]\[\s*\d+\])?[^:\r\n]+:\s*(Warning|Error):", text)
    return {"scope": "Raw log summary; requires separate job exit/source/binary review",
            "sha256": digest(path), "completed": len(pairs), "unique": len(counts),
            "failures": [name for state, name in pairs if state != "Success"],
            "duplicate_completions": [name for name, count in counts.items() if count != 1],
            "warning_severity_lines": severities.count("Warning"),
            "error_severity_lines": severities.count("Error"),
            "paths": sorted(counts)}


def parse_job_record(path: Path, root: Path) -> dict:
    path = inside(path, root)
    text = path.read_text(encoding="utf-8-sig")
    ends = re.findall(r"(?m)^end[^\r\n]*\bexit\s+(-?\d+)\s+seconds\s+(\d+)\s*$", text)
    if len(ends) != 1:
        raise EvidenceError("Need exactly one explicit end/exit/seconds record")
    return {"scope": "Recorded exit only, not live liveness", "sha256": digest(path),
            "exit_code": int(ends[0][0]), "seconds": int(ends[0][1])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--automation-log", type=Path)
    parser.add_argument("--job-record", type=Path)
    args = parser.parse_args()
    result = verify_receipt(args.receipt, args.base, args.root)
    if args.automation_log:
        result["automation"] = summarize_automation(args.automation_log, args.root)
    if args.job_record:
        result["job"] = parse_job_record(args.job_record, args.root)
    print(json.dumps(result, indent=2))
    return 0 if result["all_verified"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EvidenceError, OSError, UnicodeError) as error:
        print(json.dumps({"status": "invalid_evidence", "error": str(error)}))
        raise SystemExit(2)
