"""Export Parry Addendum candidate SoundWaves to off-repo WAVs (C-1186).

Extracts 3 short metallic clash/impact candidates:
1. Sword_Attack_Short_2 (RealisticSwordSoundEffects) - 0.35s transient
2. SwordImpact1 (AdvancedARPGCombat) - crisp metallic blade clang
3. SwordImpact3 (AdvancedARPGCombat) - heavy metal parry ring
"""
import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

ADDENDUM_CANDIDATES = [
    ("GAP01_Addendum_Opt1_SwordAttackShort2", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_Short_2"),
    ("GAP01_Addendum_Opt2_SwordImpact1", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1"),
    ("GAP01_Addendum_Opt3_SwordImpact3", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact3"),
]

OUT_DIR = r"D:\FightVideo\SFX_audition\RawWavs"

def log(msg):
    if IN_ENGINE:
        unreal.log(f"[ExportParryAddendum] {msg}")
    print(f"[ExportParryAddendum] {msg}")

def export_addendum():
    if not IN_ENGINE:
        log("ERROR: Must run inside Unreal Engine editor environment.")
        return False

    os.makedirs(OUT_DIR, exist_ok=True)
    exporter = unreal.SoundExporterWAV()

    success_count = 0
    for label, asset_path in ADDENDUM_CANDIDATES:
        asset = unreal.load_asset(asset_path)
        if not asset:
            log(f"WARNING: Asset not found: {asset_path}")
            continue

        wav_path = os.path.join(OUT_DIR, f"{label}.wav")
        task = unreal.AssetExportTask()
        task.set_editor_property("object", asset)
        task.set_editor_property("filename", wav_path)
        task.set_editor_property("exporter", exporter)
        task.set_editor_property("automated", True)
        task.set_editor_property("prompt", False)
        task.set_editor_property("replace_identical", True)

        ok = unreal.Exporter.run_asset_export_task(task)
        if ok and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            log(f"Exported {label}: {wav_path} ({os.path.getsize(wav_path):,} bytes)")
            success_count += 1
        else:
            log(f"ERROR exporting {label} to {wav_path}")

    log(f"Export completed: {success_count}/{len(ADDENDUM_CANDIDATES)} assets exported successfully.")
    return success_count == len(ADDENDUM_CANDIDATES)

if __name__ == "__main__":
    ok = export_addendum()
    sys.exit(0 if ok else 1)
