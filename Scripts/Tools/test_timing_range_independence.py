from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EDITOR = ROOT / "Scripts" / "Editor"
MEASURED_NAMES = re.compile(r"^(?:dur|durs|duration|durations|rate|rates|measured|observed|actual|samples|mean|record|records|elapsed|hit_time|t_hit)$", re.I)


def range_expressions(source: str) -> list[ast.AST]:
    tree = ast.parse(source)
    found: list[ast.AST] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == "range_seconds":
                found.append(value)
    return found


def measured_dependencies(expression: ast.AST) -> set[str]:
    return {node.id for node in ast.walk(expression)
            if isinstance(node, ast.Name) and MEASURED_NAMES.match(node.id)}


def containing_scope(tree: ast.AST, lineno: int) -> ast.AST:
    candidates = [node for node in ast.walk(tree)
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module))
                  and getattr(node, "lineno", 0) <= lineno <= getattr(node, "end_lineno", 10**9)]
    return min(candidates, key=lambda node: getattr(node, "end_lineno", 10**9) - getattr(node, "lineno", 0))


def transitive_measured_dependencies(expression: ast.AST, scope: ast.AST) -> set[str]:
    assignments: dict[str, list[ast.AST]] = {}
    for node in ast.walk(scope):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.setdefault(target.id, []).append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments.setdefault(node.target.id, []).append(node.value)

    found: set[str] = set()
    pending = [node.id for node in ast.walk(expression) if isinstance(node, ast.Name)]
    visited: set[str] = set()
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        visited.add(name)
        if MEASURED_NAMES.match(name):
            found.add(name)
        for value in assignments.get(name, []):
            pending.extend(node.id for node in ast.walk(value) if isinstance(node, ast.Name))
    return found


class TimingRangeIndependenceTests(unittest.TestCase):
    def test_detector_catches_measured_duration_even_through_arithmetic(self) -> None:
        expression = ast.parse("[duration - 0.1, duration + 0.1]", mode="eval").body
        self.assertEqual(measured_dependencies(expression), {"duration"})

    def test_editor_driver_timing_ranges_do_not_use_measured_values(self) -> None:
        inspected = 0
        for path in sorted(EDITOR.glob("pie_*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for expression in range_expressions(source):
                inspected += 1
                direct = measured_dependencies(expression)
                scope = containing_scope(tree, getattr(expression, "lineno", 1))
                dependencies = direct | transitive_measured_dependencies(expression, scope)
                self.assertFalse(dependencies, f"{path.name}: {ast.unparse(expression)} depends on {sorted(dependencies)}")
        self.assertGreaterEqual(inspected, 15)


if __name__ == "__main__":
    unittest.main()
