"""Emit a read-only plan for comparing the three phase-two aura choices.

This utility does not import Unreal, mutate an asset, edit a component, or save.
It prints the selected option's apply/readback checklist and rollback manifest as
JSON. A future runtime experiment still requires an explicit owner decision and
Lead-owned PIE validation.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


SOURCE_ASSET = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura"
BOOST_ASSET = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost.NS_Boss_PhaseTwoAura_Boost"
OPTIONS: dict[str, dict[str, Any]] = {
    "current": {
        "asset": SOURCE_ASSET,
        "attachment": {"component": "PhaseTwoAuraEffect", "socket": "NAME_None"},
        "description": "Approved current aura and current attachment behavior.",
    },
    "boosted": {
        "asset": BOOST_ASSET,
        "attachment": {"component": "PhaseTwoAuraEffect", "socket": "NAME_None"},
        "description": "Boost candidate at the current mesh-origin attachment.",
    },
    "boosted_on_spine": {
        "asset": BOOST_ASSET,
        "attachment": {"component": "PhaseTwoAuraEffect", "socket": "spine_03"},
        "description": "Boost candidate attached at spine_03 for the body-rising look.",
    },
}

REQUIRED_READBACK = (
    "asset object path and package identity",
    "source/candidate asset hashes and dirty state before and after",
    "Niagara system active state and emitter/module values",
    "component asset, attachment parent, socket, relative transform, and active state",
    "route, boss health fraction, camera identity, and capture run identity",
)


def build_plan(option: str) -> dict[str, Any]:
    if option not in OPTIONS:
        raise ValueError(f"unknown option: {option}")
    selected = OPTIONS[option]
    return {
        "schema": "aura-choice-plan-v1",
        "mode": "dry-run-only",
        "option": option,
        "description": selected["description"],
        "proposed_state": {
            "asset": selected["asset"],
            "attachment": dict(selected["attachment"]),
        },
        "readback_required": list(REQUIRED_READBACK),
        "apply_manifest": {
            "executed": False,
            "requires_owner_choice": True,
            "requires_complete_readback": True,
            "asset_save_permitted": False,
        },
        "rollback_manifest": {
            "source_state": "CAPTURE_REQUIRED_BEFORE_ANY_FUTURE_EXPERIMENT",
            "restore_asset": "recorded original component asset path",
            "restore_attachment": "recorded original parent/socket/relative transform",
            "restore_active_state": "recorded original active state",
            "verify_after_rollback": list(REQUIRED_READBACK),
            "asset_save_permitted": False,
        },
        "safety": "No Unreal API, asset mutation, component mutation, or save was performed.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--option", choices=sorted(OPTIONS), default="current")
    parser.add_argument("--apply", action="store_true", help="refused; this tool is dry-run only")
    parser.add_argument("--save", action="store_true", help="refused; this tool never saves assets")
    args = parser.parse_args(argv)
    if args.apply or args.save:
        parser.error("apply/save requests are refused; this utility only emits a dry-run plan")
    print(json.dumps(build_plan(args.option), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
