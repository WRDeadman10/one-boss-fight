#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
generate_not_yet_census.py

Generates the exhaustive Track B NOT YET Census Report (Reviews/NOT_YET_CENSUS.md)
by extracting exact IDs, titles, and observables from witness_status_v3.json.
Classifies all 24 NOT YET requirements by Dependency Class, Code Reference, and Engine Cost.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
JSON_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"
OUTPUT_MD = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/NOT_YET_CENSUS.md"

CENSUS_METADATA = {
    "BOSS-AWR-006": {
        "dep_class": "PLAYER-SIDE",
        "reason": "Player flask/heavy commitment state listener not exposed to boss perception (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:180)",
        "cost": "M"
    },
    "BOSS-AWR-007": {
        "dep_class": "NEEDS NEW SYSTEM",
        "reason": "Line-of-sight raycast filter and obstacle memory search state missing in candidate selection (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:45)",
        "cost": "L"
    },
    "BOSS-AWR-008": {
        "dep_class": "NEEDS NEW SYSTEM",
        "reason": "Recent player movement buffer and roll-catch adaptation weights not tracked in context (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:30)",
        "cost": "L"
    },
    "BOSS-SEL-009": {
        "dep_class": "ENGINE-ONLY",
        "reason": "AI reaction delay window [0.2-0.4s] before responding to player actions not wired in selector tick (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:165)",
        "cost": "M"
    },
    "BOSS-EXE-005": {
        "dep_class": "ENGINE-ONLY",
        "reason": "Phase threshold crossing priority over active stagger only exists in unit tests (Source/OneBossFight/Tests/RPGBossTransitionTests.cpp:25)",
        "cost": "M"
    },
    "BOSS-ANM-003": {
        "dep_class": "NEEDS ART",
        "reason": "Dynamic hold duration limits and release audio/visual notifies require authored animation notify tracks (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:120)",
        "cost": "L"
    },
    "BOSS-ANM-006": {
        "dep_class": "NEEDS NEW SYSTEM",
        "reason": "Motion Warping plugin integration and translation/rotation clamping not enabled in runtime (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:140)",
        "cost": "L"
    },
    "BOSS-HIT-010": {
        "dep_class": "NEEDS DESIGN DECISION",
        "reason": "Simultaneous direct weapon and secondary splash precedence arbiter not defined in damage resolver (Source/OneBossFight/Damage/RPGDamageResolver.cpp:130)",
        "cost": "M"
    },
    "BOSS-HIT-011": {
        "dep_class": "NEEDS NEW SYSTEM",
        "reason": "Outward expanding ring/annulus sweep shape component not implemented in move executor (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:190)",
        "cost": "L"
    },
    "BOSS-HIT-012": {
        "dep_class": "NEEDS NEW SYSTEM",
        "reason": "Two-character grab state machine and interrupt victim release handler not implemented (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:220)",
        "cost": "L"
    },
    "BOSS-MOV-002": {
        "dep_class": "NEEDS DESIGN DECISION",
        "reason": "Center-arena bias wall-clearance scoring when player hugs perimeter not implemented (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:200)",
        "cost": "M"
    },
    "BOSS-MOV-003": {
        "dep_class": "ENGINE-ONLY",
        "reason": "Continuous movement commitment hysteresis / direction latching across frames not implemented (Source/OneBossFight/Player/RPGBossTrackRules.h:35)",
        "cost": "S"
    },
    "BOSS-MOV-004": {
        "dep_class": "NEEDS ART",
        "reason": "Attack trajectory clamping against arena geometry bounds requires collision channel authoring (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:150)",
        "cost": "M"
    },
    "BOSS-MOV-005": {
        "dep_class": "ENGINE-ONLY",
        "reason": "Leashing to arena center when player exits arena bounds not wired (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:185)",
        "cost": "S"
    },
    "BOSS-MOV-006": {
        "dep_class": "NEEDS ART",
        "reason": "Production level L_SevarogArena geometry clearance and snag point audit requires level art verification (Source/OneBossFight/Tests/RPGAutomationTests.cpp:210)",
        "cost": "M"
    },
    "BOSS-PAC-002": {
        "dep_class": "NEEDS DESIGN DECISION",
        "reason": "Deliberate tempo pause nodes in combo sequences not authored in profile combo graph (Source/OneBossFight/Player/RPGBossComboRules.h:45)",
        "cost": "S"
    },
    "BOSS-PAC-003": {
        "dep_class": "PLAYER-SIDE",
        "reason": "Finisher recovery opening window validation against player counter-attack loop requires player attack intake (Source/OneBossFight/Player/RPGBossRules.h:60)",
        "cost": "M"
    },
    "BOSS-PAC-004": {
        "dep_class": "NEEDS ART",
        "reason": "Vulnerability visual/audio cues (e.g. weapon lodged in ground) require animation assets and notifies (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:135)",
        "cost": "L"
    },
    "BOSS-PAC-005": {
        "dep_class": "PLAYER-SIDE",
        "reason": "Mathematical verification that recovery duration exceeds player startup + travel time by >= 0.3s requires player moveset timings (Source/OneBossFight/Player/RPGBossRules.h:80)",
        "cost": "M"
    },
    "BOSS-DEF-004": {
        "dep_class": "ENGINE-ONLY",
        "reason": "Move card hyperarmor tag checking during active hit windows not wired into damage receiver (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:330)",
        "cost": "S"
    },
    "BOSS-DEF-005": {
        "dep_class": "NEEDS ART",
        "reason": "Boss defensive actions (backstep, block animations) not authored in boss profile moveset (Source/OneBossFight/Player/RPGBossFrameworkProfile.h:40)",
        "cost": "M"
    },
    "BOSS-PHS-005": {
        "dep_class": "NEEDS DESIGN DECISION",
        "reason": "Player extreme kiting/hugging distance thresholds and anti-cheese trigger rules not defined (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:55)",
        "cost": "M"
    },
    "BOSS-QA-006": {
        "dep_class": "PLAYER-SIDE",
        "reason": "Combat camera framing evaluation requires player follow camera / lock-on system testing (Source/OneBossFight/Player/RPGFrameworkCharacter.cpp:50)",
        "cost": "M"
    },
    "BOSS-QA-007": {
        "dep_class": "NEEDS ART",
        "reason": "Low VFX and audio-only/visual-only accessibility contrast test harness requires multi-channel asset audit (Source/OneBossFight/Tests/RPGAutomationTests.cpp:240)",
        "cost": "L"
    }
}

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    not_yet_reqs = [r for r in data["requirements"] if r["status"] == "NOT YET"]
    assert len(not_yet_reqs) == 24, f"Expected exactly 24 NOT YET requirements, found {len(not_yet_reqs)}"

    lines_md = []
    lines_md.append("# Track B Remaining Requirements Census: 24 NOT YET Rows\n")
    lines_md.append("**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  ")
    lines_md.append("**Task Reference:** `[C-565]` (Track B Direction Selection Census)  ")
    lines_md.append("**Source Authority:** `witness_status_v3.json` (exact titles and observables)  ")
    lines_md.append("**Total Census:** 24 requirements currently classified as `NOT YET`  \n")
    lines_md.append("---\n")
    lines_md.append("## 1. Executive Summary & Classification Matrix\n")
    lines_md.append("This document classifies all 24 remaining `NOT YET` combat requirements to inform the Owner's strategic roadmap choice across **Direction A** (Framework completion to full duel), **Direction B** (Track B soulslike boss framework polish), and **Direction C** (Pack-level authoring & Greystone integration).\n")
    lines_md.append("### Classification Definitions:")
    lines_md.append("- **ENGINE-ONLY:** Pure C++ / runtime rules or hooks; no art or external system dependencies.")
    lines_md.append("- **NEEDS ART:** Requires animations, montages, notify tracks, VFX/SFX, or arena mesh assets.")
    lines_md.append("- **NEEDS DESIGN DECISION:** Requires designer threshold parameters, precedence rules, or pacing formulas.")
    lines_md.append("- **NEEDS NEW SYSTEM:** Requires an entire unbuilt architectural subsystem (AoE sweeps, memory buffers, grab state machines).")
    lines_md.append("- **PLAYER-SIDE:** Depends on player character combat mechanics, input buffers, or counter-attack intake.\n")
    lines_md.append("### Cost Estimate Scale (in Engine Witness Runs):")
    lines_md.append("- **S (Small):** 1-2 runs; a simple log line, query param, or cvar test hook.")
    lines_md.append("- **M (Medium):** 2-4 runs; a new rule struct/method, unit tests, and live PIE proof scenario.")
    lines_md.append("- **L (Large):** 4+ runs; new multi-component system, asset plumbing, and multi-actor interaction harness.\n")
    lines_md.append("---\n")
    lines_md.append("## 2. Complete 24-Row NOT YET Census Table\n")
    lines_md.append("| ID | Exact Title | Exact Observable | Dependency Class | Code Reference & Reason | Cost |")
    lines_md.append("|:---|:---|:---|:---:|:---|:---:|")

    print(f"=== TRACK B NOT YET CENSUS ({len(not_yet_reqs)} ROWS) ===")
    print(f"{'ID':<14} | {'Title':<28} | {'Dep Class':<22} | {'Cost':<4} | Reason")
    print("-" * 100)

    for r in not_yet_reqs:
        rid = r["id"]
        title = r["title"]
        obs = r["observable"]
        meta = CENSUS_METADATA.get(rid)
        assert meta is not None, f"Missing metadata for {rid}"
        dep = meta["dep_class"]
        reason = meta["reason"]
        cost = meta["cost"]

        # Markdown row (escape pipes in observable if any)
        obs_escaped = obs.replace("|", "\\|")
        lines_md.append(f"| **{rid}** | {title} | {obs_escaped} | `{dep}` | {reason} | **{cost}** |")

        print(f"{rid:<14} | {title:<28} | {dep:<22} | {cost:<4} | {reason}")

    lines_md.append("\n---\n")
    lines_md.append("## 3. Census Distribution Breakdown\n")
    
    # Calculate distributions
    dep_counts = {}
    cost_counts = {}
    for meta in CENSUS_METADATA.values():
        dep_counts[meta["dep_class"]] = dep_counts.get(meta["dep_class"], 0) + 1
        cost_counts[meta["cost"]] = cost_counts.get(meta["cost"], 0) + 1

    lines_md.append("### By Dependency Class:")
    for dep, count in sorted(dep_counts.items(), key=lambda x: -x[1]):
        lines_md.append(f"- **{dep}:** {count} requirements ({count/24*100:.1f}%)")

    lines_md.append("\n### By Engine Run Cost:")
    for cost, count in sorted(cost_counts.items(), key=lambda x: -x[1]):
        lines_md.append(f"- **Cost {cost}:** {count} requirements ({count/24*100:.1f}%)")

    # Write output markdown with pure LF
    content_str = "\n".join(lines_md) + "\n"
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(content_str)

    print("-" * 100)
    print(f"Successfully generated {OUTPUT_MD} with pure LF (24 rows).")

if __name__ == "__main__":
    main()
