"""
Lists the actors of the open level grouped by class (count, one sample location and folder), plus the lighting actors in detail. Log prefix [Level].
Run with Scripts/run_in_editor.py.
"""
import unreal

log = lambda m: unreal.log("[Level] " + m)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by = {}
for a in actors:
    by.setdefault(a.get_class().get_name(), []).append(a)
log("%d actors in %s" % (len(actors), unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()))
for cn, lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    a = lst[0]
    l = a.get_actor_location()
    log("%4d %-34s e.g. %-28s (%.0f,%.0f,%.0f) folder=%s" % (len(lst), cn, a.get_actor_label(), l.x, l.y, l.z, a.get_folder_path()))
for cn in ("DirectionalLight", "SkyLight", "SkyAtmosphere", "ExponentialHeightFog", "PostProcessVolume", "VolumetricCloud", "PointLight", "SpotLight", "RectLight"):
    for a in by.get(cn, []):
        l = a.get_actor_location()
        r = a.get_actor_rotation()
        props = {}
        for comp in a.get_components_by_class(unreal.ActorComponent):
            for pn in ("intensity", "light_color", "source_radius", "attenuation_radius", "mobility", "fog_density", "fog_height_falloff", "volumetric_fog", "cast_shadows", "atmosphere_sun_light"):
                try:
                    props.setdefault(pn, comp.get_editor_property(pn))
                except Exception:
                    pass
        log("%s %s at (%.0f,%.0f,%.0f) rot (%.0f,%.0f,%.0f) %s" % (cn, a.get_actor_label(), l.x, l.y, l.z, r.pitch, r.yaw, r.roll, props))
