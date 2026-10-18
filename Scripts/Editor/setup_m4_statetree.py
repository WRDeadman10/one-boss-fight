"""
Builds the boss StateTree asset and assigns it to BP_SevarogBoss. Idempotent.

Run headless from the project root (editor closed):
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m4_statetree.py -unattended -nullrhi
"""

import unreal

BOSS_DIR = "/Game/OneBossFight/Boss"
TREE_NAME = "ST_Boss"
BOSS_BP = "/Game/OneBossFight/Characters/BP_SevarogBoss"


def log(msg):
    unreal.log("[StateTreeSetup] " + msg)


tree = unreal.RPGBossStateTreeBuilder.build_boss_state_tree(BOSS_DIR, TREE_NAME)
if tree is None:
    raise RuntimeError("StateTree build or compile failed; see the log above.")
unreal.EditorAssetLibrary.save_loaded_asset(tree, False)
log("Saved %s/%s" % (BOSS_DIR, TREE_NAME))

bp = unreal.load_asset(BOSS_BP)
cdo = unreal.get_default_object(bp.generated_class())
component = cdo.get_components_by_class(unreal.RPGBossStateTreeComponent)[0]
component.set_editor_property("boss_state_tree", tree)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
log("BP_SevarogBoss now runs the boss StateTree.")
