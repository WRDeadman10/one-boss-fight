import unreal

for name in sorted(dir(unreal.AnimationLibrary)):
    if "notify" in name.lower():
        unreal.log(f"AnimationLibrary: {name}")
