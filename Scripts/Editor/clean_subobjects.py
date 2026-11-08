"""
Cleans all ANS_CollisionTrace_C subobjects in the 3 attack montages
so that neither active nor orphaned subobjects have AttackData set.
"""

import os
import unreal

AL = unreal.AnimationLibrary

def log(msg):
    unreal.log(f"[CleanSubobjects] {msg}")

def clean_montages():
    targets = [
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
        "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge"
    ]
    
    out_t3d_dir = "C:/UnrealProject/OneBossFight/Saved/C992_t3d"

    for path in targets:
        m = unreal.EditorAssetLibrary.load_asset(path)
        m_name = m.get_name()
        
        # Check active notifies
        for ev in AL.get_animation_notify_events(m):
            st = ev.get_editor_property("notify_state_class")
            if st and "ANS_CollisionTrace" in st.get_class().get_name():
                try:
                    st.set_editor_property("AttackData", None)
                    st.modify()
                    log(f"{m_name}: active notify state AttackData set to None")
                except Exception as e:
                    log(f"{m_name}: error setting active st: {e}")

        # Check any subobject named ANS_CollisionTrace_C_0..10
        for i in range(10):
            sub_path = f"{path}.{m_name}:ANS_CollisionTrace_C_{i}"
            sub = unreal.load_object(None, sub_path)
            if sub:
                try:
                    sub.set_editor_property("AttackData", None)
                    sub.modify()
                    log(f"Found and cleaned subobject {sub_path}")
                except Exception as e:
                    log(f"Error on {sub_path}: {e}")

        m.modify()
        unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        
        # Re-export t3d
        task = unreal.AssetExportTask()
        task.object = m
        task.filename = f"{out_t3d_dir}/{m_name}.t3d"
        task.automated = True
        task.prompt = False
        task.replace_identical = True
        unreal.Exporter.run_asset_export_task(task)
        log(f"Re-exported {m_name}.t3d")

if __name__ == "__main__":
    clean_montages()
