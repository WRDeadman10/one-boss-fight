"""Sevarog on the pack, step 3: pawn Blueprint (child copy of the pack great-sword boss), combat style (his ability copies), enemy info.
Run in the open editor after steps 1 and 2. Idempotent (recreates the assets)."""
import re
import unreal

log = lambda m: unreal.log("[SevPack3] " + m)
A = "/Game/AdvancedARPGCombat/"
GS = A + "MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
OUT = "/Game/OneBossFight/SevarogPack"
ABIL = OUT + "/Abilities"
PAWN = OUT + "/BP_SevarogBossPack"
STYLE = OUT + "/SevarogCombatStyle"
INFO = OUT + "/SevarogEnemyInfo"
PROXY = OUT + "/SM_SevarogScytheProxy"
ANIM_BP = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint"
SEV_MESH = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog"
BOSS_HEALTH = 1500.0


def duplicate(src, dst):
    if unreal.EditorAssetLibrary.does_asset_exist(dst):
        unreal.EditorAssetLibrary.delete_asset(dst)
    asset = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
    if asset is None:
        raise RuntimeError("duplicate failed %s -> %s" % (src, dst))
    return asset


# ---- combat style ------------------------------------------------------------------------------------------------------
style = duplicate(GS + "ExampleGreatSwordBossCombatStyle", STYLE)
sets = style.get_editor_property("AbilitiesSet")
text = sets[0].export_text()
text = text.replace(GS + "GA_GS_Boss_", ABIL + "/GA_Sev_")
text = re.sub(r'"[^"]*GA_Sev_TurnInPlace[^"]*",?', "", text)  # no Sevarog turn-in-place montages
text = text.replace(",)", ")")
# GA_Sev_X.GA_GS_Boss_X_C -> GA_Sev_X.GA_Sev_X_C
text = re.sub(r"GA_Sev_(\w+)\.GA_GS_Boss_\w+_C", r"GA_Sev_\1.GA_Sev_\1_C", text)
left = re.findall(r"GA_GS_Boss_\w+", text)
log("abilities in style: %s (unconverted: %s)" % (re.findall(r"GA_Sev_\w+?\.", text), left))
entry = sets[0]
entry.import_text(text)
style.set_editor_property("AbilitiesSet", [entry])
style.set_editor_property("Anim Layer Class", None)  # Sevarog keeps his own animation Blueprint, no linked layer
unreal.EditorAssetLibrary.save_loaded_asset(style)

# ---- pawn --------------------------------------------------------------------------------------------------------------
pawn = duplicate(GS + "BP_ExampleGreatSwordBoss", PAWN)
cdo = unreal.get_default_object(pawn.generated_class())
capsule = cdo.get_editor_property("capsule_component")
capsule.set_editor_property("capsule_half_height", 155.0)
capsule.set_editor_property("capsule_radius", 90.0)
mesh_component = cdo.get_editor_property("mesh")
mesh_component.set_editor_property("skeletal_mesh_asset", unreal.load_asset(SEV_MESH))
mesh_component.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -155.0))
mesh_component.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))

sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
for handle in sub.k2_gather_subobject_data_for_blueprint(pawn):
    data = lib.get_data(handle)
    obj = lib.get_object(data)
    if isinstance(obj, unreal.StaticMeshComponent) and "Weapon Mesh" in str(lib.get_display_name(data)):
        obj.set_editor_property("static_mesh", unreal.load_asset(PROXY))
        obj.set_editor_property("visible", False)
        obj.set_editor_property("hidden_in_game", True)
        log("weapon mesh component set to the hidden scythe proxy")
unreal.BlueprintEditorLibrary.compile_blueprint(pawn)
unreal.EditorAssetLibrary.save_loaded_asset(pawn)

# ---- enemy info --------------------------------------------------------------------------------------------------------
info = duplicate(GS + "ExampleGreatSwordBoss", INFO)
info.set_editor_property("Anim Class", unreal.load_asset(ANIM_BP).generated_class())
info.set_editor_property("DefaultCombatStyle", style)
info.set_editor_property("EnemyName", "Sevarog")
try:
    info.set_editor_property("AI Pawn Class", unreal.SoftClassPath(pawn.generated_class().get_path_name()))
except Exception as exc:
    log("soft class set failed (%s)" % str(exc)[:80])
attrs = info.get_editor_property("Default Attributes")
for key in list(attrs.keys()):
    if "Attribute.Health" in key.export_text():
        value = attrs[key]
        t = re.sub(r"(BaseValue_\d+_[0-9A-F]+|MaxValue_\d+_[0-9A-F]+)=[\d.]+", lambda m: "%s=%.6f" % (m.group(1), BOSS_HEALTH), value.export_text())
        value.import_text(t)
        attrs[key] = value
        log("health set to %.0f" % BOSS_HEALTH)
info.set_editor_property("Default Attributes", attrs)
unreal.EditorAssetLibrary.save_loaded_asset(info)

# EnemyInfo reference on the pawn defaults.
pcdo = unreal.get_default_object(pawn.generated_class())
try:
    pcdo.set_editor_property("EnemyInfo", unreal.SoftObjectPath(info.get_path_name()))
    log("pawn EnemyInfo = %s" % info.get_name())
except Exception as exc:
    log("pawn EnemyInfo set failed (%s)" % str(exc)[:80])
unreal.BlueprintEditorLibrary.compile_blueprint(pawn)
unreal.EditorAssetLibrary.save_loaded_asset(pawn)
log("done")
