# C-437: KI-149 Tier 1 adaptation. EDITS (no delete/recreate) the attack_count of the three phased proof profiles 3 -> 2, reads it back, saves only those.
import unreal
NAMES = ['DA_Sevarog_PhaseProof_F6c', 'DA_Sevarog_PhaseProofBaked_F6c', 'DA_Sevarog_PhaseProofNear_F6c']
for n in NAMES:
    a = unreal.load_asset('/Game/OneBossFight/FrameworkProof/' + n)
    if a is None:
        raise SystemExit('missing ' + n)
    before = a.get_editor_property('attack_count')
    a.set_editor_property('attack_count', 2)
    after = a.get_editor_property('attack_count')
    if after != 2 or abs(a.get_editor_property('phase_two_fraction') - 0.5) > 1e-6 or str(a.get_editor_property('phase_two_id')) != 'Phase_2':
        raise SystemExit('readback mismatch ' + n)
    if not unreal.EditorAssetLibrary.save_loaded_asset(a):
        raise SystemExit('save failed ' + n)
    unreal.log('[F6C3_SET] %s attack_count %s -> %s phase_two_fraction=%s phase_two_id=%s' % (n, before, after, a.get_editor_property('phase_two_fraction'), a.get_editor_property('phase_two_id')))
