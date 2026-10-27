"""Document/source inventory and all83 work map, not runtime acceptance."""
import collections
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parent


def record(path):
    data = path.read_bytes()
    text = data.decode('utf-8-sig', errors='replace')
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
            'headings': [s for s in text.splitlines() if re.match(r'^#{1,3} ', s)]}


def save_new(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write('\n')


def main():
    files = sorted([*(ROOT / 'Documentation').rglob('*.md'),
                    *(ROOT / 'Docs/BossCombatReview').rglob('*.md')])
    inventory = [record(p) for p in files]
    snapshot = json.loads((OUT / 'Step2Preparation/AUDIT_CLASSIFICATIONS_2026-10-27.json').read_text())
    statuses = {r['id']: r for r in snapshot['rows']}
    reference = ROOT / 'Docs/BossCombatReview/Reference/06_REFERENCE_REQUIREMENTS.md'
    reconciliation = OUT / 'D03_RECONCILIATION_PROGRESS.md'
    commentary = {}
    for line in reconciliation.read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('| **BOSS-'):
            cells = [x.strip() for x in line.strip('|').split('|')]
            key = re.search(r'BOSS-[A-Z]+-\d{3}', cells[0])[0]
            commentary[key] = cells[2]
    stages = {'AWR': 'P6 awareness/adaptation', 'SEL': 'P6 selection/request seam P2',
              'EXE': 'P2 action identity/lifecycle', 'COM': 'P5 combo/recovery with P2 gates',
              'ANM': 'P1 readability/P2 timeline/motion', 'HIT': 'P3 resolution/P4 geometry',
              'MOV': 'P6 movement with P2 motion owner', 'PAC': 'P5 openings/P7 pacing',
              'DEF': 'P3 defense with P2 cleanup', 'PHS': 'P7 phases with P2 priority',
              'QA': 'Cross-cutting/P8 actual validation'}
    rows = []
    for line in reference.read_text(encoding='utf-8-sig').splitlines():
        if not line.startswith('| BOSS-'):
            continue
        cells = [x.strip() for x in line.strip('|').split('|')]
        assert len(cells) == 8, cells[0]
        key, feature, behavior, why, inputs, observable, verification, origin = cells
        rows.append({'id': key, 'feature': feature, 'required': True,
                     'provisional_classification': statuses[key]['provisional_D03_status'],
                     'expected_behavior': behavior, 'required_inputs': inputs,
                     'observable_result': observable, 'verification_method': verification,
                     'reference_origin': origin, 'prior_reconciliation': commentary[key],
                     'implementation_stage': stages[key.split('-')[1]],
                     'dependency': 'DD1 boss/participant data integration; timeline where applicable',
                     'current_final_acceptance': 'NOT_RECOUNTED; evidence review required',
                     'implementation_work_status': 'PLANNED; existing partial behavior retained'})
    assert len(rows) == 83 and len({r['id'] for r in rows}) == 83
    assert set(statuses) == {r['id'] for r in rows} == set(commentary)
    counts = dict(collections.Counter(r['provisional_classification'] for r in rows))
    assert counts == {'PARTIAL': 66, 'UNVERIFIED': 16, 'MISSING': 1}
    save_new('DOCUMENT_INVENTORY_2026-10-27.json',
             {'scope': 'All Markdown files read for inventory/hash/headings; not semantic acceptance of historical claims.',
              'file_count': len(files), 'files': inventory})
    save_new('ALL83_EXECUTION_LEDGER_2026-10-27.json',
             {'scope': 'Owner implementation work map, not new implementation or runtime proof.',
              'source_records': [record(reference), record(reconciliation)],
              'counts': counts, 'current_final_completion_percentage': None,
              'authoring_preference': 'Unreal Data Assets/Details first, custom wizard later',
              'rows': rows})
    print(json.dumps({'document_files_read': len(files), 'requirements': len(rows),
                      'classifications': counts, 'unique_ids': True,
                      'verification_and_stage_present_for_all': True}))


if __name__ == '__main__':
    main()
