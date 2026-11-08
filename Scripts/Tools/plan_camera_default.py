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
    enabled = set(values)
    return {
        **base,
        "choice": normalized,
        "owner_decision_ref": decision_ref,
        "proposed_config": {
            "file": "Config/DefaultGame.ini",
            "applies_to": ["Development", "Shipping"],
            "section_proposal": "[/Script/OneBossFight.RPGCameraRig]",
            "keys_proposal": {
                "bDefaultHideBossInside": "true" if "HideBossInside" in enabled else "false",
                "bDefaultLockOnFraming": "true" if "LockOnFraming" in enabled else "false",
            },
            "runtime_type_proposal": "two bool UPROPERTY(Config) properties",
            "missing_or_invalid_fallback": "false/false (all behavior disabled)",
        },
        "runtime_plan": {
            "enabled_behaviors": list(values),
            "production_path": "move B/C behavior bodies outside !UE_BUILD_SHIPPING and enable only the selected config behavior",
            "development_diagnostics": "remain guarded by !UE_BUILD_SHIPPING",
            "development_cvars": "remain guarded test overrides and default off; do not become Shipping dependencies",
            "cvar_and_config_rule": "effective behavior is selected config behavior OR its Development-only test CVar",
        },
        "required_readback": [
            "effective bDefaultHideBossInside and bDefaultLockOnFraming in Development and Shipping",
            "false/false fallback when config keys are absent",
            "selected behavior and Development-only diagnostic symbols/logs in each staged build",
            "DATA-default packaged route behavior with same-run activation witness",
        ],
        "rollback_plan": [
            "restore bDefaultHideBossInside=false and bDefaultLockOnFraming=false in the shared default config",
            "keep Development-only experiments available only under their existing guard",
            "rebuild and repackage both configurations, then rerun the DATA-default smoke check",
        ],
        "gates": [
            "owner confirms the supplied reference is a real decision and the selected option matches its exact text",
            "native config/source contract and full native suite pass",
            "Lead builds both configurations and checks staged config/symbols/logs",
            "Lead packages and smoke-tests the DATA-default route with a same-run activation witness; KI-037/KI-066 coverage reviewed",
        ],
        "evidence_gap": "C-1090 and C-1105 cover bounded B+C attack/look cases; no owner choice, full KI-037/KI-066 coverage, Shipping proof, or package proof is implied",
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
