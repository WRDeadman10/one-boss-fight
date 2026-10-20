"""Compares notifies of a pack boss montage and our Sevarog montages, and exports BT_ExampleBoss to text (Saved/bt_exampleboss.t3d)."""
import unreal

log = lambda m: unreal.log("[BossMont] " + m)
PACK = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/"


def dump(path):
    m = unreal.load_asset(path)
    if m is None:
        log("MISSING " + path)
        return
    log("== %s len=%.2f" % (path.split("/")[-1], m.get_play_length()))
    for n in unreal.AnimationLibrary.get_animation_notify_events(m):
        out = []
        for f in ("notify_name", "notify_state_class", "notify", "notify_trigger_chance"):
            try:
                v = n.get_editor_property(f)
                out.append("%s=%s" % (f, v.get_class().get_name() if hasattr(v, "get_class") else v))
            except Exception as e:
                out.append("%s=?" % f)
        try:
            out.append("t=%.2f dur=%.2f" % (n.get_trigger_time(), n.get_duration()))
        except Exception:
            pass
        log("   " + " ".join(out))


dump(PACK + "GS_Attack01_Montage")
dump(PACK + "GS_LeapAttack_Montage")
registry = unreal.AssetRegistryHelpers.get_asset_registry()
for a in registry.get_assets_by_path("/Game/OneBossFight/Boss", recursive=True):
    if str(a.asset_class_path.asset_name) == "AnimMontage":
        dump(str(a.package_name) + "." + str(a.asset_name))

bt = unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss")
task = unreal.AssetExportTask()
task.object = bt
task.filename = "C:/Users/winss/Documents/Unreal Projects/OneBossFight/Saved/bt_exampleboss.t3d"
task.automated = True
task.prompt = False
task.replace_identical = True
log("export bt: %s" % unreal.Exporter.run_asset_export_task(task))
