"""Fail-closed predicate checker for a Lead-transcribed BF-X05 evidence receipt.

This validates receipt fields and evidence citations; it is not a live-log
parser and does not establish that cited excerpts came from a genuine run.
"""
import argparse
import json
import math
import re
from pathlib import Path


ROWS = ("ID-01", "PACK-01", "FW-01", "PART-01", "HUD-01", "TERM-01", "RETRY-01", "RESET-01", "REPLACE-01")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ReceiptError(ValueError):
    pass


def _need(condition, message):
    if not condition:
        raise ReceiptError(message)


def _finite_number(value, field):
    _need(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value), field + " must be finite numeric")
    return float(value)


def _count_is(value, expected):
    return isinstance(value, int) and not isinstance(value, bool) and value == expected


def _evidence(receipt, row):
    entries = receipt.get("evidence", {}).get(row)
    _need(isinstance(entries, list) and entries, row + " missing evidence citations")
    for entry in entries:
        _need(isinstance(entry, dict), row + " evidence entry must be an object")
        _need(isinstance(entry.get("log"), str) and entry["log"].strip(), row + " evidence log path missing")
        _need(isinstance(entry.get("excerpt"), str) and entry["excerpt"].strip(), row + " evidence excerpt missing")
    return entries


def validate(data):
    _need(isinstance(data, dict) and data.get("schema_version") == 1, "schema_version must be 1")
    _need(isinstance(data.get("build_id"), str) and data["build_id"].strip(), "build_id missing")
    _need(isinstance(data.get("map"), str) and data["map"].strip(), "map missing")
    runs = data.get("runs")
    _need(isinstance(runs, dict) and set(runs) == {"default_off", "framework_opt_in"}, "runs must contain default_off and framework_opt_in")
    pack, fw = runs["default_off"], runs["framework_opt_in"]
    for name, run in runs.items():
        _need(isinstance(run, dict), name + " must be an object")
        _need(run.get("build_id") == data["build_id"], name + " build_id mismatch")
        _need(run.get("map") == data["map"], name + " map mismatch")
        _need(isinstance(run.get("world"), str) and run["world"].strip(), name + " world missing")
    _need(pack["world"] != fw["world"], "two arms must have distinct world identities")
    _need(pack.get("route_flag") is False and pack.get("selected_route") == "Pack", "PACK-01 route or selector flag incorrect")
    _need(_count_is(pack.get("pack_boss_count"), 1) and _count_is(pack.get("framework_boss_count"), 0) and pack.get("framework_binding") is False,
          "PACK-01 requires one pack boss and no framework binding/candidate")
    _need(fw.get("route_flag") is True and fw.get("selected_route") == "Framework", "FW-01 route or selector flag incorrect")
    _need(_count_is(fw.get("pack_boss_count"), 0) and _count_is(fw.get("framework_boss_count"), 1) and fw.get("framework_binding") is True,
          "FW-01 requires exactly one framework boss and no pack boss")
    _need(isinstance(fw.get("definition_path"), str) and fw["definition_path"].startswith("/Game/"), "FW-01 definition path missing")
    _need(isinstance(fw.get("definition_sha256"), str) and SHA256.fullmatch(fw["definition_sha256"]), "FW-01 definition SHA-256 invalid")
    _need(fw.get("definition_sha256") == fw.get("definition_hash_readback"), "FW-01 definition hash readback mismatch")
    deferred = fw.get("deferred_selection", {})
    _need(isinstance(deferred, dict), "FW-01 deferred_selection witness missing")
    _need(deferred.get("pack_isolated_before_spawn") is True, "FW-01 pack must be isolated before framework spawn")
    _need(deferred.get("framework_spawn_before_selection") is True, "FW-01 framework actor must spawn before selection")
    _need(deferred.get("selector_flag") == 1 and deferred.get("definition_path") == fw["definition_path"],
          "FW-01 deferred selector flag/definition mismatch")
    _need(deferred.get("activation_result") == "Activated", "FW-01 deferred activation did not succeed")

    participants = fw.get("participants", {})
    boss, player = participants.get("boss", {}), participants.get("player", {})
    _need(isinstance(boss.get("object_id"), str) and boss["object_id"], "PART-01 boss identity missing")
    _need(isinstance(player.get("object_id"), str) and player["object_id"] and player["object_id"] != boss["object_id"], "PART-01 player identity missing or aliases boss")
    _need(boss.get("slot") == "Boss" and player.get("slot") == "Player", "PART-01 participant slots incorrect")
    generation = boss.get("generation")
    _need(isinstance(generation, int) and not isinstance(generation, bool) and generation > 0 and player.get("generation") == generation,
          "PART-01 requires one shared positive generation")

    current = _finite_number(fw.get("health_current"), "health_current")
    maximum = _finite_number(fw.get("health_max"), "health_max")
    displayed = _finite_number(fw.get("hud_health_fraction"), "hud_health_fraction")
    _need(maximum > 0 and 0 <= current <= maximum, "HUD-01 native health out of bounds")
    _need(fw.get("active") is True and isinstance(fw.get("phase"), str) and fw["phase"], "HUD-01 boss must be active with a phase")
    _need(fw.get("hud_owner_object_id") == boss["object_id"] and 0 <= displayed <= 1, "HUD-01 bound owner/fraction invalid")
    _need(abs(displayed - current / maximum) <= 0.01, "HUD-01 displayed fraction disagrees with native health")

    _need(fw.get("terminal_callback_actor") == boss["object_id"] and fw.get("terminal_callback_generation") == generation,
          "TERM-01 terminal callback actor/generation mismatch")
    _need(fw.get("completed") is True and _count_is(fw.get("victory_count"), 1), "TERM-01 requires one completion and one victory")
    configured_delay = _finite_number(fw.get("retry_configured_delay_seconds"), "retry_configured_delay_seconds")
    measured_delay = _finite_number(fw.get("retry_measured_delay_seconds"), "retry_measured_delay_seconds")
    _need(configured_delay >= 0 and measured_delay >= 0 and fw.get("retry_visible") is True, "RETRY-01 retry state/delay invalid")
    _need(abs(configured_delay - measured_delay) <= 0.05, "RETRY-01 measured delay differs by more than 0.05s")

    reset = fw.get("reset", {})
    _need(_count_is(reset.get("count"), 1) and isinstance(reset.get("generation"), int) and not isinstance(reset.get("generation"), bool) and reset["generation"] > generation,
          "RESET-01 requires one reset and generation advancement")
    _need(reset.get("prior_generation_callback_refused") is True and isinstance(reset.get("prior_generation_refusal"), str) and reset["prior_generation_refusal"],
          "RESET-01 prior-generation callback refusal missing")
    replacement = fw.get("replacement_actor", {})
    _need(isinstance(replacement.get("object_id"), str) and replacement["object_id"] != boss["object_id"], "REPLACE-01 replacement actor identity invalid")
    _need(replacement.get("callback_refused") is True and isinstance(replacement.get("refusal"), str) and replacement["refusal"],
          "REPLACE-01 replacement callback refusal missing")

    for row in ROWS:
        _evidence(data, row)
    return {"schema_version": 1, "result": "PASS", "rows": [{"id": row, "result": "PASS", "evidence_count": len(_evidence(data, row))} for row in ROWS],
            "build_id": data["build_id"], "map": data["map"], "live_run_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.receipt.read_text(encoding="utf-8"))
        result = validate(data)
    except (OSError, json.JSONDecodeError, ReceiptError) as error:
        result = {"schema_version": 1, "result": "FAIL", "error": str(error), "live_run_verified": False}
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
