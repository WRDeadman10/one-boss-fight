"""Version-pinned offline reproductions of A127 oracle gaps; no Unreal imports."""
import copy
import hashlib
import contextlib
import io
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[5]
peer = ROOT / 'Docs/BossCombatReview/Execution/Antigravity/test_shadow_wire_oracle.py'
pin = '34eb8b502025261bd460844e5167f41df398e5d29228b0a55eca3a9c7190fd4b'
assert hashlib.sha256(peer.read_bytes()).hexdigest() == pin, 'Peer changed: review new bytes before replay'
ns = runpy.run_path(str(peer), run_name='codex_offline_review')
baseline = ns['COMPLETE_31_FIELD_BASELINE_ROW']
oracle = ns['ReferenceWireContractOracle']
results = []

def probe(name, mutate, expected):
    row = copy.deepcopy(baseline)
    mutate(row)
    try:
        accepted, reason = oracle.validate_buffer([row])
        actual = accepted
    except Exception as exc:
        actual, reason = type(exc).__name__, str(exc)
    assert actual == expected, (name, actual, expected)
    results.append({'case': name, 'actual': actual, 'reason': reason})

probe('noncanonical leading-zero ordinal accepted', lambda r: r.update(observation_ordinal='01'), True)
probe('non-ASCII ordinal accepted', lambda r: r.update(observation_ordinal='١'), True)
probe('newline-terminated ordinal accepted', lambda r: r.update(observation_ordinal='1\n'), True)
probe('zero first observation ordinal accepted', lambda r: r.update(observation_ordinal='0'), True)
probe('uint32 crossing loop overflow accepted', lambda r: r['compiled_crossings'][0].update(loop_ordinal=2**32), True)
probe('int32 engine instance overflow accepted', lambda r: r.update(engine_instance=2**31), True)
probe('non-string status raises rather than rejects', lambda r: r.update(comparison_status=[]), 'TypeError')
probe('huge JSON integer raises rather than rejects', lambda r: r.update(current=10**400), 'OverflowError')
probe('source-permitted empty observed segment rejected', lambda r: r.update(observed_segment_asset=''), False)
# Execute the actual runner's failure branch with an in-memory contradictory case.
runner = ns['execute_harness']
runner.__globals__['build_test_cases'] = lambda: [{'id': 'CODEX-CONTRADICTION', 'title': 'runner failure check',
    'category': 'offline', 'payload': [copy.deepcopy(baseline)], 'oracle_expected': False}]
with contextlib.redirect_stdout(io.StringIO()):
    try:
        runner()
    except SystemExit as exc:
        runner_exit = exc.code
    else:
        runner_exit = 0
assert runner_exit == 1, runner_exit
print(json.dumps({'scope': 'offline A127 reproduction, not UE tests or parity', 'peer_sha256': pin,
                  'baseline_fields': len(baseline), 'runner_contradiction_exit': runner_exit,
                  'reproduced': len(results), 'results': results}, indent=2))
