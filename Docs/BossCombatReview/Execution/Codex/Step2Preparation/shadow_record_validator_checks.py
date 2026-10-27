"""Offline staged-driver schema checks. No Unreal import or editor execution.

Extracts only validate_records via AST; does not execute the driver/module top level.
Synthetic payloads test rejection behavior, not real playback or full semantic parity.
"""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[5]
DRAFT = ROOT / 'Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py'
PRODUCER = ROOT / 'Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp'
source = DRAFT.read_bytes()
tree = ast.parse(source, filename=str(DRAFT))
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_records')
namespace = {'json': json, 'math': math, 're': re}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(DRAFT), 'exec'), namespace)
validate = namespace['validate_records']

BASE = dict(world_session='SyntheticWorld', encounter_instance='SyntheticEncounter',
            participant_slot='Boss', source_asset='/Game/SyntheticFixture', variant='Fixture',
            coverage_scope='SYNTHETIC_ONLY', asset_sha256='a' * 64, adapter_sha256='b' * 64,
            previous=0., current=.1, game_time=1., actual_rate=1., observation_ordinal='1',
            generation=1, compiled_crossings=[], legacy_snapshot={}, comparison_status='MATCH')


class Buffer:
    def __init__(self, rows, count=None):
        self.rows = rows
        self.count = len(rows) if count is None else count

    def get_record_count(self):
        return self.count

    def get_record_json_for_test(self, index):
        return json.dumps(self.rows[index])


passed = []


def check(name, buffer, expected):
    actual = validate(buffer)
    assert actual is expected, (name, actual, expected)
    passed.append(name)


# Independently inspect the actual producer's wire declaration; not C++ execution.
producer_bytes = PRODUCER.read_bytes()
assert 'SetStringField(TEXT("observation_ordinal"), LexToString(O.Sample))' in producer_bytes.decode('utf-8')
check('valid synthetic record with producer decimal-string ordinal', Buffer([BASE]), True)
check('no samples reject', Buffer([]), False)
check('bool count reject', Buffer([BASE], True), False)
check('over-cap count reject before access', Buffer([], 4097), False)
for field, value in [('current', True), ('game_time', None), ('actual_rate', float('nan')),
                     ('previous', float('inf')), ('observation_ordinal', 1),
                     ('observation_ordinal', 1.9), ('observation_ordinal', True),
                     ('observation_ordinal', '1.9'), ('observation_ordinal', '01'),
                     ('observation_ordinal', ' 1'), ('observation_ordinal', '0'),
                     ('observation_ordinal', '18446744073709551616'),
                     ('generation', True), ('generation', 0), ('generation', 0x100000000),
                     ('asset_sha256', 123), ('adapter_sha256', 'bad'),
                     ('comparison_status', 'INVALID_RUN'), ('authoritative_action', {}),
                     ('compiled_crossings', {}), ('legacy_snapshot', [])]:
    row = copy.deepcopy(BASE)
    row[field] = value
    check(f'reject {field}={value!r}', Buffer([row]), False)
check('non-object JSON rejects', Buffer([[]]), False)
class MalformedBuffer(Buffer):
    def get_record_json_for_test(self, index):
        return '{broken JSON'


check('malformed JSON rejects', MalformedBuffer([BASE]), False)
check('repeated ordinal rejects', Buffer([BASE, BASE]), False)
row = dict(BASE, observation_ordinal='2', actual_rate=-1., comparison_status='INCONCLUSIVE_SAMPLING')
check('strictly newer reverse inconclusive row is diagnostic', Buffer([BASE, row]), True)
check('uint64 above JS safe integer retains precision', Buffer([dict(BASE, observation_ordinal='9007199254740993')]), True)
check('uint64 max retains precision', Buffer([dict(BASE, observation_ordinal='18446744073709551615')]), True)
print(json.dumps({'scope': 'offline staged-validator checks; NOT Unreal/playback/semantic parity proof',
                  'draft_sha256': hashlib.sha256(source).hexdigest(),
                  'producer_sha256': hashlib.sha256(producer_bytes).hexdigest(),
                  'passed': len(passed), 'total': len(passed), 'checks': passed}, indent=2))
