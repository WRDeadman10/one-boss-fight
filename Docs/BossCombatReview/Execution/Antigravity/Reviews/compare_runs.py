#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
compare_runs.py

Comparative analysis and deterministic replay / FPS parity validator for [FrameworkProof] logs.
Evaluates N PIE raw logs across:
1. Target tokens: decision, hit, RESULT, invariant, combo_*, phase_transition, stance_break (or all tokens in --exact mode).
2. Options:
   --exact: Compare every [FrameworkProof] line in sequence across all tokens.
   --ignore-token <token>: Omit specific tokens (e.g. pack_style_known) from comparison.
   --damage-tol, --score-tol, --range-tol: Configurable float tolerances (default 0.0, 0.05, 10.0).
   --require-exact-hits: Include duplicate contact events in sequence comparison.
3. First-difference reporting: pinpoint exact file, line, token, and payload mismatch.
4. Summary table: per-run counts (decisions, hits, accepted hits, duplicate hits, total damage, RESULT outcome).
5. PASS / FAIL determination.
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set

FRAMEWORK_PROOF_RE = re.compile(r"\[FrameworkProof\]\s+([A-Za-z0-9_]+)(?:\s+(.*))?$")
KV_RE = re.compile(r'([A-Za-z0-9_]+)=([^\s]+)')

DEFAULT_TARGET_TOKENS = {
    "decision", "hit", "RESULT", "invariant",
    "phase_transition", "stance_break"
}

def is_target_token(token: str, exact_mode: bool = False) -> bool:
    if exact_mode:
        return True
    if token in DEFAULT_TARGET_TOKENS:
        return True
    if token.startswith("combo_"):
        return True
    return False

def parse_kv_payload(payload: str) -> Dict[str, str]:
    return dict(KV_RE.findall(payload))

def parse_log_file(file_path: Path,
                   exact_mode: bool = False,
                   ignore_duplicate_hits: bool = True,
                   ignored_tokens: Optional[Set[str]] = None) -> Dict[str, Any]:
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if ignored_tokens is None:
        ignored_tokens = set()
        
    events = []
    first_seq = None
    ignored_counts = {tok: 0 for tok in ignored_tokens}
    
    counts = {
        "decisions": 0,
        "total_hits": 0,
        "accepted_hits": 0,
        "duplicate_hits": 0,
        "total_damage": 0.0,
        "result_outcome": "None",
        "invariant_applied": None,
        "total_fp_lines": 0,
    }
    
    for lnum, line in enumerate(lines, start=1):
        if "[FrameworkProof]" not in line:
            continue
        m = FRAMEWORK_PROOF_RE.search(line)
        if not m:
            continue
        counts["total_fp_lines"] += 1
        token = m.group(1)
        payload = (m.group(2) or "").strip()
        
        # Track metrics regardless of filtering
        if token == "decision":
            counts["decisions"] += 1
        elif token == "hit":
            counts["total_hits"] += 1
            kv_pre = parse_kv_payload(payload)
            outcome = kv_pre.get("outcome", "")
            if "Accepted" in outcome:
                counts["accepted_hits"] += 1
                try:
                    counts["total_damage"] += float(kv_pre.get("hpApplied", 0.0))
                except ValueError:
                    pass
            elif "RejectedDuplicate" in outcome:
                counts["duplicate_hits"] += 1
        elif token == "invariant":
            kv_pre = parse_kv_payload(payload)
            if "appliedDamage" in kv_pre:
                try:
                    counts["invariant_applied"] = float(kv_pre["appliedDamage"])
                except ValueError:
                    pass
        elif token == "RESULT":
            kv_pre = parse_kv_payload(payload)
            counts["result_outcome"] = kv_pre.get("outcome", "Unknown")

        # Skip ignored tokens
        if token in ignored_tokens:
            ignored_counts[token] += 1
            continue

        if not is_target_token(token, exact_mode=exact_mode):
            continue
            
        kv = parse_kv_payload(payload)
            
        # Filter duplicate hits from canonical sequence if requested (non-exact mode default)
        if token == "hit" and ignore_duplicate_hits and not exact_mode:
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
            "payload": payload,
            "kv": kv,
            "raw": line.strip()
        })
        
    return {
        "path": file_path,
        "counts": counts,
        "ignored_counts": ignored_counts,
        "events": events
    }

def compare_runs(runs: List[Dict[str, Any]],
                 exact_mode: bool = False,
                 damage_tol: float = 0.0,
                 score_tol: float = 0.05,
                 range_tol: float = 10.0) -> Tuple[bool, List[str], Dict[str, float], Optional[Dict[str, Any]]]:
    """
    Compare N runs against baseline (run 0).
    Returns (bPass, failure_messages, max_diffs, first_difference).
    """
    if len(runs) < 2:
        return True, ["At least 2 runs required for comparison."], {}, None
        
    base = runs[0]
    b_events = base["events"]
    failures = []
    first_diff = None
    
    max_diffs = {
        "damage": 0.0,
        "score": 0.0,
        "range": 0.0,
        "hpApplied": 0.0
    }
    
    def record_diff(run_idx: int, step_idx: int, b_lnum: int, r_lnum: int, tok: str, detail: str):
        nonlocal first_diff
        msg = f"Run {run_idx} ({runs[run_idx]['path'].name}:{r_lnum}) vs Baseline ({base['path'].name}:{b_lnum}) step {step_idx} [{tok}]: {detail}"
        failures.append(msg)
        if first_diff is None:
            first_diff = {
                "run_index": run_idx,
                "step_index": step_idx,
                "baseline_file": base["path"].name,
                "baseline_line": b_lnum,
                "target_file": runs[run_idx]["path"].name,
                "target_line": r_lnum,
                "token": tok,
                "detail": detail
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
            record_diff(i, min(len(b_events), len(r["events"])), 
                        b_events[-1]["line_number"] if b_events else 0,
                        r["events"][-1]["line_number"] if r["events"] else 0,
                        "LENGTH", f"Event count mismatch: {len(r['events'])} != baseline {len(b_events)}")

    # 3. Compare event by event up to min length
    for i, r in enumerate(runs[1:], start=1):
        min_len = min(len(b_events), len(r["events"]))
        for idx in range(min_len):
            be = b_events[idx]
            re_ev = r["events"][idx]
            
            # Check token match
            if be["token"] != re_ev["token"]:
                record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                            f"Token mismatch '{re_ev['token']}' != baseline '{be['token']}'")
                continue
                
            b_kv = be["kv"]
            r_kv = re_ev["kv"]
            
            if exact_mode:
                # In exact mode, compare exact payload text
                if be["payload"] != re_ev["payload"]:
                    record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                f"Payload mismatch: '{re_ev['payload']}' != baseline '{be['payload']}'")
                continue
                
            # Structured KV comparisons
            all_keys = set(b_kv.keys()) | set(r_kv.keys())
            for k in all_keys:
                if k in ("seq", "rel_seq"):
                    if "rel_seq" in b_kv and "rel_seq" in r_kv:
                        if b_kv["rel_seq"] != r_kv["rel_seq"]:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"rel_seq mismatch {r_kv['rel_seq']} != {b_kv['rel_seq']}")
                    continue
                    
                bv = b_kv.get(k)
                rv = r_kv.get(k)
                
                if bv is None or rv is None:
                    record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                f"Key '{k}' missing in one run ({bv} vs {rv})")
                    continue
                    
                # Float comparisons
                if k in ("score",):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs["score"] = max(max_diffs["score"], diff)
                        if diff > score_tol:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"score diff {diff:.6f} > tol {score_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"{k} mismatch {rv} != {bv}")
                elif k in ("range",):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs["range"] = max(max_diffs["range"], diff)
                        if diff > range_tol:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"range diff {diff:.3f} > tol {range_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"{k} mismatch {rv} != {bv}")
                elif k in ("hpApplied", "appliedDamage", "damage"):
                    try:
                        bf, rf = float(bv), float(rv)
                        diff = abs(bf - rf)
                        max_diffs[k] = max(max_diffs.get(k, 0.0), diff)
                        if diff > damage_tol:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"{k} diff {diff} > tol {damage_tol} ({rf} vs {bv})")
                    except ValueError:
                        if bv != rv:
                            record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                        f"{k} mismatch {rv} != {bv}")
                else:
                    if bv != rv:
                        record_diff(i, idx, be["line_number"], re_ev["line_number"], be["token"],
                                    f"{k} mismatch '{rv}' != '{bv}'")
                        
    b_pass = len(failures) == 0
    return b_pass, failures, max_diffs, first_diff

def print_summary_table(runs: List[Dict[str, Any]]):
    print("=" * 88)
    print(f"{'Run Log':<36} | {'Dec':<4} | {'Hits':<5} | {'AccHits':<7} | {'DupHits (Diag)':<14} | {'Damage':<7} | {'Outcome'}")
    print("-" * 88)
    for r in runs:
        c = r["counts"]
        rel = f"{r['path'].parent.name}/{r['path'].name}"
        if len(rel) > 34:
            rel = rel[-34:]
        print(f"{rel:<36} | {c['decisions']:<4} | {c['total_hits']:<5} | {c['accepted_hits']:<7} | {c['duplicate_hits']:<14} | {c['total_damage']:<7.1f} | {c['result_outcome']}")
    print("=" * 88)

def main():
    parser = argparse.ArgumentParser(description="Compare FrameworkProof event sequences across N PIE runs.")
    parser.add_argument("logs", nargs="+", help="Paths to raw log files to compare")
    parser.add_argument("--exact", action="store_true", help="Compare every FrameworkProof line across all tokens")
    parser.add_argument("--ignore-token", action="append", default=[], dest="ignored_tokens",
                        help="Token to ignore from comparison (e.g. --ignore-token pack_style_known)")
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
            
    ignored_tokens = set(args.ignored_tokens)
    parsed_runs = [parse_log_file(fp, exact_mode=args.exact,
                                  ignore_duplicate_hits=not args.require_exact_hits,
                                  ignored_tokens=ignored_tokens) for fp in file_paths]
    
    print("\nFRAMEWORK PROOF MULTI-RUN REPRODUCIBILITY & PARITY REPORT")
    if args.exact:
        print("[MODE] EXACT COMPARISON (All FrameworkProof tokens aligned)")
    if ignored_tokens:
        print(f"[IGNORED TOKENS] {', '.join(sorted(ignored_tokens))}")
    print_summary_table(parsed_runs)
    
    # Print ignored line counts
    if ignored_tokens:
        print("Ignored Lines Per Run:")
        for r in parsed_runs:
            counts_str = ", ".join(f"{k}={v}" for k, v in r["ignored_counts"].items())
            print(f"  {r['path'].name}: {counts_str}")
        print("-" * 88)
        
    b_pass, failures, max_diffs, first_diff = compare_runs(
        parsed_runs,
        exact_mode=args.exact,
        damage_tol=args.damage_tol,
        score_tol=args.score_tol,
        range_tol=args.range_tol
    )
    
    if not args.exact:
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
        if first_diff:
            print("\n" + "#" * 88)
            print(f"  FIRST DIFFERENCE DETECTED AT STEP #{first_diff['step_index']}:")
            print(f"  Token:         {first_diff['token']}")
            print(f"  Baseline:      {first_diff['baseline_file']}:{first_diff['baseline_line']}")
            print(f"  Target:        {first_diff['target_file']}:{first_diff['target_line']}")
            print(f"  Detail:        {first_diff['detail']}")
            print("#" * 88 + "\n")
        for f in failures[:15]:
            print(f"  [MISMATCH] {f}")
        if len(failures) > 15:
            print(f"  ... and {len(failures) - 15} more failures.")
        print("=" * 88)
        sys.exit(1)

if __name__ == "__main__":
    main()
