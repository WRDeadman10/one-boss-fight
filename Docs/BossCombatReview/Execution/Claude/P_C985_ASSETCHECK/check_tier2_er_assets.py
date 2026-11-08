"""Lead read-only asset check (C-985): loads the ER and Tier 2 assets and logs class, length, skeleton and material domain. Saves nothing."""
import unreal
LOG = "[AssetCheck] "
def log(m): unreal.log(LOG + m)
boss_mesh = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple")
boss_skel = boss_mesh.get_editor_property("skeleton") if boss_mesh else None
log("boss mesh skeleton=%s" % (boss_skel.get_path_name() if boss_skel else None))
montages = ["/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage", "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter", "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
            "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light", "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
            "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"]
for path in montages:
    a = unreal.load_asset(path)
    if not a:
        log("MISSING %s" % path); continue
    skel = a.get_editor_property("skeleton")
    slots = [unreal.RPGMontageUtils.get_montage_slot(a)]
    log("montage %s class=%s length=%.4f slots=%s skeleton_match=%s notifies=%s" % (
        a.get_name(), a.get_class().get_name(), a.get_play_length(), [str(s) for s in slots],
        bool(skel and boss_skel and skel == boss_skel), list(unreal.RPGMontageUtils.describe_notifies(a))))
mpc = unreal.load_asset("/Game/OneBossFight/Data/MPC_CombatFeedback")
log("mpc class=%s scalars=%s" % (mpc.get_class().get_name() if mpc else None,
    [(str(p.get_editor_property("parameter_name")), p.get_editor_property("default_value")) for p in mpc.get_editor_property("scalar_parameters")] if mpc else None))
ppm = unreal.load_asset("/Game/OneBossFight/Effects/PPM_ParryDistortion")
log("ppm class=%s domain=%s" % (ppm.get_class().get_name() if ppm else None, ppm.get_editor_property("material_domain") if ppm else None))
ns = unreal.load_asset("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura")
log("ns class=%s path=%s" % (ns.get_class().get_name() if ns else None, ns.get_path_name() if ns else None))
log("finished")
unreal.SystemLibrary.quit_editor()

