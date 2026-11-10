"""Author the isolated C-1257 Greystone ER player candidate.

Default mode is --dry-run: it validates source montage and retarget sequence
readbacks without constructing montage USTRUCTs in Python. Pass --write only for the approved Lead-run authoring
path. Write mode creates five new assets only under ALLOWLIST, saves then
reloads each package for notify/property readback, and removes only assets
created by this invocation if any validation fails.
"""
import re
import sys
import traceback

try:
    import unreal
except ImportError:
    unreal = None

PREFIX = "[GreystoneER] "
ALLOWLIST = "/Game/OneBossFight/Player/Greystone/"
CHILD_PATH = ALLOWLIST + "BP_GreystoneERPlayer"
PARENT_PATH = "/Game/OneBossFight/GreystonePack/BP_GreystonePlayer"
SKELETON_PATH = "/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone_Skeleton"
TIMING_CLASS_PATH = "/Script/OneBossFight.RPGDodgeTiming"
CREATED_ASSETS = []
WRITE_MODE = False

MONTAGES = [
    {
        "source": "/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2",
        "sequence": "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Backstep_Mixamo_V2_Fit_Greystone",
        "name": "AM_ER_Backstep_Mixamo_V2_Fit_Greystone",
        "field": "backstep_montage",
        "track_names": ["1", "2"],
        "notifies": [("ANS_iFrames", 0.091, 0.323, True, None),
                     ("ANS_InputBuffer", 0.198, 0.369, True, None)],
    },
    {
        "source": "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light",
        "sequence": "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Light_Fit_Greystone",
        "name": "AM_ER_Attack_Air_Light_Fit_Greystone",
        "field": "air_light_montage",
        "track_names": ["1", "2"],
        "notifies": [
            ("ANS_DisableMovement", 0.000, 0.600, True, None),
            ("ANS_CollisionTrace", 0.150, 0.186, True, "default"),
        ],
    },
    {
        "source": "/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge",
        "sequence": "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_Air_Heavy_Plunge_Fit_Greystone",
        "name": "AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone",
        "field": "air_heavy_montage",
        "track_names": ["1", "2", "3"],
        "notifies": [
            ("ANS_DisableMovement", 0.000, 0.867, True, None),
            ("ANS_InputBuffer", 0.150, 0.214, True, None),
            ("ANS_CollisionTrace", 0.150, 0.186, True, "strong"),
        ],
    },
    {
        "source": "/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter",
        "sequence": "/Game/OneBossFight/Player/FitTest/Greystone/AN_ER_Attack_GuardCounter_Fit_Greystone",
        "name": "AM_ER_Attack_GuardCounter_Fit_Greystone",
        "field": "guard_counter_montage",
        "track_names": ["1", "2", "3", "4", "5", "6", "7"],
        "notifies": [
            ("ANS_DisableMovement", 0.000, 0.800, True, None),
            ("ANS_SetDesiredRotation", 0.000, 0.123, True, "copy"),
            ("ANS_CancelFrames", 0.000, 0.137, True, None),
            ("ANS_InputBuffer", 0.151, 0.120, True, None),
            ("ANS_CollisionTrace", 0.168, 0.089, True, "strong"),
            ("AnimNotify_PlaySound", 0.168, 0.000, False, "copy"),
            ("ANS_MovementCancel", 0.351, 0.449, True, None),
        ],
    },
]

NOTIFY_CLASS_PATHS = {
    "ANS_iFrames": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_iFrames.ANS_iFrames_C",
    "ANS_InputBuffer": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C",
    "ANS_DisableMovement": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_DisableMovement.ANS_DisableMovement_C",
    "ANS_CollisionTrace": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/AnimNotifies/ANS_CollisionTrace.ANS_CollisionTrace_C",
    "ANS_SetDesiredRotation": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_SetDesiredRotation.ANS_SetDesiredRotation_C",
    "ANS_CancelFrames": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_CancelFrames.ANS_CancelFrames_C",
    "AnimNotify_PlaySound": "/Script/Engine.AnimNotify_PlaySound",
    "ANS_MovementCancel": "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_MovementCancel.ANS_MovementCancel_C",
}
ATTACK_DATA = {
    "strong": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/DataAssets/AttackData/StrongMeleeAttackData",
}
CHILD_FIELDS = {
    "BackstepMontage": "backstep_montage",
    "AirLightMontage": "air_light_montage",
    "AirHeavyMontage": "air_heavy_montage",
    "GuardCounterMontage": "guard_counter_montage",
    "QuickMontage": "/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey",
    "FullMontage": "/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey",
}
EXPECTED = {
    "ANS_iFrames": (0.075, 0.343), "ANS_InputBuffer": (0.164, 0.351),
    "ANS_DisableMovement": (0.0, 0.600), "ANS_CollisionTrace": (0.150, 0.336),
    "ANS_SetDesiredRotation": (0.0, 0.123), "ANS_CancelFrames": (0.0, 0.137),
    "ANS_MovementCancel": (0.351, 0.800),
}


def log(message):
    if unreal:
        unreal.log(PREFIX + str(message))
    print(PREFIX + str(message))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path):
    obj = unreal.load_asset(path)
    require(obj is not None, "missing required asset: " + path)
    return obj


def prop(obj, name):
    return obj.get_editor_property(name)


def set_prop(obj, name, value):
    obj.set_editor_property(name, value)


def package_name(obj):
    return str(obj.get_path_name()).split(".", 1)[0]


def register_created_asset(asset):
    path = package_name(asset)
    require(path.startswith(ALLOWLIST), "new asset escaped approved allowlist: " + path)
    require(path not in CREATED_ASSETS, "asset registered twice: " + path)
    CREATED_ASSETS.append(path)
    log("CREATED_ASSET_TRACKED=" + path)


def rollback_created_assets():
    eal = unreal.EditorAssetLibrary
    deleted = []
    failed = []
    for path in reversed(CREATED_ASSETS):
        if not path.startswith(ALLOWLIST):
            failed.append((path, "outside allowlist; refused deletion"))
            continue
        try:
            if not eal.does_asset_exist(path):
                log("ROLLBACK_ALREADY_ABSENT=" + path)
                continue
            ok = bool(eal.delete_asset(path))
            if ok and not eal.does_asset_exist(path):
                deleted.append(path)
                log("ROLLBACK_DELETED=" + path)
            else:
                failed.append((path, "EditorAssetLibrary.delete_asset failed"))
                log("ROLLBACK_DELETE_FAILED=" + path)
        except Exception as exc:
            failed.append((path, repr(exc)))
            log("ROLLBACK_DELETE_ERROR path=%s error=%s" % (path, repr(exc)))
    log("ROLLBACK_RECEIPT created=%d deleted=%d failed=%d" %
        (len(CREATED_ASSETS), len(deleted), len(failed)))
    for path, reason in failed:
        log("ROLLBACK_REMAINS path=%s reason=%s" % (path, reason))
    return not failed


def reload_saved_asset(asset, expected_class_name):
    path = package_name(asset)
    require(path.startswith(ALLOWLIST), "reload target escaped allowlist: " + path)
    require(unreal.EditorAssetLibrary.does_asset_exist(path), "saved package is absent: " + path)
    loading = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    modes = getattr(unreal, "ReloadPackagesInteractionMode", None)
    require(loading is not None and modes is not None and hasattr(loading, "reload_packages"),
            "UE 5.5 package reload API is unavailable")
    mode = getattr(modes, "ASSUME_POSITIVE", None)
    require(mode is not None, "UE 5.5 non-interactive reload mode is unavailable")
    result = loading.reload_packages([asset.get_outermost()], mode)
    ok = bool(result[0]) if isinstance(result, tuple) else bool(result)
    error = str(result[1]) if isinstance(result, tuple) and len(result) > 1 else ""
    require(ok, "saved package reload failed: %s %s" % (path, error))
    reloaded = unreal.EditorAssetLibrary.load_asset(path)
    require(reloaded is not None, "reloaded asset failed to load: " + path)
    require(reloaded.get_class().get_name() == expected_class_name,
            "reloaded asset class mismatch at %s: %s" % (path, reloaded.get_class().get_name()))
    require(package_name(reloaded) == path, "reloaded asset package identity mismatch: " + path)
    log("PACKAGE_RELOADED path=%s class=%s" % (path, expected_class_name))
    return reloaded


def parse_dry_run():
    cmd = unreal.SystemLibrary.get_command_line()
    return bool(re.search(r"(?:^|\s)--dry-run(?:\s|$)", cmd)) or not bool(re.search(r"(?:^|\s)--write(?:\s|$)", cmd))


def notify_descriptions(montage):
    lines = list(unreal.RPGMontageUtils.describe_notifies(montage))
    require(lines, "RPGMontageUtils returned no montage/notify description")
    parsed = []
    pattern = re.compile(r"^(\[state\]\s+)?(.+?)\s+at\s+([0-9.]+)\s+s(?:\s+for\s+([0-9.]+)\s+s)?$")
    for line in lines[1:]:
        match = pattern.match(str(line).strip())
        require(match, "unparsed notify description, refusing incomplete receipt: " + str(line))
        parsed.append({"state": bool(match.group(1)), "class": match.group(2).strip(),
                       "time": float(match.group(3)), "duration": float(match.group(4) or 0.0),
                       "line": str(line).strip()})
    return lines[0], parsed


def short_notify_name(name):
    return name[:-2] if name.endswith("_C") else name


def wrapper_notify_rows(montage):
    library = getattr(unreal, "RPGMontageWrapperLibrary", None)
    require(library is not None, "editor C++ montage wrapper readback is unavailable; build Editor target")
    rows_value = library.describe_montage_notifies(montage)
    require(rows_value is not None,
            "C++ montage notify readback returned no row array")
    try:
        rows = [str(row) for row in rows_value]
    except TypeError as exc:
        raise RuntimeError("C++ montage notify readback is not iterable: " + repr(rows_value)) from exc
    return rows


def compare_wrapper_notify_rows(spec, source_rows, target_rows, target_sequence):
    pattern = re.compile(
        r"^notify=(\d+) class=(.*?) trigger=([0-9.]+) duration=([0-9.]+) "
        r"track=(-?\d+) slots=\[(.*?)\] segments=\[(.*?)\]$")
    segment_pattern = re.compile(r"^(.+?)@([0-9.]+)$")
    require(len(source_rows) == len(target_rows),
            "%s source/target native notify row counts differ" % spec["name"])
    target_path = target_sequence.get_path_name()
    target_length = float(target_sequence.get_play_length())
    for source_row, target_row in zip(source_rows, target_rows):
        source = pattern.match(source_row)
        target = pattern.match(target_row)
        require(source is not None and target is not None,
                "%s C++ notify row format is invalid: %s / %s" % (spec["name"], source_row, target_row))
        require(source.groups()[:6] == target.groups()[:6],
                "%s source/target notify identity, timing, track, or slot differs: %s / %s" %
                (spec["name"], source_row, target_row))
        source_segments = [segment_pattern.match(item) for item in source.group(7).split(",") if item]
        target_segments = [segment_pattern.match(item) for item in target.group(7).split(",") if item]
        require(source_segments and all(item is not None for item in source_segments),
                "%s source segment description is missing or malformed" % spec["name"])
        require(len(target_segments) == len(source_segments) and all(item is not None for item in target_segments),
                "%s target segment layout differs from source" % spec["name"])
        for segment in target_segments:
            require(segment.group(1) == target_path and abs(float(segment.group(2)) - target_length) <= 0.000001,
                    "%s target segment path/length mismatch: %s expected %s@%.6f" %
                    (spec["name"], segment.group(0), target_path, target_length))
    return len(source_rows)


def source_readback(spec):
    source = load(spec["source"])
    seq = load(spec["sequence"])
    require(source.get_class().get_name() == "AnimMontage", "source wrapper is not AnimMontage")
    require(seq.get_class().get_name() == "AnimSequence", "fit output is not AnimSequence")
    require(package_name(prop(seq, "skeleton")) == SKELETON_PATH,
            "fit sequence skeleton mismatch: %s actual=%s expected=%s" % (spec["sequence"], package_name(prop(seq, "skeleton")), SKELETON_PATH))
    info, desc = notify_descriptions(source)
    native_rows = wrapper_notify_rows(source)
    require(len(native_rows) == len(desc),
            "%s C++ source notify readback disagrees with montage helper count" % spec["name"])
    section_match = re.search(r"\bsections\s+(\d+)\b", info)
    require(section_match is not None, "source section count unavailable from montage helper")
    sections = int(section_match.group(1))
    actual_slot = str(unreal.RPGMontageUtils.get_montage_slot(source))
    require(actual_slot != "None", "source montage has no slot")
    names = [short_notify_name(d["class"]) for d in desc]
    expected_names = [n[0] for n in spec["notifies"]]
    require(sorted(names) == sorted(expected_names), "%s notify class inventory differs from the approved plan: %s" % (spec["name"], names))
    track_names = list(unreal.AnimationLibrary.get_animation_notify_track_names(source))
    require(track_names == spec["track_names"], "%s notify track names/order differ from the approved plan: %s" % (spec["name"], track_names))
    # Root-motion extraction is authored on the sequence segment, not the
    # montage in UE 5.5. Compare the source montage's first segment with the
    # Greystone retarget sequence that the new wrapper will reference.
    source_sequence = source.get_first_anim_reference()
    require(source_sequence is not None, "%s source montage segment has no sequence" % spec["name"])
    for field in ("enable_root_motion", "root_motion_root_lock"):
        source_value = prop(source_sequence, field)
        target_value = prop(seq, field)
        require(source_value == target_value,
                "%s retarget sequence root-motion setting differs from source (%s: %s != %s)" %
                (spec["name"], field, source_value, target_value))
        log("ROOT_MOTION_SEQUENCE montage=%s field=%s source=%s target=%s" %
            (spec["name"], field, source_value, target_value))
    expected_by_name = {row[0]: row for row in spec["notifies"]}
    for d in desc:
        class_name = short_notify_name(d["class"])
        require(class_name in expected_by_name, "%s source has unexpected notify class: %s" % (spec["name"], class_name))
        _short_name, _start, _duration, is_state, _payload = expected_by_name[class_name]
        require(d["state"] == is_state, "%s notify kind mismatch: %s" % (spec["name"], d["line"]))
        log("SOURCE_NOTIFY_READBACK montage=%s %s" % (spec["name"], d["line"]))
    return source, seq, info, desc, actual_slot, sections


def readback_montage(spec, montage, expected_slot, source_desc,
                     expected_sequence=None, expected_sections=None):
    actual_slot = str(unreal.RPGMontageUtils.get_montage_slot(montage))
    require(actual_slot == expected_slot,
            "%s slot readback mismatch: expected %s got %s" % (spec["name"], expected_slot, actual_slot))
    require(package_name(prop(montage, "skeleton")) == SKELETON_PATH,
            "%s skeleton readback mismatch" % spec["name"])
    tracks = list(unreal.AnimationLibrary.get_animation_notify_track_names(montage))
    require(tracks == spec["track_names"],
            "%s notify-track readback mismatch: expected %s got %s" % (spec["name"], spec["track_names"], tracks))
    if expected_sequence is not None:
        actual_sequence = montage.get_first_anim_reference()
        require(actual_sequence is not None and actual_sequence.get_path_name() == expected_sequence.get_path_name(),
                "%s target sequence readback mismatch" % spec["name"])
        for field in ("enable_root_motion", "root_motion_root_lock"):
            require(prop(actual_sequence, field) == prop(expected_sequence, field),
                    "%s root-motion readback mismatch: %s" % (spec["name"], field))
    desc_header, parsed = notify_descriptions(montage)
    native_rows = wrapper_notify_rows(montage)
    require(len(native_rows) == len(parsed),
            "%s C++ target notify readback disagrees with montage helper count" % spec["name"])
    if expected_sections is not None:
        section_match = re.search(r"\bsections\s+(\d+)\b", desc_header)
        require(section_match is not None and int(section_match.group(1)) == expected_sections,
                "%s section-count readback mismatch: expected %s, got %s" % (spec["name"], expected_sections, desc_header))
    lines = [p["line"] for p in parsed]
    require(len(parsed) == len(spec["notifies"]), "%s notify count readback mismatch" % spec["name"])
    source_rows = [(short_notify_name(x["class"]), x["state"], round(x["time"], 4), round(x["duration"], 4))
                   for x in source_desc]
    target_rows = [(short_notify_name(x["class"]), x["state"], round(x["time"], 4), round(x["duration"], 4))
                   for x in parsed]
    require(target_rows == source_rows,
            "%s source-time notify readback mismatch: source=%s target=%s" % (spec["name"], source_rows, target_rows))
    log("CPP_NOTIFY_READBACK %s rows=%s" % (spec["name"], native_rows))
    log("NOTIFY_READBACK %s header=%s slot=%s tracks=%s count=%d" %
        (spec["name"], desc_header, actual_slot, tracks, len(parsed)))
    for line in lines:
        log("NOTIFY %s %s" % (spec["name"], line))


def child_component_handle(bp):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = list(subsystem.k2_gather_subobject_data_for_blueprint(bp))
    # C-1280 Lead fix: UE 5.5 exposes is_root_actor/is_root_component, not is_root. The actor node is the first
    # gathered handle (the pattern proven by greystone_sevarog_11_polish.py); non-scene components attach under it.
    require(len(handles) > 0, "SubobjectDataSubsystem returned no handles for the child Blueprint")
    root = None
    for handle in handles:
        data = lib.get_data(handle)
        if getattr(lib, "is_root_actor")(data) if hasattr(lib, "is_root_actor") else False:
            root = handle
            break
    if root is None:
        root = handles[0]
    existing = existing_child_timing(bp)
    require(existing is None, "child already inherits a URPGDodgeTiming component; refusing to add a second one")
    params = unreal.AddNewSubobjectParams()
    set_prop(params, "parent_handle", root)
    set_prop(params, "new_class", unreal.load_class(None, TIMING_CLASS_PATH))
    set_prop(params, "blueprint_context", bp)
    result = subsystem.add_new_subobject(params)
    handle = result[0] if isinstance(result, tuple) else result
    reason = str(result[1]) if isinstance(result, tuple) and len(result) > 1 else ""
    require(handle is not None and not reason, "failed to add URPGDodgeTiming component: " + reason)
    data = lib.get_data(handle)
    component = lib.get_object(data)
    require(component is not None and component.get_class().get_name() == "RPGDodgeTiming", "new subobject is not URPGDodgeTiming")
    return subsystem, handle, component


def existing_child_timing(bp):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    for handle in list(subsystem.k2_gather_subobject_data_for_blueprint(bp)):
        data = lib.get_data(handle)
        component = lib.get_object(data)
        if component is not None and component.get_class().get_name() == "RPGDodgeTiming":
            return component
    return None


def readback_child_bp(bp, montages):
    parent = load(PARENT_PATH)
    parent_cdo = unreal.get_default_object(parent.generated_class())
    child_cdo = unreal.get_default_object(bp.generated_class())
    source_mesh = prop(parent_cdo, "mesh")
    target_mesh = prop(child_cdo, "mesh")
    require(prop(target_mesh, "skeletal_mesh_asset") == prop(source_mesh, "skeletal_mesh_asset"),
            "reloaded child Greystone mesh readback mismatch")
    require(prop(target_mesh, "anim_class") == prop(source_mesh, "anim_class"),
            "reloaded child Greystone AnimBP readback mismatch")
    timing = existing_child_timing(bp)
    require(timing is not None, "reloaded child has no URPGDodgeTiming component")
    for property_name, value in CHILD_FIELDS.items():
        if property_name in ("BackstepMontage", "AirLightMontage", "AirHeavyMontage", "GuardCounterMontage"):
            value = montages[value]
        else:
            value = load(value)
        field = property_name[0].lower() + property_name[1:]
        actual = prop(timing, field)
        require(actual is not None and actual.get_path_name() == value.get_path_name(),
                "reloaded child montage assignment mismatch: %s" % property_name)
        log("CHILD_READBACK field=%s asset=%s" % (property_name, actual.get_path_name()))
    require(package_name(prop(target_mesh, "skeletal_mesh_asset")).endswith("/Greystone"),
            "reloaded child mesh is not the Greystone skeletal mesh")
    return timing


def create_child_bp(montages):
    eal = unreal.EditorAssetLibrary
    require(CHILD_PATH.startswith(ALLOWLIST), "child path escaped allowlist")
    require(not eal.does_asset_exist(CHILD_PATH), "refusing to overwrite child BP: " + CHILD_PATH)
    parent = load(PARENT_PATH)
    factory = unreal.BlueprintFactory()
    set_prop(factory, "parent_class", parent.generated_class())
    bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset("BP_GreystoneERPlayer", ALLOWLIST.rstrip("/"), unreal.Blueprint, factory)
    require(bp is not None and bp.get_path_name().startswith(ALLOWLIST), "child Blueprint creation failed/outside allowlist")
    register_created_asset(bp)
    parent_cdo = unreal.get_default_object(parent.generated_class())
    child_cdo = unreal.get_default_object(bp.generated_class())
    source_mesh = prop(parent_cdo, "mesh")
    target_mesh = prop(child_cdo, "mesh")
    set_prop(target_mesh, "skeletal_mesh_asset", prop(source_mesh, "skeletal_mesh_asset"))
    set_prop(target_mesh, "animation_mode", prop(source_mesh, "animation_mode"))
    set_prop(target_mesh, "anim_class", prop(source_mesh, "anim_class"))
    require(package_name(prop(target_mesh, "skeletal_mesh_asset")).endswith("/Greystone"), "child mesh is not Greystone")
    require(prop(target_mesh, "anim_class") == prop(source_mesh, "anim_class"), "Greystone visual AnimBP was not preserved")
    subsystem, handle, timing = child_component_handle(bp)
    for property_name, value in CHILD_FIELDS.items():
        if property_name in ("BackstepMontage", "AirLightMontage", "AirHeavyMontage", "GuardCounterMontage"):
            value = montages[value]
        else:
            value = load(value)
        field = property_name[0].lower() + property_name[1:]
        set_prop(timing, field, value)
        require(prop(timing, field) == value, "child component assignment readback mismatch: " + property_name)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    require(bp.get_path_name().startswith(ALLOWLIST), "compiled child escaped allowlist")
    require(eal.save_loaded_asset(bp), "failed to save child Blueprint")
    log("SAVED " + bp.get_path_name())
    reloaded = reload_saved_asset(bp, "Blueprint")
    readback_child_bp(reloaded, montages)
    return reloaded


def run():
    global WRITE_MODE
    require(unreal is not None, "must run in Unreal Editor Python")
    dry = parse_dry_run()
    WRITE_MODE = not dry
    eal = unreal.EditorAssetLibrary
    log("MODE=" + ("DRY_RUN_TRANSIENT" if dry else "WRITE"))
    require(unreal.load_asset(SKELETON_PATH) is not None, "Greystone skeleton missing")
    montage_paths = [ALLOWLIST + x["name"] for x in MONTAGES]
    if dry:
        require(not eal.does_asset_exist(CHILD_PATH), "dry-run refused: child already exists")
        for path in montage_paths:
            require(not eal.does_asset_exist(path), "dry-run refused: output already exists " + path)
    else:
        for path in [CHILD_PATH] + montage_paths:
            require(path.startswith(ALLOWLIST), "write target escaped allowlist: " + path)
            require(not eal.does_asset_exist(path), "refusing overwrite of existing output: " + path)

    validated_sources = []
    for spec in MONTAGES:
        source, seq, source_info, source_desc, slot, sections = source_readback(spec)
        log("SOURCE %s %s slot=%s sections=%s sequence=%s" % (spec["name"], source_info, slot, sections, seq.get_path_name()))
        validated_sources.append((source, seq, slot, sections, source_desc))

    targets = {}
    for spec, validated in zip(MONTAGES, validated_sources):
        source, seq, slot, sections, source_desc = validated
        if dry:
            log("DRY_RUN_WRAPPER_PLAN source=%s targetSequence=%s slot=%s sections=%s sourceNotifies=%d" %
                (source.get_path_name(), seq.get_path_name(), slot, sections, len(source_desc)))
            continue
        wrapper_library = getattr(unreal, "RPGMontageWrapperLibrary", None)
        require(wrapper_library is not None, "editor C++ RPGMontageWrapperLibrary is unavailable; build Editor target")
        # C-1280 Lead fix: OutError is an out-parameter returned in the tuple, not a 5th argument.
        result = wrapper_library.create_retarget_wrapper(
            source, seq, unreal.load_asset(SKELETON_PATH), ALLOWLIST + spec["name"])
        montage = result[0] if isinstance(result, tuple) else result
        error = str(result[1]) if isinstance(result, tuple) and len(result) > 1 else ""
        require(montage is not None, "C++ montage wrapper creation failed: " + error)
        register_created_asset(montage)
        readback_montage(spec, montage, slot, source_desc, seq, sections)
        if not dry:
            require(package_name(prop(montage, "skeleton")) == SKELETON_PATH, "wrapper skeleton readback mismatch")
        if not dry:
            require(montage.get_path_name().startswith(ALLOWLIST), "montage package escaped allowlist")
            require(eal.save_loaded_asset(montage), "failed to save montage: " + spec["name"])
            log("SAVED " + montage.get_path_name())
            montage = reload_saved_asset(montage, "AnimMontage")
            readback_montage(spec, montage, slot, source_desc, seq, sections)
        targets[spec["field"]] = montage

    if dry:
        log("CHILD_BP=transient-plan-only path=%s parent=%s mesh=Greystone animbp=existing-Greystone-visual" % (CHILD_PATH, PARENT_PATH))
        log("PREFLIGHT_PASS=1; SAVED_COUNT=0; PACKAGE_COUNT=0; PACK_PATH_WRITES=0; source timings inventoried; C++ wrapper required for write mode")
    else:
        bp = create_child_bp(targets)
        log("CHILD_BP_SAVED=" + bp.get_path_name())
        log("SAVED_COUNT=%d; PACKAGE_COUNT=%d; PACK_PATH_WRITES=0; DEFAULT_PLAYER_UNCHANGED=1" %
            (len(CREATED_ASSETS), len(CREATED_ASSETS)))
    return True


if __name__ == "__main__":
    try:
        ok = run()
    except Exception as exc:
        log("ERROR " + repr(exc))
        traceback.print_exc()
        if WRITE_MODE and CREATED_ASSETS:
            try:
                rollback_created_assets()
            except Exception as rollback_exc:
                log("ROLLBACK_FATAL=" + repr(rollback_exc))
        ok = False
    if unreal is not None:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
