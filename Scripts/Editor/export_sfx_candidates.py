"""Export SFX candidate SoundWave assets to standard WAV files for the Owner Listen Pack (SFX-03).

Runs under ENGINE_LOCK. Uses unreal.AssetExportTask and unreal.SoundExporterWAV.
Output is placed in D:/FightVideo/SFX_audition/RawWavs (off-repo per C-1181).
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

CANDIDATES = [
    # Gap 1: Parry Success
    ("GAP01_OptionA_Parry_SharpeningFast", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Sharpening/Sword_Sharpening_Fast_Speed"),
    ("GAP01_OptionB_Parry_AttackShort1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_Short_1"),
    ("GAP01_OptionC_Parry_ShieldImpact4", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4"),
    # Gap 2: Boss Recoil
    ("GAP02_OptionA_Recoil_SevarogBlock", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_Block_01"),
    ("GAP02_OptionB_Recoil_SevarogPainHeavy", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_PainHeavy_01"),
    ("GAP02_OptionC_Recoil_SevarogFrustration", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_Frustration_01"),
    # Gap 3: Phase 2 Aura Ignite
    ("GAP03_OptionA_Ignite_VefectsShockwave04", "/Game/Vefects/Easy_Shockwaves_VFX/Audio/Waves/SFX_Vefects_Shockwave_04_1s"),
    ("GAP03_OptionB_Ignite_Explosion01", "/Game/StarterContent/Audio/Explosion01"),
    ("GAP03_OptionC_Ignite_VefectsShockwave01", "/Game/Vefects/Easy_Shockwaves_VFX/Audio/Waves/SFX_Vefects_Shockwave_01_1s"),
    # Gap 4: Player Backstep
    ("GAP04_OptionA_Backstep_Swoosh1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_1"),
    ("GAP04_OptionB_Backstep_Swoosh3", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_3"),
    ("GAP04_OptionC_Backstep_Unsheathe1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Unsheathe/Sword_Unsheathe_1"),
    # Gap 5: Boss Stance Break
    ("GAP05_OptionA_StanceBreak_Collapse01", "/Game/StarterContent/Audio/Collapse01"),
    ("GAP05_OptionB_StanceBreak_GuardianImpact", "/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ArrowSounds/A_Guardian_Impact01"),
    ("GAP05_OptionC_StanceBreak_SevarogDizzy", "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_ProfileDizzy_010"),
]

OUT_DIR = r"D:\FightVideo\SFX_audition\RawWavs"


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[ExportSFX] {msg}")
    print(f"[ExportSFX] {msg}")


def export_candidates():
    if not IN_ENGINE:
        log("ERROR: Must run inside Unreal Engine editor environment.")
        return False

    os.makedirs(OUT_DIR, exist_ok=True)
    exporter = unreal.SoundExporterWAV()

    success_count = 0
    for label, asset_path in CANDIDATES:
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

    log(f"Export completed: {success_count}/{len(CANDIDATES)} assets exported successfully.")
    return success_count == len(CANDIDATES)


if __name__ == "__main__":
    ok = export_candidates()
    sys.exit(0 if ok else 1)
