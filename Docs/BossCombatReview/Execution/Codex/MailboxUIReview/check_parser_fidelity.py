"""Read-only parser-fidelity review. No module top-level/server/browser execution.

AST-extracts MailboxParser only and parses a temporary immutable copy of mailbox bytes.
This does not test rendered layout, deployed version, selection or composer behavior.
"""
import argparse
import ast
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=str(ROOT / 'Scripts/MailboxViewer.py'))
    parser.add_argument('--mailbox', default=str(ROOT / 'Documentation/TEAM_MAILBOX.md'))
    args = parser.parse_args()
    source = Path(args.source).read_bytes()
    raw = Path(args.mailbox).read_bytes()
    tree = ast.parse(source.decode('utf-8-sig'), filename=args.source)
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MailboxParser')
    namespace = {'os': os, 're': re, 'datetime': datetime.datetime, 'MAILBOX_PATH': 'UNUSED_REAL_PATH'}
    exec(compile(ast.Module(body=[node], type_ignores=[]), args.source, 'exec'), namespace)
    with tempfile.TemporaryDirectory(prefix='codex-parser-review-') as tmp:
        mailbox = Path(tmp) / 'snapshot.md'
        mailbox.write_bytes(raw)
        parsed = namespace['MailboxParser'].parse_file(str(mailbox))
    text = raw.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    heads = list(re.finditer(r'(?m)^### \[(?P<id>[A-Z]+-\d+)\][^\r\n]*', text))
    expected = []
    for i, head in enumerate(heads):
        end = heads[i+1].start() if i+1 < len(heads) else len(text)
        body = text[head.end():end].strip()
        expected.append({'id': head['id'], 'body_sha256': digest(body.encode()), 'body_chars': len(body)})
    actual = [{'id': m['id'], 'body_sha256': digest(m['body'].encode()), 'body_chars': len(m['body'])}
              for m in parsed['messages']]
    counts = Counter(r['id'] for r in actual)
    duplicates = sorted(k for k, v in counts.items() if v != 1)
    byid = {r['id']: r for r in actual}
    baseline = json.loads((HERE / 'VIEWER_BASELINE_5f88c092_2026-10-27.json').read_text(encoding='utf-8'))
    changed = [r['id'] for r in baseline['records'] if byid.get(r['id']) != r]
    latest_expected = expected[-1]['id'] if expected else None
    latest_actual = parsed['latest']['id'] if parsed['latest'] else None
    ok = actual == expected and not duplicates and not changed and latest_expected == latest_actual
    print(json.dumps({
        'scope': 'AST parser/text fidelity ONLY; NOT rendered/composer/deployed UI proof',
        'source_sha256': digest(source), 'mailbox_sha256': digest(raw),
        'raw_headers': len(expected), 'parser_records': len(actual),
        'ordered_ids_and_normalized_bodies_equal': actual == expected,
        'baseline_records': len(baseline['records']), 'baseline_changed_or_missing': changed,
        'duplicate_ids': duplicates, 'latest_expected': latest_expected, 'latest_actual': latest_actual,
        'passed': ok,
    }, indent=2))
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
