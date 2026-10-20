"""Sevarog on the pack, step 3b: the two soft references (info -> pawn class, pawn -> info). Python needs the object itself, not a path."""
import unreal

log = lambda m: unreal.log("[SevPack3b] " + m)
OUT = "/Game/OneBossFight/SevarogPack"
pawn = unreal.load_asset(OUT + "/BP_SevarogBossPack")
info = unreal.load_asset(OUT + "/SevarogEnemyInfo")
try:
    info.set_editor_property("AI Pawn Class", pawn.generated_class())
    log("info.AI Pawn Class = %s" % info.get_editor_property("AI Pawn Class"))
except Exception as exc:
    log("info soft class failed: %s" % str(exc)[:120])
unreal.EditorAssetLibrary.save_loaded_asset(info)
cdo = unreal.get_default_object(pawn.generated_class())
try:
    cdo.set_editor_property("EnemyInfo", info)
    log("pawn.EnemyInfo = %s" % cdo.get_editor_property("EnemyInfo"))
except Exception as exc:
    log("pawn soft object failed: %s" % str(exc)[:120])
# The copied great-sword boss defaults EnemyInfoRef to the pack's sword mob info; the hard reference is what the pawn uses at BeginPlay.
cdo.set_editor_property("EnemyInfoRef", info)
log("pawn.EnemyInfoRef = %s" % cdo.get_editor_property("EnemyInfoRef").get_name())
unreal.BlueprintEditorLibrary.compile_blueprint(pawn)
unreal.EditorAssetLibrary.save_loaded_asset(pawn)
