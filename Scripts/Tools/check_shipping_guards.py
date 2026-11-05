#!/usr/bin/env python3
"""Find Shipping-visible uses of console variables declared non-Shipping-only.

This is a focused source guard check for the defect class from BUILD-222.
It deliberately handles CVar declarations, not arbitrary C++ name resolution.
Unknown preprocessor expressions are treated as active in both configurations
so they cannot hide a possible Shipping reference.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


CONFIGS = ("Development", "Shipping")
DECLARATION = re.compile(
    r"\b(?:TAutoConsoleVariable|FAutoConsoleVariableRef|FAutoConsoleVariable)"
    r"\s*(?:<[^;\n]+?>)?\s+(CVar[A-Za-z_][A-Za-z0-9_]*)\s*\(" 
)
IDENTIFIER = re.compile(r"\bCVar[A-Za-z_][A-Za-z0-9_]*\b")
DIRECTIVE = re.compile(r"^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)$")


@dataclass(frozen=True)
class Declaration:
    path: str
    line: int
    name: str


@dataclass(frozen=True)
class Finding:
    declaration: Declaration
    use_line: int
    use_text: str


def _strip_comments_and_literals(line: str) -> str:
    """Keep code identifiers while removing comments and quoted contents."""
    line = re.sub(r"//.*$", "", line)
    line = re.sub(r"/\*.*?\*/", "", line)
    line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
    line = re.sub(r"'(?:\\.|[^'\\])*'", "''", line)
    return line


def _condition_modes(kind: str, expression: str) -> frozenset[str]:
    expr = expression.strip()
    if kind == "ifdef":
        expr = f"defined({expr})"
    elif kind == "ifndef":
        expr = f"!defined({expr})"
    values = {}
    for config in CONFIGS:
        env = {
            "UE_BUILD_SHIPPING": config == "Shipping",
            "WITH_EDITOR": config == "Development",
            "WITH_EDITORONLY_DATA": config == "Development",
            "WITH_DEV_AUTOMATION_TESTS": config == "Development",
        }
        parsed = expr
        parsed = re.sub(r"defined\s*\(\s*(\w+)\s*\)", lambda m: "1" if env.get(m.group(1), True) else "0", parsed)
        parsed = re.sub(r"\b(UE_BUILD_SHIPPING|WITH_EDITORONLY_DATA|WITH_EDITOR|WITH_DEV_AUTOMATION_TESTS)\b",
                        lambda m: "1" if env[m.group(1)] else "0", parsed)
        parsed = parsed.replace("&&", " and ").replace("||", " or ")
        parsed = re.sub(r"!(?!=)", " not ", parsed)
        if re.fullmatch(r"[\s01()andornot]+", parsed):
            try:
                values[config] = bool(eval(parsed, {"__builtins__": {}}, {}))
            except (SyntaxError, TypeError, NameError):
                values[config] = True
        else:
            values[config] = True
    return frozenset(config for config, active in values.items() if active)


def _line_modes(lines: list[str]) -> list[frozenset[str]]:
    modes = frozenset(CONFIGS)
    stack: list[tuple[frozenset[str], frozenset[str], bool]] = []
    result = []
    for line in lines:
        clean = _strip_comments_and_literals(line)
        match = DIRECTIVE.match(clean)
        if not match:
            result.append(modes)
            continue
        directive, expression = match.group(1), match.group(2).strip()
        if directive in ("if", "ifdef", "ifndef"):
            parent = modes
            branch = _condition_modes(directive, expression)
            stack.append((parent, branch, False))
            modes = parent & branch
        elif directive == "elif" and stack:
            parent, previous, saw_else = stack[-1]
            if not saw_else:
                branch = _condition_modes("if", expression) - previous
                stack[-1] = (parent, previous | branch, False)
                modes = parent & branch
            else:
                modes = frozenset()
        elif directive == "else" and stack:
            parent, previous, _ = stack[-1]
            branch = parent - previous
            stack[-1] = (parent, parent, True)
            modes = branch
        elif directive == "endif" and stack:
            parent, _, _ = stack.pop()
            modes = parent
        result.append(modes)
    return result


def scan_text(text: str, path: str = "<memory>") -> tuple[list[Declaration], list[Finding]]:
    lines = text.splitlines()
    modes = _line_modes(lines)
    declarations: list[Declaration] = []
    for index, line in enumerate(lines):
        if "Development" not in modes[index] or "Shipping" in modes[index]:
            continue
        code = _strip_comments_and_literals(line)
        for match in DECLARATION.finditer(code):
            declarations.append(Declaration(path, index + 1, match.group(1)))

    findings: list[Finding] = []
    for declaration in declarations:
        for index, line in enumerate(lines):
            if index + 1 == declaration.line:
                continue
            if "Shipping" not in modes[index]:
                continue
            code = _strip_comments_and_literals(line)
            if re.search(rf"\b{re.escape(declaration.name)}\b", code):
                findings.append(Finding(declaration, index + 1, line.strip()))
    return declarations, findings


def scan_tree(root: Path) -> tuple[list[Declaration], list[Finding]]:
    declarations: list[Declaration] = []
    findings: list[Finding] = []
    for path in sorted((*root.rglob("*.h"), *root.rglob("*.cpp"))):
        rel = path.as_posix()
        found_declarations, found_findings = scan_text(path.read_text(encoding="utf-8", errors="replace"), rel)
        declarations.extend(found_declarations)
        findings.extend(found_findings)
    return declarations, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("Source"), help="Source tree to scan")
    args = parser.parse_args()
    declarations, findings = scan_tree(args.source)
    print(f"[SHIPPING_GUARDS] declarations={len(declarations)} shipping_uses={len(findings)}")
    for declaration in declarations:
        print(f"DECL {declaration.path}:{declaration.line} {declaration.name}")
    for finding in findings:
        d = finding.declaration
        print(f"USE {d.path}:{d.line} {d.name} -> {finding.use_line}: {finding.use_text}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
