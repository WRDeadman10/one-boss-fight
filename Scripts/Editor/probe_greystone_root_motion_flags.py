"""C-1283 Lead read-only probe: why does the Greystone child show 0 cm root-motion displacement?

Reads (never writes): the Greystone child BP and the mannequin BP -> mesh anim class -> AnimInstance CDO
root_motion_mode; the montages assigned on URPGDodgeTiming (backstep/quick) for both pawns -> segment
sequences -> enable_root_motion / root_motion_root_lock / force_root_lock; the source ER montages' sequences.
Log prefix [GreystoneRMProbe]; ends with "[GreystoneRMProbe] finished".
"""
import unreal

PREFIX = "[GreystoneRMProbe] "
CHILD = "/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer"
GREY_PARENT = "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer"
MANNEQUIN = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Characters/BP_CombatPlayerCharacter"
MONTAGES = [
    "/Game/OneBossFight/Player/Greystone/AM_ER_Backstep_Mixamo_V2_Fit_Greystone",
    "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2",
    "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey",
    "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_Small_Forward_Roll_Montage",
    "/Game/OneBossFight/Player/Greystone/AM_ER_Attack_Air_Light_Fit_Greystone",
    "/Game/OneBossFight/Player/Greystone/AM_ER_Attack_GuardCounter_Fit_Greystone",
]


def log(m):
    unreal.log(PREFIX + m)


def prop(obj, name):
    try:
        return obj.get_editor_property(name)
    except Exception as exc:
        return "ERR(%s)" % exc.__class__.__name__


def describe_bp(path):
    bp = unreal.load_asset(path)
    if bp is None:
        log("BP %s missing" % path)
        return
    cls = bp.generated_class()
    cdo = unreal.get_default_object(cls)
    mesh = prop(cdo, "mesh")
    anim_class = prop(mesh, "anim_class") if mesh else None
    mode = prop(mesh, "animation_mode") if mesh else None
    sk = prop(mesh, "skeletal_mesh_asset") if mesh else None
    rm_mode = None
    if anim_class:
        anim_cdo = unreal.get_default_object(anim_class)
        rm_mode = prop(anim_cdo, "root_motion_mode")
    log("BP %s class=%s mesh=%s animation_mode=%s anim_class=%s anim_root_motion_mode=%s" %
        (path.rsplit("/", 1)[-1], cls.get_name(), sk.get_path_name() if sk else None, mode,
         anim_class.get_path_name() if anim_class else None, rm_mode))
    movement = None
    for comp_name in ("CharacterMovement", "CharMoveComp"):
        try:
            movement = cdo.get_component_by_class(unreal.CharacterMovementComponent)
            break
        except Exception:
            movement = None
    if movement:
        log("BP %s movement default_land_movement_mode=%s" % (path.rsplit("/", 1)[-1], prop(movement, "default_land_movement_mode")))
    timing = None
    try:
        timing = cdo.get_component_by_class(unreal.RPGDodgeTiming)
    except Exception:
        timing = None
    if timing:
        log("BP %s RPGDodgeTiming backstep=%s quick=%s full=%s" %
            (path.rsplit("/", 1)[-1], prop(timing, "backstep_montage"), prop(timing, "quick_montage"), prop(timing, "full_montage")))
    else:
        log("BP %s RPGDodgeTiming component not on CDO (runtime-attached for the pack player)" % path.rsplit("/", 1)[-1])


def describe_montage(path):
    montage = unreal.load_asset(path)
    if montage is None:
        log("MONTAGE %s missing" % path)
        return
    seq = montage.get_first_anim_reference()
    skel = prop(montage, "skeleton")
    log("MONTAGE %s skeleton=%s slot=%s length=%.4f blend_in=%s blend_out=%s" %
        (montage.get_name(), skel.get_name() if skel else None, prop(montage, "slot_anim_tracks") and "n/a", montage.get_play_length(),
         prop(prop(montage, "blend_in"), "blend_time"), prop(prop(montage, "blend_out"), "blend_time")))
    if seq is None:
        log("MONTAGE %s first segment sequence=None" % montage.get_name())
        return
    log("SEQUENCE %s path=%s skeleton=%s enable_root_motion=%s root_motion_root_lock=%s force_root_lock=%s length=%.4f frames=%s" %
        (montage.get_name(), seq.get_path_name(), prop(seq, "skeleton").get_name() if prop(seq, "skeleton") else None,
         prop(seq, "enable_root_motion"), prop(seq, "root_motion_root_lock"), prop(seq, "force_root_lock"),
         seq.get_play_length(), prop(seq, "number_of_sampled_frames")))
    try:
        delta = seq.extract_root_motion(0.0, seq.get_play_length(), False)
        log("ROOTMOTION %s extracted_translation=(%.2f,%.2f,%.2f) distance_cm=%.2f" %
            (montage.get_name(), delta.translation.x, delta.translation.y, delta.translation.z, delta.translation.size()))
    except Exception as exc:
        log("ROOTMOTION %s extract failed: %r" % (montage.get_name(), exc))


for bp_path in (CHILD, GREY_PARENT, MANNEQUIN):
    try:
        describe_bp(bp_path)
    except Exception as exc:
        log("BP %s ERROR %r" % (bp_path, exc))
for m in MONTAGES:
    try:
        describe_montage(m)
    except Exception as exc:
        log("MONTAGE %s ERROR %r" % (m, exc))
log("finished")
