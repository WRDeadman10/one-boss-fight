"""
Prints what the combat setup needs to know about Greystone: mesh sockets, weapon-related bones,
the AnimBP class and the slot names / notifies of the shipped attack montages.

Run headless:
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/inspect_greystone_combat.py -unattended -nullrhi
"""

import unreal

ROOT = "/Game/ParagonGreystone"


def log(message):
    unreal.log("[GreystoneInspect] " + message)


def main():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous([ROOT], True)
    assets = registry.get_assets_by_path(ROOT, recursive=True)
    by_name = {}
    for data in assets:
        by_name[(str(data.asset_class_path.asset_name), str(data.asset_name))] = data

    mesh = by_name[("SkeletalMesh", "Greystone")].get_asset()
    sockets = mesh.get_editor_property("sockets") if hasattr(mesh, "sockets") else []
    log("mesh sockets (%d): %s" % (len(sockets), [str(s.socket_name) for s in sockets]))
    skeleton = mesh.get_editor_property("skeleton")
    log("skeleton methods: %s" % [m for m in dir(skeleton) if "socket" in m.lower() or "bone" in m.lower()])
    log("mesh methods: %s" % [m for m in dir(mesh) if "socket" in m.lower() or "bone" in m.lower()])
    for name in ("weapon_r", "weapon_l", "Weapon_R", "hand_r", "FX_Sword_Base", "FX_Sword_Tip"):
        found = mesh.find_socket(name) if hasattr(mesh, "find_socket") else None
        log("find_socket(%s) -> %s" % (name, found))

    comp = unreal.new_object(unreal.SkeletalMeshComponent)
    comp.set_skeletal_mesh_asset(mesh)
    bones = [str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
    log("bone count %d; weapon-ish: %s" % (len(bones), [
        b for b in bones if any(k in b.lower() for k in ("weapon", "sword", "hand", "shield", "blade", "prop"))]))

    # Is the sword part of the main mesh or a separate one? List other skeletal meshes in the pack.
    log("skeletal meshes: %s" % sorted({k[1] for k in by_name if k[0] == "SkeletalMesh"}))

    montage = by_name[("AnimMontage", "Attack_PrimaryA_Montage")].get_asset()
    log("montage methods: %s" % [m for m in dir(montage) if any(k in m.lower() for k in ("slot", "notify", "section", "track"))])
    log("montage notify events: %s" % [str(n.get_editor_property("notify_name")) for n in montage.get_editor_property("notifies")])

    for name in ("Attack_A_Med", "Attack_B_Med", "Attack_C_Med", "Attack_D_Med", "Attack_RMB",
                 "HitReact_Front", "Death", "Deflect_InPlace", "Stun_Start"):
        seq = by_name[("AnimSequence", name)].get_asset()
        log("%s length=%.2f rate=%s notifies=%s" % (
            name, seq.get_play_length(), seq.get_editor_property("rate_scale"),
            [str(n.get_editor_property("notify_name")) for n in seq.get_editor_property("notifies")]))

    anim_bp = by_name[("AnimBlueprint", "Greystone_AnimBlueprint")].get_asset()
    log("AnimBP generated class: %s" % anim_bp.generated_class())
    log("AnimBP path: %s" % by_name[("AnimBlueprint", "Greystone_AnimBlueprint")].get_object_path_string()
        if hasattr(by_name[("AnimBlueprint", "Greystone_AnimBlueprint")], "get_object_path_string")
        else by_name[("AnimBlueprint", "Greystone_AnimBlueprint")].object_path)


main()
