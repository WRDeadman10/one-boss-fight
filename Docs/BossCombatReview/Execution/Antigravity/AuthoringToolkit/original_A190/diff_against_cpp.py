#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
diff_against_cpp.py - Single-Purpose Review Aid for C++ / Python Validator Parity

Deterministic, offline read-only comparison tool.
Given an RPGBoss*Adapters.cpp path (or multiple paths / all accepted adapters),
extracts the ordered list of Refuse(...) token checks (token strings and field
constants in exact C++ source order) and compares that order and token set with
the corresponding Python validator of the same component in authoring_core.py,
printing OK or the first difference.

Pure standard library: ZERO unreal imports, ZERO engine processes.
Deterministic, pure CRLF line endings, strictly run with python -B.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# Component name to Python validator function name mapping
COMPONENT_VALIDATOR_MAP = {
    "Bleed": "validate_bleed_domain",
    "LowSweep": "validate_low_sweep_domain",
    "Shockwave": "validate_shockwave_domain",
    "HealPunish": "validate_heal_punish_domain",
    "Look": "validate_look_domain",
}

DEFAULT_ADAPTERS = [
    "Source/OneBossFight/Player/RPGBossBleedAdapters.cpp",
    "Source/OneBossFight/Player/RPGBossLowSweepAdapters.cpp",
    "Source/OneBossFight/Player/RPGBossShockwaveAdapters.cpp",
    "Source/OneBossFight/Player/RPGBossHealPunishAdapters.cpp",
]


def extract_cpp_checks(cpp_path: Path) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Extracts ordered list of (Token, Field) validation checks from a C++ adapter file.
    Resolves C++ Field constants (e.g. FieldDamage -> LowSweep.Damage) using definitions
    found in the matching header and cpp file.
    """
    if not cpp_path.exists():
        raise FileNotFoundError(f"C++ adapter file not found: {cpp_path}")

    cpp_text = cpp_path.read_text(encoding="utf-8")
    h_path = cpp_path.with_suffix(".h")
    h_text = h_path.read_text(encoding="utf-8") if h_path.exists() else ""

    # 1. Field map: FieldName -> Manifest String ("LowSweep.Damage")
    field_map = dict(re.findall(r'(Field\w+)\s*=\s*TEXT\("([^"]+)"\)', h_text + "\n" + cpp_text))

    # 2. Identify component name from filename
    comp_match = re.search(r"RPGBoss(\w+)Adapters\.cpp", cpp_path.name)
    comp_name = comp_match.group(1) if comp_match else ""

    val_match = re.search(rf"bool\s+Validate{comp_name}\s*\([^{{]+\{{", cpp_text)
    if not val_match:
        # Fallback search for any Validate function
        val_match = re.search(r"bool\s+Validate\w+\s*\([^{{]+\{{", cpp_text)
        if not val_match:
            return comp_name, []

    start_pos = val_match.end()
    depth = 1
    end_pos = start_pos
    while end_pos < len(cpp_text) and depth > 0:
        if cpp_text[end_pos] == "{":
            depth += 1
        elif cpp_text[end_pos] == "}":
            depth -= 1
        end_pos += 1
    body = cpp_text[start_pos : end_pos - 1]

    # 3. Scalar fields array
    m_scalars = re.search(r"FScalar\s+Scalars\[\]\s*=\s*\{(.*?)\}\s*;", body, re.DOTALL)
    scalar_fields = []
    if m_scalars:
        items = re.findall(r"\{(Field\w+)", m_scalars.group(1))
        scalar_fields = [field_map.get(f, f) for f in items]

    checks: List[Tuple[str, str]] = []

    # 4. Check for NotFinite scalar loop
    not_finite_match = re.search(r'TEXT\("([^"]*\.NotFinite)(?::[^"]*)?"\)', body)
    if not_finite_match and scalar_fields:
        token = not_finite_match.group(1)
        for sf in scalar_fields:
            checks.append((token, sf))

    # 5. Remove scalar array definition and scalar loop to avoid duplicate matching
    scalar_loop_end = 0
    loop_match = re.search(r"for\s*\([^)]*FScalar[^)]*\)", body)
    if loop_match:
        l_start = loop_match.end()
        brace_pos = body.find("{", l_start)
        if brace_pos != -1:
            d = 1
            cur = brace_pos + 1
            while cur < len(body) and d > 0:
                if body[cur] == "{":
                    d += 1
                elif body[cur] == "}":
                    d -= 1
                cur += 1
            scalar_loop_end = cur

    body_rest = body[scalar_loop_end:]

    # 6. Parse domain checks outside scalar loop
    pattern = re.compile(
        r'Refuse\(\s*\w+\s*,\s*TEXT\("([^"]+)"\)\s*,\s*(Field\w+)\s*\)'
        r'|OutError\s*=\s*FString::Printf\(TEXT\("([^:"]+)(?::\s*%s|.*?)"\)\s*,\s*(Field\w+)'
        r'|CheckRequiredReference\(\s*(Field\w+)'
        r'|TEXT\("InvalidDependency\.Malformed:\s*%s\[%d\]"\)\s*,\s*(Field\w+)'
    )

    for m in pattern.finditer(body_rest):
        if m.group(1) and m.group(2):  # Refuse(OutError, TEXT("Token"), Field)
            token = m.group(1)
            raw_field = m.group(2)
            checks.append((token, field_map.get(raw_field, raw_field)))
        elif m.group(3) and m.group(4):  # OutError = FString::Printf(TEXT("Token: ..."), Field)
            token = m.group(3).strip()
            raw_field = m.group(4)
            checks.append((token, field_map.get(raw_field, raw_field)))
        elif m.group(5):  # CheckRequiredReference(Field...)
            raw_field = m.group(5)
            field = field_map.get(raw_field, raw_field)
            checks.append(("InvalidDependency.Missing", field))
            checks.append(("InvalidDependency.Malformed", field))
        elif m.group(6):  # HealPunish SpawnSockets malformed array element loop
            raw_field = m.group(6)
            checks.append(("InvalidDependency.Malformed", field_map.get(raw_field, raw_field)))

    return comp_name, checks


def extract_python_checks(func_name: str, core_path: Path) -> List[Tuple[str, str]]:
    """
    Extracts ordered list of (Token, Field) validation checks from a Python domain validator
    function in authoring_core.py.
    """
    if not core_path.exists():
        raise FileNotFoundError(f"authoring_core.py not found: {core_path}")

    core_text = core_path.read_text(encoding="utf-8")

    m = re.search(rf"def\s+{func_name}\s*\(.*?\)\s*(?:->\s*[^:]+)?:\n", core_text)
    if not m:
        return []

    start_pos = m.end()
    lines = core_text[start_pos:].splitlines()
    body_lines = []
    base_indent = None
    for line in lines:
        if not line.strip():
            body_lines.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        if base_indent is None:
            base_indent = indent
        elif indent < base_indent and (line.startswith("def ") or line.startswith("class ")):
            break
        body_lines.append(line)

    full_body = "\n".join(body_lines)

    # 1. Scalar fields - extract first element of each tuple
    m_scalars = re.search(r"scalar_fields\s*=\s*\[(.*?)\]", full_body, re.DOTALL)
    scalar_fields = []
    if m_scalars:
        scalar_fields = re.findall(r'\(\s*"([^"]+)"\s*,', m_scalars.group(1))

    checks: List[Tuple[str, str]] = []

    # 2. NotFinite loop
    m_finite = re.search(r'errs\.append\([fF]?"([^:"]+)\.NotFinite', full_body)
    if m_finite and scalar_fields:
        token = m_finite.group(1).strip() + ".NotFinite"
        for sf in scalar_fields:
            checks.append((token, sf))

    # 3. Reference fields loop (e.g. in Bleed)
    m_refs = re.search(r"ref_fields\s*=\s*\[(.*?)\]", full_body, re.DOTALL)
    ref_fields = []
    if m_refs:
        ref_fields = re.findall(r'\(\s*"([^"]+)"\s*,', m_refs.group(1))

    # 4. Remove scalar loop lines
    loop_line_idx = None
    for idx, line in enumerate(body_lines):
        if "in scalar_fields:" in line:
            loop_line_idx = idx
            break

    if loop_line_idx is not None:
        post_loop_idx = loop_line_idx + 1
        while post_loop_idx < len(body_lines):
            l = body_lines[post_loop_idx]
            if l.strip() and (len(l) - len(l.lstrip())) == base_indent:
                break
            post_loop_idx += 1
        active_lines = body_lines[post_loop_idx:]
    else:
        active_lines = body_lines[:]

    # 5. Check if there is a ref_fields loop in active_lines
    ref_loop_idx = None
    for idx, line in enumerate(active_lines):
        if "in ref_fields:" in line:
            ref_loop_idx = idx
            break

    if ref_loop_idx is not None and ref_fields:
        post_ref_idx = ref_loop_idx + 1
        while post_ref_idx < len(active_lines):
            l = active_lines[post_ref_idx]
            if l.strip() and (len(l) - len(l.lstrip())) == base_indent:
                break
            post_ref_idx += 1

        pre_ref_text = "\n".join(active_lines[:ref_loop_idx])
        post_ref_text = "\n".join(active_lines[post_ref_idx:])

        for m_app in re.finditer(r'(?:errs|errors)\.append\(\s*([fF]?"[^"]+")', pre_ref_text, re.DOTALL):
            cleaned = m_app.group(1).strip('fF"\'')
            if ":" in cleaned:
                parts = cleaned.split(":", 1)
                tok = parts[0].strip()
                rest = parts[1].strip()
                field_name_m = re.match(r"([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)", rest)
                fld = field_name_m.group(1) if field_name_m else rest
                if checks and checks[-1] == (tok, fld):
                    continue
                checks.append((tok, fld))

        for rf in ref_fields:
            checks.append(("InvalidDependency.Missing", rf))
            checks.append(("InvalidDependency.Malformed", rf))

        for m_app in re.finditer(r'(?:errs|errors)\.append\(\s*([fF]?"[^"]+")', post_ref_text, re.DOTALL):
            cleaned = m_app.group(1).strip('fF"\'')
            if ":" in cleaned:
                parts = cleaned.split(":", 1)
                tok = parts[0].strip()
                rest = parts[1].strip()
                field_name_m = re.match(r"([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)", rest)
                fld = field_name_m.group(1) if field_name_m else rest
                if checks and checks[-1] == (tok, fld):
                    continue
                checks.append((tok, fld))
    else:
        active_text = "\n".join(active_lines)
        for m_app in re.finditer(r'(?:errs|errors)\.append\(\s*([fF]?"[^"]+")', active_text, re.DOTALL):
            cleaned = m_app.group(1).strip('fF"\'')
            if ":" in cleaned:
                parts = cleaned.split(":", 1)
                tok = parts[0].strip()
                rest = parts[1].strip()
                field_name_m = re.match(r"([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)?)", rest)
                fld = field_name_m.group(1) if field_name_m else rest
                if checks and checks[-1] == (tok, fld):
                    continue
                checks.append((tok, fld))

    return checks


def compare_adapter(cpp_path: Path, core_path: Path) -> Tuple[bool, str, Dict]:
    """
    Compares a single C++ adapter file against its corresponding Python domain validator.
    Returns (bIsOk, formatted_output, summary_dict).
    """
    comp_name, cpp_checks = extract_cpp_checks(cpp_path)
    func_name = COMPONENT_VALIDATOR_MAP.get(comp_name)

    lines = []
    lines.append(f"COMPONENT: {comp_name}")
    lines.append(f"  C++ Source:       {cpp_path.as_posix()}")
    lines.append(f"  Python Validator: authoring_core.py::{func_name}")

    if not func_name:
        lines.append(f"  RESULT: SKIPPED (No mapped Python validator for component '{comp_name}')")
        return False, "\n".join(lines), {"component": comp_name, "status": "SKIPPED"}

    py_checks = extract_python_checks(func_name, core_path)

    lines.append(f"  C++ Checks Extracted:    {len(cpp_checks)}")
    lines.append(f"  Python Checks Extracted: {len(py_checks)}")

    diff_idx = None
    max_len = max(len(cpp_checks), len(py_checks))

    for i in range(max_len):
        c = cpp_checks[i] if i < len(cpp_checks) else ("<MISSING>", "<MISSING>")
        p = py_checks[i] if i < len(py_checks) else ("<MISSING>", "<MISSING>")
        if c != p and diff_idx is None:
            diff_idx = i

    if diff_idx is not None:
        c = cpp_checks[diff_idx] if diff_idx < len(cpp_checks) else ("<MISSING>", "<MISSING>")
        p = py_checks[diff_idx] if diff_idx < len(py_checks) else ("<MISSING>", "<MISSING>")
        lines.append(f"  RESULT: DIFFERENCE at check #{diff_idx + 1}")
        lines.append(f"    C++:    {c[0]}: {c[1]}")
        lines.append(f"    Python: {p[0]}: {p[1]}")
        return False, "\n".join(lines), {
            "component": comp_name,
            "status": "DIFFERENCE",
            "diff_index": diff_idx + 1,
            "cpp_check": f"{c[0]}: {c[1]}",
            "python_check": f"{p[0]}: {p[1]}",
        }
    else:
        lines.append(f"  RESULT: OK (all {len(cpp_checks)} checks match in exact source order)")
        return True, "\n".join(lines), {
            "component": comp_name,
            "status": "OK",
            "checks_matched": len(cpp_checks),
        }


def run_diff_suite(adapter_paths: Optional[List[str]] = None,
                   core_path: Optional[Path] = None,
                   output_report_path: Optional[Path] = None) -> int:
    """
    Executes the review aid over a list of adapters and prints/writes reports.
    Returns 0 if all adapters pass OK, 1 if any adapter differs or fails.
    """
    root_dir = Path(".").resolve()
    if core_path is None:
        core_path = root_dir / "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py"

    if adapter_paths:
        target_paths = [Path(p) for p in adapter_paths]
    else:
        target_paths = [root_dir / p for p in DEFAULT_ADAPTERS]
        # Include Look if present
        look_path = root_dir / "Source/OneBossFight/Player/RPGBossLookAdapters.cpp"
        if look_path.exists():
            target_paths.append(look_path)

    report_lines = []
    report_lines.append("================================================================================")
    report_lines.append("diff_against_cpp.py: Single-Purpose Review Aid Verification Report")
    report_lines.append("================================================================================")
    report_lines.append(f"Total Adapters Evaluated: {len(target_paths)}")
    report_lines.append("")

    all_ok = True
    summaries = []

    for path in target_paths:
        ok, text, summary = compare_adapter(path, core_path)
        if not ok:
            all_ok = False
        summaries.append(summary)
        report_lines.append(text)
        report_lines.append("")

    report_lines.append("================================================================================")
    report_lines.append("SUMMARY RESULTS:")
    report_lines.append("================================================================================")
    for s in summaries:
        comp = s["component"]
        st = s["status"]
        if st == "OK":
            report_lines.append(f"  [{st}]        {comp:12s} ({s['checks_matched']} checks verified)")
        elif st == "DIFFERENCE":
            report_lines.append(f"  [{st}] {comp:12s} (mismatch at #{s['diff_index']}: C++ '{s['cpp_check']}' vs Py '{s['python_check']}')")
        else:
            report_lines.append(f"  [{st}]   {comp:12s}")

    overall_status = "ALL ADAPTERS OK" if all_ok else "DIFFERENCES DETECTED"
    report_lines.append("--------------------------------------------------------------------------------")
    report_lines.append(f"OVERALL STATUS: {overall_status}")
    report_lines.append("================================================================================")

    full_report = "\r\n".join(report_lines) + "\r\n"

    # Print to stdout
    print(full_report)

    # Save to report file if requested
    if output_report_path:
        output_report_path.write_text(full_report, encoding="utf-8")
        print(f"Report written to: {output_report_path.as_posix()}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="diff_against_cpp.py: Check C++ and Python validator parity")
    parser.add_argument("paths", nargs="*", help="Optional path(s) to RPGBoss*Adapters.cpp")
    parser.add_argument("--report", action="store_true", help="Write report to AuthoringToolkit/diff_report.txt")
    parser.add_argument("--output", type=str, default=None, help="Explicit output report file path")
    args = parser.parse_args()

    report_file = None
    if args.output:
        report_file = Path(args.output)
    elif args.report or len(args.paths) == 0:
        report_file = Path("Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_report.txt")

    exit_code = run_diff_suite(
        adapter_paths=args.paths if args.paths else None,
        output_report_path=report_file
    )
    sys.exit(exit_code)
