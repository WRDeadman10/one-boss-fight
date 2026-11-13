"""BQ-22 (Queue BQ batch 5; D4): offline validator for BENCHMARK_RUN_RECEIPT_V1 (a proposal awaiting Lead adoption).

Library function ``validate(receipt, schema=None, root=None) -> list[str]`` returns refusal reasons (empty = structurally valid).
1. Structural: a small, dependency-free subset of JSON Schema read from the schema file itself (type, required,
   additionalProperties false, enum, const, pattern, minLength, minimum, maximum, exclusiveMinimum, $ref, items, uniqueItems).
   Any other keyword found in the schema is a refusal, so the validator can never silently skip a rule.
2. Semantic (the BI X03 negative list): UTC timestamps that end in Z and do not run backwards; a "target" device claim needs a
   console session; a "valid" verdict carries no reasons; artifact paths are relative to ``root`` with no traversal, absolute
   path or symlink escape; when ``root`` is given, each artifact must exist with the recorded byte count and SHA-256.
It never decides acceptance policy (sample counts, proxy substitution, the 60 FPS target): that stays with the Lead.
Fail-closed: anything it cannot check is a refusal, not a pass. Library only: no CLI, no file writes.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "Documentation" / "Boss" / "BENCHMARK_RUN_RECEIPT_V1.schema.json"

# Keywords this validator enforces, plus annotation-only keywords it may ignore safely.
_ENFORCED = {"type", "required", "additionalProperties", "enum", "const", "pattern", "minLength", "minimum", "maximum",
             "exclusiveMinimum", "$ref", "items", "uniqueItems", "properties"}
_ANNOTATIONS = {"$schema", "$id", "$defs", "title", "description", "format", "$comment"}
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool}


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _type_errors(node: Any, kind: Any, where: str) -> list[str]:
    errors: list[str] = []
    _check(node, {"type": kind}, {}, where, errors)
    return errors


def _check(node: Any, rule: Any, root_schema: dict, where: str, errors: list[str]) -> None:
    if not isinstance(rule, dict):
        errors.append(f"{where}: schema rule is not an object")
        return
    unknown = set(rule) - _ENFORCED - _ANNOTATIONS
    if unknown:
        errors.append(f"{where}: unsupported schema keyword(s) {sorted(unknown)}")
        return
    if "$ref" in rule:
        ref = rule["$ref"]
        defs = root_schema.get("$defs", {})
        if not isinstance(ref, str) or not ref.startswith("#/$defs/") or ref[len("#/$defs/"):] not in defs:
            errors.append(f"{where}: unsupported $ref {ref!r}")
            return
        _check(node, defs[ref[len("#/$defs/"):]], root_schema, where, errors)
        return
    if "const" in rule and node != rule["const"]:
        errors.append(f"{where}: expected {rule['const']!r}")
        return
    if "enum" in rule and node not in rule["enum"]:
        errors.append(f"{where}: {node!r} not in {rule['enum']}")
        return
    kind = rule.get("type")
    if isinstance(kind, list):
        # A list of types: the node must satisfy at least one alternative (checked with the type keyword alone).
        if not any(not _type_errors(node, k, where) for k in kind):
            errors.append(f"{where}: expected one of {kind}")
            return
        kind = None
    if kind == "integer":
        if not (isinstance(node, int) and not isinstance(node, bool)):
            errors.append(f"{where}: expected integer")
            return
    elif kind == "number":
        if not _is_number(node):
            errors.append(f"{where}: expected number")
            return
    elif kind in _TYPES:
        if not isinstance(node, _TYPES[kind]):
            errors.append(f"{where}: expected {kind}")
            return
    elif kind is not None:
        errors.append(f"{where}: unsupported type {kind!r}")
        return
    if _is_number(node):
        if isinstance(node, float) and not math.isfinite(node):
            errors.append(f"{where}: not finite")
            return
        if "minimum" in rule and node < rule["minimum"]:
            errors.append(f"{where}: below minimum {rule['minimum']}")
        if "maximum" in rule and node > rule["maximum"]:
            errors.append(f"{where}: above maximum {rule['maximum']}")
        if "exclusiveMinimum" in rule and node <= rule["exclusiveMinimum"]:
            errors.append(f"{where}: must be greater than {rule['exclusiveMinimum']}")
    if isinstance(node, str):
        if len(node) < rule.get("minLength", 0):
            errors.append(f"{where}: shorter than {rule['minLength']}")
        if "pattern" in rule and not re.search(rule["pattern"], node):
            errors.append(f"{where}: does not match {rule['pattern']}")
    if isinstance(node, list):
        if rule.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in node}) != len(node):
            errors.append(f"{where}: items not unique")
        if "items" in rule:
            for index, item in enumerate(node):
                _check(item, rule["items"], root_schema, f"{where}[{index}]", errors)
    if isinstance(node, dict):
        props = rule.get("properties", {})
        for key in rule.get("required", []):
            if key not in node:
                errors.append(f"{where}.{key}: missing")
        extra = rule.get("additionalProperties")
        for key in node:
            if key in props:
                continue
            if extra is False:
                errors.append(f"{where}.{key}: not allowed")
            elif isinstance(extra, dict):
                _check(node[key], extra, root_schema, f"{where}.{key}", errors)
        for key, sub in props.items():
            if key in node:
                _check(node[key], sub, root_schema, f"{where}.{key}", errors)


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None


def _artifact_errors(name: str, art: Any, root: Path | None) -> list[str]:
    if not isinstance(art, dict) or not isinstance(art.get("path"), str):
        return []  # the structural pass has already refused it
    raw = art["path"]
    pure = PurePosixPath(raw.replace("\\", "/"))
    if pure.is_absolute() or re.match(r"^[A-Za-z]:", raw) or ".." in pure.parts:
        return [f"artifacts.{name}: path must be relative to the receipt root without '..'"]
    if root is None:
        return []
    root_resolved = root.resolve()
    target = (root / pure).resolve()
    if target != root_resolved and root_resolved not in target.parents:
        return [f"artifacts.{name}: resolves outside the receipt root (symlink)"]
    if not target.is_file():
        return [f"artifacts.{name}: file missing"]
    data = target.read_bytes()
    errors = []
    if len(data) != art.get("bytes"):
        errors.append(f"artifacts.{name}: byte count mismatch")
    if hashlib.sha256(data).hexdigest() != art.get("sha256"):
        errors.append(f"artifacts.{name}: sha256 mismatch")
    return errors


def validate(receipt: Any, schema: dict | None = None, root: Path | None = None) -> list[str]:
    """Return every refusal reason for one receipt; an empty list means it passed both passes."""
    schema = schema if schema is not None else load_schema()
    if not isinstance(receipt, dict):
        return ["receipt: expected a JSON object"]
    errors: list[str] = []
    _check(receipt, schema, schema, "receipt", errors)
    started, completed = _utc(receipt.get("started_at_utc")), _utc(receipt.get("completed_at_utc"))
    if started is None:
        errors.append("started_at_utc: not a UTC timestamp ending in Z")
    if completed is None:
        errors.append("completed_at_utc: not a UTC timestamp ending in Z")
    if started and completed and completed < started:
        errors.append("completed_at_utc: earlier than started_at_utc")
    device = receipt.get("device") if isinstance(receipt.get("device"), dict) else {}
    if device.get("target_class") == "target" and device.get("session_type") != "console":
        errors.append("device: a target-class claim needs a console session")
    validity = receipt.get("validity") if isinstance(receipt.get("validity"), dict) else {}
    if validity.get("verdict") == "valid" and validity.get("reasons"):
        errors.append("validity: a valid verdict cannot carry refusal reasons")
    artifacts = receipt.get("artifacts") if isinstance(receipt.get("artifacts"), dict) else {}
    for name, art in artifacts.items():
        errors.extend(_artifact_errors(name, art, root))
    return errors
