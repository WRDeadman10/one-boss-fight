from pathlib import Path
import importlib.util,json,sys
import unreal
R=Path(__file__).resolve().parent
p=R.parents[2]/'Antigravity/HitWindowProbe/probe_weapon_motion.py'
# Explicit fixed workspace path, no source/tool edits and no input changes.
p=Path('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/HitWindowProbe/probe_weapon_motion.py')
spec=importlib.util.spec_from_file_location('approved_A243_probe',p);probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
value=probe.resolve_world_space_enum(unreal)
fallback=type(value) is int
observed={'enum_repr':repr(value),'enum_type':type(value).__name__,'integer_fallback':fallback,'measurement_certification':'UNKNOWN' if fallback else 'reflected WORLD enum observed'}
(R/'enum_observed.json').write_text(json.dumps(observed,indent=2)+'\n',encoding='utf-8')
print('[PROBE_ENUM] '+json.dumps(observed))
result=probe.run_probe(output_json_path=str(R/'probe_summary.json'))
print('[PROBE_RUNNER_EXIT] '+str(result))
if result:raise RuntimeError('Approved probe returned failure '+str(result))
