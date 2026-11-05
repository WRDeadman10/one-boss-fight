#!/usr/bin/env python3
"""Compare every typed G044 boss/player setting against cited legacy defaults.

The checked-in table deliberately distinguishes MATCH/MISMATCH from
NOT-COMPARABLE. Unknown legacy Blueprint values are never guessed.
"""
from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import math
import re
from pathlib import Path
from typing import Any

CONFIG_GROUPS = (
    "attack_tracker", "bleed", "close_clip_swap", "death", "dormant_wake",
    "encounter_policy", "fireball", "heal_punish", "look", "low_sweep",
    "phase_dependencies", "phase_flow", "phases", "shockwave",
    "stagger_policy", "stagger_profile", "stats",
)

# Runtime-use proof for the selected G044 route. These line citations are
# checked against Source on every audit, just like legacy-default citations.
# Player definition leaves are compiled and retained for the target-only
# participant, but no BossCore plan configures their values onto that actor.
PLAYER_RUNTIME_EVIDENCE = (
    {
        "file": "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp",
        "line": 270,
        "excerpt": "\tPlayerSelection.Role = ERPGPreflightRole::TargetOnly;",
        "reason": "selected route assigns the player TargetOnly",
    },
    {
        "file": "Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp",
        "line": 463,
        "excerpt": "\t\t\tif (bBossCore)",
        "reason": "preflight explicitly gives TargetOnly no BossCore plan",
    },
    {
        "file": "Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp",
        "line": 566,
        "excerpt": "\t\t\tif (Request.Role == ERPGPreflightRole::BossCore)",
        "reason": "plans are constructed only for BossCore",
    },
    {
        "file": "Source/OneBossFight/Player/RPGEncounterBinding.cpp",
        "line": 437,
        "excerpt": "\tfor (const FRPGComponentPlan& Plan : Plans)",
        "reason": "actor component configuration runs only by iterating supplied plans",
    },
)


class AuditError(ValueError):
    pass


def _set_manifest_path(root: Any, path: str, value: Any) -> None:
    """Set one exact flattened manifest path, including list indices."""
    parts = re.findall(r"[^.\[\]]+|\[[^\]]+\]", path)
    if not parts:
        raise AuditError(f"invalid manifest path {path!r}")
    current = root
    for token in parts[:-1]:
        if token.startswith("["):
            key = token[1:-1]
            if not isinstance(current, list):
                raise AuditError(f"legacy default path does not fit template: {path}")
            if key.isdigit():
                index = int(key)
                if index >= len(current):
                    raise AuditError(f"legacy default path does not fit template: {path}")
            else:
                index = next((i for i, item in enumerate(current)
                              if isinstance(item, dict) and item.get("phase_id") == key), -1)
                if index < 0:
                    raise AuditError(f"legacy default phase does not fit template: {path}")
            current = current[index]
        else:
            if not isinstance(current, dict) or token not in current:
                raise AuditError(f"legacy default path does not fit template: {path}")
            current = current[token]
    token = parts[-1]
    if token.startswith("["):
        key = token[1:-1]
        if not isinstance(current, list):
            raise AuditError(f"legacy default path does not fit template: {path}")
        if key.isdigit():
            index = int(key)
            if index >= len(current):
                raise AuditError(f"legacy default path does not fit template: {path}")
        else:
            index = next((i for i, item in enumerate(current)
                          if isinstance(item, dict) and item.get("phase_id") == key), -1)
            if index < 0:
                raise AuditError(f"legacy default phase does not fit template: {path}")
        current[index] = value
    else:
        if not isinstance(current, dict) or token not in current:
            raise AuditError(f"legacy default path does not fit template: {path}")
        current[token] = value


def emit_legacy_baseline(template: dict[str, Any], table: dict[str, Any],
                         project_root: Path = Path.cwd()) -> dict[str, Any]:
    """Copy a full G044-shaped template and replace every boss leaf by its cited legacy value."""
    result = copy.deepcopy(template)
    boss_paths = {path for path in typed_fields(result) if path.startswith("definitions.boss.")}
    rules = table.get("rules")
    if not isinstance(rules, list):
        raise AuditError("defaults table rules must be an array")
    assigned: set[str] = set()
    for path in sorted(boss_paths):
        matches = [rule for rule in rules if isinstance(rule, dict)
                   and isinstance(rule.get("pattern"), str)
                   and (path == rule["pattern"] if not any(c in rule["pattern"] for c in "*?")
                        else fnmatch.fnmatchcase(path, rule["pattern"]))]
        if not matches:
            continue
        matches.sort(key=lambda row: (-len(row["pattern"].replace("*", "").replace("?", "")),
                                      row["pattern"].count("*") + row["pattern"].count("?")))
        rule = matches[0]
        if rule.get("status") != "comparable" or "legacy_value" not in rule:
            raise AuditError(f"{path}: cannot emit a non-comparable legacy default")
        cite = rule.get("source")
        if (not isinstance(cite, dict) or not isinstance(cite.get("file"), str)
                or type(cite.get("line")) is not int or cite["line"] < 1):
            raise AuditError(f"{path}: default rule needs a file:line citation")
        cited_path = (project_root / cite["file"]).resolve()
        try:
            cited_path.relative_to(project_root.resolve())
            lines = cited_path.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError, UnicodeError) as exc:
            raise AuditError(f"{path}: cited source cannot be read: {exc}") from exc
        if cite["line"] > len(lines) or lines[cite["line"] - 1].strip() != cite.get("excerpt"):
            raise AuditError(f"{path}: stale source citation {cite['file']}:{cite['line']}")
        value = rule["legacy_value"]
        if isinstance(value, list) and rule["pattern"].endswith("*"):
            suffix = path[len(rule["pattern"][:-1]):]
            index_match = re.match(r"\[(\d+)\](?:\.object_path)?$", suffix)
            if index_match:
                index = int(index_match.group(1))
                value = value[index] if index < len(value) else None
        _set_manifest_path(result["definitions"], path.removeprefix("definitions."), value)
        assigned.add(path)
    missing = sorted(boss_paths - assigned)
    if missing:
        raise AuditError("no exact cited legacy default for boss leaves: " + ", ".join(missing[:8]))
    return result


def validate_tuning_allowlist(rows: list[dict[str, Any]], intentional_fields: set[str]) -> list[str]:
    """Return mismatch field paths not explicitly listed as intentional tuning."""
    return [row["path"] for row in rows
            if row.get("status") == "MISMATCH" and row.get("path") not in intentional_fields]


def parse_intentional_tuning(rows: list[dict[str, Any]], approved: Any) -> set[str]:
    """Validate S26 records and bind approval to the exact current mismatch value."""
    if not isinstance(approved, list):
        raise AuditError("intentional tuning file must be a JSON array of approval records")
    mismatch_by_path = {row["path"]: row["manifest_value"] for row in rows
                        if row.get("status") == "MISMATCH"}
    fields: set[str] = set()
    for index, record in enumerate(approved):
        if not isinstance(record, dict) or set(record) != {
                "field", "value", "reason", "owner_approval_id"}:
            raise AuditError(f"intentional tuning record {index} must contain exactly field, value, reason, owner_approval_id")
        field = record["field"]
        if not isinstance(field, str) or not field:
            raise AuditError(f"intentional tuning record {index} field must be a nonempty string")
        if field in fields:
            raise AuditError(f"duplicate intentional tuning field: {field}")
        fields.add(field)
        if field not in mismatch_by_path:
            raise AuditError(f"intentional tuning field is not a current MISMATCH: {field}")
        if not _equal(record["value"], mismatch_by_path[field]):
            raise AuditError(f"intentional tuning approved value does not match the draft: {field}")
        if not isinstance(record["reason"], str) or not record["reason"].strip():
            raise AuditError(f"intentional tuning record {index} needs a nonempty reason")
        if not isinstance(record["owner_approval_id"], str) or not record["owner_approval_id"].strip():
            raise AuditError(f"intentional tuning record {index} needs an owner approval id")
    return fields


def _flatten(value: Any, prefix: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            result.update(_flatten(child, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.update(_flatten(child, f"{prefix}[{index}]"))
    else:
        result[prefix] = value
    return result


def typed_fields(manifest: dict[str, Any]) -> dict[str, Any]:
    definitions = manifest.get("definitions")
    if not isinstance(definitions, dict) or set(definitions) != {"boss", "player"}:
        raise AuditError("manifest definitions must contain exactly boss and player")
    rows: dict[str, Any] = {}
    for role, definition in definitions.items():
        if not isinstance(definition, dict):
            raise AuditError(f"definitions.{role} must be an object")
        for group in CONFIG_GROUPS:
            if group not in definition:
                raise AuditError(f"definitions.{role}.{group} is missing")
            value = definition[group]
            if group == "phases":
                if not isinstance(value, list):
                    raise AuditError(f"definitions.{role}.phases must be an array")
                for phase in value:
                    phase_id = phase.get("phase_id") if isinstance(phase, dict) else None
                    if not isinstance(phase_id, str) or not phase_id:
                        raise AuditError("every phase must have a nonempty phase_id")
                    for key, item in phase.items():
                        if key == "phase_id":
                            continue
                        path = f"definitions.{role}.phases[{phase_id}].{key}"
                        rows[path] = item
            else:
                rows.update(_flatten(value, f"definitions.{role}.{group}"))
    return rows


def _equal(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and set(left) == {"object_path"} and isinstance(right, str):
        return left["object_path"] == right
    if isinstance(right, dict) and set(right) == {"object_path"} and isinstance(left, str):
        return right["object_path"] == left
    if isinstance(left, str) and isinstance(right, str):
        enum_match = re.search(r"\.([A-Z][A-Z0-9_]*):\s*\d+>\s*$", left)
        if enum_match:
            return enum_match.group(1).replace("_", "").lower() == right.replace("_", "").lower()
    if type(left) in (int, float) and type(right) in (int, float):
        return math.isfinite(left) and math.isfinite(right) and math.isclose(left, right, rel_tol=0, abs_tol=1e-5)
    return type(left) is type(right) and left == right


def _checked_runtime_classification(path: str, project_root: Path) -> tuple[str, list[dict[str, str]]]:
    if not path.startswith("definitions.player."):
        return "NOT_PLAYER", []
    for cite in PLAYER_RUNTIME_EVIDENCE:
        cited_path = (project_root / cite["file"]).resolve()
        try:
            cited_path.relative_to(project_root.resolve())
            source_lines = cited_path.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError, UnicodeError) as exc:
            raise AuditError(f"{path}: runtime classification source cannot be read: {exc}") from exc
        if cite["line"] > len(source_lines) or source_lines[cite["line"] - 1].strip() != cite["excerpt"].strip():
            raise AuditError(f"{path}: stale runtime classification citation {cite['file']}:{cite['line']}")
    return "INERT", [
        {"file": cite["file"], "line": cite["line"], "excerpt": cite["excerpt"], "reason": cite["reason"]}
        for cite in PLAYER_RUNTIME_EVIDENCE
    ]


def audit(manifest: dict[str, Any], table: dict[str, Any], project_root: Path = Path.cwd()) -> list[dict[str, Any]]:
    fields = typed_fields(manifest)
    rules = table.get("rules")
    if not isinstance(rules, list):
        raise AuditError("defaults table rules must be an array")
    output = []
    for path, value in fields.items():
        matches = [rule for rule in rules if isinstance(rule, dict)
                   and isinstance(rule.get("pattern"), str)
                   and (path == rule["pattern"] if not any(c in rule["pattern"] for c in "*?")
                        else fnmatch.fnmatchcase(path, rule["pattern"]))]
        if not matches:
            raise AuditError(f"{path}: no cited default rule")
        specificity = lambda row: (-len(row["pattern"].replace("*", "").replace("?", "")),
                                   row["pattern"].count("*") + row["pattern"].count("?"))
        matches.sort(key=specificity)
        if len(matches) > 1 and specificity(matches[0]) == specificity(matches[1]):
            raise AuditError(f"{path}: ambiguous equally specific default rules")
        rule = matches[0]
        legacy_value = rule.get("legacy_value")
        if isinstance(legacy_value, list) and rule["pattern"].endswith("*"):
            prefix = rule["pattern"][:-1]
            suffix = path[len(prefix):] if path.startswith(prefix) else ""
            match = __import__("re").match(r"\[(\d+)\](?:\.object_path)?$", suffix)
            if match:
                index = int(match.group(1))
                legacy_value = legacy_value[index] if index < len(legacy_value) else None
        cite = rule.get("source")
        if (not isinstance(cite, dict) or not isinstance(cite.get("file"), str)
                or type(cite.get("line")) is not int or cite["line"] < 1):
            raise AuditError(f"{path}: default rule needs a file:line citation")
        cited_path = (project_root / cite["file"]).resolve()
        try:
            cited_path.relative_to(project_root.resolve())
            source_lines = cited_path.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError, UnicodeError) as exc:
            raise AuditError(f"{path}: cited source cannot be read: {exc}") from exc
        if cite["line"] > len(source_lines) or source_lines[cite["line"] - 1].strip() != cite.get("excerpt"):
            raise AuditError(f"{path}: stale source citation {cite['file']}:{cite['line']}")
        status = rule.get("status")
        runtime_classification, runtime_evidence = _checked_runtime_classification(path, project_root)
        row = {"path": path, "manifest_value": value, "status": status,
               "runtime_classification": runtime_classification,
               "runtime_evidence": runtime_evidence,
               "source": cite, "reason": rule.get("reason", "")}
        if status == "comparable":
            if "legacy_value" not in rule:
                raise AuditError(f"{path}: comparable rule is missing legacy_value")
            row["legacy_value"] = legacy_value
            row["status"] = "MATCH" if _equal(value, legacy_value) else "MISMATCH"
        elif status == "not_comparable":
            if not row["reason"]:
                raise AuditError(f"{path}: NOT-COMPARABLE requires a reason")
            row["status"] = "NOT-COMPARABLE"
        else:
            raise AuditError(f"{path}: unsupported table status {status!r}")
        output.append(row)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--defaults", type=Path, default=Path(__file__).with_name("legacy_defaults_g044.json"))
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="emit machine-readable rows")
    parser.add_argument("--emit-legacy-baseline", action="store_true",
                        help="write a full boss-defaulted manifest using input as shape/identity template")
    parser.add_argument("--output", type=Path, help="new output path required with --emit-legacy-baseline")
    parser.add_argument("--intentional-tuning", type=Path,
                        help="JSON array of exact mismatching boss field paths explicitly approved as tuning")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        table = json.loads(args.defaults.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(table, dict):
            raise AuditError("manifest and defaults roots must be objects")
        if args.emit_legacy_baseline:
            if args.output is None:
                raise AuditError("--output is required with --emit-legacy-baseline")
            if args.output.exists():
                raise AuditError(f"output already exists; refusing overwrite: {args.output}")
            manifest = emit_legacy_baseline(manifest, table, args.project_root.resolve())
            rows = audit(manifest, table, args.project_root.resolve())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                                   encoding="utf-8")
            print(f"WROTE {args.output} ({len(rows)} checked typed fields)")
        else:
            rows = audit(manifest, table, args.project_root.resolve())
        intentional_fields: set[str] = set()
        if args.intentional_tuning:
            approved = json.loads(args.intentional_tuning.read_text(encoding="utf-8"))
            intentional_fields = parse_intentional_tuning(rows, approved)
        unapproved = validate_tuning_allowlist(rows, intentional_fields)
    except (OSError, UnicodeError, json.JSONDecodeError, AuditError) as exc:
        parser.exit(2, f"error: {exc}\n")
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    else:
        for row in rows:
            source = row["source"]
            runtime_citations = ",".join(
                f"{cite['file']}:{cite['line']}" for cite in row["runtime_evidence"]
            ) or "—"
            print(f"{row['status']} {row['path']} = {row['manifest_value']!r}; "
                  f"legacy={row.get('legacy_value', 'unknown')!r}; "
                  f"runtime={row['runtime_classification']} [{runtime_citations}]; "
                  f"{source['file']}:{source['line']} {row['reason']}")
        counts = {name: sum(row["status"] == name for row in rows)
                  for name in ("MATCH", "MISMATCH", "NOT-COMPARABLE")}
        print(f"SUMMARY fields={len(rows)} MATCH={counts['MATCH']} "
              f"MISMATCH={counts['MISMATCH']} NOT-COMPARABLE={counts['NOT-COMPARABLE']}")
    return 1 if unapproved else 0


if __name__ == "__main__":
    raise SystemExit(main())
