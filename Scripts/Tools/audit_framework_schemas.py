"""Audit FrameworkProof schema duplicates, source/docs mapping, log samples, and regex looseness."""
import argparse
import ast
import re
import sys
from collections import Counter
from pathlib import Path

from check_validator_tokens import emitted_tokens, table_tokens

FIELD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")
FIELD_KEY = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=")
NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
UE_LOG_CALL = re.compile(r'UE_LOG\s*\((?P<body>(?:[^;"\\]|"(?:\\.|[^"\\])*")*);', re.DOTALL)
TEXT_LITERAL = re.compile(r'TEXT\s*\(\s*"((?:\\.|[^"\\])*)"')
TOKEN_IN_TEXT = re.compile(r"\[FrameworkProof\]\s*([A-Za-z_][A-Za-z0-9_]*)")


def duplicate_schema_keys(source):
    """Return (key, kind, first_line, duplicate_line) for duplicate SCHEMAS keys."""
    tree = ast.parse(source)
    rows = []
    for node in ast.walk(tree):
        value = None
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCHEMAS" for t in node.targets):
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "SCHEMAS":
            value = node.value
        if not isinstance(value, ast.Dict):
            continue
        seen = {}
        for key_node, pattern_node in zip(value.keys, value.values):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                continue
            key = key_node.value
            pattern = ast.dump(pattern_node, include_attributes=False)
            if key in seen:
                old_pattern, old_line = seen[key]
                kind = "exact duplicate" if pattern == old_pattern else "conflicting duplicate"
                rows.append((key, kind, old_line, key_node.lineno))
            else:
                seen[key] = (pattern, key_node.lineno)
    return rows


def numeric_permissiveness_witness(pattern, payload):
    """Return one payload with a numeric sample field corrupted but still regex-accepted."""
    compiled = re.compile(pattern)
    if not compiled.fullmatch(payload):
        return None
    for match in FIELD.finditer(payload):
        key, value = match.groups()
        if not NUMBER.fullmatch(value):
            continue
        malformed = payload[:match.start(2)] + "NOT_A_NUMBER" + payload[match.end(2):]
        if compiled.fullmatch(malformed):
            return malformed
    return None


def schema_locations(validator_source):
    tree = ast.parse(validator_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SCHEMAS" for t in node.targets):
            if isinstance(node.value, ast.Dict):
                return {k.value: k.lineno for k in node.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    return {}


def table_token_counts(markdown, title=None):
    text = markdown
    if title:
        text = text.split(title, 1)[1] if title in text else ""
    return Counter(token for line in text.splitlines() if line.startswith("|")
                   for token in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", line))


def index_problems(counts, schema_tokens):
    """Return duplicate and missing schema-token rows for a documentation index."""
    duplicates = sorted(token for token, count in counts.items() if count > 1)
    missing = sorted(set(schema_tokens) - set(counts))
    return duplicates, missing


def emitted_locations(source_dir):
    from check_validator_tokens import FRAMEWORK_LOG, strip_cpp_comments
    locations = {}
    for path in sorted((*source_dir.rglob("*.cpp"), *source_dir.rglob("*.h"))):
        source = strip_cpp_comments(path.read_text(encoding="utf-8", errors="replace"))
        for match in FRAMEWORK_LOG.finditer(source):
            locations.setdefault(match.group(1), []).append("%s:%d" % (path.relative_to(source_dir.parent), source.count("\n", 0, match.start()) + 1))
    return locations


def emitted_fields(source_dir):
    """Map emitted tokens to fields present in their literal UE_LOG format strings."""
    from check_validator_tokens import strip_cpp_comments
    fields = {}
    locations = {}
    for path in sorted((*source_dir.rglob("*.cpp"), *source_dir.rglob("*.h"))):
        source = strip_cpp_comments(path.read_text(encoding="utf-8", errors="replace"))
        for call in UE_LOG_CALL.finditer(source):
            for literal in TEXT_LITERAL.finditer(call.group("body")):
                format_text = literal.group(1)
                token_match = TOKEN_IN_TEXT.search(format_text)
                if not token_match:
                    continue
                token = token_match.group(1)
                field_text = format_text[token_match.end():]
                fields.setdefault(token, set()).update(key for key, _ in FIELD.findall(field_text))
                locations.setdefault(token, []).append("%s:%d" % (path.relative_to(source_dir.parent), source.count("\n", 0, call.start()) + 1))
    return fields, locations


def literal_format_variants(source_dir, validator, samples):
    """Build one representative payload for every literal UE_LOG format string."""
    from check_validator_tokens import strip_cpp_comments
    rows = []
    format_spec = re.compile(r"%(?:[-+#0 ]*\d*(?:\.\d+)?)?(?:ll|l|z)?[diuoxXfFeEgGaAcsp]")
    for path in sorted((*source_dir.rglob("*.cpp"), *source_dir.rglob("*.h"))):
        source = strip_cpp_comments(path.read_text(encoding="utf-8", errors="replace"))
        for call in UE_LOG_CALL.finditer(source):
            line_number = source.count("\n", 0, call.start()) + 1
            for literal in TEXT_LITERAL.finditer(call.group("body")):
                text = literal.group(1).replace(r"\n", " ").replace(r"\t", " ")
                marker = TOKEN_IN_TEXT.search(text)
                if not marker:
                    continue
                token = marker.group(1)
                if token in {"ERROR", "overlay"}:
                    # These literals contain a separately formatted/dynamic payload.
                    continue
                tail = text[marker.end():]
                sample_payload = samples.get(token, (None, None, ""))[2]
                sample_values = dict(FIELD.findall(sample_payload))
                key_matches = list(FIELD_KEY.finditer(tail))
                if not key_matches and not tail.strip():
                    payload = ""
                else:
                    rendered = []
                    prefix = tail[:key_matches[0].start()].strip() if key_matches else tail.strip()
                    for index, key_match in enumerate(key_matches):
                        key = key_match.group(1)
                        end = key_matches[index + 1].start() if index + 1 < len(key_matches) else len(tail)
                        template = tail[key_match.end():end].strip()
                        # Keep fixed enum/literal values (e.g. state=Aborted); for
                        # printf fields, use a retained valid value when available.
                        if format_spec.search(template):
                            # FVector::ToString emits a three-axis value inside one %s.
                            if key in {"start", "end", "capsule", "mesh", "projected", "targetLocation", "base", "tip"} and sample_values.get(key, "").startswith("X="):
                                next_outer = next((k for k in key_matches[index + 1:] if k.group(1) in {"end", "distanceCm", "rangeCm", "bandMin", "bandMax", "capsule", "mesh", "fullPath", "result", "base", "tip"}), None)
                                sample_pattern = (re.escape(key) + r"=(.*?)(?=\s+" + re.escape(next_outer.group(1)) + r"=|$)") if next_outer else (re.escape(key) + r"=(.*)$")
                                sample_match = re.search(sample_pattern, sample_payload)
                                value = sample_match.group(1) if sample_match else sample_values.get(key, "X=0 Y=0 Z=0")
                            else:
                                value = sample_values.get(key)
                            if value is None:
                                if re.search(r"%s", template):
                                    value = "X"
                                else:
                                    value = "1"
                        else:
                            value = template
                        rendered.append(f"{key}={value}")
                    payload = " ".join(([prefix] if prefix else []) + rendered)
                ok, _, _, error = validator.validate_line(f"[FrameworkProof] {token}" + (f" {payload}" if payload else ""))
                rows.append((token, path, line_number, payload, ok, error))
    return rows


def log_samples(root, validator):
    samples = {}
    for path in sorted((root / "Docs").rglob("*.log")):
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = validator.LINE_RE.search(line)
            if not match:
                continue
            token, payload = match.groups()
            if token in validator.SCHEMAS and token not in samples:
                ok, _, _, _ = validator.validate_line(line)
                if ok:
                    samples[token] = (path.relative_to(root).as_posix(), number, payload or "")
    return samples


def audit(root):
    reviews = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
    validator_path = reviews / "validate_framework_proof_logs.py"
    validator_source = validator_path.read_text(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(reviews))
    import validate_framework_proof_logs as validator
    emitted = emitted_tokens(root / "Source")
    source_map = emitted_locations(root / "Source")
    source_fields_map, field_locations = emitted_fields(root / "Source")
    locations = schema_locations(validator_source)
    samples = log_samples(root, validator)
    literal_variants = literal_format_variants(root / "Source", validator, samples)
    log_tokens = (root / "Documentation/Boss/LOG_TOKENS.md").read_text(encoding="utf-8")
    semantic = table_tokens(log_tokens.split("## Emission source locations", 1)[0])
    emission = table_tokens(log_tokens, "## Emission source locations")
    semantic_counts = table_token_counts(log_tokens.split("## Emission source locations", 1)[0])
    emission_counts = table_token_counts(log_tokens, "## Emission source locations")
    schema_field_map = {token: set(FIELD_KEY.findall(pattern))
                        for token, pattern in validator.SCHEMAS.items()}
    duplicates = duplicate_schema_keys(validator_source)
    permissive = {}
    for token, (_, _, payload) in samples.items():
        witness = numeric_permissiveness_witness(validator.SCHEMAS[token], payload)
        if witness:
            permissive[token] = witness
    return (validator, emitted, source_map, locations, samples, semantic, emission,
            duplicates, permissive, source_fields_map, field_locations, schema_field_map,
            semantic_counts, emission_counts, literal_variants)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    (validator, emitted, source_map, locations, samples, semantic, emission,
     duplicates, permissive, source_fields_map, field_locations, schema_field_map,
     semantic_counts, emission_counts, literal_variants) = audit(root)

    print("FrameworkProof schema audit: %d schemas, %d emitted tokens, %d retained valid token samples" %
          (len(validator.SCHEMAS), len(emitted), len(samples)))
    index_errors = False
    if duplicates:
        for key, kind, first, duplicate in duplicates:
            print("DUPLICATE %s: %s lines %d,%d" % (kind, key, first, duplicate))
    else:
        print("DUPLICATES: none")
    for index_name, counts in (("semantic", semantic_counts), ("emission-source", emission_counts)):
        repeated, missing = index_problems(counts, validator.SCHEMAS)
        print("INDEX %s | duplicate=%s | missing_schema_tokens=%s" %
              (index_name, ",".join(repeated) or "none", ",".join(missing) or "none"))
        index_errors |= bool(repeated or missing)
    missing_samples = sorted(set(validator.SCHEMAS) - set(samples))
    print("SCHEMAS WITHOUT VALID RETAINED SAMPLE: " + (", ".join(missing_samples) if missing_samples else "none"))
    for token in sorted(emitted):
        print("MAP %s | source=%s | schema_line=%s | semantic=%s | emission=%s | sample=%s" % (
            token, ",".join(source_map.get(token, [])) or "missing",
            locations.get(token, "missing"), "yes" if token in semantic else "NO",
            "yes" if token in emission else "NO",
            ("%s:%d" % samples[token][:2]) if token in samples else "none"))
    print("TELEMETRY FIELD DRIFT:")
    drift_count = 0
    for token in sorted(emitted):
        source_fields = source_fields_map.get(token, set())
        schema_fields = schema_field_map.get(token, set())
        if token in {"ERROR", "overlay"}:
            print("FIELDS %s | classification=unbounded/dynamic payload; static key comparison skipped" % token)
            continue
        extra = sorted(source_fields - schema_fields)
        absent = sorted(schema_fields - source_fields - {"X", "Y", "Z"})
        if extra or absent:
            drift_count += 1
            print("FIELDS %s | source=%s | schema=%s | unexpected=%s | schema_only=%s | emission=%s" %
                  (token, ",".join(sorted(source_fields)) or "-",
                   ",".join(sorted(schema_fields)) or "-", ",".join(extra) or "-",
                   ",".join(absent) or "-", ",".join(field_locations.get(token, [])) or "unresolved"))
    if not drift_count:
        print("none detected")
    print("LITERAL UE_LOG FORMAT VALIDATION:")
    format_mismatches = [row for row in literal_variants if not row[4]]
    if format_mismatches:
        for token, path, line_number, payload, _, error in format_mismatches:
            print("FORMAT MISMATCH %s | %s:%d | payload=%s | %s" %
                  (token, path.relative_to(root), line_number, payload or "<empty>", error))
    else:
        print("%d literal variants validated; 0 mismatches (dynamic ERROR/overlay excluded)" % len(literal_variants))
    print("NUMERIC REGEX PERMISSIVENESS (sample numeric field replaced by NOT_A_NUMBER):")
    if permissive:
        for token, witness in sorted(permissive.items()):
            sample_path, sample_line, _ = samples[token]
            print("LOOSE %s sample=%s:%d: [FrameworkProof] %s %s" %
                  (token, sample_path, sample_line, token, witness))
    else:
        print("none detected in first valid samples")
    return 1 if (duplicates or index_errors or format_mismatches or emitted - set(validator.SCHEMAS) or emitted - semantic or emitted - emission) else 0


if __name__ == "__main__":
    raise SystemExit(main())
