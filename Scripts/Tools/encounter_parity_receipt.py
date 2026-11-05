"""Pure builders and strict validation for captured encounter parity receipts.

The caller supplies captured run facts; this module never reads Unreal state or
rewrites logs. See Documentation/Boss/ENCOUNTER_PARITY_RECEIPTS_H006_H010.md.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

SCHEMA = "onebossfight.encounter-parity/v2"
IDENTITY_FIELDS = (
    "map", "build_id", "content_sha256", "settings_sha256", "seed",
    "driver", "driver_args", "input_sha256",
)
HEX256 = re.compile(r"[0-9a-f]{64}")


class ReceiptError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    """Hash a source artifact in chunks without modifying it."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _nonempty_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReceiptError(f"{name} must be nonempty text")


def _validate_identity(identity: Any) -> None:
    if not isinstance(identity, dict):
        raise ReceiptError("identity must be an object")
    missing = [key for key in IDENTITY_FIELDS if key not in identity]
    if missing:
        raise ReceiptError("incomplete identity: " + ", ".join(missing))
    for key in ("map", "build_id", "driver"):
        _nonempty_text(identity[key], f"identity.{key}")
    for key in ("content_sha256", "settings_sha256", "input_sha256"):
        value = identity[key]
        if not isinstance(value, str) or not HEX256.fullmatch(value):
            raise ReceiptError(f"identity.{key} must be lowercase SHA-256")
    if type(identity["seed"]) not in (int, str) or (isinstance(identity["seed"], str) and not identity["seed"].strip()):
        raise ReceiptError("identity.seed must be a nonempty string or integer")
    if not isinstance(identity["driver_args"], list) or any(not isinstance(arg, str) for arg in identity["driver_args"]):
        raise ReceiptError("identity.driver_args must be an ordered string array")


def _validate_selection(selection: Any) -> None:
    if not isinstance(selection, dict) or type(selection.get("selected")) is not bool:
        raise ReceiptError("selection.selected boolean is required")
    if selection["selected"]:
        _nonempty_text(selection.get("definition"), "selection.definition")
        digest = selection.get("manifest_sha256")
        if not isinstance(digest, str) or not HEX256.fullmatch(digest):
            raise ReceiptError("selection.manifest_sha256 must be lowercase SHA-256")
        for key in ("encounter_instance", "boss_slot", "player_slot", "initial_boss_phase"):
            _nonempty_text(selection.get(key), f"selection.{key}")
    elif any(selection.get(key) is not None for key in (
            "definition", "manifest_sha256", "encounter_instance", "boss_slot", "player_slot", "initial_boss_phase")):
        raise ReceiptError("unselected route must not claim a selected definition or manifest")


def _validate_participants(participants: Any, *, allow_legacy_generation_zero: bool = False) -> None:
    if not isinstance(participants, list) or not participants:
        raise ReceiptError("participants must be a nonempty ordered array")
    roles: set[str] = set()
    for index, participant in enumerate(participants):
        prefix = f"participants[{index}]"
        if not isinstance(participant, dict):
            raise ReceiptError(f"{prefix} must be an object")
        role = participant.get("role")
        if role not in ("boss", "player") or role in roles:
            raise ReceiptError(f"{prefix}.role must be a unique boss or player")
        roles.add(role)
        for key in ("actor_class", "actor_id"):
            _nonempty_text(participant.get(key), f"{prefix}.{key}")
        for key in ("participant_generation", "reset_count"):
            value = participant.get(key)
            if key == "participant_generation":
                if allow_legacy_generation_zero and value in (0, "0") and type(value) in (int, str):
                    valid_generation = True
                elif type(value) is int:
                    valid_generation = 0 < value <= 0xFFFFFFFFFFFFFFFF
                elif isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value):
                    valid_generation = len(value) < 20 or (len(value) == 20 and value <= "18446744073709551615")
                else:
                    valid_generation = False
                if not valid_generation:
                    raise ReceiptError(f"{prefix}.{key} must be a nonzero uint64 integer or exact decimal string")
            elif type(value) is not int or value < 0:
                raise ReceiptError(f"{prefix}.{key} must be a nonnegative integer")
    if roles != {"boss", "player"}:
        raise ReceiptError("participants must contain exactly one boss and one player")


def build_receipt(capture: dict[str, Any]) -> dict[str, Any]:
    """Build v2 from explicit driver/harness observations; reject placeholders."""
    if not isinstance(capture, dict):
        raise ReceiptError("capture must be an object")
    route = capture.get("route")
    if route not in ("legacy", "data"):
        raise ReceiptError("route must be legacy or data")
    run_id = capture.get("run_id")
    _nonempty_text(run_id, "run_id")
    identity = capture.get("identity")
    _validate_identity(identity)
    selection = capture.get("selection")
    _validate_selection(selection)
    if route == "data" and not selection["selected"]:
        raise ReceiptError("data route requires a selected definition")
    if route == "legacy" and selection["selected"]:
        raise ReceiptError("legacy route cannot claim a selected definition")
    participants = capture.get("participants")
    _validate_participants(participants, allow_legacy_generation_zero=(route == "legacy"))
    marker = capture.get("final_marker")
    if not isinstance(marker, (str, dict)) or not marker:
        raise ReceiptError("final_marker must be nonempty text or an object")
    checks = capture.get("checks")
    if not isinstance(checks, dict) or type(checks.get("passed")) is not int or type(checks.get("minimum")) is not int:
        raise ReceiptError("checks must contain integer passed and minimum")
    if checks["minimum"] <= 0 or checks["passed"] < 0:
        raise ReceiptError("checks.minimum must be positive and checks.passed must be nonnegative")
    marker_total = marker.get("total") if isinstance(marker, dict) else None
    check_limit = marker_total if type(marker_total) is int and marker_total > 0 else checks["minimum"]
    if checks["passed"] > check_limit:
        raise ReceiptError(f"checks.passed ({checks['passed']}) exceeds captured total ({check_limit})")
    terminal = capture.get("terminal")
    if not isinstance(terminal, dict) or type(terminal.get("clean")) is not bool:
        raise ReceiptError("terminal.clean must be a boolean")
    _nonempty_text(terminal.get("result"), "terminal.result")
    activation = capture.get("activation")
    if not isinstance(activation, dict) or not isinstance(activation.get("outcome"), str) or not activation["outcome"].strip():
        raise ReceiptError("activation.outcome is required")
    components = capture.get("components")
    if not isinstance(components, dict):
        raise ReceiptError("components must be an object")
    for role in ("boss", "player"):
        census = components.get(role)
        if not isinstance(census, list) or any(not isinstance(item, str) or not item for item in census):
            raise ReceiptError(f"components.{role} must be an array of component identities")
    observables = capture.get("observables")
    if not isinstance(observables, dict) or not observables:
        raise ReceiptError("observables must be a nonempty object")
    for name, value in observables.items():
        if not isinstance(name, str) or not name or not isinstance(value, dict):
            raise ReceiptError("each observable must be a named object with source evidence")
        for key in ("value", "source_log", "source_log_sha256", "trial_id"):
            if key not in value:
                raise ReceiptError(f"observable {name} is missing {key}")
        _nonempty_text(value["source_log"], f"observables.{name}.source_log")
        _nonempty_text(value["trial_id"], f"observables.{name}.trial_id")
        if "check_status" in value and value["check_status"] not in ("PASS", "FAIL"):
            raise ReceiptError(f"observables.{name}.check_status must be PASS or FAIL")
        if "check_message" in value and not isinstance(value["check_message"], str):
            raise ReceiptError(f"observables.{name}.check_message must be text")
        if not isinstance(value["source_log_sha256"], str) or not HEX256.fullmatch(value["source_log_sha256"]):
            raise ReceiptError(f"observables.{name}.source_log_sha256 must be lowercase SHA-256")
        # Typed comparison semantics are opt-in and declared by the driver.
        comparison = value.get("comparison")
        if comparison is not None:
            if not isinstance(comparison, dict):
                raise ReceiptError(f"observables.{name}.comparison must be an object")
            kind = comparison.get("type")
            if kind == "exact":
                if set(comparison) != {"type"}:
                    raise ReceiptError(f"observables.{name}.comparison exact contract only accepts type")
                continue
            if kind == "stochastic":
                if set(comparison) != {"type", "scenario_ran_field", "threshold"}:
                    raise ReceiptError(f"observables.{name}.comparison stochastic contract has invalid fields")
                scenario_field = comparison["scenario_ran_field"]
                threshold = comparison["threshold"]
                if not isinstance(scenario_field, str) or not scenario_field:
                    raise ReceiptError(f"observables.{name}.comparison.scenario_ran_field must be a field name")
                if not isinstance(threshold, dict) or threshold.get("op") not in ("gte", "eq"):
                    raise ReceiptError(f"observables.{name}.comparison.threshold must declare gte or eq")
                if set(threshold) not in ({"left_field", "op", "right_value"}, {"left_field", "op", "right_field"}):
                    raise ReceiptError(f"observables.{name}.comparison.threshold has invalid fields")
                if not isinstance(threshold["left_field"], str) or not threshold["left_field"]:
                    raise ReceiptError(f"observables.{name}.comparison.threshold.left_field must be a field name")
                if "right_field" in threshold and (not isinstance(threshold["right_field"], str) or not threshold["right_field"]):
                    raise ReceiptError(f"observables.{name}.comparison.threshold.right_field must be a field name")
                if "right_value" in threshold and type(threshold["right_value"]) not in (int, float, bool, str):
                    raise ReceiptError(f"observables.{name}.comparison.threshold.right_value must be a scalar")
                observed = value["value"]
                if (not isinstance(observed, dict) or type(observed.get(scenario_field)) is not bool
                        or threshold["left_field"] not in observed
                        or ("right_field" in threshold and threshold["right_field"] not in observed)):
                    raise ReceiptError(f"stochastic observable {name} value is missing its run/threshold fields")
                continue
            bounds_key = {"timing_seconds": "range_seconds", "rate_ratio": "range"}.get(kind)
            if bounds_key is None or set(comparison) != {"type", bounds_key}:
                raise ReceiptError(f"observables.{name}.comparison has an unsupported typed comparison")
            bounds = comparison[bounds_key]
            if (not isinstance(bounds, list) or len(bounds) != 2
                    or any(type(bound) not in (int, float) or not math.isfinite(bound) for bound in bounds)
                    or bounds[0] < 0 or bounds[1] < bounds[0]):
                raise ReceiptError(f"observables.{name}.comparison.{bounds_key} must be [min,max] finite nonnegative values")
            if type(value["value"]) not in (int, float) or not math.isfinite(value["value"]):
                raise ReceiptError(f"typed observable {name} value must be a finite number")
    return {
        "schema": SCHEMA,
        "route": route,
        "run_id": run_id,
        "identity": identity,
        "selection": selection,
        "participants": participants,
        "final_marker": marker,
        "checks": checks,
        "terminal": terminal,
        "activation": activation,
        "components": components,
        "observables": observables,
    }


def build_receipt_from_snapshot(snapshot: dict[str, Any], run_facts: dict[str, Any]) -> dict[str, Any]:
    """Join the runtime snapshot to explicit run identity/outcome facts and validate v2."""
    if not isinstance(snapshot, dict) or snapshot.get("schema") != "onebossfight.encounter-runtime-snapshot/v1":
        raise ReceiptError("snapshot must use onebossfight.encounter-runtime-snapshot/v1")
    if not isinstance(run_facts, dict):
        raise ReceiptError("run_facts must be an object")
    route = snapshot.get("route")
    selection_source = snapshot.get("selection")
    if not isinstance(selection_source, dict) or type(selection_source.get("selected")) is not bool:
        raise ReceiptError("snapshot.selection.selected boolean is required")
    selected = selection_source["selected"]
    selection = {"selected": selected}
    selection_fields = ("definition", "manifest_sha256", "encounter_instance", "boss_slot", "player_slot", "initial_boss_phase")
    for key in selection_fields:
        value = selection_source.get(key)
        selection[key] = value if selected else None
    rows = snapshot.get("participants")
    participants: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        raise ReceiptError("snapshot.participants must be an array")
    for row in rows:
        if not isinstance(row, dict):
            raise ReceiptError("snapshot participant rows must be objects")
        participant = {key: row.get(key) for key in (
            "role", "actor_class", "actor_id", "participant_generation", "reset_count")}
        if route == "legacy" and participant["participant_generation"] in (None, ""):
            participant["participant_generation"] = "0"  # legacy has no data-binding generation
        participants.append(participant)
    facts = {key: run_facts.get(key) for key in (
        "run_id", "identity", "final_marker", "checks", "terminal", "observables")}
    capture = {
        "route": route,
        **facts,
        "selection": selection,
        "participants": participants,
        "activation": snapshot.get("activation"),
        "components": snapshot.get("components"),
    }
    return build_receipt(capture)


def write_receipt(path: Path, capture: dict[str, Any]) -> dict[str, Any]:
    """Atomically write a deterministic receipt; caller owns capture and logs."""
    receipt = build_receipt(capture)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    return receipt
