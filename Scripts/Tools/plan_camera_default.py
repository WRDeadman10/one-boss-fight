"""Print a no-write plan for a future, owner-authorized camera default."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


CHOICES = {
    "B": ("HideBossInside",),
    "C": ("LockOnFraming",),
    "BC": ("HideBossInside", "LockOnFraming"),
}


def build_plan(choice: str | None, owner_decision_ref: str | None) -> dict[str, Any]:
    normalized = (choice or "").strip().upper()
    decision_ref = (owner_decision_ref or "").strip()
    base: dict[str, Any] = {
        "schema": "onebossfight.camera-default-migration-plan/v1",
        "mode": "dry-run-only",
        "apply_available": False,
        "save_available": False,
        "status": "READY_FOR_REVIEW",
        "decision_reference_is_verified": False,
        "owner_approval_authenticated": False,
        "source_mutation": False,
        "config_mutation": False,
    }
    if not normalized:
        return {**base, "status": "WAITING_FOR_OWNER", "reason": "no camera option was supplied"}
    if normalized not in CHOICES:
        return {**base, "status": "INVALID_CHOICE", "reason": "choice must be B, C, or BC under the current owner brief"}
    if not decision_ref:
        return {**base, "status": "WAITING_FOR_OWNER", "reason": "a recorded owner decision reference is required"}

    values = CHOICES[normalized]
    return {
        **base,
        "choice": normalized,
        "owner_decision_ref": decision_ref,
        "proposed_config": {
            "file": "Config/DefaultGame.ini",
            "applies_to": ["Development", "Shipping"],
            "section_proposal": "[/Script/OneBossFight.RPGCameraSettings]",
            "key_proposal": "SelectedBehavior",
            "value_proposal": normalized,
            "missing_or_invalid_fallback": "None (all behavior disabled)",
        },
        "runtime_plan": {
            "enabled_behaviors": list(values),
            "production_path": "selected behavior must be available in both configurations",
            "development_diagnostics": "remain guarded by !UE_BUILD_SHIPPING",
            "development_cvars": "remain test controls and default off; do not become Shipping dependencies",
        },
        "required_readback": [
            "effective SelectedBehavior in Development and Shipping",
            "all-off fallback when config is missing or invalid",
            "selected behavior and diagnostic symbols/logs in each staged build",
            "packaged route behavior on legacy and selected-data routes",
        ],
        "rollback_plan": [
            "restore SelectedBehavior=None in the shared default config",
            "keep Development-only experiments available only under their existing guard",
            "rebuild and repackage both configurations, then rerun route smoke checks",
        ],
        "gates": [
            "owner confirms the supplied reference is a real decision and the selected option matches its exact text",
            "native config/source contract and full native suite pass",
            "Lead builds both configurations and checks staged config/symbols/logs",
            "Lead packages and smoke-tests both routes; KI-037/KI-066 coverage reviewed",
        ],
        "evidence_gap": "C-1090 covers one B+C attack-mode case only; no owner choice, broad matrix, Shipping proof, or package proof is implied",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choice", help="B, C, or BC from the current owner decision brief")
    parser.add_argument("--owner-decision-ref", help="reference to an already recorded owner decision")
    args = parser.parse_args(argv)
    result = build_plan(args.choice, args.owner_decision_ref)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "READY_FOR_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
