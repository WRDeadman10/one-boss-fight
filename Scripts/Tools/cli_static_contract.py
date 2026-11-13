"""BP-04 hotfix (X-2288, reworked per X-2290): a conservative static contract that `--help` exits inside argparse before
any side effect. The analysed tool is never imported or executed; only its source is parsed with `ast`.

A tool is PROVEN only if every rule holds. Anything not explicitly allowed fails closed (UNPROVEN):

 Import time (module top level, recursively for local sibling modules it imports, resolved next to the analysed file):
  1. Allowed top-level statements: `import`/`from ... import` of standard-library modules or of local sibling modules that
     themselves pass the import-time rules (checked recursively); docstrings; the `sys.path.insert(...)` guard;
     assignments and annotated assignments whose every call is a known pure constructor/method; function definitions
     whose decorators and default values are pure; class definitions whose decorators, bases and body obey these same
     rules; and the `if __name__ == "__main__":` dispatch block. Any other statement (if/try/for/with/expression call)
     fails.
  2. Non-standard-library, non-local imports fail closed.

 `--help` path:
  3. The `__main__` block contains only `main()`, `raise SystemExit(main())` or `sys.exit(main())`.
  4. `main` is a plain function whose decorators are on SAFE_DECORATORS and whose defaults are constants.
  5. `main.body` is read **sequentially, statement by statement**. Before the parse statement, every statement must be a
     direct assignment or expression statement (no if/for/while/with/try/match, no nested def/class/lambda/comprehension)
     whose every call is parser setup. The parse statement itself must be a direct assignment or expression statement
     whose outermost call is `parse_args`/`parse_known_args`/`parse_intermixed_args`.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}

PURE_CALLS = {
    "Path", "compile", "frozenset", "set", "tuple", "dict", "list", "namedtuple", "TypeVar", "field", "float", "int",
    "str", "bool", "Decimal", "Fraction", "MappingProxyType", "with_name", "with_suffix", "escape", "join", "resolve",
    "sorted", "range", "len",
}
PURE_DECORATORS = {"dataclass", "staticmethod", "classmethod", "property", "lru_cache", "cache", "redaction_scope"}
PARSER_SETUP_CALLS = {
    "ArgumentParser", "add_argument", "add_argument_group", "add_mutually_exclusive_group", "add_subparsers",
    "add_parser", "set_defaults", "add_redact_argument", "Path", "join", "dedent", "strip", "format", "resolve",
    "with_name", "with_suffix", "splitlines", "cwd", "str",
}
PARSE_CALLS = {"parse_args", "parse_known_args", "parse_intermixed_args"}
SAFE_DECORATORS = {"redaction_scope"}
NESTING = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp,
           ast.GeneratorExp)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
    return None


def _calls(node: ast.AST) -> list[ast.Call]:
    return [n for n in ast.walk(node) if isinstance(n, ast.Call)]


def _has_nesting(node: ast.AST) -> bool:
    return any(isinstance(n, NESTING) for n in ast.walk(node))


def _is_stdlib_constant_getattr(call: ast.Call) -> bool:
    """`getattr(os, "O_BINARY", 0)`: a constant attribute lookup on a standard-library module name, with constant
    arguments only. This is the single getattr form treated as pure (atomic_io's flag probe)."""
    return (_call_name(call) == "getattr" and isinstance(call.func, ast.Name) and len(call.args) in (2, 3)
            and not call.keywords and isinstance(call.args[0], ast.Name) and call.args[0].id in STDLIB
            and all(isinstance(a, ast.Constant) for a in call.args[1:]))


def _only_calls(node: ast.AST, allowed: set[str]) -> list[str]:
    return sorted({_call_name(c) or "<dynamic>" for c in _calls(node) if not _is_stdlib_constant_getattr(c)} - allowed)


# X-2292: guards are matched by EXACT AST shape (ast.dump equality), so no extra terms, calls or other paths can hide in them.
_PATH_GUARD_SHAPES = {
    ast.dump(ast.parse(f"{alias}.path.insert(0, str(Path(__file__).resolve().parent))", mode="eval").body)
    for alias in ("sys", "_sys")
}
_MAIN_GUARD_SHAPES = {ast.dump(ast.parse(f'__name__ == {quote}__main__{quote}', mode="eval").body) for quote in ('"', "'")}


def _is_path_guard(node: ast.stmt) -> bool:
    """Only the repository-local guard `sys.path.insert(0, str(Path(__file__).resolve().parent))` (or `_sys.`)."""
    return isinstance(node, ast.Expr) and ast.dump(node.value) in _PATH_GUARD_SHAPES


def _is_main_guard(node: ast.stmt) -> bool:
    """Only `if __name__ == "__main__":` exactly (one Eq, one string constant, no calls or chained terms), no else."""
    return isinstance(node, ast.If) and ast.dump(node.test) in _MAIN_GUARD_SHAPES and not node.orelse


def _decorator_name(node: ast.AST) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _import_ok(node: ast.stmt, seen: set[str], base: Path) -> tuple[bool, str]:
    names = []
    if isinstance(node, ast.Import):
        names = [alias.name for alias in node.names]
    elif isinstance(node, ast.ImportFrom):
        if node.level:
            return False, f"line {node.lineno}: relative import"
        names = [node.module or ""]
    for name in names:
        root = name.split(".")[0]
        if root in STDLIB:
            continue
        local = base / f"{root}.py"
        if local.is_file():
            if root in seen:
                continue
            ok, why = import_time_safe(local, seen | {root})
            if not ok:
                return False, f"line {node.lineno}: local import {root!r} is not import-safe ({why})"
            continue
        if root == "Scripts":  # package-style self import, e.g. Scripts.Tools.x
            leaf = name.split(".")[-1]
            local = base / f"{leaf}.py"
            if local.is_file():
                ok, why = import_time_safe(local, seen | {leaf})
                if ok:
                    continue
                return False, f"line {node.lineno}: local import {leaf!r} is not import-safe ({why})"
        return False, f"line {node.lineno}: import {name!r} is neither standard library nor a local sibling"
    return True, ""


def _body_ok(body: list[ast.stmt], seen: set[str], where: str, base: Path) -> tuple[bool, str]:
    for node in body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            ok, why = _import_ok(node, seen, base)
            if not ok:
                return False, why
            continue
        if isinstance(node, ast.Pass):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # docstring
        if _is_path_guard(node):
            continue
        if _is_main_guard(node) and where == "module":
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            if _has_nesting(node):
                return False, f"{where} line {node.lineno}: nested definition in an assignment"
            bad = _only_calls(node, PURE_CALLS)
            if bad:
                return False, f"{where} line {node.lineno}: calls {bad}"
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if _decorator_name(decorator) not in PURE_DECORATORS:
                    return False, f"{where} line {node.lineno}: decorator {_decorator_name(decorator)!r} is not known pure"
            defaults = node.args.defaults + [d for d in node.args.kw_defaults if d is not None]
            for default in defaults:
                if _only_calls(default, PURE_CALLS) or _has_nesting(default):
                    return False, f"{where} line {node.lineno}: default value of {node.name}() calls code"
            continue
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if _decorator_name(decorator) not in PURE_DECORATORS:
                    return False, f"{where} line {node.lineno}: class decorator {_decorator_name(decorator)!r} is not known pure"
            if any(_only_calls(base, PURE_CALLS) for base in node.bases):
                return False, f"{where} line {node.lineno}: class base calls code"
            ok, why = _body_ok(node.body, seen, f"class {node.name}", base)
            if not ok:
                return False, why
            continue
        return False, f"{where} line {node.lineno}: {type(node).__name__} statement is not provably side-effect free"
    return True, ""


def import_time_safe(path: Path, seen: set[str] | None = None) -> tuple[bool, str]:
    """Rules 1-2: importing the module runs nothing but definitions and pure constants (recursively for local imports)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return _body_ok(tree.body, seen if seen is not None else {path.stem}, "module", Path(path).resolve().parent)


def analyse(path: Path) -> tuple[bool, str]:
    """Return (proven, reason). `proven` means `--help` provably exits inside argparse before any side effect."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    ok, why = _body_ok(tree.body, {path.stem}, "module", Path(path).resolve().parent)
    if not ok:
        return False, why
    guards = [n for n in tree.body if _is_main_guard(n)]
    if len(guards) != 1:
        return False, "expected exactly one `if __name__ == \"__main__\":` block"
    for stmt in guards[0].body:
        call = stmt.value if isinstance(stmt, ast.Expr) else stmt.exc if isinstance(stmt, ast.Raise) else None
        names = [_call_name(c) for c in _calls(stmt)] if call is not None else ["<statement>"]
        if call is None or not set(names) <= {"main", "SystemExit", "exit"} or "main" not in names or _has_nesting(stmt):
            return False, f"__main__ block line {stmt.lineno} does more than dispatch to main()"
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    if len(mains) != 1:
        return False, "expected exactly one top-level main()"
    main = mains[0]
    for decorator in main.decorator_list:
        if _decorator_name(decorator) not in SAFE_DECORATORS:
            return False, f"main decorator {_decorator_name(decorator)!r} is not on the safe list"
    for default in main.args.defaults + [d for d in main.args.kw_defaults if d is not None]:
        if not isinstance(default, ast.Constant):
            return False, "main() has a non-constant default value"
    for stmt in main.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue  # docstring
        if not isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.Expr)) or _has_nesting(stmt):
            return False, f"main() line {stmt.lineno}: {type(stmt).__name__} before parse_args (only direct setup allowed)"
        value = stmt.value
        if isinstance(value, ast.Call) and _call_name(value) in PARSE_CALLS:
            bad = _only_calls(value, PARSER_SETUP_CALLS | PARSE_CALLS)
            if bad:
                return False, f"main() line {stmt.lineno}: parse statement also calls {bad}"
            return True, "direct, unconditional parser setup precedes a direct parse call; import time is side-effect free"
        bad = _only_calls(stmt, PARSER_SETUP_CALLS)
        if bad:
            return False, f"main() line {stmt.lineno}: calls {bad} before parse_args"
    return False, "main() never reaches a direct parse_args statement"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Report which Scripts/Tools tools satisfy the static --help contract.")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    targets = args.paths or sorted(p for p in HERE.glob("*.py") if not p.stem.startswith("test_"))
    for target in targets:
        proven, reason = analyse(target)
        print(f"{'PROVEN' if proven else 'UNPROVEN'}\t{target.stem}\t{reason}")
