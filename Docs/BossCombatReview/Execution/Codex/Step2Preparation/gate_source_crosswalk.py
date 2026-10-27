"""Read source as data; emit a static review aid. Never import/run PIE scripts."""
import ast
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[5]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    runner = ROOT / 'Scripts/RunDrivers.ps1'
    raw = runner.read_bytes()
    registry = raw.decode('utf-8-sig').split('$drivers = @(', 1)[1].split('\n)', 1)[0]
    definitions = re.findall(r"N = '([^']+)';\s+K = '([RS])'; Min = (\d+)", registry)
    rows = []
    for name, kind, minimum in definitions:
        path = ROOT / 'Scripts/Editor' / (name + '.py')
        data = path.read_bytes()
        tree = ast.parse(data.decode('utf-8-sig'), filename=str(path))
        prefixes = []
        finals = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'log' for t in node.targets):
                for child in ast.walk(node.value):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str) and re.fullmatch(r'\[[^\]]+\] ', child.value):
                        prefixes.append({'line': node.lineno, 'prefix': child.value})
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'log':
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str) and child.value.startswith(('RESULT ', 'SUMMARY ')):
                        finals.append({'line': node.lineno, 'format_literal': child.value})
        rows.append({'driver': name, 'kind': kind, 'minimum': int(minimum),
                     'source': path.relative_to(ROOT).as_posix(), 'sha256': sha(data),
                     'log_assignment_prefixes': prefixes, 'final_log_literals': finals,
                     'needs_manual_mapping': len(prefixes) != 1 or not finals})
    assert len(rows) == 40 and len({r['driver'] for r in rows}) == 40
    print(json.dumps({'scope': 'Static AST/registry extraction only; no driver execution, reachability, runtime attribution or acceptance proof.',
                      'runner_sha256': sha(raw), 'rows': rows}, indent=2))


if __name__ == '__main__':
    main()
