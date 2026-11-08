"""
Inspects all ARPGFireSource actors and lighting in L_SevarogArena.
"""

import unreal

def inspect_braziers():
    level_path = "/Game/OneBossFight/Levels/L_SevarogArena"
    unreal.EditorLevelLibrary.load_level(level_path)
    
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    fire_actors = []
    for a in actors:
        if a.get_class().get_name() == "RPGFireSource":
            fire_actors.append(a)
            
    unreal.log(f"[BrazierAudit] Found {len(fire_actors)} RPGFireSource actors in {level_path}")
    
    cardinals = ["BrazierFire_00", "BrazierFire_03", "BrazierFire_06", "BrazierFire_09"]
    
    results = []
    for a in sorted(fire_actors, key=lambda x: x.get_actor_label()):
        label = a.get_actor_label()
        cast_shadows = a.get_editor_property("bCastShadows")
        radius = a.get_editor_property("AttenuationRadius")
        intensity = a.get_editor_property("BaseIntensity")
        color = a.get_editor_property("LightColor")
        loc = a.get_actor_location()
        
        is_cardinal = any(c in label for c in cardinals)
        results.append({
            "label": label,
            "cast_shadows": cast_shadows,
            "is_cardinal": is_cardinal,
            "radius": radius,
            "intensity": intensity,
            "location": (loc.x, loc.y, loc.z)
        })
        unreal.log(f"[BrazierAudit] {label}: CastShadows={cast_shadows}, Cardinal={is_cardinal}, Radius={radius}, Int={intensity}, Loc=({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f})")

    # Check ExponentialHeightFog / Volumetric fog
    fog_actors = [a for a in actors if "ExponentialHeightFog" in a.get_class().get_name()]
    for fa in fog_actors:
        comp = fa.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if comp:
            v_fog = comp.get_editor_property("volumetric_fog")
            unreal.log(f"[FogAudit] {fa.get_actor_label()}: VolumetricFogEnabled={v_fog}")

if __name__ == "__main__":
    inspect_braziers()
    unreal.SystemLibrary.quit_editor()
