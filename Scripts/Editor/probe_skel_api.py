import unreal
log = lambda m: unreal.log("[SkelApi] " + m)
for name in ("EditorSkeletonLibrary", "SkeletonLibrary", "SkeletalMeshEditorSubsystem", "EditorSkeletalMeshLibrary"):
    obj = getattr(unreal, name, None)
    log("%s: %s" % (name, [n for n in dir(obj) if not n.startswith("_") and "ocket" in n] if obj else None))
sm = unreal.load_asset("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin")
log("mesh dir sockets: %s" % [n for n in dir(sm) if "ocket" in n])
