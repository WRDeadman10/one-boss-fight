#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
validate_framework_proof_logs.py (v3.20)

Formal schema and semantic validator for all [FrameworkProof] structured telemetry lines
emitted by the One Boss Fight Sevarog Combat Framework (F3d through F11, Track B, B_QA002, B_HIT005, B_AWR001, B_AWR002, B_EXE007, B_QA003B, B_EXE004, B_MOV005, B_EXE005, and B_MOV003).

Validates:
1. Header prefix (optional Unreal Engine standard log prefix: [YYYY.MM.DD-HH.MM.SS:mmm][frame]LogCategory: Verbosity:)
2. Exact [FrameworkProof] token tag
3. Registered schema match for all 65 recognized telemetry tokens
4. Semantic checks per log:
   - seq= (when present) is unique and strictly increasing per process log across decisions
   - candidate and refusal lines of a decision carry the exact same seq as their decision
   - attack= ids in decision lines:
     * With seq: unique decision identity is guaranteed by seq (repeated attack= after mid-attack abort is resolved)
     * Without seq (legacy logs): duplicate attack= is recorded as "legacy, no seq" finding
   - gate= ids in combo_gate are unique except the logged combo_gate_duplicate
   - instance= in playback_start is not reused inside one generation
   - UE timestamps (when present) never go backwards
5. Detailed diagnostics on any malformed, unregistered, or semantically irregular lines
"""

import sys
import re
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# Vector format pattern: X=<float> Y=<float> Z=<float>
VEC = r"X=[^\s]+ Y=[^\s]+ Z=[^\s]+"

# 59 Canonical FrameworkProof Schemas
SCHEMAS = {
    # 1. Encounter Lifecycle & Framework Fixture
    "dependencies": r"^mesh=[^\s]+ skeleton=[^\s]+ animClass=[^\s]+ sequence=[^\s]+ slot=[^\s]+ resolved=\d+ label=[^\s]+$",
    "slot_graph": r"^name=[^\s]+ nodeClass=[^\s]+ verified=\d+ label=[^\s]+$",
    "boss_health": r"^max=[^\s]+ playerHitDamage=[^\s]+ label=[^\s]+$",
    "boss_health_read": r"^reader=[^\s]+ ok=\d+ value=[^\s]+ max=[^\s]+$",
    "target_health_init": r"^value=[^\s]+ readback=[^\s]+ label=[^\s]+$",
    "target_health_mismatch": r"^valid=\d+ actual=[^\s]+ expected=[^\s]+ generation=\d+(?:\s+reason=[^\s]+)?$",
    "target_fault_injected": r"^kind=[^\s]+$",
    "pack_style_known": r"^waitedSeconds=[^\s]+$",
    "bystander_spawned": r"^ok=\d+ name=[^\s]+ x=[^\s]+ y=[^\s]+ z=[^\s]+$",
    "encounter_reset": r"^(?:generation=\d+ oldState=[^\s]+ executorRearmed=\d+ bossHealth=[^\s]+ targetHealth=[^\s]+|refused generation=\d+ reason=[^\s]+)$",
    "boss_dead": r"^generation=\d+ executorAborted=\d+$",
    "RESULT": r"^outcome=[^\s]+(?:\s+acceptedHits=\d+)?(?:\s+attacks=\d+)?$",
    "ERROR": r"^token=[^\s]+(?:\s+.*)?$",

    # 2. Navigation & Locomotion
    "nav_ready": r"^waitedSeconds=[^\s]+$",
    "nav_not_ready": r"^navSystem=\d+ buildInProgress=\d+ targetLocation=" + VEC + r"$",
    "nav": r"^request=\d+ projected=" + VEC + r" fullPath=\d+ result=\d+$",
    "walk": r"^start=" + VEC + r" end=" + VEC + r" distanceCm=[^\s]+ rangeCm=[^\s]+ bandMin=[^\s]+ bandMax=[^\s]+ capsule=" + VEC + r" mesh=" + VEC + r"$",
    "walk_resumed": r"^generation=\d+$",
    "reposition": r"^attempt=\d+ max=\d+ range=[^\s]+ reason=[^\s]+$",
    "reposition_turn": r"^start yawToTarget=[^\s]+ range=[^\s]+ ratePerSecond=[^\s]+$",
    "reposition_turn_end": r"^flips=\d+ latchDir=[^\s]+ seconds=[^\s]+$",
    "hyperarmor_absorbed": r"^card=[^\s]+ postureKept=[^\s]+ amountSkipped=[^\s]+$",
    "combo_pause": r"^seconds=[^\s]+ next=[^\s]+$",
    "combo_pause_end": r"^$",
    "walk_center_bias": r"^targetFromCenterCm=[^\s]+ thresholdCm=[^\s]+ bias=[^\s]+ near=[01] awayX=[^\s]+ awayY=[^\s]+ biasedX=[^\s]+ biasedY=[^\s]+$",
    "anticheese": r"^state=[^\s]+ streak=\d+ rangeCm=[^\s]+ thresholdCm=[^\s]+ seq=\d+$",
    "arena_leash": r"^(?:state=Start targetDistanceCm=[^\s]+ radiusCm=[^\s]+ centerX=[^\s]+ centerY=[^\s]+|state=AtCenter distanceCm=[^\s]+|state=Resume(?:\s+bossDistanceToCenterCm=[^\s]+ atCenter=\d+)?)$",

    # 2b. Player Drink & Flask Reaction Latency (BOSS-SEL-009 / v3.14)
    "player_drinks_scheduled": r"^count=\d+$",
    "player_drink_started": r"^n=\d+ offset=[^\s]+ ok=[01] length=[^\s]+$",
    "flask_perceived": r"^count=\d+ latencySeconds=[^\s]+ windowMin=[^\s]+ windowMax=[^\s]+$",
    "flask_reaction": r"^count=\d+ measuredSeconds=[^\s]+ windowMin=[^\s]+ windowMax=[^\s]+$",
    "flask_end": r"^count=\d+$",

    # 2c. Line-of-Sight & Obstacle Search Memory (BOSS-AWR-007 / v3.15)
    "los_lost": r"^lastKnownX=[^\s]+ lastKnownY=[^\s]+ blocker=[^\s]+$",
    "los_search_start": r"^x=[^\s]+ y=[^\s]+$",
    "los_regained": r"^lostForSeconds=[^\s]+$",
    "los_resume": r"^$",
    "los_search_timeout": r"^seconds=[^\s]+$",

    # 2d. Dodge Direction Histogram & Soft Adaptation (BOSS-AWR-008 / v3.16)
    "player_dodges_scheduled": r"^count=\d+$",
    "player_dodge_started": r"^n=\d+ offset=[^\s]+ direction=[^\s]+ ok=[01]$",
    "dodge_observed": r"^n=\d+ direction=[^\s]+ speedCm=[^\s]+ back=\d+ depth=\d+$",
    "dodge_pattern": r"^state=[^\s]+ back=\d+ depth=\d+ threshold=\d+ seq=\d+$",

    # 2e. Player Activity & Greed Adaptation (BOSS-AWR-006 / v3.20)
    "player_activity": r"^from=[^\s]+ to=[^\s]+ attackKind=[^\s]+$",
    "player_swing": r"^from=[^\s]+ to=[^\s]+ heavy=[01]$",
    "greed_pattern": r"^state=[^\s]+ source=[^\s]+ seq=\d+$",

    # 3. Candidate Selection & Gate Decisions (v3.0 adds optional seq=\d+)
    "candidate": r"^attack=\d+ card=[^\s]+ score=[^\s]+(?:\s+seq=\d+)?$",
    "refusal": r"^attack=\d+ card=[^\s]+ reason=[^\s]+(?:\s+seq=\d+)?$",
    "decision": r"^attack=\d+ chosen=[^\s]+ score=[^\s]+ range=[^\s]+(?:\s+phase=[^\s]+)?(?:\s+seq=\d+)?$",

    # 4. Heading Tracking & Motion Commitment
    "heading_commit": r"^instance=\d+ yaw=[^\s]+ turnedDegrees=[^\s]+ maxRateDegPerSec=[^\s]+ capDegPerSec=[^\s]+(?:\s+decisionRangeCm=[^\s]+ liveRangeCm=[^\s]+)?(?:\s+decisionYawDeg=[^\s]+ liveYawDeg=[^\s]+)?$",
    "heading_locked": r"^instance=\d+ yawAtCommit=[^\s]+ maxDriftAfterCommitDegrees=[^\s]+$",
    "warp_step": r"^instance=\d+ from=[^\s]+ to=[^\s]+ distCm=[^\s]+ neededCm=[^\s]+ stepCm=[^\s]+(?:\s+actualCm=[^\s]+)? movedCm=[^\s]+ budgetCm=[^\s]+ neededDeg=[^\s]+ stepDeg=[^\s]+ turnedDeg=[^\s]+ budgetDeg=[^\s]+$",
    "warp_summary": r"^instance=\d+ movedCm=[^\s]+ maxDistanceCm=[^\s]+ turnedDeg=[^\s]+ maxAngleDeg=[^\s]+$",

    # 5. Playback & Montages
    "playback_start": r"^encounter=\d+ generation=\d+ instance=\d+ montage=[^\s]+ slot=[^\s]+ rate=[^\s]+ label=[^\s]+$",
    "playback": r"^instance=\d+ position=[^\s]+ nodeWeight=[^\s]+ montageWeight=[^\s]+ base=" + VEC + r" tip=" + VEC + r"$",
    "montage_natural_end": r"^instance=\d+ lastPosition=[^\s]+ naturalEnd=[^\s]+$",
    "montage_end_suppressed": r"^instance=\d+ position=[^\s]+$",
    "watchdog_timeout": r"^instance=\d+ elapsedSeconds=[^\s]+ timeoutSeconds=[^\s]+ recoveryEndSeconds=[^\s]+ playRate=[^\s]+$",
    "watchdog_recovered": r"^attacksDone=\d+$",
    "cleanup": r"^reason=.* modelIdle=\d+ ownedMontageStopped=\d+$",
    "stale_callback": r"^oldInstance=\d+ newInstance=\d+ refused=\d+ error=[^\s]+ newAttackAlive=\d+$",

    # 6. Sweeps, Events, and Damage Resolution
    "event": r"^encounter=\d+ generation=\d+ instance=\d+ kind=[^\s]+ window=[^\s]+ group=[^\s]+ localSeconds=[^\s]+ label=[^\s]+$",
    "sweep": r"^instance=\d+ window=[^\s]+ from=[^\s]+ to=[^\s]+ tipDistanceCm=[^\s]+ substeps=\d+ clamped=\d+(?:\s+baked=\d+)?$",
    "ring_sweep": r"^instance=\d+ window=[^\s]+ from=[^\s]+ to=[^\s]+ frontLoCm=[^\s]+ frontHiCm=[^\s]+ thicknessCm=[^\s]+ targetDistCm=[^\s]+ targetRadiusCm=[^\s]+ dzCm=[^\s]+ heightCm=[^\s]+ contact=[01]$",
    "grab_catch": r"^instance=\d+ window=[^\s]+ socket=[^\s]+ releaseAt=[^\s]+ modeBefore=[^\s]+ modeHeld=[^\s]+ attached=[01]$",
    "grab_damage": r"^instance=\d+ key=[^\s]+ outcome=[^\s]+ hpApplied=[^\s]+$",
    "grab_release": r"^instance=\d+ reason=[^\s]+ interrupted=[01] attached=[01] mode=[^\s]+ floorFound=[01] floorZ=[^\s]+ feetZ=[^\s]+ gapCm=[^\s]+$",
    "sweep_filter": r"^instance=\d+ window=[^\s]+ ignoredPawns=\d+ first=[^\s]* targetContact=\d+ selfHits=\d+$",
    "hit": r"^instance=\d+ window=[^\s]+ key=[^\s]+ outcome=[^\s]+ hpApplied=[^\s]+ healthBefore=[^\s]+ healthAfter=[^\s]+$",
    "invariant": r"^(?:targetHPBefore=[^\s]+ targetHPAfter=[^\s]+ expectedHP=[^\s]+ acceptedHits=\d+ appliedDamage=[^\s]+|targetHPBefore=[^\s]+ targetHPAfter=[^\s]+ damageAPIInvocationsByThisExecutor=\d+)$",

    # 7. Player Hits & Intake Authority
    "pending_hit_queued": r"^weapon=[^\s]+ kind=[^\s]+ blades=\d+$",
    "attack_row": r"^weapon=[^\s]+ kind=[^\s]+ found=\d+ posture=[^\s]+ bleed=[^\s]+ healthMult=[^\s]+(?:\s+via=[^\s]+)?$",
    "boss_hit": r"^damage=[^\s]+ healthBefore=[^\s]+ healthAfter=[^\s]+$",
    "player_hits_scheduled": r"^count=\d+$",
    "player_hit_injected": r"^n=\d+ offset=[^\s]+ ok=\d+$",
    "target_shifts_scheduled": r"^count=\d+$",
    "target_shift_injected": r"^n=\d+ dx=[^\s]+ dy=[^\s]+ dz=[^\s]+$",

    # 8. Posture, Stagger, and Bleed System
    "posture_drain": r"^amount=[^\s]+ postureBefore=[^\s]+ postureAfter=[^\s]+ max=[^\s]+$",
    "posture_regen_start": r"^posture=[^\s]+ sinceLastDrainSeconds=[^\s]+ delaySeconds=[^\s]+ perSecond=[^\s]+$",
    "posture_regen_full": r"^posture=[^\s]+ max=[^\s]+$",
    "stance_break": r"^state=[^\s]+ duration=[^\s]+ generation=\d+ phase=[^\s]+$",
    "stagger_anim": r"^(?:state=Start sequence=[^\s]+ slot=[^\s]+ length=[^\s]+|state=Loop sequence=[^\s]+ slot=[^\s]+ loops=\d+|state=End sequence=[^\s]+ slot=[^\s]+ length=[^\s]+|state=Finished(?:\s+postureRefilled=[^\s]+)?)$",
    "stagger_recovery": r"^postureRefilled=[^\s]+ generation=\d+$",
    "posture_held": r"^reason=[^\s]+ posture=[^\s]+$",
    "stagger_superseded": r"^reason=[^\s]+ health=[^\s]+ max=[^\s]+ fraction=[^\s]+$",
    "bleed_buildup": r"^amount=[^\s]+ buildup=[^\s]+ threshold=[^\s]+ result=.*$",
    "bleed_proc": r"^procs=\d+ damage=[^\s]+ healthBefore=[^\s]+ healthAfter=[^\s]+ nextThreshold=[^\s]+$",

    # 9. Phase Transitions
    "phase_transition": r"^attack=\d+ from=[^\s]+ to=[^\s]+ health=[^\s]+ max=[^\s]+ fraction=[^\s]+$",
    "phase_anim": r"^(?:state=Triggered sequence=[^\s]+ slot=[^\s]+ length=[^\s]+ from=[^\s]+ to=[^\s]+|state=Finished phase=[^\s]+)$",

    # 10. Conditional Combos (Track B)
    "combo_start": r"^root=[^\s]+ move=[^\s]+ maxDepth=\d+$",
    "combo_step": r"^node=[^\s]+ move=[^\s]+ depth=\d+$",
    "combo_gate": r"^gate=\d+ node=[^\s]+ outcome=[^\s]+ range=[^\s]+ yaw=[^\s]+ result=[^\s]+ next=[^\s]+ reason=.*$",
    "combo_gate_duplicate": r"^gate=\d+ result=[^\s]+ reason=[^\s]+ stateUnchanged=\d+$",
    "combo_end": r"^reason=[^\s]+$",

    # 11. Runtime Diagnostics & Overlay
    "overlay": r"^Card=[^\s]+ State=[^\s]+ Phase=[^\s]+ Range=[^\s]+ Cone=[^\s]+ Window=[^\s]+ Posture=[^\s]+ Health=[^\s]+ Stagger=[^\s]+ PhaseHold=[^\s]+$",
}

COMPILED_SCHEMAS = {tok: re.compile(pat) for tok, pat in SCHEMAS.items()}
LINE_RE = re.compile(r"\[FrameworkProof\]\s+([A-Za-z0-9_]+)(?:\s+(.*))?$")
TS_RE = re.compile(r"^\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}):(\d{3})\]")

CANDIDATE_REFUSAL_RE = re.compile(r"\[FrameworkProof\]\s+(?:candidate|refusal)\s+attack=(\d+)\s+.*?(?:\s+seq=(\d+))?$")
DECISION_RE = re.compile(r"\[FrameworkProof\]\s+decision\s+attack=(\d+)\s+.*?(?:\s+seq=(\d+))?$")
GATE_RE = re.compile(r"\[FrameworkProof\]\s+combo_gate\s+gate=(\d+)")
INSTANCE_RE = re.compile(r"\[FrameworkProof\]\s+playback_start\s+.*?\bgeneration=(\d+)\s+instance=(\d+)")
ENC_RESET_RE = re.compile(r"\[FrameworkProof\]\s+encounter_reset\b")

def parse_ue_timestamp(line: str):
    m = TS_RE.match(line)
    if not m:
        return None
    try:
        dt = datetime.strptime(m.group(1), "%Y.%m.%d-%H.%M.%S")
        return dt.timestamp() + float(m.group(2)) / 1000.0
    except Exception:
        return None

def validate_line(line: str):
    """
    Validate a single log line containing [FrameworkProof].
    Returns (bValid, token, payload, error_message).
    """
    if "[FrameworkProof]" not in line:
        return True, None, None, None
        
    m = LINE_RE.search(line)
    if not m:
        return False, None, None, "Malformed [FrameworkProof] declaration"
        
    token = m.group(1)
    payload = (m.group(2) or "").strip()
    
    if token not in COMPILED_SCHEMAS:
        # Ephemeral non-canonical diagnostic hooks from historical experiments (e.g. screenshot_requested in B_QA001B)
        if token in {"screenshot_requested"}:
            return True, token, payload, None
        return False, token, payload, f"Unrecognized token '{token}'"
        
    if not COMPILED_SCHEMAS[token].match(payload):
        return False, token, payload, f"Payload does not match schema for '{token}'"
        
    return True, token, payload, None

def validate_log_file(file_path: Path):
    """
    Validate all [FrameworkProof] lines in a log file, enforcing both syntax
    and per-log semantic monotonicity checks.
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")
    results = {
        "file": file_path.as_posix(),
        "total_lines": 0,
        "framework_proof_lines": 0,
        "token_counts": Counter(),
        "syntax_failures": [],
        "semantic_violations": []
    }
    
    lines = text.splitlines()
    results["total_lines"] = len(lines)
    
    last_ts = None
    last_attack = 0
    seen_attacks = set()
    seen_gates = set()
    gen_instances = set()
    current_gen = 1
    
    last_decision_seq = 0
    seen_decision_seqs = set()
    pending_trace_seqs = []
    
    for lnum, line in enumerate(lines, start=1):
        # 1. Timestamp monotonicity check across lines with UE timestamp
        ts = parse_ue_timestamp(line)
        if ts is not None:
            if last_ts is not None and ts < last_ts - 0.0001:
                results["semantic_violations"].append({
                    "line_number": lnum,
                    "kind": "TIMESTAMP_BACKWARDS",
                    "details": f"Timestamp {ts} < last_ts {last_ts}",
                    "raw_line": line
                })
            last_ts = ts

        if "[FrameworkProof]" not in line:
            continue
            
        results["framework_proof_lines"] += 1
        ok, tok, payload, err = validate_line(line)
        if ok:
            results["token_counts"][tok] += 1
        else:
            results["syntax_failures"].append({
                "line_number": lnum,
                "token": tok,
                "payload": payload,
                "error": err,
                "raw_line": line
            })
            
        # Semantic checks
        if ENC_RESET_RE.search(line):
            last_attack = 0
            seen_attacks.clear()
            seen_gates.clear()
            gen_instances.clear()
            pending_trace_seqs.clear()
            current_gen += 1
            continue
            
        # Semantic check A: candidate/refusal trace collection
        m_trace = CANDIDATE_REFUSAL_RE.search(line)
        if m_trace and tok in ("candidate", "refusal"):
            trace_seq_str = m_trace.group(2)
            if trace_seq_str is not None:
                t_seq = int(trace_seq_str)
                # When a new query cycle starts, clear pending traces from previous unselected cycles
                if pending_trace_seqs and pending_trace_seqs[-1][1] != t_seq:
                    pending_trace_seqs.clear()
                pending_trace_seqs.append((lnum, t_seq))

        # Semantic check B: decision line evaluation
        m_dec = DECISION_RE.search(line)
        if m_dec and tok == "decision":
            att = int(m_dec.group(1))
            seq_str = m_dec.group(2)
            
            if seq_str is not None:
                # Modern engine with seq=N
                dec_seq = int(seq_str)
                if dec_seq in seen_decision_seqs:
                    results["semantic_violations"].append({
                        "line_number": lnum,
                        "kind": "DUPLICATE_DECISION_SEQ",
                        "details": f"Duplicate decision seq={dec_seq} encountered",
                        "raw_line": line
                    })
                elif dec_seq <= last_decision_seq:
                    results["semantic_violations"].append({
                        "line_number": lnum,
                        "kind": "NON_INCREASING_DECISION_SEQ",
                        "details": f"Decision seq={dec_seq} <= last_decision_seq={last_decision_seq}",
                        "raw_line": line
                    })
                seen_decision_seqs.add(dec_seq)
                last_decision_seq = dec_seq
                
                # Verify that preceding candidate/refusal traces carried the exact same seq
                for t_lnum, t_seq in pending_trace_seqs:
                    if t_seq != dec_seq:
                        results["semantic_violations"].append({
                            "line_number": t_lnum,
                            "kind": "TRACE_DECISION_SEQ_MISMATCH",
                            "details": f"Trace seq={t_seq} does not match decision seq={dec_seq}",
                            "raw_line": line
                        })
                pending_trace_seqs.clear()
            else:
                # Legacy log without seq
                if att in seen_attacks:
                    results["semantic_violations"].append({
                        "line_number": lnum,
                        "kind": "DUPLICATE_ATTACK_ID",
                        "details": f"attack={att} repeated (legacy, no seq; aborted attack re-evaluation)",
                        "raw_line": line
                    })
                elif att <= last_attack:
                    results["semantic_violations"].append({
                        "line_number": lnum,
                        "kind": "NON_INCREASING_ATTACK_ID",
                        "details": f"attack={att} <= last_attack={last_attack} (legacy, no seq)",
                        "raw_line": line
                    })
            seen_attacks.add(att)
            last_attack = att
            
        # Semantic check C: gate= ids in combo_gate unique
        m_gate = GATE_RE.search(line)
        if m_gate:
            gid = int(m_gate.group(1))
            if gid in seen_gates:
                results["semantic_violations"].append({
                    "line_number": lnum,
                    "kind": "DUPLICATE_GATE_ID",
                    "details": f"gate={gid} already seen in run",
                    "raw_line": line
                })
            seen_gates.add(gid)
            
        # Semantic check D: instance= in playback_start not reused in one generation
        m_inst = INSTANCE_RE.search(line)
        if m_inst:
            gen = int(m_inst.group(1))
            inst = int(m_inst.group(2))
            key = (gen, inst)
            if key in gen_instances:
                results["semantic_violations"].append({
                    "line_number": lnum,
                    "kind": "REUSED_INSTANCE_ID",
                    "details": f"generation={gen} instance={inst} already started",
                    "raw_line": line
                })
            gen_instances.add(key)
                
    return results

def main():
    parser = argparse.ArgumentParser(description="Validate [FrameworkProof] structured log telemetry.")
    parser.add_argument("log_files", nargs="*", help="Specific log files to validate. If omitted, scans all tracked logs.")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[5]

    if args.log_files:
        files = [Path(f) for f in args.log_files]
    else:
        import subprocess
        res = subprocess.run(["git", "ls-files", "Docs/*.log"], cwd=repo_root, capture_output=True, text=True)
        files = [repo_root / f for f in res.stdout.splitlines() if f.strip()]

    total_files = len(files)
    total_fp_lines = 0
    total_syntax_failures = 0
    total_semantic_violations = 0
    aggregated_counts = Counter()
    all_syntax_failures = []
    all_semantic_violations = []

    for fpath in files:
        if not fpath.exists():
            continue
        res = validate_log_file(fpath)
        total_fp_lines += res["framework_proof_lines"]
        aggregated_counts.update(res["token_counts"])
        if res["syntax_failures"]:
            total_syntax_failures += len(res["syntax_failures"])
            all_syntax_failures.extend(res["syntax_failures"])
        if res["semantic_violations"]:
            total_semantic_violations += len(res["semantic_violations"])
            for v in res["semantic_violations"]:
                v["file"] = fpath.relative_to(repo_root).as_posix()
                all_semantic_violations.append(v)

    report = {
        "total_log_files_checked": total_files,
        "total_framework_proof_lines": total_fp_lines,
        "total_tokens_recognized": len(SCHEMAS),
        "total_tokens_observed": len(aggregated_counts),
        "total_syntax_failures": total_syntax_failures,
        "total_semantic_violations": total_semantic_violations,
        "token_counts": dict(aggregated_counts.most_common()),
        "syntax_failures": all_syntax_failures,
        "semantic_violations": all_semantic_violations
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("================================================================================")
        print(" FRAMEWORK PROOF STRUCTURED LOG TELEMETRY VALIDATION REPORT (v3.14)")
        print("================================================================================")
        print(f"Log files checked:          {total_files}")
        print(f"Total [FrameworkProof] lines: {total_fp_lines}")
        print(f"Registered token schemas:   {len(SCHEMAS)}")
        print(f"Observed tokens in logs:    {len(aggregated_counts)}")
        print(f"Syntax failures (mismatches): {total_syntax_failures}")
        print(f"Semantic violations (findings): {total_semantic_violations}")
        print("--------------------------------------------------------------------------------")
        print("Token Occurrences (Descending):")
        for tok, cnt in aggregated_counts.most_common():
            print(f"  {tok:25s}: {cnt:6d} occurrences")
        print("--------------------------------------------------------------------------------")
        print(f"Semantic Findings Summary ({total_semantic_violations} occurrences):")
        sem_counts = Counter(v["kind"] for v in all_semantic_violations)
        for k, v in sem_counts.items():
            print(f"  {k:25s}: {v:6d}")
        if all_semantic_violations:
            print("\nDetailed list of semantic findings:")
            for v in all_semantic_violations:
                print(f"  [{v['kind']}] {v['file']}:{v['line_number']} -> {v['details']}")
        print("================================================================================")
        if total_syntax_failures == 0:
            print("ALL COMMITTED LOGS CONFORM TO SYNTAX SCHEMAS (100% GREEN)")
        else:
            print(f"VALIDATION FAILED ({total_syntax_failures} syntax errors)")
        print("================================================================================")

    return 0 if total_syntax_failures == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
