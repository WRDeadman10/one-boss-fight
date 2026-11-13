"""BK-78 (C, implementer; X-1996): read-only validator for a PENDING definition-input provenance manifest.

The manifest records, per definition field, either a sourced value or an explicit OWNER_DECISION_REQUIRED row. It is
not authoring evidence and not asset data: the validator refuses any manifest that claims to be either, and refuses
any attempt to promote an unresolved row (an APPROVED-style status, or a value on an OWNER_DECISION_REQUIRED row).

Checks (always): schema and flags, required field coverage, unique fields, row status/value/type rules, citation
shape (relative path, 64-hex SHA-256), and that every excerpt citation's SHA-256 equals the hash of its excerpt text.
With --verify-sources (still read-only): each cited file exists under the repo, an excerpt citation's text occurs in
the file, and a file citation's SHA-256 equals the file's current hash.

Exit 0 = valid PENDING manifest, 1 = invalid. Never writes, never loads assets, never launches Unreal.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

SCHEMA = "onebossfight.pending-definition-inputs/v1"
STATUSES = {"SOURCE_BACKED", "SOURCE_BACKED_AWAITING_OWNER", "OWNER_DECISION_REQUIRED"}
VALUED = {"SOURCE_BACKED", "SOURCE_BACKED_AWAITING_OWNER"}
REQUIRED_FIELDS = {
    "Stats.MaxHealth", "Stats.MaxPosture", "Stats.PostureRegenDelay", "Stats.PostureRegenRate",
    "Phases[Phase_1].PhaseId", "Phases[Phase_1].EntryHealthFraction", "Phases[Phase_1].SpeedMultiplier",
    "Phases[Phase_1].RateMultiplier", "Phases[Phase_1].AttackMultiplier",
}
REQUIRED_TOP_LEVEL_KEYS = {"schema", "manifest_state", "authoring_evidence", "executable", "rows"}
OPTIONAL_TOP_LEVEL_KEYS = {"definition_target", "decision_request", "prepared_by", "warning"}
TOP_LEVEL_KEYS = REQUIRED_TOP_LEVEL_KEYS | OPTIONAL_TOP_LEVEL_KEYS
ROW_KEYS = {"field_path", "type", "units", "status", "value", "citations", "note"}
OPTIONAL_ROW_KEYS = {"candidate", "candidate_note"}
HEX64 = re.compile(r"[0-9a-f]{64}")
DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


# X-2058 / A-854 BUG-2: SOURCE_BACKED means "sourced", not "any number". Valued rows and candidates must satisfy the
# same native C++ ranges the owner-approval envelope enforces (validate_owner_approval_envelope.FIELDS; parity is
# test-pinned): RPGBossStatsAdapters.h:38 / .cpp:74,79,84,89 and RPGBossPhaseAdapters.cpp:122,131.
# field -> (low, low_inclusive, high); high None = unbounded. PhaseId must be exactly Phase_1.
NATIVE_RANGES = {
    "Stats.MaxHealth": (1.0, False, None),
    "Stats.MaxPosture": (0.0, False, None),
    "Stats.PostureRegenDelay": (0.0, True, None),
    "Stats.PostureRegenRate": (0.0, True, None),
    "Phases[Phase_1].EntryHealthFraction": (0.0, False, 1.0),
    "Phases[Phase_1].SpeedMultiplier": (0.0, False, None),
    "Phases[Phase_1].RateMultiplier": (0.0, False, None),
    "Phases[Phase_1].AttackMultiplier": (0.0, False, None),
}
PHASE_ID_FIELD, PHASE_ID = "Phases[Phase_1].PhaseId", "Phase_1"


def in_native_range(field, value):
    low, low_inclusive, high = NATIVE_RANGES[field]
    if value < low or (value == low and not low_inclusive):
        return False
    return high is None or value <= high


def loads_strict(text):
    """X-2058 / A-854 BUG-1: duplicate keys AND NaN/Infinity anywhere in the manifest are refused."""
    def bad_constant(name):
        raise ValueError("non-finite JSON constant refused: %s" % name)
    return json.loads(text, object_pairs_hook=reject_duplicate_json_keys, parse_constant=bad_constant)


def reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: %s" % key)
        result[key] = value
    return result


def check_citation(cite, where, errors, root, verify_sources):
    if not isinstance(cite, dict):
        errors.append("%s: citation must be an object" % where)
        return
    path, scope, digest = cite.get("path"), cite.get("scope"), cite.get("sha256")
    if not isinstance(path, str) or not path or path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", path) or ".." in Path(path).parts:
        errors.append("%s: citation path must be a repo-relative path, got %r" % (where, path))
        return
    if scope not in ("file", "excerpt"):
        errors.append("%s: citation scope must be 'file' or 'excerpt', got %r" % (where, scope))
        return
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        errors.append("%s: citation sha256 must be 64 lowercase hex, got %r" % (where, digest))
        return
    if scope == "excerpt":
        excerpt = cite.get("excerpt")
        if not isinstance(excerpt, str) or not excerpt.strip():
            errors.append("%s: excerpt citation needs non-empty excerpt text" % where)
            return
        line_no = cite.get("line")
        if isinstance(line_no, bool) or not isinstance(line_no, int) or line_no <= 0:
            errors.append("%s: excerpt citation needs a positive one-based line number" % where)
            return
        if sha256_text(excerpt) != digest:
            errors.append("%s: excerpt sha256 does not match its excerpt text (tampered or stale)" % where)
    if verify_sources:
        root = root.resolve()
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            errors.append("%s: cited path resolves outside the repository root: %s" % (where, path))
            return
        if not target.is_file():
            errors.append("%s: cited file does not exist: %s" % (where, path))
            return
        if scope == "file":
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                errors.append("%s: file sha256 differs from the current file: %s" % (where, path))
        else:
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            line_no = cite.get("line")
            if isinstance(line_no, bool) or not isinstance(line_no, int) or line_no <= 0 or line_no > len(lines):
                errors.append("%s: excerpt line number is outside %s" % (where, path))
            elif cite.get("excerpt", "").strip() != lines[line_no - 1].strip():
                errors.append("%s: excerpt no longer matches cited line %d of %s exactly" % (where, line_no, path))


def validate(manifest, root=DEFAULT_ROOT, verify_sources=False):
    errors = []
    if not isinstance(manifest, dict):
        return {"valid": False, "errors": ["manifest must be a JSON object"]}
    if manifest.get("schema") != SCHEMA:
        errors.append("schema must be %s" % SCHEMA)
    if manifest.get("manifest_state") != "PENDING":
        errors.append("manifest_state must be PENDING (promotion is out of scope for this manifest)")
    if manifest.get("authoring_evidence") is not False:
        errors.append("authoring_evidence must be false: a pending manifest is not authoring evidence")
    if manifest.get("executable") is not False:
        errors.append("executable must be false: a pending manifest is not asset data")
    unknown_top = set(manifest) - TOP_LEVEL_KEYS
    if unknown_top:
        errors.append("unknown top-level keys (possible conflicting approval claims): %s" % ", ".join(sorted(unknown_top)))
    missing_top = REQUIRED_TOP_LEVEL_KEYS - set(manifest)
    if missing_top:
        errors.append("missing top-level keys: %s" % ", ".join(sorted(missing_top)))
    rows = manifest.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty list")
        return {"valid": False, "errors": errors}
    seen, counts = set(), {status: 0 for status in STATUSES}
    for index, row in enumerate(rows):
        where = "row %d" % index
        if not isinstance(row, dict):
            errors.append("%s: must be an object" % where)
            continue
        field = row.get("field_path")
        where = "row %d (%s)" % (index, field)
        missing = ROW_KEYS - set(row)
        unknown = set(row) - ROW_KEYS - OPTIONAL_ROW_KEYS
        if missing:
            errors.append("%s: missing keys %s" % (where, sorted(missing)))
        if unknown:
            errors.append("%s: unknown keys %s" % (where, sorted(unknown)))
        if isinstance(field, str):
            if field in seen:
                errors.append("%s: duplicate field_path" % where)
            seen.add(field)
        status = row.get("status")
        if not isinstance(field, str) or field not in REQUIRED_FIELDS:
            errors.append("%s: field_path must be one of the required definition fields" % where)
        if not isinstance(status, str) or status not in STATUSES:  # X-2064: unhashable status -> invalid, not TypeError
            errors.append("%s: status %r refused; a pending manifest cannot approve or promote rows (allowed: %s)"
                          % (where, status, ", ".join(sorted(STATUSES))))
            continue
        counts[status] += 1
        value, kind = row.get("value"), row.get("type")
        if kind not in ("float", "name"):
            errors.append("%s: type must be 'float' or 'name'" % where)
        if status in VALUED:
            if value is None:
                errors.append("%s: %s row needs a value" % (where, status))
            elif kind == "float" and (isinstance(value, bool) or not isinstance(value, (int, float))):
                errors.append("%s: float value must be a number" % where)
            elif kind == "float" and not is_finite_number(value):
                errors.append("%s: float value must be finite" % where)
            elif kind == "name" and not (isinstance(value, str) and value):
                errors.append("%s: name value must be a non-empty string" % where)
            elif kind == "float" and isinstance(field, str) and field in NATIVE_RANGES and not in_native_range(field, value):
                errors.append("%s: value %r is outside the native range for %s" % (where, value, field))
            elif kind == "name" and field == PHASE_ID_FIELD and value != PHASE_ID:
                errors.append("%s: %s value must be %s" % (where, PHASE_ID_FIELD, PHASE_ID))
            if "candidate" in row:
                errors.append("%s: a valued row must not also carry a candidate" % where)
        else:
            if value is not None:
                errors.append("%s: OWNER_DECISION_REQUIRED row must have value null (premature promotion refused)" % where)
            if "candidate" in row:
                candidate = row["candidate"]
                if kind == "float" and not is_finite_number(candidate):
                    errors.append("%s: float candidate must be a finite number" % where)
                elif kind == "name" and not (isinstance(candidate, str) and candidate):
                    errors.append("%s: name candidate must be a non-empty string" % where)
                elif kind == "float" and isinstance(field, str) and field in NATIVE_RANGES and not in_native_range(field, candidate):
                    errors.append("%s: candidate %r is outside the native range for %s" % (where, candidate, field))
                elif kind == "name" and field == PHASE_ID_FIELD and candidate != PHASE_ID:
                    errors.append("%s: %s candidate must be %s" % (where, PHASE_ID_FIELD, PHASE_ID))
        if not isinstance(row.get("units"), str):
            errors.append("%s: units must be a string" % where)
        if not isinstance(row.get("note"), str) or not row.get("note", "").strip():
            errors.append("%s: note must be a non-empty string" % where)
        citations = row.get("citations")
        if not isinstance(citations, list) or not citations:
            errors.append("%s: at least one citation is required" % where)
        else:
            for c_index, cite in enumerate(citations):
                check_citation(cite, "%s citation %d" % (where, c_index), errors, root, verify_sources)
    absent = sorted(REQUIRED_FIELDS - seen)
    if absent:
        errors.append("required fields missing: %s" % ", ".join(absent))
    return {"valid": not errors, "errors": errors, "counts": counts,
            "owner_decisions_required": [r.get("field_path") for r in rows
                                         if isinstance(r, dict) and r.get("status") == "OWNER_DECISION_REQUIRED"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest")
    parser.add_argument("--verify-sources", action="store_true", help="also re-hash cited files and find excerpts (read-only)")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        manifest = loads_strict(Path(args.manifest).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print("INVALID cannot read manifest: %s" % error)
        return 1
    result = validate(manifest, Path(args.root), args.verify_sources)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("%s counts=%s" % ("VALID" if result["valid"] else "INVALID", result.get("counts")))
        for field in result.get("owner_decisions_required", []):
            print("  OWNER_DECISION_REQUIRED " + field)
        for error in result["errors"]:
            print("  - " + error)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
