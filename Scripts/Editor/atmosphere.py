"""
Sets the arena's mood: a low warm dusk sun raking across the ruins, volumetric fog with light shafts and a ground mist layer, a cloud deck,
a real-time sky light and a global post process (bloom, vignette, grain, grading). Actors are created once (folder "Atmosphere") and reused;
change the numbers in the TUNING block and rerun. Run with Scripts/run_in_editor.py with L_SevarogArena open. Log prefix [Atmos].
"""
import unreal

log = lambda m: unreal.log("[Atmos] " + m)
FOLDER = "Atmosphere"

TUNING = dict(
    sun_pitch=2.5, sun_yaw=215.0, sun_intensity=3.2, sun_color=(1.0, 0.68, 0.44),
    moon_pitch=-36.0, moon_yaw=240.0, moon_intensity=2.6, moon_color=(0.58, 0.70, 1.0),
    sky_intensity=1.1,
    fog_density=0.011, fog_height_falloff=0.22, fog_color=(0.22, 0.28, 0.40), fog_inscatter_dir=(0.9, 0.52, 0.30),
    mist_density=0.05, mist_height_falloff=3.5, mist_offset=0.0,
    exposure_min=0.08, exposure_max=5.0, exposure_bias=0.7, bloom=1.1, vignette=0.45, grain=0.07,
)
T = TUNING

sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = sub.get_all_level_actors()


def by_class(name):
    return [a for a in actors if a.get_class().get_name() == name]


def ensure(cls, label):
    found = [a for a in by_class(cls.static_class().get_name()) if a.get_actor_label() == label]
    if found:
        return found[0]
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    a.set_actor_label(label)
    a.set_folder_path(FOLDER)
    return a


def setp(obj, name, value):
    """set_editor_property that logs a missing property instead of aborting the whole script."""
    try:
        obj.set_editor_property(name, value)
    except Exception as e:
        log("property %s failed: %s" % (name, str(e)[:120]))


def color(rgb):
    return unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1.0)


# ---- sun
sun = [a for a in by_class("DirectionalLight") if a.get_actor_label() == "Sun"][0]
sun.set_actor_rotation(unreal.Rotator(roll=0, pitch=T["sun_pitch"], yaw=T["sun_yaw"]), False)
sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
sc.set_mobility(unreal.ComponentMobility.MOVABLE)
sc.set_editor_property("intensity", T["sun_intensity"])
sc.set_editor_property("light_color", unreal.Color(r=int(T["sun_color"][0] * 255), g=int(T["sun_color"][1] * 255), b=int(T["sun_color"][2] * 255), a=255))
sc.set_editor_property("use_temperature", False)
sc.set_editor_property("cast_shadows", True)
sc.set_editor_property("cast_volumetric_shadow", True)
sc.set_editor_property("volumetric_scattering_intensity", 3.5)
sc.set_editor_property("enable_light_shaft_bloom", False)
sc.set_editor_property("bloom_scale", 0.18)
sc.set_editor_property("bloom_threshold", 0.0)
sc.set_editor_property("dynamic_shadow_distance_movable_light", 9000.0)
log("sun set")

# ---- moon: a cool second directional light that is not the atmosphere sun, so shadows stay readable after the sun has set
moon = ensure(unreal.DirectionalLight, "Moon")
moon.set_actor_rotation(unreal.Rotator(roll=0, pitch=T["moon_pitch"], yaw=T["moon_yaw"]), False)
mc = moon.get_component_by_class(unreal.DirectionalLightComponent)
mc.set_mobility(unreal.ComponentMobility.MOVABLE)
setp(mc, "intensity", T["moon_intensity"])
setp(mc, "light_color", unreal.Color(r=int(T["moon_color"][0] * 255), g=int(T["moon_color"][1] * 255), b=int(T["moon_color"][2] * 255), a=255))
setp(mc, "atmosphere_sun_light", True)
setp(mc, "atmosphere_sun_light_index", 1)
setp(mc, "forward_shading_priority", 1)  # the moon lights fog and translucency: the sun is below the horizon
setp(mc, "atmosphere_sun_disk_color_scale", unreal.LinearColor(0.55, 0.65, 1.0, 1.0))
setp(mc, "cast_shadows", True)
setp(mc, "cast_volumetric_shadow", True)
setp(mc, "volumetric_scattering_intensity", 2.0)
setp(mc, "dynamic_shadow_distance_movable_light", 9000.0)
log("moon set")

# ---- sky light
sky = by_class("SkyLight")[0]
kc = sky.get_component_by_class(unreal.SkyLightComponent)
kc.set_editor_property("real_time_capture", True)
kc.set_editor_property("intensity", T["sky_intensity"])
kc.set_editor_property("lower_hemisphere_is_black", False)
kc.set_editor_property("lower_hemisphere_color", unreal.LinearColor(0.05, 0.045, 0.04, 1.0))
log("sky light set")

# ---- height fog with volumetric fog and a low mist layer
fog = ensure(unreal.ExponentialHeightFog, "DuskFog")
fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
setp(fc, "fog_density", T["fog_density"])
setp(fc, "fog_height_falloff", T["fog_height_falloff"])
setp(fc, "fog_inscattering_luminance", color(T["fog_color"]))
setp(fc, "fog_max_opacity", 0.92)
setp(fc, "start_distance", 200.0)
setp(fc, "directional_inscattering_luminance", color(T["fog_inscatter_dir"]))
setp(fc, "directional_inscattering_exponent", 6.0)
setp(fc, "enable_volumetric_fog", True)
setp(fc, "volumetric_fog_scattering_distribution", 0.45)
setp(fc, "volumetric_fog_albedo", unreal.Color(r=200, g=205, b=215, a=255))
setp(fc, "volumetric_fog_extinction_scale", 1.2)
setp(fc, "volumetric_fog_distance", 8000.0)
setp(fc, "volumetric_fog_start_distance", 0.0)
second = fc.get_editor_property("second_fog_data")
setp(second, "fog_density", T["mist_density"])
setp(second, "fog_height_falloff", T["mist_height_falloff"])
setp(second, "fog_height_offset", T["mist_offset"])
setp(fc, "second_fog_data", second)
log("fog set")

# ---- clouds
try:
    cloud = ensure(unreal.VolumetricCloud, "CloudDeck")
    cc = cloud.get_component_by_class(unreal.VolumetricCloudComponent)
    mat = None
    for p in ("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst", "/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud"):
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mat = unreal.EditorAssetLibrary.load_asset(p)
            break
    if mat:
        cc.set_editor_property("material", mat)
        cc.set_editor_property("layer_bottom_altitude", 4.0)
        cc.set_editor_property("layer_height", 7.0)
        log("clouds set with " + mat.get_name())
    else:
        log("no cloud material found, clouds skipped")
except Exception as e:
    log("clouds failed: %s" % e)

# ---- post process
ppv = ensure(unreal.PostProcessVolume, "DuskPost")
ppv.set_editor_property("unbound", True)
s = ppv.get_editor_property("settings")
for name, value in (
    ("bloom_intensity", T["bloom"]), ("bloom_threshold", 0.6),
    ("auto_exposure_min_brightness", T["exposure_min"]), ("auto_exposure_max_brightness", T["exposure_max"]),
    ("auto_exposure_bias", T["exposure_bias"]), ("auto_exposure_speed_up", 2.5), ("auto_exposure_speed_down", 1.5),
    ("vignette_intensity", T["vignette"]), ("film_grain_intensity", T["grain"]),
    ("scene_fringe_intensity", 0.6),
    ("color_saturation", unreal.Vector4(0.88, 0.9, 0.95, 1.0)),
    ("color_contrast", unreal.Vector4(1.06, 1.06, 1.06, 1.0)),
    ("color_gain", unreal.Vector4(1.02, 0.99, 0.96, 1.0)),
    ("ambient_occlusion_intensity", 0.6), ("ambient_occlusion_radius", 120.0),
    ("lumen_scene_lighting_quality", 2.0), ("lumen_final_gather_quality", 2.0), ("lumen_scene_detail", 1.5),
):
    try:
        s.set_editor_property("override_" + name, True)
        s.set_editor_property(name, value)
    except Exception as e:
        log("post setting %s failed: %s" % (name, e))
for name, value in (("dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.LUMEN), ("reflection_method", unreal.ReflectionMethod.LUMEN)):
    try:
        s.set_editor_property("override_" + name, True)
        s.set_editor_property(name, value)
    except Exception as e:
        log("post setting %s failed: %s" % (name, e))
ppv.set_editor_property("settings", s)
log("post process set")
unreal.EditorLevelLibrary.save_current_level()
log("done and saved")
