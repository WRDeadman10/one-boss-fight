# C3 (lead, Claude): READ-ONLY dump of the saved DA_WeaponAttacks rows (style, kind, posture, stamina, bleed, health multiplier), one JSON line per row, so the weapon validator can be driven by real data.
import json
import unreal

t = unreal.load_asset('/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks')
if t is None:
    raise SystemExit('DA_WeaponAttacks not found')
rows = list(t.get_editor_property('rows'))
styles = {}
for r in rows:
    w = str(r.get_editor_property('weapon'))
    k = str(r.get_editor_property('kind'))
    styles.setdefault(w, []).append(k)
    unreal.log('[C3_ROW] ' + json.dumps({'weapon': w, 'kind': k, 'posture': r.get_editor_property('posture_damage'), 'stamina': r.get_editor_property('stamina_cost'),
                                         'bleed': r.get_editor_property('bleed_buildup'), 'health_mult': r.get_editor_property('health_damage_multiplier')}))
unreal.log('[C3_SUMMARY] ' + json.dumps({'rows': len(rows), 'styles': {k: len(v) for k, v in styles.items()}}))
