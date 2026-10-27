"""Read-only audit classification recount; never treats old labels as live acceptance.

Optional snapshot writes are new files in this helper's own directory only.
No Unreal, network, git, Source/Config/asset writes or calendar estimates.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
INPUTS = {
    'reference': 'Docs/BossCombatReview/Reference/06_REFERENCE_REQUIREMENTS.md',
    'historical_audit': 'Docs/BossCombatReview/ExistingBossAudit/03_REFERENCE_COMPARISON_MATRIX.md',
    'provisional_D03': 'Docs/BossCombatReview/Execution/Codex/D03_RECONCILIATION_PROGRESS.md',
}


def collect(kind, relative):
    raw = (ROOT / relative).read_bytes()
    rows = {}
    for line_number, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
        if not re.match(r'^\|\s*(?:\*\*)?BOSS-[A-Z]+-\d{3}', line):
            continue
        cells = [x.strip() for x in line.strip().strip('|').split('|')]
        if kind == 'provisional_D03' and (len(cells) < 5 or '->' not in cells[1]):
            continue  # The short owner-decision proposal table is not the row companion.
        ident = re.search(r'BOSS-[A-Z]+-\d{3}', cells[0]).group()
        if ident in rows:
            raise ValueError(f'duplicate {ident} in {relative}')
        status = None
        if kind == 'historical_audit':
            status = cells[4]
            if status not in {'IMPLEMENTED', 'PARTIAL', 'MISSING', 'UNVERIFIED', 'NOT APPLICABLE'}:
                raise ValueError(f'unknown audit status: {ident}: {status}')
        elif kind == 'provisional_D03':
            status = cells[1].split('->', 1)[1].strip().split(';', 1)[0]
            if status not in {'IMPLEMENTED', 'PARTIAL', 'MISSING', 'UNVERIFIED'}:
                raise ValueError(f'unknown provisional status: {ident}: {status}')
        rows[ident] = {'status': status, 'line': line_number}
    if len(rows) != 83:
        raise ValueError(f'{relative}: expected83 unique rows, found{len(rows)}')
    return {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--new-snapshot', help='New JSON filename in this helper directory; refuses overwrite')
    args = parser.parse_args()
    sources = {k: collect(k, p) for k, p in INPUTS.items()}
    ids = set(sources['reference']['rows'])
    if any(set(v['rows']) != ids for v in sources.values()):
        raise ValueError('reference/audit/provisional ID sets differ')
    result = {
        'scope': 'source-pinned documentary classifications; NOT live acceptance, gameplay tests or completion percentage',
        'reference_ids': 83,
        'id_sets_equal': True,
        'historical_counts': dict(Counter(x['status'] for x in sources['historical_audit']['rows'].values())),
        'provisional_D03_counts': dict(Counter(x['status'] for x in sources['provisional_D03']['rows'].values())),
        'owner_target': 'ALL83 implemented with evidence; historical NOT APPLICABLE and pending-waiver text superseded',
        'current_accepted_83_row_percentage': None,
        'calendar_finish_date': None,
        'sources': {k: {p: v[p] for p in ('path', 'sha256')} for k, v in sources.items()},
        'rows': [{
            'id': ident,
            'historical_status': sources['historical_audit']['rows'][ident]['status'],
            'provisional_D03_status': sources['provisional_D03']['rows'][ident]['status'],
            'source_lines': {k: v['rows'][ident]['line'] for k, v in sources.items()},
            'required': True,
            'current_final_acceptance': 'NOT_ESTABLISHED_BY_THIS_RECOUNT',
        } for ident in sorted(ids)],
    }
    if args.new_snapshot:
        dest = (HERE / args.new_snapshot).resolve()
        if dest.parent != HERE or dest.suffix != '.json':
            raise ValueError('snapshot must be a new .json file directly in helper directory')
        with dest.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
