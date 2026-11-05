"""Lead wrapper (C-834): run Codex's read-only snapshot probe in a fresh editor process, then quit.
The probe itself stays bridge-friendly (it does not quit); this wrapper adds the quit for headless lead runs."""
import importlib.util
import unreal

PROBE = r"C:\UnrealProject\OneBossFight\Scripts\Editor\probe_encounter_parity_snapshot.py"
spec = importlib.util.spec_from_file_location("probe_encounter_parity_snapshot", PROBE)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)  # registers the probe tick

watch = {"handle": None, "after": 0}


def quit_tick(_delta):
    if not probe.state["done"]:
        return
    watch["after"] += 1
    if watch["after"] < 60:  # let end-play settle before quitting
        return
    unreal.unregister_slate_post_tick_callback(watch["handle"])
    unreal.log("[EncounterSnapshotProbe] wrapper quit")
    unreal.SystemLibrary.quit_editor()


watch["handle"] = unreal.register_slate_post_tick_callback(quit_tick)
