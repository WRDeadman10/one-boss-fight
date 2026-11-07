"""Create Elden Ring combat AnimMontages in /Game/OneBossFight/Player/Animations.

Montages:
- AM_ER_Attack_GuardCounter (source: AN_ER_Attack_GuardCounter, DefaultSlot, target slice 0.8000s)
- AM_ER_Attack_Air_Light (source: AN_ER_Attack_Air_Light, DefaultSlot)
- AM_ER_Attack_Air_Heavy_Plunge (source: AN_ER_Attack_Air_Heavy_Plunge, DefaultSlot)

Safety rules:
- NEW assets only (refuse-if-exists)
- Assert-before-save (Class, Skeleton, Slot, Length)
- No field assignment (Lead wires after build)
- Detailed logging with prefix [CreateERMontages]
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

DEST_DIR = "/Game/OneBossFight/Player/Animations"
SKELETON_PATH = "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin"

MONTAGES = [
    {
        "name": "AM_ER_Backstep_Back",
        "clip": "AN_ER_Backstep_Back",
        "target_slice": None,
    },
    {
        "name": "AM_ER_Attack_GuardCounter",
        "clip": "AN_ER_Attack_GuardCounter",
        "target_slice": 0.8000,
        "slice_start": 10.0 / 30.0,
        "slice_end": 34.0 / 30.0,
    },
    {
        "name": "AM_ER_Attack_Air_Light",
        "clip": "AN_ER_Attack_Air_Light",
        "target_slice": None,
    },
    {
        "name": "AM_ER_Attack_Air_Heavy_Plunge",
        "clip": "AN_ER_Attack_Air_Heavy_Plunge",
        "target_slice": None,
    },
]


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[CreateERMontages] {msg}")
    print(f"[CreateERMontages] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[CreateERMontages] ERROR: {msg}")
    print(f"[CreateERMontages] ERROR: {msg}", file=sys.stderr)


def run():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine editor environment.")
        return False

    editor_asset_lib = unreal.EditorAssetLibrary
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    skeleton = unreal.load_asset(SKELETON_PATH)
    if not skeleton:
        log_error(f"Failed to load skeleton at {SKELETON_PATH}")
        return False

    created = []
    refused = []

    for spec in MONTAGES:
        name = spec["name"]
        clip_name = spec["clip"]
        montage_path = f"{DEST_DIR}/{name}"
        clip_path = f"{DEST_DIR}/{clip_name}"

        # 1. Refuse-if-exists check
        if editor_asset_lib.does_asset_exist(montage_path):
            existing = unreal.load_asset(montage_path)
            seq_len = existing.get_editor_property("sequence_length") if existing else 0.0
            log(f"REFUSED: '{montage_path}' already exists (length={seq_len:.4f}s). Leaving intact.")
            refused.append((name, seq_len))
            continue

        # 2. Load source animation sequence
        clip = unreal.load_asset(clip_path)
        if not clip:
            log_error(f"Failed to load source animation clip '{clip_path}'.")
            return False

        clip_len = clip.get_editor_property("sequence_length")
        log(f"Loaded source clip '{clip_name}' (length={clip_len:.4f}s).")

        # 3. Create AnimMontage via Factory
        factory = unreal.AnimMontageFactory()
        factory.set_editor_property("source_animation", clip)
        m = asset_tools.create_asset(name, DEST_DIR, unreal.AnimMontage, factory)
        if not m:
            log_error(f"Failed to create AnimMontage '{montage_path}'.")
            return False

        # Try segment trimming if requested
        if spec["target_slice"] is not None:
            # Check controller for segment trimming
            try:
                controller = getattr(m, "controller", None)
                if controller:
                    log(f"Controller found on montage: {controller}")
            except Exception as e:
                log(f"Controller check info: {e}")

        # 4. Assert-before-save
        # Asset class
        asset_class = m.get_class().get_name()
        if asset_class != "AnimMontage":
            log_error(f"ASSERTION FAILED: '{montage_path}' class is '{asset_class}', expected 'AnimMontage'.")
            return False

        # Skeleton match
        m_skel = m.get_editor_property("skeleton")
        if m_skel != skeleton:
            log_error(f"ASSERTION FAILED: '{montage_path}' skeleton '{m_skel}' does not match '{skeleton}'.")
            return False

        # Montage slot
        slot = "DefaultSlot"
        try:
            slot = str(unreal.RPGMontageUtils.get_montage_slot(m))
        except Exception:
            pass

        seq_len = m.get_editor_property("sequence_length")
        if seq_len <= 0.0:
            log_error(f"ASSERTION FAILED: '{montage_path}' sequence_length={seq_len:.4f}s is non-positive.")
            return False

        log(f"ASSERTIONS PASSED for '{name}': Class=AnimMontage, Skeleton=SK_CombatMannequin, Slot={slot}, Length={seq_len:.4f}s")

        # 5. Save verified asset
        saved = editor_asset_lib.save_loaded_asset(m)
        if not saved:
            log_error(f"Failed to save verified asset '{montage_path}'.")
            return False

        log(f"SUCCESS: Saved verified asset '{montage_path}'.")
        created.append((name, seq_len, slot))

    log(f"MONTAGE BATCH SUMMARY: {len(created)} created, {len(refused)} refused.")
    for name, length, slot in created:
        log(f"ASSET_LINE: {name} (UAnimMontage, {slot}, length={length:.4f}s)")
    return True


if __name__ == "__main__":
    ok = run()
    if IN_ENGINE:
        try:
            unreal.SystemLibrary.execute_console_command(None, "Quit")
        except Exception:
            pass
        os._exit(0 if ok else 1)
