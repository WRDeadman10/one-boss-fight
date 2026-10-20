"""Prints action-level modifiers/triggers and settings for every IA_ asset."""
import unreal

registry = unreal.AssetRegistryHelpers.get_asset_registry()
for a in registry.get_assets_by_path("/Game/OneBossFight/Input", recursive=True):
    if str(a.asset_class_path.asset_name) != "InputAction":
        continue
    act = a.get_asset()
    def desc(items):
        return [i.get_class().get_name() if i else "NULL" for i in items]
    unreal.log("[ActInspect] %s type=%s consume=%s triggers=%s mods=%s trigger_when_paused=%s" % (
        act.get_name(), act.get_editor_property("value_type"), act.get_editor_property("consume_input"),
        desc(act.get_editor_property("triggers")), desc(act.get_editor_property("modifiers")),
        act.get_editor_property("trigger_when_paused")))
