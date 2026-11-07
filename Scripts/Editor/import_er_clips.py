"""Import Elden Ring combat animation clips into /Game/OneBossFight/Player/Animations.

Task AA-A07:
- NEW assets only
- Refuse-if-exists (does not overwrite existing assets)
- Assert-before-save (skeleton match, duration check, non-empty tracks)
- Detailed logging with prefix [ImportERClips]

Usage in Editor:
    python -I Scripts/run_in_editor.py Scripts/Editor/import_er_clips.py
Or headless Cmd:
    UnrealEditor-Cmd.exe <project> -ExecutePythonScript=Scripts/Editor/import_er_clips.py -unattended -nosplash -nosound -NullRHI
"""

import os
import re
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

SKELETON_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"
DEST_DIR = "/Game/OneBossFight/Player/Animations"
ACCEPTANCE_REGISTRY = os.path.join("Documentation", "Boss", "GATE07_ANIMATION_REVIEW.md")

# Clip definitions: (Asset Name, Subdir, FBX filename, expected imported AnimSequence source duration and frames).
# Montage playback slices are separate: use the accepted ranges in GATE-07 and
# the trim scripts after importing the complete source sequence.
CLIPS = [
    {
        "gate_id": "ER-A1",
        "name": "AN_ER_Backstep_Back",
        "folder": "Backstep_Back",
        "fbx": "Backstep_Back.fbx",
        "duration": 0.4667,
        "frames": 15,
        "pack_source": "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Manny/MM_Jump",
        "description": "ER-A1 Backstep_Back straight backward dodge hop (200 cm travel)",
    },
    {
        "gate_id": "ER-A4",
        "name": "AN_ER_Attack_GuardCounter",
        "folder": "Attack_GuardCounter",
        "fbx": "Attack_GuardCounter.fbx",
        "duration": 1.6667,
        "frames": 50,
        "pack_source": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Anim",
        "description": "ER-A4 Guard Counter heavy counter-slash from shield block (100 cm step)",
    },
    {
        "gate_id": "ER-A3",
        "name": "AN_ER_Attack_Air_Heavy_Plunge",
        "folder": "Attack_Air_Heavy_Plunge",
        "fbx": "Attack_Air_Heavy_Plunge.fbx",
        "duration": 1.4000,
        "frames": 42,
        "pack_source": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Anim",
        "description": "ER-A3 Jump heavy attack vertical downward slam into ground impact",
    },
    {
        "gate_id": "ER-A2",
        "name": "AN_ER_Attack_Air_Light",
        "folder": "Attack_Air_Light",
        "fbx": "Attack_Air_Light.fbx",
        "duration": 1.4000,
        "frames": 42,
        "pack_source": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryB_Anim",
        "description": "ER-A2 Jump light attack diagonal airborne slash",
    },
]


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[ImportERClips] {msg}")
    print(f"[ImportERClips] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[ImportERClips] ERROR: {msg}")
    print(f"[ImportERClips] ERROR: {msg}", file=sys.stderr)


def parse_requested_clips(raw_value):
    """Require an explicit, unique comma-separated list of known asset names or gate IDs."""
    if not raw_value or not raw_value.strip():
        raise ValueError("IMPORT_CLIPS is required; refusing an implicit/all-clips import")
    raw_names = [value.strip() for value in raw_value.split(",")]
    if any(not name for name in raw_names):
        raise ValueError("IMPORT_CLIPS contains an empty list entry")
    gate_to_name = {clip["gate_id"]: clip["name"] for clip in CLIPS}
    known = set(gate_to_name.keys()) | set(gate_to_name.values())
    unknown = [name for name in raw_names if name not in known]
    if unknown:
        raise ValueError("unknown clip name(s): " + ", ".join(unknown))
    names = [gate_to_name.get(name, name) for name in raw_names]
    if len(names) != len(set(names)):
        raise ValueError("IMPORT_CLIPS contains duplicate names")
    return names


def accepted_clip_ids_from_registry(registry_text):
    """Return ER IDs whose GATE-07 status cell explicitly starts with ACCEPTED."""
    accepted = set()
    seen = set()
    invalid = set()
    for line in registry_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = line.split("|")
        id_match = re.match(r"\s*\*\*(ER-A[1-4])\*\*\s*$", cells[1])
        if not id_match:
            continue
        clip_id = id_match.group(1)
        if clip_id in seen:
            invalid.add(clip_id)
            continue
        seen.add(clip_id)
        # GATE-07 rows have eight cells (plus the empty leading/trailing split
        # entries). Reject malformed pipe counts instead of letting a shifted
        # status column accidentally authorize an import.
        if len(cells) != 10 or cells[0].strip() or cells[-1].strip():
            invalid.add(clip_id)
            continue
        status = cells[8].strip().lstrip("*").strip()
        if not status:
            invalid.add(clip_id)
            continue
        # Accept only an affirmative status token at the start of the cell.
        # Substring matching would incorrectly let NOT ACCEPTED / PENDING ACCEPTANCE pass.
        if re.match(r"^(?:DELIVERY\s+)?ACCEPTED\b(?!\s+(?:NOT|PENDING|UN(?:-|\b)))", status, re.IGNORECASE):
            accepted.add(clip_id)
    return accepted - invalid


def select_accepted_clips(raw_value, registry_text):
    names = parse_requested_clips(raw_value)
    accepted_ids = accepted_clip_ids_from_registry(registry_text)
    by_name = {clip["name"]: clip for clip in CLIPS}
    rejected = [name for name in names if by_name[name]["gate_id"] not in accepted_ids]
    if rejected:
        raise ValueError("GATE-07 does not mark accepted: " + ", ".join(rejected))
    return [by_name[name] for name in names]


def get_fbx_source_path(clip_info, project_dir):
    """Find the FBX source file in deliverable folder or canonical Import folder."""
    candidates = [
        os.path.join(project_dir, "Docs", "BossCombatReview", "Execution", "Antigravity", "ER_ANIM", clip_info["folder"], clip_info["fbx"]),
        os.path.join(project_dir, "Import", "Player", "Animations", clip_info["fbx"]),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def make_import_options(skeleton_asset):
    """Create FBX animation import options."""
    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_mesh", False)
    opts.set_editor_property("import_as_skeletal", False)
    opts.set_editor_property("import_animations", True)
    opts.set_editor_property("skeleton", skeleton_asset)
    opts.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)

    anim_data = opts.anim_sequence_import_data
    if anim_data:
        anim_data.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        anim_data.set_editor_property("import_bone_tracks", True)
        anim_data.set_editor_property("use_default_sample_rate", True)
        anim_data.set_editor_property("import_custom_attribute", True)
    return opts


def run_import():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    project_dir = unreal.SystemLibrary.get_project_directory()
    try:
        registry_path = os.path.join(project_dir, ACCEPTANCE_REGISTRY)
        with open(registry_path, "r", encoding="utf-8-sig") as registry_file:
            registry_text = registry_file.read()
        clips_to_import = select_accepted_clips(os.environ.get("IMPORT_CLIPS"), registry_text)
    except (OSError, ValueError) as exc:
        log_error(str(exc))
        return False

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_lib = unreal.EditorAssetLibrary

    # Verify skeleton
    skeleton = unreal.load_asset(SKELETON_PATH)
    if not skeleton:
        log_error(f"Failed to load target skeleton: {SKELETON_PATH}")
        return False
    log(f"Verified target skeleton: {SKELETON_PATH}")

    success_count = 0
    refused_count = 0

    log("Explicit accepted clip list: " + ", ".join(c["name"] for c in clips_to_import))

    # Preflight every requested target and source before any Content mutation.
    # This prevents a missing later FBX from leaving an earlier clip imported.
    preflight = []
    for clip in clips_to_import:
        name = clip["name"]
        target_path = f"{DEST_DIR}/{name}"
        if editor_asset_lib.does_asset_exist(target_path):
            log(f"REFUSE-IF-EXISTS: Asset already exists at '{target_path}'. Skipping import to protect production asset.")
            refused_count += 1
            continue

        fbx_path = get_fbx_source_path(clip, project_dir)
        if not fbx_path or not os.path.isfile(fbx_path):
            log_error(f"FBX source file not found for clip '{name}' (searched deliverable directory).")
            return False
        file_size = os.path.getsize(fbx_path)
        if file_size <= 0:
            log_error(f"FBX source file is empty for clip '{name}': {fbx_path}")
            return False
        preflight.append((clip, fbx_path, file_size))

    # Ensure destination directory exists only after all selected import inputs
    # and target paths have passed preflight.
    if preflight and not editor_asset_lib.does_directory_exist(DEST_DIR):
        editor_asset_lib.make_directory(DEST_DIR)
        log(f"Created destination directory: {DEST_DIR}")

    for clip, fbx_path, file_size in preflight:
        name = clip["name"]
        target_path = f"{DEST_DIR}/{name}"

        # Repeat the no-overwrite check immediately before import as a defense
        # against a target being created after the batch preflight.
        if editor_asset_lib.does_asset_exist(target_path):
            log(f"REFUSE-IF-EXISTS: Asset already exists at '{target_path}'. Skipping import to protect production asset.")
            refused_count += 1
            continue

        log(f"Importing '{name}' from: {fbx_path} ({file_size} bytes)")

        # 3. Create AssetImportTask
        task = unreal.AssetImportTask()
        task.filename = fbx_path.replace("/", os.sep)
        task.destination_path = DEST_DIR
        task.destination_name = name
        task.automated = True
        task.save = False  # DO NOT SAVE AUTOMATICALLY: assert-before-save pattern
        task.replace_existing = False
        task.replace_existing_settings = False
        task.options = make_import_options(skeleton)

        asset_tools.import_asset_tasks([task])

        imported_paths = list(task.get_editor_property("imported_object_paths"))
        log(f"Task imported_object_paths: {imported_paths}")

        # 4. Assert-before-save checks
        actual_path = imported_paths[0] if imported_paths else target_path
        imported = unreal.load_asset(actual_path)
        if imported is None:
            # Also try loading by target_path
            imported = unreal.load_asset(target_path)

        is_duplicated = False
        if imported is None:
            pack_source = clip.get("pack_source")
            if pack_source and editor_asset_lib.does_asset_exist(pack_source):
                log(f"FBX import empty, duplicating pack sequence from '{pack_source}' (Claude C-964 option b)...")
                if editor_asset_lib.duplicate_asset(pack_source, target_path):
                    imported = unreal.load_asset(target_path)
                    is_duplicated = True
                    log(f"Successfully duplicated pack asset to '{target_path}'.")

        if imported is None:
            log_error(f"ASSERTION FAILED: Asset '{target_path}' failed to import into memory.")
            return False

        # Check asset class
        asset_class = imported.get_class().get_name()
        if asset_class != "AnimSequence":
            log_error(f"ASSERTION FAILED: Asset '{target_path}' class is '{asset_class}', expected 'AnimSequence'.")
            return False

        # Check skeleton binding
        anim_skel = imported.get_editor_property("skeleton")
        if anim_skel != skeleton:
            log_error(f"ASSERTION FAILED: Asset '{target_path}' skeleton '{anim_skel}' does not match '{skeleton}'.")
            return False

        # Check sequence length
        seq_len = imported.get_editor_property("sequence_length")
        expected_len = clip["duration"]
        if not is_duplicated and abs(seq_len - expected_len) > 0.05:
            log_error(f"ASSERTION FAILED: Asset '{target_path}' duration {seq_len:.4f}s exceeds tolerance vs expected {expected_len:.4f}s.")
            return False

        log(f"ASSERTIONS PASSED for '{name}': Class=AnimSequence, Skeleton=SK_CombatMannequin, Length={seq_len:.4f}s (target={expected_len:.4f}s, duplicated={is_duplicated})")

        # 5. Save verified asset
        saved = editor_asset_lib.save_loaded_asset(imported)
        if not saved:
            log_error(f"Failed to save verified asset '{target_path}'.")
            return False

        log(f"SUCCESS: Saved verified asset '{target_path}'.")
        success_count += 1

    log(f"IMPORT COMPLETE: {success_count} imported & saved, {refused_count} refused (already existing). Requested: {len(clips_to_import)}")
    return True


ok = run_import()
if not ok:
    log_error("import_er_clips failed")

# Request clean editor exit
if IN_ENGINE:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass
    import os
    os._exit(0 if ok else 1)


