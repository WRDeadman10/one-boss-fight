# PAC-003 / PAC-005 data dump (lead, Claude): READ-ONLY. What the pack player's light/heavy attack montages and movement say about startup and travel.
# Prints one JSON line per montage and one for the movement; changes nothing, saves nothing.
import json
import unreal

ANIM_DIR = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations'
PLAYER_BP = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C'


def tag(t, payload):
    unreal.log('[PAC003_%s] %s' % (t, json.dumps(payload, default=str)))


reg = unreal.AssetRegistryHelpers.get_asset_registry()
assets = reg.get_assets_by_path(ANIM_DIR, recursive=True)
tag('COUNT', {'assets_under_animations': len(assets)})
names = []
for a in assets:
    n = str(a.asset_name)
    if a.asset_class_path.asset_name == 'AnimMontage' and any(k in n for k in ('Attack_Primary', 'ChargedAttack', 'Attack_D_Med', 'SprintAttack', 'Retaliation')):
        names.append((n, str(a.package_name)))
tag('MONTAGES', {'names': [n for n, _ in names]})
for n, pkg in sorted(names):
    m = unreal.load_asset(pkg + '.' + n)
    if m is None:
        continue
    notifies = []
    for ev in unreal.AnimationLibrary.get_animation_notify_events(m):
        row = {'attrs': [a for a in dir(ev) if not a.startswith('_')]} if not notifies else {}
        for a in ('notify_name', 'display_time', 'trigger_time_offset', 'duration', 'link_value', 'end_trigger_time_offset'):
            try:
                row[a] = str(ev.get_editor_property(a))
            except Exception as ex:  # noqa
                row[a] = 'ERR'
        for g in ('get_trigger_time', 'get_end_trigger_time', 'get_duration', 'get_display_time'):
            if hasattr(ev, g):
                try:
                    row[g] = str(getattr(ev, g)())
                except Exception:
                    row[g] = 'ERR'
        state = ev.get_editor_property('notify_state_class')
        plain = ev.get_editor_property('notify')
        row['cls'] = state.get_class().get_name() if state is not None else (plain.get_class().get_name() if plain is not None else '')
        notifies.append(row)
    tag('MONTAGE', {'name': n, 'length': float(m.get_play_length()), 'rate_scale': float(m.get_editor_property('rate_scale')), 'notifies': notifies})

cls = unreal.load_class(None, PLAYER_BP)
if cls is not None:
    cdo = unreal.get_default_object(cls)
    mv = cdo.get_editor_property('character_movement')
    cap = cdo.get_editor_property('capsule_component')
    tag('MOVEMENT', {'max_walk_speed': float(mv.get_editor_property('max_walk_speed')), 'max_acceleration': float(mv.get_editor_property('max_acceleration')),
                     'capsule_radius': float(cap.get_editor_property('capsule_radius')), 'capsule_half_height': float(cap.get_editor_property('capsule_half_height'))})
else:
    tag('MOVEMENT', {'error': 'player class not loaded'})
