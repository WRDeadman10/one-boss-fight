import unreal
log = lambda m: unreal.log("[PI] " + m)
obj = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/PlayerInfo")
d = obj.get_editor_property("Default Attributes")
for k, v in d.items():
    try:
        name = k.get_editor_property("tag_name")
    except Exception as e:
        name = "? " + str(e)[:60]
    fields = []
    for f in ("Base Value", "Max Value", "Current Value", "BaseValue", "MaxValue", "Value"):
        try:
            fields.append("%s=%s" % (f, v.get_editor_property(f)))
        except Exception:
            pass
    log("%s => %s" % (name, v.export_text()[:600]))
ext = obj.get_editor_property("ExtendedAttributes")
for e in ext:
    log("ext: %s" % (e.get_path_name() if hasattr(e, "get_path_name") else e))
