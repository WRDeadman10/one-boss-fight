"""Read a saved gate log and emit an error inventory; no engine or source changes."""
import collections
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[5]
LOG = ROOT / 'Docs/BossCombatReview/Execution/Claude/Evidence/exports/gate_2026-10-27/gate_engine_log_slice_from_1405.log'


def main():
    data = LOG.read_bytes()
    lines = data.decode('utf-8-sig').splitlines()
    finals = []
    for number, line in enumerate(lines, 1):
        match = re.search(r'LogPython: \[([^\]]+)\] (?:RESULT \d+/\d+ passed|SUMMARY \d+ checks, \d+ failed)', line)
        if match:
            finals.append({'line': number, 'tag': match[1]})
    errors = []
    groups = collections.defaultdict(list)
    for number, line in enumerate(lines, 1):
        match = re.search(r'(\w+): Error: (.*)', line)
        if not match:
            continue
        channel, body = match.groups()
        # Normalize only runtime instance numbers; preserve semantic text and asset identities.
        signature = re.sub(r'_C_\d+\b', '_C_<instance>', body)
        signature = re.sub(r'TRASH_', '<trash>', signature)
        before = next((f for f in reversed(finals) if f['line'] < number), None)
        after = next((f for f in finals if f['line'] > number), None)
        item = {'line': number, 'channel': channel, 'raw': line,
                'previous_final': before, 'next_final': after}
        errors.append(item)
        groups[(channel, signature)].append(number)
    group_rows = [{'channel': channel, 'signature': signature, 'count': len(numbers),
                   'first_line': numbers[0], 'last_line': numbers[-1], 'lines': numbers}
                  for (channel, signature), numbers in groups.items()]
    group_rows.sort(key=lambda g: (-g['count'], g['first_line']))
    print(json.dumps({'scope': 'Saved-log inventory only. Neighboring finals are navigation, not causal/driver/teardown attribution or baseline equivalence. No errors waived.',
                      'source': LOG.relative_to(ROOT).as_posix(),
                      'source_bytes': len(data), 'source_sha256': hashlib.sha256(data).hexdigest(),
                      'total_errors': len(errors), 'channels': dict(collections.Counter(e['channel'] for e in errors)),
                      'final_count': len(finals), 'normalized_groups': group_rows, 'errors': errors}, indent=2))


if __name__ == '__main__':
    main()
