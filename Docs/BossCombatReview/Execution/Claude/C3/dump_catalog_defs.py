# C3 (lead, Claude): READ-ONLY dump of the shipped weapon definitions (the exact soft paths the engine accepts), to compare with a new weapon config.
import json
import unreal

for n in ('DA_Weapon_Claymore', 'DA_Weapon_Sword', 'DA_Weapon_DualSwords', 'DA_Weapon_FengMaoPolearm'):
    a = unreal.load_asset('/Game/OneBossFight/Data/Catalog/%s.%s' % (n, n))
    if a is None:
        unreal.log('[C3DEF] %s missing' % n)
        continue
    d = a.get_editor_property('definition')
    def txt(v):
        for attr in ('export_text', 'to_string'):
            f = getattr(v, attr, None)
            if f:
                try:
                    return str(f())
                except Exception:
                    pass
        return str(v)
    out = {k: txt(d.get_editor_property(k)) for k in ('weapon_id', 'style_name', 'style_asset', 'item_path', 'item_base_class', 'actor_class', 'ability_class', 'hud_weapon_word', 'icon', 'require_exact_rows')}
    out['actions'] = [str(x) for x in d.get_editor_property('actions')]
    unreal.log('[C3DEF] ' + n + ' ' + json.dumps(out))
