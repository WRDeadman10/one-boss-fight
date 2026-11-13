"""BQ-54 (Queue BQ batch 11; B15): F4b checklist automation, static.

TASKS.md F4b lists the live checks still owed: dodge i-frame rejection in PIE, dead-target / stale-generation cases,
block/parry, selector, combo graph, phases and Greystone visuals. This library maps each item to the native automation
tests and the PIE drivers that already exist for it, and verifies (statically) that every mapped test name is still
registered in Source/OneBossFight/Tests and every driver file still exists. It reports a gap when an item has no native
test or no driver. It never runs a test, driver or engine; the live run of each item stays ENG.

Library only: ``evaluate(root) -> list[dict]`` and ``summary(rows) -> dict``. No CLI, no file writes.
"""
from __future__ import annotations

import re
from pathlib import Path

# id, F4b wording, native test name strings, PIE driver paths (relative to the repo root), remaining live gate.
F4B_ITEMS = (
    {"id": "F4b-1", "item": "dodge i-frame rejection in PIE",
     "native": ["OneBossFight.Combat.DamageResolver.Decide", "OneBossFight.Dodge.DecisionSeams"],
     "drivers": ["Scripts/Editor/pie_iframes.py", "Scripts/Editor/pie_er_default_wiring_dodge.py"],
     "gate": "ENG: PIE contact during i-frames logs RejectedInvulnerable and leaves the hit unspent"},
    {"id": "F4b-2", "item": "dead-target / stale-generation cases",
     "native": ["OneBossFight.Combat.DamageResolver.Decide", "OneBossFight.Framework.MoveModel.GenerationAndDoubleStart",
                "OneBossFight.Binding.EncounterSelection.RebindRefusesDeadBoss"],
     "drivers": ["Scripts/Editor/pie_phase_reset.py"],
     "gate": "ENG: a hit after death / after a reset logs RejectedDead / RejectedStale in PIE"},
    {"id": "F4b-3", "item": "block/parry",
     "native": ["OneBossFight.Framework.BlockChip.Rules", "OneBossFight.Framework.BossParryFair.Rules",
                "OneBossFight.Framework.Combo.ParriedSample"],
     "drivers": ["Scripts/Editor/pie_tier2_parry.py", "Scripts/Editor/pie_er_block_probe.py"],
     "gate": "ENG: live parry contact and block on the default player; Greystone pawn not covered by these drivers"},
    {"id": "F4b-4", "item": "selector",
     "native": ["OneBossFight.Framework.MoveModel.Eligibility", "OneBossFight.Framework.EncounterLoop.PureSelectorModelRestart"],
     "drivers": ["Scripts/Editor/pie_selector_viewport.py"],
     "gate": "ENG: live selection trace on the data route"},
    {"id": "F4b-5", "item": "combo graph",
     "native": ["OneBossFight.Framework.Combo.EdgeMutationReachability", "OneBossFight.Framework.Combo.FallbackAfterModelRefusal"],
     "drivers": ["Scripts/Editor/pie_close_combo_watch.py"],
     "gate": "ENG: live combo edge taken (S4 to S5 boundary, BQ-37/39)"},
    {"id": "F4b-6", "item": "phases",
     "native": ["OneBossFight.Binding.PhaseFlow.Validation", "OneBossFight.Binding.PhasesCluster.Oracle"],
     "drivers": ["Scripts/Editor/pie_boss_phase_two.py"],
     "gate": "ENG: done for X26 P1/P2 (R4); keep as regression"},
    {"id": "F4b-7", "item": "Greystone visuals",
     "native": [],
     "drivers": ["Scripts/Editor/verify_greystone_wrapper_readback.py", "Scripts/Editor/verify_greystone_saved_wrapper_notifies.py"],
     "gate": "ART/OWN: visual review by the owner; no native test can judge looks"},
)

_NAME = re.compile(r'"(OneBossFight\.[A-Za-z0-9_.]+)"')


def registered_test_names(root: Path) -> set[str]:
    """Every automation name string found in Source/OneBossFight/Tests/*.cpp."""
    names: set[str] = set()
    tests = root / "Source" / "OneBossFight" / "Tests"
    for path in sorted(tests.glob("*.cpp")) if tests.is_dir() else []:
        names.update(_NAME.findall(path.read_text(encoding="utf-8", errors="replace")))
    return names


def evaluate(root: Path, items=F4B_ITEMS) -> list[dict]:
    registered = registered_test_names(root)
    rows = []
    for item in items:
        native_missing = [n for n in item["native"] if n not in registered]
        driver_missing = [d for d in item["drivers"] if not (root / d).is_file()]
        gaps = []
        if not item["native"]:
            gaps.append("no native test mapped")
        if native_missing:
            gaps.append("native test name not registered: " + ", ".join(native_missing))
        if not item["drivers"]:
            gaps.append("no driver mapped")
        if driver_missing:
            gaps.append("driver file missing: " + ", ".join(driver_missing))
        rows.append({"id": item["id"], "item": item["item"], "status": "static-ok" if not gaps else "gap",
                     "gaps": gaps, "gate": item["gate"]})
    return rows


def summary(rows: list[dict]) -> dict:
    return {"items": len(rows), "static_ok": sum(r["status"] == "static-ok" for r in rows),
            "gaps": [r["id"] for r in rows if r["status"] == "gap"], "live_verified": 0}
