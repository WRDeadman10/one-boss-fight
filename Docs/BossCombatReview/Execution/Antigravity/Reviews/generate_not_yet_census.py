#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
generate_not_yet_census.py

Generates the exhaustive Track B NOT YET Census Report (Reviews/NOT_YET_CENSUS.md)
by extracting exact IDs, titles, and observables from witness_status_v3.json.
Classifies all 24 NOT YET requirements by Dependency Class, Code Reference, and Engine Cost.
Enforces strict disk citation verification: fails if cited file does not exist, line is past EOF,
or quoted string is not present in that exact line. Unimplemented items use 'no code: <what is missing>'.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
JSON_PATH = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json"
OUTPUT_MD = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews/NOT_YET_CENSUS.md"

VALID_DEP_CLASSES = {
    "ENGINE-ONLY",
    "NEEDS ART",
    "NEEDS DESIGN DECISION",
    "NEEDS NEW SYSTEM",
    "PLAYER-SIDE",
}

VALID_COSTS = {"S", "M", "L"}

CENSUS_METADATA = {
    "BOSS-AWR-006": {
        "dep_class": "PLAYER-SIDE",
        "cost": "M",
        "cite": None,
        "explanation": "no code: boss only reads target HP and transform; player activity tag listener and flask/heavy commitment observer not implemented in framework boss",
    },
    "BOSS-AWR-007": {
        "dep_class": "NEEDS NEW SYSTEM",
        "cost": "L",
        "cite": None,
        "explanation": "no code: line-of-sight raycasts and obstacle search memory not implemented in boss selector or perception",
    },
    "BOSS-AWR-008": {
        "dep_class": "NEEDS NEW SYSTEM",
        "cost": "L",
        "cite": None,
        "explanation": "no code: player movement history and dodge histogram tracking not implemented in AI context",
    },
    "BOSS-SEL-009": {
        "dep_class": "ENGINE-ONLY",
        "cost": "M",
        "cite": None,
        "explanation": "no code: AI reaction delay window [0.2-0.4s] buffering not implemented in boss tick loop",
    },
    "BOSS-EXE-005": {
        "dep_class": "ENGINE-ONLY",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Tests/RPGAutomationTests.cpp",
            "line": 226,
            "quote": 'TestEqual(TEXT("below the threshold during a break is queued',
        },
        "explanation": "legacy unit test asserts phase transition queues behind stagger; framework boss has no runtime phase threshold vs stagger priority arbitration wired",
    },
    "BOSS-ANM-003": {
        "dep_class": "NEEDS ART",
        "cost": "L",
        "cite": None,
        "explanation": "no code: variable windup hold min/max durations and release cues not authored in move cards or montage tracks",
    },
    "BOSS-ANM-006": {
        "dep_class": "NEEDS NEW SYSTEM",
        "cost": "L",
        "cite": None,
        "explanation": "no code: Motion Warping plugin not enabled in uproject and warp clamping bounds not implemented",
    },
    "BOSS-HIT-010": {
        "dep_class": "NEEDS DESIGN DECISION",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGDamageResolver.cpp",
            "line": 152,
            "quote": "Result.Outcome = RPGDamageRules::Decide(bTargetAlive, bAtta",
        },
        "explanation": "resolver decide rule only takes alive, generation, duplicate, and invulnerable flags; no direct vs secondary splash precedence arbiter defined",
    },
    "BOSS-HIT-011": {
        "dep_class": "NEEDS NEW SYSTEM",
        "cost": "L",
        "cite": {
            "file": "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp",
            "line": 201,
            "quote": "const FCollisionShape Shape=FCollisionShape::MakeCapsule(W.",
        },
        "explanation": "sweep only constructs linear swept capsules along weapon key poses; outward expanding ring/annulus component not implemented",
    },
    "BOSS-HIT-012": {
        "dep_class": "NEEDS NEW SYSTEM",
        "cost": "L",
        "cite": None,
        "explanation": "no code: grab state machine, victim attachment sync, and interrupt release fail-safe not implemented",
    },
    "BOSS-MOV-002": {
        "dep_class": "NEEDS DESIGN DECISION",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp",
            "line": 188,
            "quote": "// Opt-in repositioning: nobody is eligible from here (the ",
        },
        "explanation": "repositioning only walks straight toward target band without arena boundary or wall clearance scoring",
    },
    "BOSS-MOV-003": {
        "dep_class": "ENGINE-ONLY",
        "cost": "S",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGBossTrackRules.h",
            "line": 13,
            "quote": "if (bCommitted||!FMath::IsFinite(DegPerSecond)||!FMath::IsFi",
        },
        "explanation": "nearest code, not the feature: turn tracking turns shortest-way each tick without movement direction latching or continuous locomotion hysteresis",
    },
    "BOSS-MOV-004": {
        "dep_class": "NEEDS ART",
        "cost": "M",
        "cite": None,
        "explanation": "no code: forward charge attack animations with root motion require level art perimeter collision geometry and collision preset authoring to prevent clipping",
    },
    "BOSS-MOV-005": {
        "dep_class": "ENGINE-ONLY",
        "cost": "S",
        "cite": {
            "file": "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp",
            "line": 94,
            "quote": "if(P&&P->ArenaRadiusCm>0.f&&FVector::Dist2D(Target->GetActor",
        },
        "explanation": "target leaving ArenaRadiusCm triggers TargetFault OffArena which halts and fails the boss; active leashing back to arena center and neutral reset not implemented",
    },
    "BOSS-MOV-006": {
        "dep_class": "NEEDS ART",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Tests/RPGAutomationTests.cpp",
            "line": 766,
            "quote": 'IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGArenaCollisionTest, "On',
        },
        "explanation": "collision tests only verify legacy ARPGGreyboxArena geometry; production level L_SevarogArena clearance and snag point audit requires level art verification",
    },
    "BOSS-PAC-002": {
        "dep_class": "NEEDS DESIGN DECISION",
        "cost": "S",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGBossComboRules.h",
            "line": 12,
            "quote": "struct FComboEdge",
        },
        "explanation": "combo graph edges only specify target node, range, yaw, and outcome; no tempo pause delay or deliberate pacing duration field exists",
    },
    "BOSS-PAC-003": {
        "dep_class": "PLAYER-SIDE",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGBossMoveCard.h",
            "line": 60,
            "quote": "UPROPERTY(EditAnywhere) float RecoveryEndSeconds = 0.f;",
        },
        "explanation": "move card specifies static RecoveryEndSeconds; validation against player punish attack timings requires player moveset intake",
    },
    "BOSS-PAC-004": {
        "dep_class": "NEEDS ART",
        "cost": "L",
        "cite": None,
        "explanation": "no code: visual/audio recovery cues (e.g. scythe lodged in ground) require authored animation notify tracks and VFX",
    },
    "BOSS-PAC-005": {
        "dep_class": "PLAYER-SIDE",
        "cost": "M",
        "cite": None,
        "explanation": "no code: punish margin formula (recovery > player startup + travel + 0.3s) requires player moveset startup data",
    },
    "BOSS-DEF-004": {
        "dep_class": "ENGINE-ONLY",
        "cost": "S",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGWeaponAttackTable.h",
            "line": 44,
            "quote": "float HyperArmorStart = -1.f;",
        },
        "explanation": "nearest code, not the feature: hyperarmor window fields exist only for player attacks in RPGWeaponAttackTable; hyperarmor tags not implemented for boss move cards",
    },
    "BOSS-DEF-005": {
        "dep_class": "NEEDS ART",
        "cost": "M",
        "cite": None,
        "explanation": "no code: defensive moves (backstep, block) not authored in boss profile moveset or animation cards",
    },
    "BOSS-PHS-005": {
        "dep_class": "NEEDS DESIGN DECISION",
        "cost": "M",
        "cite": {
            "file": "Source/OneBossFight/Player/RPGBossMoveSelector.cpp",
            "line": 49,
            "quote": "if (Out.ChosenIndex==INDEX_NONE || T.Score>Out.Score) { Out.",
        },
        "explanation": "candidate evaluation selects solely by highest score among eligible cards; no anti-cheese override or exploit loop detector exists",
    },
    "BOSS-QA-006": {
        "dep_class": "PLAYER-SIDE",
        "cost": "M",
        "cite": None,
        "explanation": "no code: camera framing and lock-on tracking evaluation requires player follow camera / lock-on system testing",
    },
    "BOSS-QA-007": {
        "dep_class": "NEEDS ART",
        "cost": "L",
        "cite": None,
        "explanation": "no code: low VFX / audio-only / visual-only contrast testing harness not authored in project",
    },
}

def validate_census_metadata():
    """Validates every citation against disk and checks schema rules."""
    for rid, meta in CENSUS_METADATA.items():
        dep = meta["dep_class"]
        cost = meta["cost"]
        cite = meta["cite"]
        exp = meta["explanation"]

        assert dep in VALID_DEP_CLASSES, f"[{rid}] Invalid dep_class: {dep}"
        assert cost in VALID_COSTS, f"[{rid}] Invalid cost: {cost}"

        if cite is None:
            assert exp.startswith("no code: "), f"[{rid}] Missing 'no code: ' prefix: {exp}"
        else:
            file_rel = cite["file"]
            line_no = cite["line"]
            quote = cite["quote"]

            file_abs = REPO_ROOT / file_rel
            assert file_abs.exists(), f"[{rid}] Cited file does not exist: {file_rel}"

            with open(file_abs, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            assert 1 <= line_no <= len(lines), f"[{rid}] Line {line_no} past EOF ({len(lines)}) in {file_rel}"
            actual_line = lines[line_no - 1]
            assert quote in actual_line, f"[{rid}] Quote mismatch in {file_rel}:{line_no}\nExpected: {quote!r}\nActual:   {actual_line!r}"
            assert len(quote) <= 60, f"[{rid}] Quote exceeds 60 chars ({len(quote)}): {quote!r}"

def main():
    print("--- Validating Census Metadata Against Disk ---")
    validate_census_metadata()
    print("  [PASS] All citations and schemas verified on disk.")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    not_yet_reqs = [r for r in data["requirements"] if r["status"] == "NOT YET"]
    assert len(not_yet_reqs) == 24, f"Expected exactly 24 NOT YET requirements, found {len(not_yet_reqs)}"

    lines_md = []
    lines_md.append("# Track B Remaining Requirements Census: 24 NOT YET Rows\n")
    lines_md.append("**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  ")
    lines_md.append("**Task Reference:** `[C-565]` / `[C-568]` (Track B Direction Selection Census)  ")
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
    print(f"{'ID':<14} | {'Title':<28} | {'Dep Class':<22} | {'Cost':<4} | Details")
    print("-" * 110)

    for r in not_yet_reqs:
        rid = r["id"]
        title = r["title"]
        obs = r["observable"]
        meta = CENSUS_METADATA.get(rid)
        assert meta is not None, f"Missing metadata for {rid}"
        dep = meta["dep_class"]
        cost = meta["cost"]
        cite = meta["cite"]
        exp = meta["explanation"]

        if cite:
            f_rel = cite["file"]
            ln = cite["line"]
            q = cite["quote"]
            cell_detail = f"`{f_rel}:{ln}` quote: `{q}`<br>{exp}"
            summary_log = f"{f_rel}:{ln} quote: \"{q}\" — {exp}"
        else:
            cell_detail = exp
            summary_log = exp

        # Markdown row (escape pipes in observable if any)
        obs_escaped = obs.replace("|", "\\|")
        lines_md.append(f"| **{rid}** | {title} | {obs_escaped} | `{dep}` | {cell_detail} | **{cost}** |")

        print(f"{rid:<14} | {title:<28} | {dep:<22} | {cost:<4} | {summary_log[:70]}")

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

    print("-" * 110)
    print(f"Successfully generated {OUTPUT_MD} with pure LF (24 rows).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
