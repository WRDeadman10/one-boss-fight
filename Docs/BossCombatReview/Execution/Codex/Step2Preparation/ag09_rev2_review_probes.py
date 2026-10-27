"""Independent A128 review; original A127 probes remain immutable and version-pinned."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import runpy

root = Path(__file__).resolve().parents[5]
base = root / 'Docs/BossCombatReview/Execution'
peer = base / 'Antigravity/test_shadow_wire_oracle.py'
assert hashlib.sha256(peer.read_bytes()).hexdigest() == '5a65c79af93a3dbf79070cc52c9dceb08f1d10733ca855bc5293a903d593e7f5'
ns = runpy.run_path(str(peer), run_name='codex_rev2_review')
row = ns['COMPLETE_31_FIELD_BASELINE_ROW']
oracle = ns['ReferenceWireContractOracle']
out = []
for key, value in [('observation_ordinal','01'), ('observation_ordinal','١'),
                   ('observation_ordinal','1\n'), ('observation_ordinal','0'),
                   ('engine_instance',2**31), ('comparison_status',[]), ('current',10**400)]:
    test = copy.deepcopy(row); test[key] = value
    accepted, _ = oracle.validate_buffer([test])
    assert accepted is False, key
    out.append(key + ': rejected without exception')
test = copy.deepcopy(row); test['compiled_crossings'][0]['loop_ordinal'] = 2**32
assert oracle.validate_buffer([test])[0] is False
test = copy.deepcopy(row); test['observed_segment_asset'] = ''
assert oracle.validate_buffer([test])[0] is True
for key in row:
    test = copy.deepcopy(row); del test[key]
    assert oracle.validate_buffer([test])[0] is False, key
cpp = (base / 'Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp').read_text()
keys = set(re.findall(r'Row->Set\w*Field\(TEXT\("([^"]+)"\)', cpp))
assert keys == set(row) == ns['INDEPENDENT_PRODUCER_31_KEYS'], (keys ^ set(row))
report = (base / 'Antigravity/P1_SHADOW_WIRE_ORACLE_REPORT.md').read_text(encoding='utf-8')
fixture_json = json.loads(re.search(r'```json\s*(.*?)\s*```', report, re.S).group(1))
assert fixture_json == row, 'Report baseline differs from actual fixture'
generation_results = []
for gen in [0, 2**31, 2**32-1]:
    test = copy.deepcopy(row); test['generation'] = gen
    generation_results.append({'generation':gen, 'accepted':oracle.validate_buffer([test])[0]})
assert [r['accepted'] for r in generation_results] == [True, False, False]
# Reproduce the actual pre-AST frozen-pin comparison with fake observed drift only.
node = next(n for n in ast.parse(peer.read_bytes()).body if isinstance(n, ast.For))
drift_ns = {'EXPECTED_FROZEN_PINS': ns['EXPECTED_FROZEN_PINS'],
            'OBSERVED_PINS': {**ns['OBSERVED_PINS'], 'pie_timeline_shadow.py': '0'*64}}
try:
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'fake_pin_comparison', 'exec'), drift_ns)
except RuntimeError:
    pin_drift_rejected = True
else:
    pin_drift_rejected = False
assert pin_drift_rejected
review = (base / 'Codex/AG09_A127_REVIEW.md').read_bytes()
print(json.dumps({'scope':'offline source-wire review, not Unreal/parity',
    'original_nine_probe_corrections_verified':9, 'required_key_deletions_rejected':len(row),
    'producer_key_set_equal':True, 'report_fixture_equal':True, 'fake_pin_drift_rejected':pin_drift_rejected,
    'remaining_generation_domain_results':generation_results,
    'review_raw_sha256':hashlib.sha256(review).hexdigest(),
    'review_lf_sha256':hashlib.sha256(review.replace(b'\r\n',b'\n')).hexdigest()}, indent=2))
