# Read-only probe (lead, Claude, 2026-11-04): how UE 5.5 Python builds and reads an FSoftObjectPath. Writes nothing.
# v1 result: SystemLibrary has no make_soft_object_path; the ctor repr prints {} (repr may not show fields).
import unreal

P = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Polearms/PolearmCombatStyle.PolearmCombatStyle'
ctor = unreal.SoftObjectPath(P)
unreal.log('[SOFTPATH_PROBE] ctor export=%s' % ctor.export_text())
imp = unreal.SoftObjectPath()
ok = imp.import_text(P)
unreal.log('[SOFTPATH_PROBE] import ok=%s export=%s' % (ok, imp.export_text()))
unreal.log('[SOFTPATH_PROBE] has get_asset_path_string=%s' % hasattr(ctor, 'get_asset_path_string'))
unreal.log('[SOFTPATH_PROBE] dir=%s' % [n for n in dir(ctor) if not n.startswith('_')])
