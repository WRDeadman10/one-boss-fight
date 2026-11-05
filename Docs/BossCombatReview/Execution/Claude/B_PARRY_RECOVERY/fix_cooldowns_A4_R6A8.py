"""Lead: set every candidate cooldown to 0.1 s in the two proof profiles that Codex's scripts created with the default cooldowns
(PhaseCooldownStarvation refused attack_count 4 and 8). Edits ONLY these two NEW proof assets, reads values back."""
import unreal

DIR = "/Game/OneBossFight/FrameworkProof"
lib = unreal.EditorAssetLibrary
for name in ("DA_Sevarog_ParryRecovery_Gating_A4", "DA_Sevarog_YawCone_R6A8"):
    profile = unreal.load_asset(DIR + "/" + name)
    entries = list(profile.get_editor_property("cards"))
    for entry in entries:
        entry.set_editor_property("cooldown_seconds", 0.1)
    profile.set_editor_property("cards", entries)
    assert lib.save_loaded_asset(profile), "save failed " + name
    back = [float(e.get_editor_property("cooldown_seconds")) for e in profile.get_editor_property("cards")]
    unreal.log("[LEAD_COOLDOWNS] %s cards=%d cooldowns=%s attack_count=%s" % (name, len(back), back, profile.get_editor_property("attack_count")))
    assert all(abs(c - 0.1) < 1e-4 for c in back)
