# BOSS-AWR-005 tool proof (lead, Claude): authors ONE NEW card with MaxVerticalDeltaCm = 50 through Antigravity's author_move_cards.execute_authoring (apply + save, its own readback), reloads the saved asset and logs the field; then a dry run with a negative limit must be refused. NEW asset only, refuses when it exists.
# Run: run_editor_script.ps1 -Script <this file> -OutDir <absolute dir> -Task awr005_tools -NullRhi 1
import copy
import importlib.util
import json
import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/'
TOOL = ROOT + 'Antigravity/MoveCards/author_move_cards.py'
SET = ROOT + 'Antigravity/MoveCards/move_cards_f5_set.json'
MOVE_ID = 'Move_Sevarog_VerticalProof_AWR005'
DEST = '/Game/OneBossFight/FrameworkProof/Cards/' + MOVE_ID


def tag(t, p):
    unreal.log('[AWR005_%s] %s' % (t, json.dumps(p, default=str)))


if unreal.EditorAssetLibrary.does_asset_exist(DEST):
    unreal.log_error('[AWR005_FATAL] destination exists, refusing: ' + DEST)
    raise SystemExit('exists')
spec = importlib.util.spec_from_file_location('author_move_cards', TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
data = json.load(open(SET, encoding='utf-8-sig'))
pool = data.get('cards', data) if isinstance(data, dict) else data
src = [c for c in pool if c.get('MoveId') == 'Move_Sevarog_SwingSlow_F5'][0]
card = copy.deepcopy(src)
card['MoveId'] = MOVE_ID
card['MaxVerticalDeltaCm'] = 50.0
bad = copy.deepcopy(card)
bad['MoveId'] = MOVE_ID + '_Bad'
bad['MaxVerticalDeltaCm'] = -1.0
rc_bad = mod.execute_authoring(cards_data=[bad], apply_mode=False, save_mode=False)
tag('NEGATIVE_DRY_RUN', {'return_code': rc_bad, 'expected': 'non-zero'})
if rc_bad == 0:
    unreal.log_error('[AWR005_FATAL] negative limit was accepted')
    raise SystemExit('bad accepted')
rc = mod.execute_authoring(cards_data=[card], apply_mode=True, save_mode=True)
tag('AUTHORING', {'return_code': rc})
if rc != 0:
    raise SystemExit('authoring failed')
asset = unreal.load_asset(DEST)
s = asset.get_editor_property('spec')
got = float(s.get_editor_property('max_vertical_delta_cm'))
tag('READBACK', {'move_id': str(s.get_editor_property('move_id')), 'max_vertical_delta_cm': got})
if abs(got - 50.0) > 1e-4:
    raise SystemExit('readback mismatch')
# an old card (authored before the field) must still read 0 = no limit
old = unreal.load_asset('/Game/OneBossFight/FrameworkProof/Cards/Move_Sevarog_SwingSlow_F5')
tag('OLD_CARD', {'max_vertical_delta_cm': float(old.get_editor_property('spec').get_editor_property('max_vertical_delta_cm'))})
tag('END', {'written': [DEST]})
