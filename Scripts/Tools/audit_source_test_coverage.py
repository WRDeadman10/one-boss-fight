"""Heuristic inventory of implementation translation units and test references.

This is a gap-finding aid, not a proof of behavioral coverage: it recognizes
the primary same-named header type(s) and checks whether native automation
sources mention those type identifiers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "OneBossFight"
TESTS = SOURCE / "Tests"
INCLUDE = re.compile(r'^\s*#include\s+["<]([^">]+\.h)[">]', re.MULTILINE)
TYPE = re.compile(r"\b(?:class|struct)\s+(?:ONEBOSSFIGHT_API\s+)?(\w+)")
PRIORITY = {"URPGPlayerParry": 1, "URPGRiposteInput": 2, "URPGFlaskHud": 3,
            "URPGCameraProbe": 4, "URPGHideBones": 5, "ARPGBenchmarkRunner": 6}


@dataclass(frozen=True)
class Row:
    path: str
    primary_header: str
    types: tuple[str, ...]
    matching_tests: tuple[str, ...]
    risk: str


def _risk(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "boss" in parts or "player" in parts or "combat" in parts:
        return "HIGH"
    if "arena" in parts or "ui" in parts or "audio" in parts or "pack" in parts:
        return "MEDIUM"
    return "LOW"


def inventory(source: Path = SOURCE, tests_dir: Path = TESTS) -> list[Row]:
    test_sources = sorted(tests_dir.glob("*.cpp"))
    test_text = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in test_sources}
    rows: list[Row] = []
    for cpp in sorted(p for p in source.rglob("*.cpp") if tests_dir not in p.parents):
        own = next((inc for inc in INCLUDE.findall(cpp.read_text(encoding="utf-8", errors="replace"))
                    if Path(inc).stem == cpp.stem), "")
        header = next((p for p in source.rglob(Path(own).name)), None) if own else None
        types = tuple(TYPE.findall(header.read_text(encoding="utf-8", errors="replace"))) if header else ()
        matches = tuple(sorted(name for name, body in test_text.items()
                               if any(re.search(r"\b" + re.escape(symbol) + r"\b", body) for symbol in types)))
        rows.append(Row(cpp.relative_to(ROOT).as_posix(), own or "(no same-name header)", types, matches, _risk(cpp)))
    return rows


def render(rows: list[Row]) -> str:
    tested = sum(bool(row.matching_tests) for row in rows)
    gaps = [row for row in rows if row.types and not row.matching_tests]
    no_primary = sum(not row.types for row in rows)
    lines = [
        "# U-C02 source-to-automation test gap audit",
        "",
        f"Inventory: {len(rows)} production `.cpp` translation units; {tested} have at least one native automation source that names a primary same-header type. {len(gaps)} declared primary-type candidates have no matching automation reference; {no_primary} units lack a same-name declared type and require the helper/adapter caveat below.",
        "",
        "This is a conservative static gap-finding heuristic, not proof of runtime coverage. It recognizes class/struct identifiers from the same-named header and searches `Source/OneBossFight/Tests/*.cpp` for those identifiers. It does not infer coverage from filename similarity, tests of collaborators, or indirect behavior. Risk is a review priority based on code location and is not a defect finding.",
        "",
        "## Baseline gaps and test additions",
        "",
        "The pre-test baseline found six primary class/type gaps. Manual review of the nine no-primary-header units found two additional callable surfaces without focused native coverage (`RPGPerf::FireRadiusScale` and `RPGBossInterrupt::CancelOffence`). U-C03/U-C04 added test-only coverage for all eight identified surfaces. The module entry point is not treated as a behavioral test target; helper/adapter units with existing dedicated adapter tests remain mapped in the manual section below.",
        "",
        "| Baseline risk | Implementation surface | Added automation |",
        "|---|---|---|",
        "| High | `URPGPlayerParry` | `OneBossFight.Player.Parry.ComponentContract` |",
        "| High | `URPGRiposteInput` | `OneBossFight.Player.RiposteInput.Defaults` |",
        "| High | `RPGBossInterrupt::CancelOffence` | `OneBossFight.Combat.InterruptNoComponents` |",
        "| Medium | `URPGFlaskHud` | `OneBossFight.UI.FlaskHud.InitialState` |",
        "| Medium | `URPGCameraProbe` | `OneBossFight.Camera.Probe.WorldSupport` |",
        "| Medium | `URPGHideBones` | `OneBossFight.Pack.HideBones.Defaults` |",
        "| Low | `ARPGBenchmarkRunner` | `OneBossFight.Benchmark.RunnerNoWorld` |",
        "| Medium | `RPGPerf::FireRadiusScale` | `OneBossFight.Performance.FireRadiusScaleClamp` |",
        "",
        "## Candidate gaps (ranked by risk, then source path)",
        "",
        "| Rank | Risk | Implementation file | Primary type(s) | Direct automation references |",
        "|---:|---|---|---|---|",
    ]
    for row in sorted(gaps, key=lambda item: (min((PRIORITY.get(t, 99) for t in item.types), default=99), item.path)):
        rank = min((PRIORITY.get(t, 99) for t in row.types), default=99)
        lines.append(f"| {rank} | {row.risk} | `{row.path}` | {', '.join(f'`{t}`' for t in row.types)} | none |")
    lines.extend(["", "## Units requiring manual type mapping", "", "These implementation files have no same-named header type detectable by the heuristic. They may implement free functions, adapters, or types declared in another header; the candidate-gap count above excludes them rather than claiming they are untested.", "", "| Implementation file | Primary header |", "|---|---|"])
    for row in rows:
        if not row.types:
            lines.append(f"| `{row.path}` | {row.primary_header} |")
    lines.extend(["", "## Reproduction", "", "`python -I Scripts/Tools/audit_source_test_coverage.py`", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(inventory()))
