"""Finds which Python names exist for montage notifies, sections and sockets in this engine build. Log prefix [Probe]."""
import unreal

log = lambda m: unreal.log("[Probe] " + m)
for obj_name in ("AnimationLibrary", "EditorSkeletonLibrary", "AnimMontage", "SkeletalMesh", "StaticMesh", "AnimNotifyEvent", "Skeleton", "SkeletalMeshSocket", "EditorStaticMeshLibrary"):
    o = getattr(unreal, obj_name, None)
    if o is None:
        log("%s: missing" % obj_name)
        continue
    names = [n for n in dir(o) if any(k in n.lower() for k in ("notify", "section", "socket", "bone", "root_motion", "montage"))]
    log("%s: %s" % (obj_name, ", ".join(sorted(names))))
