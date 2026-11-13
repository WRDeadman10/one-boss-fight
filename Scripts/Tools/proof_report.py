"""Report expected-sheet telemetry presence against one validated PIE log."""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BO: helper import works as a script or as Scripts.Tools.*
from redaction import add_redact_argument, display_path, display_row, install_stream_redaction, redaction_scope


INLINE = re.compile(r"`([^`]+)`")
PASS_HEADING = re.compile(r"^##\s+PASS\s*$", re.IGNORECASE)
NEXT_HEADING = re.compile(r"^##\s+\S")
IDENTITY = re.compile(r"\b(map|profile|run_id|runId|source|source_hash|source_id)=([^\s]+)")


def load_validator(root):
    reviews = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
    sys.path.insert(0, str(reviews))
    import validate_framework_proof_logs
    return validate_framework_proof_logs


def expected_checks(path, schema_tokens):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_pass = False
    found_heading = False
    checks = []
    for number, line in enumerate(lines, 1):
        if PASS_HEADING.match(line.strip()):
            in_pass = True
            found_heading = True
            continue
        if in_pass and NEXT_HEADING.match(line.strip()):
            break
        if in_pass and line.startswith("- "):
            token_spans = []
            for match in INLINE.finditer(line):
                chunk = match.group(1)
                names = {chunk} if chunk in schema_tokens else set()
                names.update(re.findall(r"\[FrameworkProof\]\s*([A-Za-z_][A-Za-z0-9_]*)", chunk))
                token_spans.extend((name, match.start()) for name in names if name in schema_tokens)
            referenced = {name for name, _ in token_spans}
            negative = set()
            for token, position in token_spans:
                before = line[max(0, position - 45):position]
                if re.search(r"\bno\b(?:\s+\w+){0,2}\s*$", before, re.IGNORECASE):
                    negative.add(token)
            checks.append((number, line[2:].strip(), referenced, negative))
    if not found_heading:
        raise ValueError("expected sheet has no '## PASS' section")
    if not checks:
        raise ValueError("PASS section has no '- ' checklist lines")
    return checks


def evidence_stale_reasons(log, manifest):
    from verify_evidence_manifest import verify
    reasons = verify(manifest)
    try:
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        entry = next((item for item in data.get("files", [])
                      if isinstance(item, dict) and item.get("file") == log.name), None)
        if entry is None:
            reasons.append(f"manifest has no hash entry for {log.name!r}")
        elif log.stat().st_mtime > manifest.stat().st_mtime + 1.0:
            reasons.append(f"log mtime is newer than evidence manifest: {log}")
    except (OSError, ValueError) as exc:
        reasons.append(f"cannot verify evidence freshness: {exc}")
    return reasons


def read_identity(log):
    observed = {key: set() for key in ("map", "profile", "run_id", "source")}
    aliases = {"runId": "run_id", "source_hash": "source", "source_id": "source"}
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        for match in IDENTITY.finditer(line):
            key = aliases.get(match.group(1), match.group(1))
            observed[key].add(match.group(2))
    return observed


def check_identity(log, expected, label="input"):
    observed = read_identity(log)
    failures = []
    for key, want in expected.items():
        values = observed.get(key, set())
        if not values:
            failure = f"{label} missing required {key} identity (expected {want!r})"
            failures.append(failure)
            print("IDENTITY MISSING " + failure)
        elif values != {want}:
            failures.append(f"{key}: expected {want!r}, observed {sorted(values)!r}")
            print(f"IDENTITY MISMATCH {failures[-1]}")
        else:
            print(f"IDENTITY MATCH {key}={want}")
    return failures


def run_completeness_issues(log):
    lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
    result_lines = [index for index, line in enumerate(lines) if re.search(r"\[FrameworkProof\]\s+RESULT(?:\s|$)", line)]
    exit_lines = [index for index, line in enumerate(lines) if "LogExit: Exiting." in line]
    issues = []
    if not result_lines:
        issues.append("missing terminal [FrameworkProof] RESULT")
    if not exit_lines:
        issues.append("missing orderly LogExit: Exiting. marker (log may be truncated)")
    elif result_lines and result_lines[-1] > exit_lines[-1]:
        issues.append("terminal RESULT appears after orderly exit marker")
    return issues


@redaction_scope  # BO-18: restore the caller's streams when main ends
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="PIE editor_raw.log")
    parser.add_argument("expected", type=Path, help="feature *_EXPECTED.md")
    parser.add_argument("--control-log", type=Path, help="paired negative-control PIE log; `no TOKEN` checks apply to this log")
    parser.add_argument("--manifest", type=Path, help="evidence_pack JSON manifest for freshness/hash checks")
    parser.add_argument("--expect-map")
    parser.add_argument("--expect-profile")
    parser.add_argument("--expect-run-id")
    parser.add_argument("--expect-source", help="expected source hash/identity recorded in the enabled log")
    parser.add_argument("--control-expect-map", help="required map identity for the paired control log")
    parser.add_argument("--control-expect-profile", help="required profile identity for the paired control log")
    parser.add_argument("--control-expect-source", help="expected source hash/identity recorded in the control log")
    parser.add_argument("--require-complete-run", action="store_true", help="require a FrameworkProof RESULT and orderly editor shutdown marker")
    add_redact_argument(parser)  # BO-05 / KI-167
    args = parser.parse_args()
    if args.redact:  # BO-23: only ever enable here; never unwrap a caller-owned wrapper when the flag is absent
        install_stream_redaction(True)  # BO-06..09: mask absolute machine paths in every printed line
    root = Path(__file__).resolve().parents[2]
    if not args.log.is_file() or not args.expected.is_file() or (args.control_log and not args.control_log.is_file()):
        parser.error("log, expected sheet, and any supplied control log must exist")

    digest = hashlib.sha256()
    with args.log.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    mtime = datetime.fromtimestamp(args.log.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
    print("Input log: %s | mtime_utc=%s | sha256=%s" % (display_path(args.log.resolve(), args.redact), mtime, digest.hexdigest()))
    expected_identity = {key: value for key, value in (("map", args.expect_map), ("profile", args.expect_profile), ("run_id", args.expect_run_id), ("source", args.expect_source)) if value is not None}
    identity_failures = check_identity(args.log, expected_identity)
    control_expected_identity = {key: value for key, value in (("map", args.control_expect_map), ("profile", args.control_expect_profile), ("source", args.control_expect_source)) if value is not None}
    if control_expected_identity and not args.control_log:
        parser.error("--control-expect-* requires --control-log")
    if args.control_log and control_expected_identity:
        control_identity_failures = check_identity(args.control_log, control_expected_identity, "control")
        identity_failures.extend(control_identity_failures)
        positive_identity = read_identity(args.log)
        for key, control_want in control_expected_identity.items():
            positive_values = positive_identity[key]
            if not positive_values:
                issue = f"enabled log missing {key} identity required to compare paired control"
                identity_failures.append(issue)
                print("IDENTITY MISSING " + issue)
            elif positive_values != {control_want}:
                issue = f"paired {key} differs: enabled={sorted(positive_values)!r}, control={control_want!r}"
                identity_failures.append(issue)
                print("IDENTITY MISMATCH " + issue)
    completeness_issues = run_completeness_issues(args.log) if args.require_complete_run else []
    for issue in completeness_issues:
        print("RUN INCOMPLETE " + issue)

    try:
        validator = load_validator(root)
        checks = expected_checks(args.expected, set(validator.SCHEMAS))
        validation = validator.validate_log_file(args.log)
        control_validation = validator.validate_log_file(args.control_log) if args.control_log else None
    except (ImportError, OSError, ValueError) as exc:
        print("proof report error: " + str(exc), file=sys.stderr)
        return 2

    counts = validation["token_counts"]
    control_counts = control_validation["token_counts"] if control_validation else counts
    stale_reasons = []
    if args.manifest:
        try:
            stale_reasons.extend(evidence_stale_reasons(args.log, args.manifest))
        except (ImportError, OSError, ValueError) as exc:
            stale_reasons.append(f"cannot verify evidence freshness: {exc}")
        if stale_reasons:
            print("EVIDENCE STALE/INVALID (separate from gameplay checks):")
            for reason in stale_reasons:
                print("STALE " + reason)
        else:
            print("EVIDENCE FRESH: manifest hashes and timestamp ordering pass")
    failures = 0
    manual = 0
    print("Evidence presence report (numeric/gameplay relationships need manual review)")
    for line_number, text, tokens, negative in checks:
        if not tokens:
            manual += 1
            print("MANUAL %s:%d | no registered telemetry token to check | %s" %
                  (args.expected, line_number, text))
            continue
        missing = sorted(token for token in tokens - negative if counts[token] == 0)
        negative_counts = control_counts if args.control_log else counts
        unexpected = sorted(token for token in negative if negative_counts[token] > 0)
        if missing or unexpected:
            failures += 1
            details = []
            if missing:
                details.append("missing " + ", ".join(missing))
            if unexpected:
                details.append("expected absent " + ", ".join(unexpected))
            print("FAIL %s:%d | %s | %s" % (args.expected, line_number, "; ".join(details), text))
        else:
            present = sorted(tokens - negative)
            absent = sorted(negative)
            detail = "present " + ", ".join(present) if present else "absence confirmed"
            if absent:
                detail += "; absent " + ", ".join(absent)
            print("PASS %s:%d | %s | %s" % (args.expected, line_number, detail, text))

    syntax_count = len(validation["syntax_failures"])
    semantic_count = len(validation["semantic_violations"])
    if control_validation:
        syntax_count += len(control_validation["syntax_failures"])
        semantic_count += len(control_validation["semantic_violations"])
        print("Control log: %d FrameworkProof lines, %d schema failures, %d semantic warnings" %
              (control_validation["framework_proof_lines"], len(control_validation["syntax_failures"]), len(control_validation["semantic_violations"])))
    print("Log: %d FrameworkProof lines, %d schema failures, %d semantic warnings" %
          (validation["framework_proof_lines"], syntax_count, semantic_count))
    if syntax_count:
        print("WARNING: validator rejected %d FrameworkProof line(s); inspect with validate_framework_proof_logs.py" % syntax_count)
    if completeness_issues:
        print("RESULT: INCOMPLETE RUN (%d missing terminal/process marker(s); distinct from gameplay FAIL)" % len(completeness_issues))
        return 2
    if failures:
        print("RESULT: FAIL (%d expected checklist line(s) lacked required telemetry)" % failures)
        return 1
    if identity_failures:
        print("RESULT: FAIL (input run identity mismatch)")
        return 1
    if stale_reasons:
        print("RESULT: STALE EVIDENCE (gameplay checklist was evaluated but is not accepted as current evidence)")
        return 3
    if manual or syntax_count or semantic_count:
        print("RESULT: INCOMPLETE (%d manual line(s); telemetry presence does not prove numeric/gameplay criteria)" % manual)
        return 2
    print("RESULT: PASS (all telemetry-presence checks; numeric/gameplay criteria still require review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
