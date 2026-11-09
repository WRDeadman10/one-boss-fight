"""Export SFX Batch 3 SoundWave assets to standard WAV files for Owner Audition Reel (C-1204).

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
    # SFX-11: Boss A1 Horizontal Slash
    ("SFX11_OptionA_A1_Attack1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_1"),
    ("SFX11_OptionB_A1_Swoosh1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_1"),
    ("SFX11_OptionC_A1_SwordSwing01", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/A_Sword_Swing01"),

    # SFX-12: Boss A2 Overhead Cleave
    ("SFX12_OptionA_A2_Attack3", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_3"),
    ("SFX12_OptionB_A2_AxeSwing01", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Weapons/Axe/A_Axe_Swing01"),
    ("SFX12_OptionC_A2_Attack5", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_5"),

    # SFX-13: Boss A3 Ground Stomp
    ("SFX13_OptionA_A3_Shockwave01", "/Game/Vefects/Easy_Shockwaves_VFX/Audio/Waves/SFX_Vefects_Shockwave_01_1s"),
    ("SFX13_OptionB_A3_Explosion01", "/Game/StarterContent/Audio/Explosion01"),
    ("SFX13_OptionC_A3_GuardianImpact01", "/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ArrowSounds/A_Guardian_Impact01"),

    # SFX-14: Boss Mid01 Forward Thrust
    ("SFX14_OptionA_Mid01_AttackShort1", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_Short_1"),
    ("SFX14_OptionB_Mid01_Swoosh4", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_4"),
    ("SFX14_OptionC_Mid01_Attack7", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_7"),

    # SFX-15: Boss Sprint Gap-Closer
    ("SFX15_OptionA_Sprint_Attack2", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_2"),
    ("SFX15_OptionB_Sprint_HammerSwing01", "/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Weapons/Hammer/A_Hammer_Swing01"),
    ("SFX15_OptionC_Sprint_Attack8", "/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_8"),
]

OUT_DIR = r"D:\FightVideo\SFX_audition\RawWavs"


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[ExportSFXBatch3] {msg}")
    print(f"[ExportSFXBatch3] {msg}")


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

        out_file = os.path.join(OUT_DIR, f"{label}.wav")
        task = unreal.AssetExportTask()
        task.object = asset
        task.exporter = exporter
        task.filename = out_file
        task.automated = True
        task.prompt = False
        task.replace_identical = True

        result = unreal.Exporter.run_asset_export_task(task)
        if result and os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            size_kb = os.path.getsize(out_file) / 1024.0
            log(f"Exported: {label} -> {out_file} ({size_kb:.1f} KB)")
            success_count += 1
        else:
            log(f"FAILED export for {label} at {asset_path}")

    log(f"Total exported: {success_count}/{len(CANDIDATES)}")
    return success_count == len(CANDIDATES)


if __name__ == "__main__":
    ok = export_candidates()
    if not ok:
        sys.exit(1)
