# PARRY (lead, Claude): READ-ONLY. Prints the AbilitiesSet of the player combat styles so we can see whether InputTag.Parry -> GA_PlayerParry is granted. Run with run_editor_script.ps1 -PyCmd 1 -NullRhi 0 (or default).
import unreal
W = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/'
for name in ('Sword/SwordCombatStyle', 'Claymore/ClaymoreCombatStyle', 'Sword/SwordAndShieldCombatStyle'):
    a = unreal.load_asset(W + name)
    if a is None:
        unreal.log('[PARRY_INSPECT] missing ' + name)
        continue
    v = a.get_editor_property('AbilitiesSet')
    unreal.log('[PARRY_INSPECT] %s class=%s n=%d' % (name, a.get_class().get_name(), len(v)))
    for e in v:
        t = e.export_text()
        unreal.log('[PARRY_INSPECT] %s entry_len=%d has_parry=%s has_block=%s' % (name, len(t), 'GA_PlayerParry' in t, 'GA_PlayerGuardBlock' in t))
        unreal.log('[PARRY_INSPECT_TEXT] ' + t[:2400])
