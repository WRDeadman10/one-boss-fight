"""
switch_character.py - Switch player or boss character to one of the 6 custom builds.
Can be executed via Scripts/run_in_editor.py or directly from command line.

Usage via command line:
    python Scripts/switch_character.py player Samurai
    python Scripts/switch_character.py boss Viking

Available builds:
    - Samurai
    - IndianYoddha
    - MedievalWarrior
    - Viking
    - IndianGoddess
    - GirlWarrior
"""

import sys
import os

BUILDS = {
    "samurai": "/Game/OneBossFight/Characters/Builds/SKM_Samurai",
    "indianyoddha": "/Game/OneBossFight/Characters/Builds/SKM_IndianYoddha",
    "yoddha": "/Game/OneBossFight/Characters/Builds/SKM_IndianYoddha",
    "indian": "/Game/OneBossFight/Characters/Builds/SKM_IndianYoddha",
    "medievalwarrior": "/Game/OneBossFight/Characters/Builds/SKM_MedievalWarrior",
    "medieval": "/Game/OneBossFight/Characters/Builds/SKM_MedievalWarrior",
    "knight": "/Game/OneBossFight/Characters/Builds/SKM_MedievalWarrior",
    "viking": "/Game/OneBossFight/Characters/Builds/SKM_Viking",
    "indiangoddess": "/Game/OneBossFight/Characters/Builds/SKM_IndianGoddess",
    "goddess": "/Game/OneBossFight/Characters/Builds/SKM_IndianGoddess",
    "girlwarrior": "/Game/OneBossFight/Characters/Builds/SKM_GirlWarrior",
    "girl": "/Game/OneBossFight/Characters/Builds/SKM_GirlWarrior",
    "valkyrie": "/Game/OneBossFight/Characters/Builds/SKM_GirlWarrior"
}

TARGETS = {
    "player": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter",
    "boss": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss"
}

def switch(target_key, build_key):
    try:
        import unreal
    except ImportError:
        # Not inside unreal, forward via run_in_editor.py
        import subprocess
        script_path = os.path.abspath(__file__)
        runner = os.path.join(os.path.dirname(script_path), "run_in_editor.py")
        cmd = [sys.executable, "-I", runner, script_path, target_key, build_key]
        subprocess.run(cmd)
        return

    target_path = TARGETS.get(target_key.lower())
    if not target_path:
        print(f"[SWITCH] Error: Unknown target '{target_key}'. Choose 'player' or 'boss'.")
        return

    build_path = BUILDS.get(build_key.lower().replace(" ", "").replace("_", ""))
    if not build_path:
        print(f"[SWITCH] Error: Unknown build '{build_key}'. Choose from: Samurai, IndianYoddha, MedievalWarrior, Viking, IndianGoddess, GirlWarrior.")
        return

    mesh_asset = unreal.load_asset(build_path)
    if not mesh_asset:
        print(f"[SWITCH] Error: Could not load mesh asset at {build_path}")
        return

    bp_asset = unreal.load_asset(target_path)
    if not bp_asset:
        print(f"[SWITCH] Error: Could not load blueprint asset at {target_path}")
        return

    gen_class = bp_asset.generated_class()
    cdo = unreal.get_default_object(gen_class)
    mesh_comp = cdo.get_editor_property("mesh")
    if mesh_comp:
        mesh_comp.set_editor_property("skeletal_mesh_asset", mesh_asset)
        unreal.EditorAssetLibrary.save_loaded_asset(bp_asset)
        print(f"[SWITCH] SUCCESS: Set {target_key.upper()} ({bp_asset.get_name()}) SkeletalMesh to {mesh_asset.get_name()}!")
    else:
        print("[SWITCH] Error: Could not locate Mesh component on CDO.")

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "player"
    b = sys.argv[2] if len(sys.argv) > 2 else "Viking"
    switch(t, b)
