"""Read-only peer validator import; generated negative fixtures live only in temporary directory."""
import copy, json, pathlib, runpy, tempfile
root = pathlib.Path('Docs/BossCombatReview/Execution/Antigravity')
api = runpy.run_path(str(root / 'audit_cue_source_inventory.py'), run_name='codex_probe')
original = json.loads((root / 'P1_CUE_SOURCE_INVENTORY.json').read_text(encoding='utf-8'))
cases = {
    'invented montage full path': lambda d: d['routes'][0].update(montage_path='/Game/NonexistentReview/Invented.Invented'),
    'invalid clock name': lambda d: d['routes'][0]['raw_timing_coordinates'].update(clock_type='UNRELATED_WALL_CLOCK'),
    'string nonfinite timing': lambda d: d['routes'][0]['raw_timing_coordinates'].update(active_start='NaN'),
    'nonexistent requirement': lambda d: d['routes'][0].update(requirements_ids=['BOSS-FAKE-999']),
    'empty required asset field': lambda d: d['routes'][0].update(clip_path=''),
    'zero route denominator': lambda d: d.update(routes=[], total_routes_count=0),
    'boolean timing value': lambda d: d['routes'][0]['raw_timing_coordinates'].update(active_start=True),
    'null timing value': lambda d: d['routes'][0]['raw_timing_coordinates'].update(active_start=None),
    'nested list nonfinite timing': lambda d: d['routes'][0]['raw_timing_coordinates'].update(active_start=[float('nan')]),
    'reversed window': lambda d: d['routes'][0]['raw_timing_coordinates'].update(active_start=9.0, active_end=0.1),
    'invented clip within approved root': lambda d: d['routes'][0].update(clip_path='/Game/OneBossFight/InventedReviewClip'),
}
with tempfile.TemporaryDirectory(prefix='codex_ag05_') as temp:
    path = pathlib.Path(temp) / 'negative.json'
    for label, change in cases.items():
        data=copy.deepcopy(original); change(data); path.write_text(json.dumps(data), encoding='utf-8')
        ok, details=api['validate_inventory'](str(path))
        print(f'{label}: validator_accepts={ok}')
