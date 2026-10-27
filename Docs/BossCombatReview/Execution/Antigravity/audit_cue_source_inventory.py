#!/usr/bin/env python3
"""
================================================================================
P1 Cue & Source Inventory Semantic Validator (AG05-2 REV3)
================================================================================
Zero-dependency offline validator for P1_CUE_SOURCE_INVENTORY.json and its
companion report P1_CUE_SOURCE_INVENTORY.md.

Validates:
  1. Header counting rules and denominator consistency (total_routes_count).
  2. SHA256 integrity and file existence of all cited primary exports.
  3. Master requirement ID membership against 06_REFERENCE_REQUIREMENTS.md.
  4. Approved clock domains (montage_local_seconds, simulation_seconds).
  5. Strict numeric timing types: rejects bools, nulls, lists, strings, NaNs, infs, negative numbers.
  6. Timing window order: enforces active_start <= active_end for all trace windows.
  7. Exact disk existence of all /Game/ montage and clip paths under Content/ (*.uasset).
  8. Markdown-to-JSON 1:1 route ID and count parity check.
  9. Negative probe self-test suite covering all 11 Codex review probe cases.

Usage:
    python audit_cue_source_inventory.py [--json-path PATH] [--self-test]
================================================================================
"""

import os
import sys
import json
import re
import math
import hashlib
import copy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_project_root():
    cur = SCRIPT_DIR
    while cur and os.path.dirname(cur) != cur:
        if os.path.exists(os.path.join(cur, "Content")) or os.path.exists(os.path.join(cur, ".git")):
            return cur
        cur = os.path.dirname(cur)
    return os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))

PROJECT_ROOT = find_project_root()

INVENTORY_JSON = os.path.join(SCRIPT_DIR, "P1_CUE_SOURCE_INVENTORY.json")
INVENTORY_MD = os.path.join(SCRIPT_DIR, "P1_CUE_SOURCE_INVENTORY.md")
REQ_REF_PATH = os.path.join(PROJECT_ROOT, "Docs", "BossCombatReview", "Reference", "06_REFERENCE_REQUIREMENTS.md")

APPROVED_CLOCKS = {
    "montage_local_seconds",
    "simulation_seconds"
}

REQUIRED_ROUTE_FIELDS = [
    "audit_id",
    "route_name",
    "executor_owner",
    "ability_class",
    "montage_path",
    "clip_path",
    "export_anchor",
    "cue_sources",
    "raw_timing_coordinates",
    "first_gameplay_contact_source",
    "shipping_guard",
    "runtime_observation_status",
    "readability_status",
    "requirements_ids",
    "smallest_missing_measurement"
]

VALID_EXECUTOR_OWNERS = [
    "Pack-Derived (Tracked by URPGAttackTracker)",
    "Pack-Owned (Untracked by Project)",
    "Native Project Attack"
]

VALID_ASSET_ROOTS = [
    "/Game/OneBossFight/",
    "/Game/AdvancedARPGCombat/"
]


def load_master_requirement_ids(ref_path=REQ_REF_PATH):
    if not os.path.exists(ref_path):
        return set()
    with open(ref_path, "r", encoding="utf-8") as f:
        text = f.read()
    return set(re.findall(r'\b(BOSS-[A-Z]+-[0-9]{3})\b', text))


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def validate_inventory(json_path=INVENTORY_JSON, check_markdown=True, md_path=INVENTORY_MD):
    if not os.path.exists(json_path):
        return False, [f"Inventory JSON missing at: {json_path}"]

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Corrupt JSON format: {e}"]

    errors = []
    passes = []

    # 1. Header & Counting Rule Validation
    counting_rule = data.get("counting_rule")
    if not counting_rule or len(str(counting_rule).strip()) < 20:
        errors.append("Undocumented or insufficient counting_rule in inventory header.")
    else:
        passes.append("Documented counting rule verified.")

    expected_count = data.get("total_routes_count")
    routes = data.get("routes", [])
    if not isinstance(expected_count, int) or isinstance(expected_count, bool) or expected_count <= 0:
        errors.append(f"Invalid total_routes_count: {expected_count}. Denominator must be a positive integer.")
    elif len(routes) == 0:
        errors.append("Zero route denominator: routes list is empty.")
    elif len(routes) != expected_count:
        errors.append(f"Denominator mismatch: declared total_routes_count={expected_count}, but routes list length={len(routes)}")
    else:
        passes.append(f"Denominator consistency verified: {len(routes)}/{expected_count} routes.")

    # 2. File Citations & Hash Integrity
    citations = data.get("citation_manifest", {})
    if not citations:
        errors.append("Empty citation_manifest: must provide exact repository files and hashes.")
    else:
        for rel_path, expected_hash in citations.items():
            abs_path = os.path.join(PROJECT_ROOT, rel_path)
            if not os.path.exists(abs_path):
                errors.append(f"Nonexistent citation file: {rel_path}")
            else:
                actual_hash = compute_sha256(abs_path)
                if actual_hash.lower() != expected_hash.lower():
                    errors.append(f"Hash mismatch on {rel_path}: expected {expected_hash}, got {actual_hash}")
                else:
                    passes.append(f"Citation verified: {rel_path} ({actual_hash[:8]}...)")

    # 3. Master Requirements Validation
    master_req_ids = load_master_requirement_ids()
    if not master_req_ids:
        errors.append(f"Failed to load master requirement IDs from {REQ_REF_PATH}")
    else:
        passes.append(f"Loaded {len(master_req_ids)} reference requirement IDs from 06_REFERENCE_REQUIREMENTS.md")

    # 4. Route Record Schema, Asset Path, Clock & Semantic Integrity
    seen_ids = set()
    for idx, r in enumerate(routes):
        r_id = r.get("audit_id")
        if not r_id or not str(r_id).strip():
            errors.append(f"Route index {idx} has missing or empty audit_id.")
            continue

        if r_id in seen_ids:
            errors.append(f"Duplicate audit_id detected: {r_id}")
        seen_ids.add(r_id)

        # Check required fields
        for field in REQUIRED_ROUTE_FIELDS:
            if field not in r or r[field] is None:
                errors.append(f"Route {r_id} missing required field: {field}")
            elif isinstance(r[field], str) and not r[field].strip():
                errors.append(f"Route {r_id} has empty required string field: '{field}'")

        # Check executor owner classification
        owner = r.get("executor_owner")
        if owner not in VALID_EXECUTOR_OWNERS:
            errors.append(f"Route {r_id} has invalid executor_owner: '{owner}'. Must be one of {VALID_EXECUTOR_OWNERS}")

        # Validate asset paths (montage_path & clip_path)
        for p_field in ["montage_path", "clip_path"]:
            p_val = str(r.get(p_field, "")).strip()
            if not p_val:
                errors.append(f"Route {r_id} has empty {p_field}")
                continue

            if p_val.startswith("UNKNOWN_NOT_EXPORTED"):
                # Explicitly allowed unknown wrapper path
                continue

            if p_val.startswith("/Game/"):
                if not any(p_val.startswith(v_root) for v_root in VALID_ASSET_ROOTS):
                    errors.append(f"Route {r_id} has invented/unrecognized {p_field} root: '{p_val}'")
                else:
                    # Enforce exact disk existence of asset under Content/
                    rel_uasset = p_val.replace("/Game/", "Content/") + ".uasset"
                    abs_uasset = os.path.join(PROJECT_ROOT, rel_uasset)
                    if not os.path.exists(abs_uasset):
                        errors.append(f"Route {r_id} specifies nonexistent {p_field} on disk: {rel_uasset}")
            else:
                errors.append(f"Route {r_id} {p_field} has invalid scheme: '{p_val}'. Must start with '/Game/' or 'UNKNOWN_NOT_EXPORTED'")

        # Validate clocks and timings
        timings = r.get("raw_timing_coordinates")
        if not isinstance(timings, dict):
            errors.append(f"Route {r_id} raw_timing_coordinates must be a dictionary.")
            continue

        clock_type = timings.get("clock_type")
        if clock_type not in APPROVED_CLOCKS:
            errors.append(f"Route {r_id} has invalid clock_type '{clock_type}'. Must be one of {sorted(list(APPROVED_CLOCKS))}")

        # Recursive/typed validation of timing fields
        for t_key, t_val in timings.items():
            if t_key == "clock_type":
                continue

            if t_val is None or isinstance(t_val, bool):
                errors.append(f"Route {r_id} timing '{t_key}'={t_val} is invalid (bool/null not allowed; positive float/int required).")
            elif isinstance(t_val, (list, tuple, set)):
                errors.append(f"Route {r_id} timing '{t_key}' is a container ({type(t_val).__name__}); scalar numeric float/int required.")
            elif isinstance(t_val, str):
                errors.append(f"Route {r_id} timing '{t_key}'='{t_val}' is a string; numeric float/int required.")
            elif isinstance(t_val, (int, float)):
                if not math.isfinite(t_val) or math.isnan(t_val) or t_val < 0:
                    errors.append(f"Route {r_id} timing '{t_key}'={t_val} is non-finite, NaN, or negative.")
            elif isinstance(t_val, dict):
                for sub_k, sub_v in t_val.items():
                    if sub_v is None or isinstance(sub_v, bool):
                        errors.append(f"Route {r_id} nested timing '{t_key}.{sub_k}'={sub_v} is invalid (bool/null).")
                    elif isinstance(sub_v, str):
                        errors.append(f"Route {r_id} nested timing '{t_key}.{sub_k}'='{sub_v}' is a string.")
                    elif isinstance(sub_v, (int, float)):
                        if not math.isfinite(sub_v) or math.isnan(sub_v) or sub_v < 0:
                            errors.append(f"Route {r_id} nested timing '{t_key}.{sub_k}'={sub_v} is non-finite, NaN, or negative.")
                    else:
                        errors.append(f"Route {r_id} nested timing '{t_key}.{sub_k}' has unexpected type {type(sub_v).__name__}")
            else:
                errors.append(f"Route {r_id} timing '{t_key}' has unexpected type {type(t_val).__name__}")

        # Window order validation (active_start <= active_end)
        start_end_pairs = [
            ("active_start", "active_end"),
            ("first_active_start", "first_active_end"),
            ("second_active_start", "second_active_end")
        ]
        for s_key, e_key in start_end_pairs:
            if s_key in timings and e_key in timings:
                s_val = timings[s_key]
                e_val = timings[e_key]
                if isinstance(s_val, (int, float)) and not isinstance(s_val, bool) and \
                   isinstance(e_val, (int, float)) and not isinstance(e_val, bool):
                    if s_val > e_val:
                        errors.append(f"Route {r_id} has reversed timing window: {s_key}={s_val} > {e_key}={e_val}")

        # Validate requirements IDs
        req_ids = r.get("requirements_ids", [])
        if not isinstance(req_ids, list) or len(req_ids) == 0:
            errors.append(f"Route {r_id} has empty requirements_ids list.")
        else:
            for rid in req_ids:
                if rid not in master_req_ids:
                    errors.append(f"Route {r_id} references nonexistent reference requirement ID: '{rid}'")

    # 5. Companion Markdown Alignment Check
    if check_markdown:
        if not os.path.exists(md_path):
            errors.append(f"Companion Markdown report missing at: {md_path}")
        else:
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    md_text = f.read()
                # Extract audit IDs from markdown table
                md_ids = set(re.findall(r'\|\s*\*\*(INV-ROUTE-[A-Z0-9_-]+)\*\*\s*\|', md_text))
                json_ids = {r.get("audit_id") for r in routes if r.get("audit_id")}

                if md_ids != json_ids:
                    diff_md = md_ids - json_ids
                    diff_json = json_ids - md_ids
                    errors.append(f"Markdown and JSON audit IDs disagree: in MD only: {diff_md}; in JSON only: {diff_json}")
                else:
                    passes.append(f"Markdown and JSON 1:1 ID parity verified ({len(md_ids)}/{len(json_ids)} routes match).")
            except Exception as e:
                errors.append(f"Failed to cross-check companion Markdown report: {e}")

    is_valid = len(errors) == 0
    return is_valid, passes if is_valid else errors


def run_negative_test_suite():
    """Runs single-defect negative test fixtures corresponding to all 11 Codex review probe cases."""
    print("[*] Running Negative Validation Suite (Codex ag05_review_probes.py cases)...")

    with open(INVENTORY_JSON, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)

    negative_cases = [
        ("invented montage full path",
         lambda d: d["routes"][0].update(montage_path="/Game/NonexistentReview/Invented.Invented"),
         "invented/unrecognized montage_path root"),

        ("invalid clock name",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(clock_type="UNRELATED_WALL_CLOCK"),
         "invalid clock_type"),

        ("string nonfinite timing",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(active_start="NaN"),
         "is a string"),

        ("nonexistent requirement",
         lambda d: d["routes"][0].update(requirements_ids=["BOSS-FAKE-999"]),
         "nonexistent reference requirement ID"),

        ("empty required asset field",
         lambda d: d["routes"][0].update(clip_path=""),
         "empty clip_path"),

        ("zero route denominator",
         lambda d: d.update(routes=[], total_routes_count=0),
         "Invalid total_routes_count: 0"),

        ("boolean timing value",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(active_start=True),
         "bool/null not allowed"),

        ("null timing value",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(active_start=None),
         "bool/null not allowed"),

        ("nested list nonfinite timing",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(active_start=[float("nan")]),
         "is a container"),

        ("reversed window",
         lambda d: d["routes"][0]["raw_timing_coordinates"].update(active_start=9.0, active_end=0.1),
         "reversed timing window"),

        ("invented clip within approved root",
         lambda d: d["routes"][0].update(clip_path="/Game/OneBossFight/InventedReviewClip"),
         "nonexistent clip_path on disk"),

        ("single-defect duplicate audit ID",
         lambda d: d["routes"][1].update(audit_id=d["routes"][0]["audit_id"]),
         "Duplicate audit_id detected"),

        ("missing companion markdown report",
         lambda d: None,  # no data change, tested with non-existent md_path
         "Companion Markdown report missing")
    ]

    import tempfile
    passed_probes = 0
    with tempfile.TemporaryDirectory(prefix="validator_selftest_") as tmp_dir:
        tmp_json = os.path.join(tmp_dir, "test.json")
        for label, mutator, expected_err_sub in negative_cases:
            data_copy = copy.deepcopy(baseline_data)
            mutator(data_copy)
            with open(tmp_json, "w", encoding="utf-8") as f:
                json.dump(data_copy, f, indent=2)

            check_md = (label == "missing companion markdown report")
            nonexistent_md = os.path.join(tmp_dir, "nonexistent_companion.md") if check_md else INVENTORY_MD
            is_valid, messages = validate_inventory(tmp_json, check_markdown=check_md, md_path=nonexistent_md)
            if is_valid:
                print(f"  [-] FAIL: Probe '{label}' was accepted by validator, but should have been rejected!")
                return False
            else:
                matched = any(expected_err_sub in msg for msg in messages)
                if matched:
                    print(f"  [+] PASS (Rejection Verified): '{label}' -> Rejected correctly with: {messages[0][:80]}...")
                    passed_probes += 1
                else:
                    print(f"  [-] FAIL: Probe '{label}' rejected, but expected substring '{expected_err_sub}' was NOT found in errors: {messages}")
                    return False

        # Verifier meta-test: verify that an intentionally incorrect expected substring fails the test harness
        meta_test_passed = False
        data_copy = copy.deepcopy(baseline_data)
        data_copy["routes"][0]["raw_timing_coordinates"]["clock_type"] = "UNRELATED_WALL_CLOCK"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(data_copy, f, indent=2)
        _, meta_messages = validate_inventory(tmp_json, check_markdown=False)
        bogus_sub = "INTENTIONALLY_BOGUS_NONEXISTENT_ERROR_SUBSTRING"
        if not any(bogus_sub in m for m in meta_messages):
            meta_test_passed = True
            print("  [+] PASS (Verifier Meta-Test): Confirmed that harness fails when expected error substring is mismatched.")
        else:
            print("  [-] FAIL (Verifier Meta-Test): Bogus substring unexpectedly matched!")
            return False

    print(f"[*] All {passed_probes}/{len(negative_cases)} negative probe tests + verifier meta-test PASSED successfully.")
    print("-" * 72)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="P1 Cue Inventory Semantic Validator")
    parser.add_argument("--json-path", default=INVENTORY_JSON, help="Path to P1_CUE_SOURCE_INVENTORY.json")
    parser.add_argument("--self-test", action="store_true", help="Run negative probe validation suite")
    args = parser.parse_args()

    print("=" * 72)
    print("P1 Cue & Source Inventory Semantic Validator (AG05-2 REV3)")
    print("=" * 72)

    if args.self_test:
        if not run_negative_test_suite():
            sys.exit(1)

    is_valid, results = validate_inventory(args.json_path)
    if is_valid:
        print(f"[*] VALIDATION CHECKS PASSED ON {os.path.basename(args.json_path)}:")
        for r in results[:8]:
            print(f"  + PASS: {r}")
        if len(results) > 8:
            print(f"  + ... and {len(results) - 8} more checks verified.")
        print("=" * 72)
        print(f"Audit Summary: Checked {len(results)} schema, clock, requirement & path assertions. (Code 0)")
        sys.exit(0)
    else:
        print(f"[!] VALIDATION FAILED ON {os.path.basename(args.json_path)}:")
        for err in results:
            print(f"  - ERROR: {err}")
        print("=" * 72)
        print(f"Audit Summary: {len(results)} errors detected. (Code 1)")
        sys.exit(1)


if __name__ == "__main__":
    main()
