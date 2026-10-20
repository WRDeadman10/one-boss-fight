"""Debug switches for the atmosphere: Saved/debug.txt holds words: nocloud, nofog, novol, nopost, nomist. Any word listed turns that piece off, everything else is on. Log prefix [DbgAtmos]."""
import os
import unreal

words = open(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\debug.txt").read().split() if os.path.exists(r"C:\Users\winss\Documents\Unreal Projects\OneBossFight\Saved\debug.txt") else []
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    lab = a.get_actor_label()
    if lab == "CloudDeck":
        a.set_actor_hidden_in_game("nocloud" in words)
        a.set_is_temporarily_hidden_in_editor("nocloud" in words)
    elif lab == "DuskFog":
        c = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        a.set_is_temporarily_hidden_in_editor("nofog" in words)
        c.set_editor_property("enable_volumetric_fog", "novol" not in words)
        s = c.get_editor_property("second_fog_data")
        s.set_editor_property("fog_density", 0.0 if "nomist" in words else 0.05)
        c.set_editor_property("second_fog_data", s)
    elif lab == "DuskPost":
        a.set_editor_property("enabled", "nopost" not in words)
unreal.log("[DbgAtmos] applied %s" % words)
