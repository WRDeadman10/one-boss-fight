"""
Gate 0 pack facts (G0-2, G0-3): the pack boss and player assets the art request depends on. Log prefix [G0]. Read only.
Run with Scripts/run_in_editor.py. Prints: boss Blueprint, mesh, skeleton, scale, capsule, sockets, bone count, weapon meshes,
montage lengths, sections and notifies of the boss attack montages, and the weapon trace notify setup.
"""
import unreal

log = lambda m: unreal.log("[G0] " + m)
ar = unreal.AssetRegistryHelpers.get_asset_registry()


def find(name, cls=None):
    out = []
    for ad in ar.get_assets_by_path("/Game/AdvancedARPGCombat", recursive=True):
        if str(ad.asset_name) == name and (cls is None or str(ad.asset_class_path.asset_name) == cls):
            out.append(ad)
    return out


def describe_mesh(mesh, label):
    if not mesh:
        log("%s: none" % label)
        return
    log("%s: %s" % (label, mesh.get_path_name()))
    try:
        sk = mesh.get_editor_property("skeleton")
        log("  skeleton: %s" % (sk.get_path_name() if sk else None))
    except Exception as e:
        log("  skeleton ERR %s" % e)
    try:
        b = mesh.get_bounds()
        log("  bounds extent: %.0f x %.0f x %.0f cm (full size %.0f x %.0f x %.0f)" % (b.box_extent.x, b.box_extent.y, b.box_extent.z, b.box_extent.x * 2, b.box_extent.y * 2, b.box_extent.z * 2))
    except Exception as e:
        log("  bounds ERR %s" % e)
    try:
        n = mesh.num_sockets()
        names = []
        for i in range(n):
            so = mesh.get_socket_by_index(i)
            names.append("%s@%s" % (so.get_editor_property("socket_name"), so.get_editor_property("bone_name")))
        log("  sockets (%d): %s" % (n, ", ".join(names)))
    except Exception as e:
        log("  sockets ERR %s" % e)


# Boss Blueprint and its components
for ad in find("BP_ExampleGreatSwordBoss"):
    log("BOSS BLUEPRINT %s" % ad.package_name)
    bp = ad.get_asset()
    cls = bp.generated_class() if hasattr(bp, "generated_class") else None
    if cls is None:
        cls = unreal.load_class(None, str(ad.package_name) + "." + str(ad.asset_name) + "_C")
    cdo = unreal.get_default_object(cls)
    try:
        log("  parent class: %s" % cls.get_super_class() if hasattr(cls, "get_super_class") else cls)
    except Exception:
        pass
    mesh_comp = cdo.get_editor_property("mesh")
    describe_mesh(mesh_comp.get_editor_property("skeletal_mesh_asset"), "BOSS MESH")
    try:
        t = mesh_comp.get_editor_property("relative_scale3d")
        loc = mesh_comp.get_editor_property("relative_location")
        log("  mesh component scale %s location %s" % (t, loc))
    except Exception as e:
        log("  scale ERR %s" % e)
    cap = cdo.get_editor_property("capsule_component")
    log("  capsule radius %.0f half height %.0f; actor scale %s" % (cap.get_editor_property("capsule_radius"), cap.get_editor_property("capsule_half_height"), cdo.get_editor_property("root_component").get_editor_property("relative_scale3d")))
    try:
        for c in cdo.get_components_by_class(unreal.SceneComponent):
            log("  component %s (%s)" % (c.get_name(), c.get_class().get_name()))
    except Exception as e:
        log("  components ERR %s" % e)

# Player mesh
for ad in find("BP_CombatPlayerCharacter"):
    bp = ad.get_asset()
    cls = unreal.load_class(None, str(ad.package_name) + "." + str(ad.asset_name) + "_C")
    cdo = unreal.get_default_object(cls)
    describe_mesh(cdo.get_editor_property("mesh").get_editor_property("skeletal_mesh_asset"), "PLAYER MESH")
    cap = cdo.get_editor_property("capsule_component")
    log("  player capsule radius %.0f half height %.0f" % (cap.get_editor_property("capsule_radius"), cap.get_editor_property("capsule_half_height")))

# Boss attack montages
names = ["GS_Attack01_Montage", "GS_Attack02_Montage", "GS_Attack03_Montage", "GS_Attack04_Montage", "GS_ChargedAttack_Montage", "GS_LeapAttack_Montage",
         "GS_SprintAttackFollowUp_Montage", "RetaliationAttack_Montage", "KnockdownStart_Anim_Montage", "Knockdown_Getup_Anim_Montage", "Ability_R_Intro_Anim_Montage",
         "Death_Fwd_Montage", "Death_Back_Montage", "DrinkingPotion_Montage", "Dodge_To_Idle_Montage", "PrimaryAttack_A_Slow_Montage", "ChargedAttack_Montage"]
for n in names:
    hits = find(n)
    if not hits:
        log("MONTAGE %s: not found" % n)
    for ad in hits:
        m = ad.get_asset()
        try:
            length = m.get_editor_property("sequence_length")
        except Exception:
            length = -1
        try:
            secs = [str(m.get_section_name(i)) for i in range(m.get_num_sections())]
        except Exception as e:
            secs = "ERR %s" % e
        try:
            slots = [str(x) for x in unreal.AnimationLibrary.get_montage_slot_names(m)]
        except Exception as e:
            slots = "ERR %s" % e
        log("MONTAGE %s %s len=%.2f sections=%s slots=%s" % (n, ad.package_name, length, secs, slots))
        try:
            for ev in unreal.AnimationLibrary.get_animation_notify_events(m):
                def prop(p):
                    try:
                        return ev.get_editor_property(p)
                    except Exception:
                        return "?"
                nsc, nfy = prop("notify_state_class"), prop("notify")
                try:
                    t = unreal.AnimationLibrary.get_anim_notify_event_trigger_time(ev)
                    d = unreal.AnimationLibrary.get_anim_notify_event_duration(ev)
                except Exception:
                    t, d = -1.0, -1.0
                log("    notify %s t=%.2f dur=%.2f state=%s notify=%s" % (prop("notify_name"), t, d, nsc.get_class().get_name() if nsc not in (None, "?") else nsc, nfy.get_class().get_name() if nfy not in (None, "?") else nfy))
        except Exception as e:
            log("    notifies ERR %s" % e)
log("done")
