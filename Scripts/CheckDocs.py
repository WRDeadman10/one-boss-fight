"""Read-only integrity checks for the project documentation and PIE driver table."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "Documentation"
RUN_DRIVERS = ROOT / "Scripts" / "RunDrivers.ps1"
TEST_PLAN = DOCS / "TEST_PLAN.md"
KNOWN_ISSUES = DOCS / "KNOWN_ISSUES.md"
AUDIT_DOCS = [
    DOCS / "PROJECT_STATE.md",
    DOCS / "TASKS.md",
    TEST_PLAN,
    DOCS / "DECISIONS.md",
    KNOWN_ISSUES,
]

# These are deliberately standalone probes, screenshots, diagnostics, or the
# Gate 4 soak harness. They are neither regression-gate rows nor TEST_PLAN
# cases, so reporting each as undocumented is audit noise rather than drift.
PIE_AUDIT_ALLOWLIST = {
    "pie_a2_diag", "pie_attr_probe", "pie_body_look", "pie_body_look_short",
    "pie_boss01_look", "pie_boss_abilities", "pie_boss_arm_diag", "pie_boss_fireball",
    "pie_boss_look_shots", "pie_cam_probe", "pie_clip_look", "pie_clip_look12",
    "pie_close_combo_watch", "pie_death_probe", "pie_debug_overlay", "pie_dump_abilities",
    "pie_dump_player_functions", "pie_g3_probe", "pie_gate_look", "pie_health_probe", "pie_hit_diag",
    "pie_hud_probe", "pie_input_smoke", "pie_jump_probe", "pie_montage_shots",
    "pie_montage_travel", "pie_player_tags", "pie_poise_enemy_test", "pie_soak",
    "pie_stamina_trace", "pie_state", "pie_stop", "pie_vfx_gallery",
}


@dataclass(frozen=True)
class Driver:
    name: str
    script: str
    minimum: int
    line: int
    balance: bool


def lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def location(path: Path, number: int) -> str:
    return f"{path.relative_to(ROOT).as_posix()}:{number}"


def quote(text: str) -> str:
    return text.strip().replace("\t", " ")[:220]


def find_line_number(all_lines: list[str], target: str) -> int:
    for number, line in enumerate(all_lines, 1):
        if line == target:
            return number
    return 1


def parse_driver_rows(path: Path) -> tuple[list[Driver], list[Driver]]:
    source = lines(path)
    gate: list[Driver] = []
    balance: list[Driver] = []
    in_balance = False
    row_pattern = re.compile(
        r"@\{\s*N\s*=\s*'(?P<name>[^']+)'(?P<body>[^}]*)\}", re.IGNORECASE
    )
    for number, line in enumerate(source, 1):
        if line.lstrip().startswith("$balance = @("):
            in_balance = True
            continue
        match = row_pattern.search(line)
        if not match:
            continue
        minimum = re.search(r"\bMin\s*=\s*(\d+)", match.group("body"))
        script = re.search(r"\bS\s*=\s*'([^']+)'", match.group("body"))
        if not minimum:
            continue
        gate_or_balance = balance if in_balance else gate
        gate_or_balance.append(
            Driver(
                name=match.group("name"),
                script=script.group(1) if script else match.group("name"),
                minimum=int(minimum.group(1)),
                line=number,
                balance=in_balance,
            )
        )
    return gate, balance


def all_markdown_documents() -> Iterable[Path]:
    for path in DOCS.rglob("*.md"):
        # Briefs and reports are instructions/audit evidence, not project-state docs.
        if "Codex" not in path.parts:
            yield path


def main() -> int:
    findings: list[str] = []
    gate, balance = parse_driver_rows(RUN_DRIVERS)
    table_scripts = {driver.script for driver in gate + balance}
    test_plan_lines = lines(TEST_PLAN)
    test_plan_text = "\n".join(test_plan_lines)
    test_plan_drivers = set(re.findall(r"\b(pie_[A-Za-z0-9_]+)\b", test_plan_text))

    # (a) Table scripts exist, and every other pie script is documented.
    for driver in gate + balance:
        expected = ROOT / "Scripts" / "Editor" / f"{driver.script}.py"
        if not expected.is_file():
            findings.append(
                f"MISSING_DRIVER_SCRIPT {location(RUN_DRIVERS, driver.line)} "
                f"row {driver.name!r} uses {driver.script!r}; expected {expected.relative_to(ROOT).as_posix()}"
            )

    for script in sorted((ROOT / "Scripts" / "Editor").glob("pie_*.py")):
        if (script.stem not in table_scripts and script.stem not in test_plan_drivers
                and script.stem not in PIE_AUDIT_ALLOWLIST):
            findings.append(
                f"UNDOCUMENTED_PIE {script.relative_to(ROOT).as_posix()}:1 "
                f"{script.name} is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md"
            )

    # (b) Gate drivers appear in the test plan, and PASS totals agree exactly.
    for driver in gate:
        matching = [
            (number, line)
            for number, line in enumerate(test_plan_lines, 1)
            if re.search(rf"\b{re.escape(driver.name)}(?:\.py)?\b", line)
        ]
        if not matching:
            findings.append(
                f"GATE_DRIVER_NOT_IN_TEST_PLAN {location(RUN_DRIVERS, driver.line)} "
                f"{driver.name} (Min {driver.minimum}) has no matching name in Documentation/TEST_PLAN.md"
            )
        for number, line in matching:
            if "automation tests" in line.lower():
                continue
            names_on_line = {
                candidate.name
                for candidate in gate
                if re.search(rf"\b{re.escape(candidate.name)}(?:\.py)?\b", line)
            }
            # A combined procedure can cite several drivers but has one aggregate
            # PASS result; its total cannot be attributed to an individual row.
            if names_on_line != {driver.name}:
                continue
            for passed, total in re.findall(r"\bPASS\s+(\d+)/(\d+)\b", line, re.IGNORECASE):
                if int(total) != driver.minimum:
                    lower = "TEST_PLAN" if int(total) < driver.minimum else "RunDrivers"
                    findings.append(
                        f"PASS_TOTAL_MISMATCH {location(TEST_PLAN, number)} {driver.name}: "
                        f"TEST_PLAN PASS {passed}/{total}, RunDrivers Min {driver.minimum}; lower total is {lower}"
                    )

    # (c) KI references resolve, rows are unique, and status disagreement is a heuristic.
    issue_lines = lines(KNOWN_ISSUES)
    issue_rows: dict[str, tuple[int, str, str]] = {}
    for number, line in enumerate(issue_lines, 1):
        match = re.match(r"^\|\s*(KI-\d+)\s*\|", line)
        if not match:
            continue
        issue_id = match.group(1)
        if issue_id in issue_rows:
            previous = issue_rows[issue_id][0]
            findings.append(
                f"DUPLICATE_KI {location(KNOWN_ISSUES, number)} {issue_id}; first row is {location(KNOWN_ISSUES, previous)}"
            )
            continue
        cells = [cell.strip() for cell in line.split("|")]
        status = cells[-2] if len(cells) >= 2 else ""
        issue_rows[issue_id] = (number, line, status)

    documents = list(all_markdown_documents())
    for document in documents:
        for number, line in enumerate(lines(document), 1):
            for issue_id in sorted(set(re.findall(r"\bKI-\d+\b", line))):
                if issue_id not in issue_rows:
                    findings.append(
                        f"UNKNOWN_KI {location(document, number)} {issue_id}: {quote(line)}"
                    )

    for issue_id, (issue_line, issue_text, status) in sorted(issue_rows.items()):
        if "open" not in status.lower():
            continue
        explicit_status = re.compile(
            rf"(?:\b{re.escape(issue_id)}\b\s+(?:is\s+)?(?:fixed|closed)\b|"
            rf"\b(?:fixed|closed)\s+{re.escape(issue_id)}\b)",
            re.IGNORECASE,
        )
        for document in documents:
            if document == KNOWN_ISSUES:
                continue
            for number, line in enumerate(lines(document), 1):
                if explicit_status.search(line):
                    findings.append(
                        f"KI_STATUS_HEURISTIC {location(KNOWN_ISSUES, issue_line)} says Open for {issue_id}; "
                        f"{location(document, number)} says fixed/closed: {quote(line)}"
                    )
                    break

    # (d) Backticked Documentation/ and Scripts/ paths in the state docs resolve.
    path_pattern = re.compile(r"`((?:Documentation|Scripts)[\\/][^`\s)\],:;]+)")
    for document in AUDIT_DOCS:
        for number, line in enumerate(lines(document), 1):
            for raw_path in path_pattern.findall(line):
                if any(token in raw_path for token in ("NN", "*", "..")):
                    continue
                normalized = raw_path.replace("\\", "/")
                candidate = ROOT / normalized
                if not candidate.exists():
                    findings.append(
                        f"MISSING_BACKTICK_PATH {location(document, number)} `{raw_path}` does not exist"
                    )

    # (e) The three authoritative headers state the final performance target.
    target_files = [ROOT / "CLAUDE.md", ROOT / "AGENTS.md", DOCS / "PERFORMANCE_LOG.md"]
    for target in target_files:
        text = target.read_text(encoding="utf-8").lower()
        has_target = "60 fps" in text and "p99" in text and "16.67" in text
        if not has_target:
            findings.append(
                f"FPS_TARGET_MISSING {target.relative_to(ROOT).as_posix()}:1 "
                "missing one of final target: 60 FPS, p99, 16.67 ms"
            )
        if "120 fps" in text and "stretch" not in text:
            findings.append(
                f"FPS_TARGET_120_NOT_STRETCH {target.relative_to(ROOT).as_posix()}:1 "
                "mentions 120 FPS without identifying it as stretch telemetry"
            )

    if findings:
        for finding in findings:
            print(finding)
        print(f"{len(findings)} finding(s)")
        return 1

    print("No documentation integrity findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
