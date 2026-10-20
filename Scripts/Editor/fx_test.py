"""
Spawns a row of candidate fire / ember systems at (700, y, 0) so they can be compared in a viewport shot (folder "FxTest"); run again to clear and respawn.
Edit CANDIDATES. Log prefix [FxTest]. Run with Scripts/run_in_editor.py.
"""
import unreal

CANDIDATES = [
    "/Game/StarterContent/Particles/P_Fire",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Effects/FX_Ambient/Fire/P_Fire_NeverEnding",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Effects/Bonfire/P_AngelGlowFallen",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/Effects/Bonfire/P_Fury_ActiveFallen",
    "/Game/ParagonSevarog/FX/Particles/Abilities/SoulStackPassive/FX/P_SoulStageEmbers",
    "/Game/ParagonGrux/FX/Particles/Skins/Grux_Beetle_Magma/P_Grux_Magma_StampedLegcyFire",
    "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Aura_Fire",
    "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Buff_Fire",
]
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    if str(a.get_folder_path()) == "FxTest":
        unreal.EditorLevelLibrary.destroy_actor(a)
for i, path in enumerate(CANDIDATES):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset is None:
        unreal.log("[FxTest] missing " + path)
        continue
    loc = unreal.Vector(700, -700 + i * 200, 5)
    if isinstance(asset, unreal.ParticleSystem):
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Emitter, loc, unreal.Rotator(0, 0, 0))
        a.get_editor_property("particle_system_component").set_template(asset)
    else:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NiagaraActor, loc, unreal.Rotator(0, 0, 0))
        a.get_editor_property("niagara_component").set_asset(asset)
    a.set_actor_label("FxTest_%d_%s" % (i, path.split("/")[-1]))
    a.set_folder_path("FxTest")
    unreal.log("[FxTest] %d %s at y=%d" % (i, path.split("/")[-1], loc.y))
