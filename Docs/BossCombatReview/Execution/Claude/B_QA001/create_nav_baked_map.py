# QA-001 helper (lead, Claude): a NEW map = the CUE proof map with its navmesh BAKED into the saved level, so a STANDALONE game (no editor, no PIE nav build) can start the framework fixture (it waits for the navmesh and fails closed without one).
# Loads the source map, builds the navigation (console RebuildNavigation), waits (a tick callback) until no build runs for 30 ticks, saves the world under the NEW name, quits. The source map file is never saved. Run with run_editor_script.ps1 -PyCmd 1 -NullRhi 0.
import json
import os
import sys
import unreal

sys.path.insert(0, 'C:/UnrealProject/OneBossFight/Scripts/Editor')
import rpg_content_lib as L  # noqa: E402

SRC = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofCUE'
DST = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofQA001'


def tag(t, payload):
    unreal.log('[QA001NAV_%s] %s' % (t, json.dumps(payload, default=str)))


if unreal.EditorAssetLibrary.does_asset_exist(DST):
    tag('FATAL', {'why': 'destination exists, refusing', 'dst': DST})
    raise SystemExit('destination exists')
if not unreal.EditorLevelLibrary.load_level(SRC):
    raise SystemExit('load_level failed')
world = unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'RebuildNavigation')
state = {'n': 0, 'idle': 0, 'handle': None, 'done': False}


def tick(_dt):
    if state['done']:
        return
    state['n'] += 1
    try:
        building = bool(unreal.NavigationSystemV1.is_navigation_being_built(world))
    except Exception as e:  # noqa
        tag('API', {'error': str(e)})
        building = False
    state['idle'] = 0 if building else state['idle'] + 1
    if state['n'] % 60 == 0:
        tag('WAIT', {'ticks': state['n'], 'building': building})
    if state['idle'] >= 30 and state['n'] >= 90:
        state['done'] = True
        unreal.unregister_slate_post_tick_callback(state['handle'])
        ok = unreal.EditorLoadingAndSavingUtils.save_map(world, DST)
        tag('SAVED', {'ok': bool(ok), 'dst': DST, 'ticks': state['n']})
        L.quit_editor_soon(60)
    elif state['n'] > 3000:
        state['done'] = True
        unreal.unregister_slate_post_tick_callback(state['handle'])
        tag('FATAL', {'why': 'navigation build did not finish in 3000 ticks'})
        L.quit_editor_soon(10)


state['handle'] = unreal.register_slate_post_tick_callback(tick)
