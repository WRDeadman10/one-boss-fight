import unreal
for n in dir(unreal):
    l = n.lower()
    if ("inputaction" in l or "inputmapping" in l or "montage" in l or "dataasset" in l or "enhancedactionkey" in l or "inputmodifier" in l or l.startswith("animationlibrary") or "inputtrigger" in l) and "factory" in l or n in ("AnimationLibrary","InputAction","InputMappingContext","EnhancedActionKeyMapping","PrimaryDataAsset"):
        unreal.log("[Probe] " + n)
unreal.log("[Probe] AnimationLibrary notify funcs: %s" % [m for m in dir(unreal.AnimationLibrary) if "notify" in m])
unreal.log("[Probe] IMC methods: %s" % [m for m in dir(unreal.InputMappingContext) if not m.startswith("_")][:40])
