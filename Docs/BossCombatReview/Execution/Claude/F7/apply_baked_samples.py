# F7 fix (lead, Claude): sets the baked blade samples on the four F7 cards DIRECTLY, with readback and save (the authoring tool skipped them silently).
import json
import unreal

DIR = '/Game/OneBossFight/FrameworkProof/Cards/'
data = json.load(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F7/move_cards_f7_baked.json', encoding='utf-8'))
for card_json in data['cards']:
    move = card_json['MoveId']
    asset = unreal.load_asset(DIR + move)
    if asset is None:
        raise SystemExit('card missing ' + move)
    spec = asset.get_editor_property('spec')
    windows = list(spec.get_editor_property('windows'))
    json_windows = card_json['Windows']
    if len(windows) != len(json_windows):
        raise SystemExit('window count mismatch ' + move)
    for k, jw in enumerate(json_windows):
        samples = []
        for s in jw['BakedSamples']:
            b = unreal.RPGBakedBladeSample()
            b.set_editor_property('time_seconds', float(s['TimeSeconds']))
            b.set_editor_property('base_cs', unreal.Vector(*[float(v) for v in s['BaseCS']]))
            b.set_editor_property('tip_cs', unreal.Vector(*[float(v) for v in s['TipCS']]))
            samples.append(b)
        windows[k].set_editor_property('baked_samples', samples)
    spec.set_editor_property('windows', windows)
    asset.set_editor_property('spec', spec)
    back = list(asset.get_editor_property('spec').get_editor_property('windows')[0].get_editor_property('baked_samples'))
    want = json_windows[0]['BakedSamples']
    if len(back) != len(want) or abs(back[0].get_editor_property('time_seconds') - want[0]['TimeSeconds']) > 1e-4 or abs(back[-1].get_editor_property('tip_cs').x - want[-1]['TipCS'][0]) > 1e-3:
        raise SystemExit('readback mismatch ' + move)
    ok = unreal.EditorAssetLibrary.save_loaded_asset(asset)
    unreal.log('[F7C_BAKED] ' + json.dumps({'move': move, 'samples': len(back), 'first_t': back[0].get_editor_property('time_seconds'), 'last_t': back[-1].get_editor_property('time_seconds'), 'saved': ok}))
    if not ok:
        raise SystemExit('save failed ' + move)
