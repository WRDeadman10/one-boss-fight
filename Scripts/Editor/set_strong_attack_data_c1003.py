"""
C-1003: Set AttackData=StrongMeleeAttackData on ANS_CollisionTrace of
AM_ER_Attack_Air_Heavy_Plunge and AM_ER_Attack_GuardCounter.
Leave AM_ER_Attack_Air_Light unset (AttackData=None).
Exports t3d representations and prints Lead check output.
"""
import os
import unreal

AL = unreal.AnimationLibrary

LOG = "[C1003_AttackData] "
def log(m): unreal.log(LOG + m)

def run():
    strong_data_path = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/StrongMeleeAttackData"
    strong_data = unreal.load_asset(strong_data_path)
    if not strong_data:
        log("ERROR: Could not load StrongMeleeAttackData from " + strong_data_path)
        return
    log("Loaded StrongMeleeAttackData: " + strong_data.get_path_name())

    configs = [
        ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter", True),
        ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge", True),
        ("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light", False),
    ]

    out_t3d_dir = "C:/UnrealProject/OneBossFight/Saved/C1003_t3d"
    os.makedirs(out_t3d_dir, exist_ok=True)

    for path, is_strong in configs:
        m = unreal.EditorAssetLibrary.load_asset(path)
        m_name = m.get_name()
        
        target_attack_data = strong_data if is_strong else None
        
        # 1. Update active notifies
        found_trace = False
        for ev in AL.get_animation_notify_events(m):
            st = ev.get_editor_property("notify_state_class")
            if st and "ANS_CollisionTrace" in st.get_class().get_name():
                found_trace = True
                st.set_editor_property("AttackData", target_attack_data)
                st.modify()
                log(f"{m_name}: active ANS_CollisionTrace AttackData set to {target_attack_data.get_name() if target_attack_data else 'None'}")

        if not found_trace:
            log(f"WARNING: No ANS_CollisionTrace found on {m_name}")

        m.modify()
        saved = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        log(f"{m_name} saved: {saved}")

        # Export t3d
        task = unreal.AssetExportTask()
        task.object = m
        task.filename = f"{out_t3d_dir}/{m_name}.t3d"
        task.automated = True
        task.prompt = False
        task.replace_identical = True
        unreal.Exporter.run_asset_export_task(task)
        log(f"Exported {m_name}.t3d to {out_t3d_dir}")

    # Lead Asset Check
    log("=== RUNNING LEAD ASSET CHECK ===")
    boss_mesh = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple")
    boss_skel = boss_mesh.get_editor_property("skeleton") if boss_mesh else None
    
    lead_lines = []
    check_montages = [
        "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
        "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Back",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
        "/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil"
    ]
    for path in check_montages:
        a = unreal.load_asset(path)
        if not a:
            line = f"MISSING {path}"
        else:
            skel = a.get_editor_property("skeleton")
            slots = [unreal.RPGMontageUtils.get_montage_slot(a)]
            line = "montage %s class=%s length=%.4f slots=%s skeleton_match=%s notifies=%s" % (
                a.get_name(), a.get_class().get_name(), a.get_play_length(), [str(s) for s in slots],
                bool(skel and boss_skel and skel == boss_skel), list(unreal.RPGMontageUtils.describe_notifies(a)))
        log("[LeadCheck] " + line)
        lead_lines.append(line)

    lead_out_path = "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/C1003_LEAD_CHECK.txt"
    with open(lead_out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lead_lines) + "\n")
    log(f"Saved Lead check to {lead_out_path}")

    unreal.SystemLibrary.quit_editor()

if __name__ == "__main__":
    run()
