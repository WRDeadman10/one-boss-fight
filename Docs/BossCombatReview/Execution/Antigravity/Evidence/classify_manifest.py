"""
classify_manifest.py - Deterministic Classifier for Boss01 Field-Source Manifest (Rev 03)

Reads Docs/BossCombatReview/Execution/Codex/WP13_BOSS01_FIELD_MANIFEST.csv
Classifies the 267 named configurable fields into ART_TIED, PURE_TUNING, or ENGINE_INVARIANT.
Marks the 1,267 generic procedural code lines as NOT_A_FIELD.
Assigns explicit RuleId for every row with complete traceability.

Zero external dependencies (Python standard library only). Compatible with 'python -I'.
Self-test suite (--self-test) includes 7 rejection/validation cases.
"""

import sys
import os
import csv
import re
from pathlib import Path

# Generic code line roles that are not configurable fields (Codex X-135, Claude C-146)
GENERIC_CODE_ROLES = {
    "IMPLEMENTATION_LITERAL",
    "PRIVATE_STATE_SEED_OR_CONSTANT",
    "DIAGNOSTIC_OR_TEXT"
}

# --- RULE DEFINITIONS & REGEX PATTERNS ---

RULES_ART = [
    ("RULE-ART-01-MONTAGE", re.compile(r"montage|animsequence|animmontage|blendspace|playabilitymontage|clippath", re.I),
     "References animation montage/sequence/clip requiring skeletal mesh tracks"),
    ("RULE-ART-02-NOTIFY-TIMING", re.compile(r"committime|activestarttime|activeendtime|recoverytime|recoveryendtime|ans_combatwindow|notify|crossing|activebegin|activeend", re.I),
     "Pinned timing scalar tied to FBX keyframes / anim notify curves"),
    ("RULE-ART-03-SOCKET-BONE", re.compile(r"socket|bone|joint|hand_r|weapon_start|weapon_end|bladeend|chestsocket|rootsocket", re.I),
     "Physical mesh attachment point or skeletal bone transform"),
    ("RULE-ART-04-VFX-NIAGARA", re.compile(r"niagara|particle|cascade|ns_|ps_|ribbon|emitter|trail", re.I),
     "Visual effect emitter anchored to weapon geometry or floor sweeps"),
    ("RULE-ART-05-TELEGRAPH-PACING", re.compile(r"closetelegraph|telegraph|pacing|lead|ratescale", re.I),
     "Playback rate dilation or wind-up duration scaling"),
    ("RULE-ART-06-LIFECYCLE-CLIP", re.compile(r"wakeclip|dormant|stagger|riposte|death|roartime", re.I),
     "Boss lifecycle state duration tied to specific animation sequences"),
    ("RULE-ART-07-HIT-GEOMETRY", re.compile(r"halfheight|capsuleradius|sweepradius|boxextent", re.I),
     "Physical geometric collision envelope that must match 3D weapon meshes")
]

RULES_NUM = [
    ("RULE-NUM-01-HEALTH", re.compile(r"maxhealth|attribute\.health|\bhealth\b|\bhp\b", re.I),
     "Vitality points pool; pure balancing scalar"),
    ("RULE-NUM-02-POSTURE-POISE", re.compile(r"posture|maxposture|postureregenrate|postureregendelay|poise", re.I),
     "Posture and poise balance thresholds"),
    ("RULE-NUM-03-DAMAGE", re.compile(r"damage|basedamage|shockwavedamage|criticalmultiplier|damagege|multiplier", re.I),
     "Health subtraction value or scaling multiplier"),
    ("RULE-NUM-04-PHASE-TRIGGER", re.compile(r"healththreshold|phase2threshold|phasethreshold", re.I),
     "HP percentage threshold triggering phase transition"),
    ("RULE-NUM-05-SPATIAL-RADII", re.compile(r"gateradius|arenaradius|activationdistance|maxblockingdistance|minrange|maxrange", re.I),
     "World-space distances and activation boundaries"),
    ("RULE-NUM-06-SPEED-TRAJECTORY", re.compile(r"projectilespeed|flightspeed|movementspeed|rotationspeed|turnrate", re.I),
     "Movement and projectile translation velocities"),
    ("RULE-NUM-07-COOLDOWNS", re.compile(r"cooldown|retrytimer|timeout|interval", re.I),
     "Behavioral cooldowns and decision intervals")
]

RULES_ENG = [
    ("RULE-ENG-01-TICK-LIFECYCLE", re.compile(r"bcanevertick|primarycomponenttick|registercomponent|beginplay|endplay|tickgroup", re.I),
     "Unreal Engine component lifecycle & tick configuration"),
    ("RULE-ENG-02-LOGGING", re.compile(r"ue_log|logrpg|display|warning|fatal", re.I),
     "Engine console and diagnostic logging statements"),
    ("RULE-ENG-03-SUBSYSTEM-SESSION", re.compile(r"subsystem|sessionid|generation|context|registry", re.I),
     "Project C++ architecture and session management"),
    ("RULE-ENG-04-SERIALIZED-EXPORT", re.compile(r"SERIALIZED_EXPORT_NOT_RUNTIME", re.I),
     "Static T3D/CDO text representation of serialized pack assets"),
    ("RULE-ENG-05-REFLECTION-BOILERPLATE", re.compile(r"staticclass|generated_body|uproperty|ufunction|cdo|include|namespace", re.I),
     "C++ reflection boilerplate, macros, and includes")
]

VALID_VALUE_KINDS = {
    "CODE_EXPRESSION", "CXX_PROPERTY_DEFAULT", "ASSET_REFERENCE_DEFAULT",
    "SERIALIZED_EXPORT_NOT_RUNTIME", "PR2_EXPORT_NOT_RUNTIME", "PR3_EXPORT_NOT_RUNTIME"
}


def classify_record(row):
    """
    Classifies a single record dict from the manifest.
    Returns: (category, rule_id, rule_rationale)
    Raises ValueError on validation failures.
    """
    record_id = row.get("RecordId", "").strip()
    source = row.get("Source", "").strip()
    val_kind = row.get("ValueKind", "").strip()
    field_role = row.get("FieldOrRole", "").strip()
    val_expr = row.get("ValueExpression", "").strip()
    def_field = row.get("DefinitionField", "").strip()
    obj_fn = row.get("ObjectOrFunction", "").strip()

    if not record_id:
        raise ValueError("Empty RecordId")
    if not source:
        raise ValueError(f"Record {record_id} has no Source")
    if val_kind not in VALID_VALUE_KINDS:
        raise ValueError(f"Record {record_id} has unknown ValueKind: '{val_kind}'")

    combined_text = f"{field_role} {def_field} {val_expr} {obj_fn}"

    # 0. Check for generic procedural code lines / diagnostics (not configurable fields, per Codex X-135 / Claude C-146)
    if val_kind != "SERIALIZED_EXPORT_NOT_RUNTIME" and field_role in GENERIC_CODE_ROLES:
        return "NOT_A_FIELD", "RULE-GENERIC-CODE-LINE", "Generic procedural C++ code expression, state seed, or diagnostic literal (not a configurable field)"

    # Check Art-Tied Rules First
    for rule_id, pattern, desc in RULES_ART:
        if pattern.search(combined_text):
            return "ART_TIED", rule_id, desc

    # Check Pure Tuning Numbers Second
    for rule_id, pattern, desc in RULES_NUM:
        if pattern.search(combined_text):
            return "PURE_TUNING", rule_id, desc

    # Check Engine Invariant Rules Third
    if val_kind == "SERIALIZED_EXPORT_NOT_RUNTIME":
        return "ENGINE_INVARIANT", "RULE-ENG-04-SERIALIZED-EXPORT", "Static T3D/CDO text representation of serialized pack assets"

    for rule_id, pattern, desc in RULES_ENG:
        if pattern.search(combined_text):
            return "ENGINE_INVARIANT", rule_id, desc

    # Default Engine Invariant Fallback
    return "ENGINE_INVARIANT", "RULE-ENG-05-SYSTEM-FALLBACK", "General C++ code expression, invariant seed, or system diagnostic"


def run_self_test():
    """Executes the validation test suite with at least 5 rejection cases."""
    print("Running classify_manifest.py self-test suite...")
    tests_passed = 0
    total_tests = 7

    # Test 1: Unknown ValueKind rejection
    try:
        classify_record({"RecordId": "T01", "Source": "Test.cpp", "ValueKind": "BOGUS_KIND"})
        print("FAIL: Test 1 (Unknown ValueKind) did not raise ValueError")
    except ValueError as e:
        assert "unknown ValueKind" in str(e)
        tests_passed += 1

    # Test 2: Empty RecordId rejection
    try:
        classify_record({"RecordId": "", "Source": "Test.cpp", "ValueKind": "CODE_EXPRESSION"})
        print("FAIL: Test 2 (Empty RecordId) did not raise ValueError")
    except ValueError as e:
        assert "Empty RecordId" in str(e)
        tests_passed += 1

    # Test 3: Missing Source rejection
    try:
        classify_record({"RecordId": "T03", "Source": "", "ValueKind": "CODE_EXPRESSION"})
        print("FAIL: Test 3 (Missing Source) did not raise ValueError")
    except ValueError as e:
        assert "has no Source" in str(e)
        tests_passed += 1

    # Test 4: Art rule match (Montage) on named field
    cat, rule, desc = classify_record({
        "RecordId": "T04", "Source": "Test.cpp", "ValueKind": "CODE_EXPRESSION",
        "FieldOrRole": "MOVE_TIMING_FIELD", "ValueExpression": "A2.MontageName = 'GS_ChargedAttack_Montage'"
    })
    assert cat == "ART_TIED" and rule == "RULE-ART-01-MONTAGE"
    tests_passed += 1

    # Test 5: Number rule match (Health) on named field
    cat, rule, desc = classify_record({
        "RecordId": "T05", "Source": "Test.cpp", "ValueKind": "CXX_PROPERTY_DEFAULT",
        "FieldOrRole": "PROPERTY", "ValueExpression": "Def->Stats.MaxHealth = 2000.f;"
    })
    assert cat == "PURE_TUNING" and rule == "RULE-NUM-01-HEALTH"
    tests_passed += 1

    # Test 6: Engine Invariant match (Tick) on named field
    cat, rule, desc = classify_record({
        "RecordId": "T06", "Source": "Test.cpp", "ValueKind": "CODE_EXPRESSION",
        "FieldOrRole": "SCHEDULING_CONSTANT", "ValueExpression": "PrimaryComponentTick.bCanEverTick = true;"
    })
    assert cat == "ENGINE_INVARIANT" and rule == "RULE-ENG-01-TICK-LIFECYCLE"
    tests_passed += 1

    # Test 7: Generic code line rejection (NOT_A_FIELD)
    cat, rule, desc = classify_record({
        "RecordId": "T07", "Source": "RPGBossDeath.cpp", "ValueKind": "CODE_EXPRESSION",
        "FieldOrRole": "IMPLEMENTATION_LITERAL", "ValueExpression": "LastPackResult = TEXT(\"already set\");"
    })
    assert cat == "NOT_A_FIELD" and rule == "RULE-GENERIC-CODE-LINE"
    tests_passed += 1

    print(f"Self-test results: {tests_passed}/{total_tests} PASSED.")
    return tests_passed == total_tests


def classify_file(input_csv, output_csv=None):
    """Processes the manifest CSV, writes classified CSV, and prints stratified reports."""
    seen_ids = set()
    records = []
    counts_full = {"ART_TIED": 0, "PURE_TUNING": 0, "ENGINE_INVARIANT": 0, "NOT_A_FIELD": 0}
    counts_named = {"ART_TIED": 0, "PURE_TUNING": 0, "ENGINE_INVARIANT": 0}
    counts_generic = 0
    rules_fired = {}

    samples = {"ART_TIED": [], "PURE_TUNING": [], "ENGINE_INVARIANT": []}

    with open(input_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec_id = row["RecordId"]
            if rec_id in seen_ids:
                raise ValueError(f"Duplicate RecordId detected: {rec_id}")
            seen_ids.add(rec_id)

            cat, rule_id, desc = classify_record(row)
            row["Classification"] = cat
            row["RuleId"] = rule_id
            row["RuleRationale"] = desc

            counts_full[cat] += 1
            rules_fired[rule_id] = rules_fired.get(rule_id, 0) + 1

            is_export = (row["ValueKind"] == "SERIALIZED_EXPORT_NOT_RUNTIME")
            if not is_export:
                if cat == "NOT_A_FIELD":
                    counts_generic += 1
                else:
                    counts_named[cat] += 1
                    # Draw stratified sample strictly from named fields
                    if len(samples[cat]) < 30:
                        samples[cat].append((rec_id, row["Source"], row["Line"], row["ValueExpression"][:70], rule_id))

            records.append(row)

    if output_csv:
        fieldnames = reader.fieldnames + ["Classification", "RuleId", "RuleRationale"]
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    total_full = len(records)
    total_named = sum(counts_named.values())

    print("\n=======================================================")
    print(f"POPULATION 1: FULL MANIFEST ({total_full} Records)")
    print("=======================================================")
    for k, v in counts_full.items():
        pct = (v / total_full) * 100.0
        print(f"  {k:<18}: {v:>5} ({pct:>5.1f}%)")

    print("\n=======================================================")
    print(f"POPULATION 2: NAMED CONFIGURABLE FIELDS ({total_named} Records)")
    print("=======================================================")
    for k, v in counts_named.items():
        pct = (v / total_named) * 100.0
        print(f"  {k:<18}: {v:>5} ({pct:>5.1f}%)")

    print("\n=======================================================")
    print(f"POPULATION 3: GENERIC PROCEDURAL CODE LINES ({counts_generic} Records)")
    print("=======================================================")
    print(f"  NOT_A_FIELD       : {counts_generic:>5} (100.0%)")

    print("\n=======================================================")
    print("RULES FIRED BREAKDOWN (Top 15 Rules)")
    print("=======================================================")
    for r, c in sorted(rules_fired.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {r:<30}: {c:>5}")

    return counts_full, counts_named, samples


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        ok = run_self_test()
        sys.exit(0 if ok else 1)

    input_file = Path("Docs/BossCombatReview/Execution/Codex/WP13_BOSS01_FIELD_MANIFEST.csv")
    output_file = Path("Docs/BossCombatReview/Execution/Antigravity/Evidence/WP13_CLASSIFIED_MANIFEST.csv")

    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    counts_full, counts_non_export, samples = classify_file(input_file, output_file)
