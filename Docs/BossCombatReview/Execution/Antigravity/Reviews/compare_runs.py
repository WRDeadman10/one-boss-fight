#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
compare_runs.py

Comparative analysis and deterministic replay / FPS parity validator for [FrameworkProof] logs.
Evaluates N PIE raw logs across:
1. Target tokens: decision, hit, RESULT, invariant, combo_*, phase_transition, stance_break.
2. Canonical event sequence alignment:
   - Exact equality for integers, IDs, names, and outcomes.
   - Bounded numerical tolerances for floats (damage, hpApplied, score, range).
   - Duplicate hit contacts (ERPGDamageOutcome::RejectedDuplicate) tracked as frame-rate scaling diagnostics.
3. Summary table: per-run counts (decisions, hits, accepted hits, duplicate hits, total damage, RESULT outcome).
4. PASS / FAIL determination.
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

FRAMEWORK_PROOF_RE = re.compile(r"\[FrameworkProof\]\s+([A-Za-z0-9_]+)(?:\s+(.*))?$")
KV_RE = re.compile(r'([A-Za-z0-9_]+)=([^\s]+)')

TARGET_TOKENS = {
    "decision", "hit", "RESULT", "invariant",
    "phase_transition", "stance_break"
}

def is_target_token(token: str) -> bool:
    if token in TARGET_TOKENS:
        return True
    if token.startswith("combo_"):
        return True
    return False

def parse_kv_payload(payload: str) -> Dict[str, str]:
    return dict(KV_RE.findall(payload))

def parse_log_file(file_path: Path, ignore_duplicate_hits: bool = True) -> Dict[str, Any]:
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    
    events = []
    first_seq = None
    
    counts = {
        "decisions": 0,
        "total_hits": 0,
        "accepted_hits": 0,
        "duplicate_hits": 0,
        "total_damage": 0.0,
        "result_outcome": "None",
        "invariant_applied": None,
    }
    
    for lnum, line in enumerate(lines, start=1):
        if "[FrameworkProof]" not in line:
            continue
        m = FRAMEWORK_PROOF_RE.search(line)
        if not m:
            continue
        token = m.group(1)
        payload = (m.group(2) or "").strip()
        
        if not is_target_token(token):
            continue
            
        kv = parse_kv_payload(payload)
        
        # Track metrics
        if token == "decision":
            counts["decisions"] += 1
        elif token == "hit":
            counts["total_hits"] += 1
            outcome = kv.get("outcome", "")
            if "Accepted" in outcome:
                counts["accepted_hits"] += 1
                try:
                    counts["total_damage"] += float(kv.get("hpApplied", 0.0))
                except ValueError:
                    pass
            elif "RejectedDuplicate" in outcome:
                counts["duplicate_hits"] += 1
        elif token == "invariant":
            if "appliedDamage" in kv:
                try:
                    counts["invariant_applied"] = float(kv["appliedDamage"])
                except ValueError:
                    pass
        elif token == "RESULT":
            counts["result_outcome"] = kv.get("outcome", "Unknown")
            
        # Filter duplicate hits from canonical sequence if requested
        if token == "hit" and ignore_duplicate_hits:
            if "Accepted" not in kv.get("outcome", ""):
                continue
                
        # Normalize seq if present
        if "seq" in kv:
            try:
                seq_val = int(kv["seq"])
                if first_seq is None:
                    first_seq = seq_val
                kv["rel_seq"] = str(seq_val - first_seq)
            except ValueError:
                pass
                
        events.append({
            "line_number": lnum,
            "token": token,
            "kv": kv,
            "raw": line.strip()
        })
        
    return {
        "path": file_path,
        "counts": counts,
        "events": events
    }

def compare_runs(runs: List[Dict[str, Any]],
                 damage_tol: float = 0.0,
                 score_tol: float = 1e-3,
                 range_tol: float = 10.0) -> Tuple[bool, List[str], Dict[str, float]]:
    """
    Compare N runs against the baseline (run 0).
    Returns (bPass, failure_messages, max_diffs).
    """
    if len(runs) < 2:
        return True, ["At least 2 runs required for comparison; single run inspected."], {}
        
    base = runs[0]
    b_events = base["events"]
    failures = []
    
    max_diffs = {
        "damage": 0.0,
        "score": 0.0,
        "range": 0.0,
        "hpApplied": 0.0
    }
    
    # 1. Compare high-level outcome metrics across runs
    for i, r in enumerate(runs[1:], start=1):
        if r["counts"]["result_outcome"] != base["counts"]["result_outcome"]:
            failures.append(f"Run {i} ({r['path'].name}) outcome mismatch: {r['counts']['result_outcome']} != {base['counts']['result_outcome']}")
        if r["counts"]["accepted_hits"] != base["counts"]["accepted_hits"]:
            failures.append(f"Run {i} ({r['path'].name}) acceptedHits mismatch: {r['counts']['accepted_hits']} != {base['counts']['accepted_hits']}")
        if abs(r["counts"]["total_damage"] - base["counts"]["total_damage"]) > damage_tol:
            diff = abs(r["counts"]["total_damage"] - base["counts"]["total_damage"])
            max_diffs["damage"] = max(max_diffs["damage"], diff)
            failures.append(f"Run {i} ({r['path'].name}) total damage mismatch: {r['counts']['total_damage']} != {base['counts']['total_damage']} (diff={diff} > tol={damage_tol})")
            
    # 2. Compare canonical event sequence length
    for i, r in enumerate(runs[1:], start=1):
        if len(r["events"]) != len(b_events):
            failures.append(f"Run {i} ({r['path'].name}) event count mismatch: {len(r['events'])} != {len(b_events)}")
            
    # 3. Compare event by event up to min length
    for i, r in enumerate(runs[1:], start=1):
        min_len = min(len(b_events), len(r["events"]))
        for idx in range(min_len):
            be = b_events[idx]
            re_ev = r["events"][idx]
            
            # Check token match
            if be["token"] != re_ev["token"]:
                failures.append(f"Run {i} step {idx}: token mismatch '{re_ev['token']}' != baseline '{be['token']}'")
                continue
                
            b_kv = be["kv"]
            r_kv = re_ev["kv"]
            
            # Compare key-value pairs
            all_keys = set(b_kv.keys()) | set(r_kv.keys())
            for k in all_keys:
                if k in ("seq", "rel_seq"):
                    # rel_seq check if present in both
                    if "rel_seq" in b_kv and "rel_seq" in r_kv:
                        if b_kv["rel_seq"] != r_kv["rel_seq"]:
                            failures.append(f"Run {i} step {idx} ({be['token']}): rel_seq mismatch {r_kv['rel_seq']} != {b_kv['rel_seq']}")
                    continue
                    
                bv = b_kv.get(k)
                rv = r_kv.get(k)
                
                if bv is None or rv is None:
                    failures.append(f"Run {i} step {idx} ({be['token']}): key '{k}' missing in one run ({bv} vs {rv})")
                    continue
                    
                # Float comparisons
                if k in ("score",):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs["score"] = max(max_diffs["score"], diff)
                        if diff > score_tol:
                            failures.append(f"Run {i} step {idx} ({be['token']}): score diff {diff:.6f} > tol {score_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            failures.append(f"Run {i} step {idx} ({be['token']}): {k} mismatch {rv} != {bv}")
                elif k in ("range",):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs["range"] = max(max_diffs["range"], diff)
                        if diff > range_tol:
                            failures.append(f"Run {i} step {idx} ({be['token']}): range diff {diff:.3f} > tol {range_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            failures.append(f"Run {i} step {idx} ({be['token']}): {k} mismatch {rv} != {bv}")
                elif k in ("hpApplied", "appliedDamage", "damage"):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs[k] = max(max_diffs.get(k, 0.0), diff)
                        if diff > damage_tol:
                            failures.append(f"Run {i} step {idx} ({be['token']}): {k} diff {diff} > tol {damage_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            failures.append(f"Run {i} step {idx} ({be['token']}): {k} mismatch {rv} != {bv}")
                else:
                    # Exact string / integer equality
                    if bv != rv:
                        failures.append(f"Run {i} step {idx} ({be['token']}): {k} mismatch '{rv}' != '{bv}'")
                        
    b_pass = len(failures) == 0
    return b_pass, failures, max_diffs

def print_summary_table(runs: List[Dict[str, Any]]):
    print("=" * 88)
    print(f"{'Run Log':<36} | {'Dec':<4} | {'Hits':<5} | {'AccHits':<7} | {'DupHits (Diag)':<14} | {'Damage':<7} | {'Outcome'}")
    print("-" * 88)
    for r in runs:
        c = r["counts"]
        p_name = r["path"].name
        if len(p_name) > 34:
            p_name = p_name[:31] + "..."
        # If path has parent directory, include parent/name
        rel = f"{r['path'].parent.name}/{r['path'].name}"
        if len(rel) > 34:
            rel = rel[-34:]
        print(f"{rel:<36} | {c['decisions']:<4} | {c['total_hits']:<5} | {c['accepted_hits']:<7} | {c['duplicate_hits']:<14} | {c['total_damage']:<7.1f} | {c['result_outcome']}")
    print("=" * 88)

def main():
    parser = argparse.ArgumentParser(description="Compare FrameworkProof event sequences across N PIE runs.")
    parser.add_argument("logs", nargs="+", help="Paths to raw log files to compare")
    parser.add_argument("--damage-tol", type=float, default=0.0, help="Allowed damage difference (default: 0.0)")
    parser.add_argument("--score-tol", type=float, default=0.05, help="Allowed score difference (default: 0.05)")
    parser.add_argument("--range-tol", type=float, default=10.0, help="Allowed range difference in cm (default: 10.0)")
    parser.add_argument("--require-exact-hits", action="store_true", help="Do not ignore duplicate hit lines in sequence")
    args = parser.parse_args()
    
    file_paths = [Path(p).resolve() for p in args.logs]
    for fp in file_paths:
        if not fp.exists():
            print(f"Error: Log file not found: {fp}", file=sys.stderr)
            sys.exit(1)
            
    parsed_runs = [parse_log_file(fp, ignore_duplicate_hits=not args.require_exact_hits) for fp in file_paths]
    
    print("\nFRAMEWORK PROOF MULTI-RUN REPRODUCIBILITY & PARITY REPORT")
    print_summary_table(parsed_runs)
    
    b_pass, failures, max_diffs = compare_runs(
        parsed_runs,
        damage_tol=args.damage_tol,
        score_tol=args.score_tol,
        range_tol=args.range_tol
    )
    
    print(f"Observed Max Differences across runs:")
    for k, v in max_diffs.items():
        print(f"  {k:<12}: {v}")
    print("-" * 88)
    
    if b_pass:
        print("RESULT: ALL RUNS PASS COMPARATIVE PARITY (DETERMINISTIC / EQUIVALENT)")
        print("=" * 88)
        sys.exit(0)
    else:
        print(f"RESULT: FAIL ({len(failures)} mismatch finding(s)):")
        for f in failures[:25]:
            print(f"  [MISMATCH] {f}")
        if len(failures) > 25:
            print(f"  ... and {len(failures) - 25} more failures.")
        print("=" * 88)
        sys.exit(1)

if __name__ == "__main__":
    main()
