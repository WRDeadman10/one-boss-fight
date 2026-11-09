"""Build the Owner SFX Audition Reel (SFX-03) using ffmpeg.

Takes exported WAVs from D:/FightVideo/SFX_audition/RawWavs/ (off-repo per C-1181),
generates clean 1080p visual cards with labels, waveforms/timings, and concatenates
into D:/FightVideo/SFX_audition/SFX_Audition_Reel.mp4 and SFX_Audition_Reel.mp3 for Owner review.
"""

import os
import subprocess
import sys
from pathlib import Path

SFX_DIR = Path(r"D:/FightVideo/SFX_audition")
RAW_DIR = SFX_DIR / "RawWavs"
TEMP_DIR = SFX_DIR / "_temp_reel"

FONT = "fontfile='C\\:/Windows/Fonts/arial.ttf'"

CARDS = [
    ("GAP01_OptionA_Parry_SharpeningFast", "GAP 1 - PLAYER PARRY SUCCESS", "Option A - Fast Deflect Clash (Preferred)", "Sword_Sharpening_Fast_Speed"),
    ("GAP01_OptionB_Parry_AttackShort1", "GAP 1 - PLAYER PARRY SUCCESS", "Option B - Short Blade Ring", "Sword_Attack_Short_1"),
    ("GAP01_OptionC_Parry_ShieldImpact4", "GAP 1 - PLAYER PARRY SUCCESS", "Option C - Buckler Clatter", "ShieldImpact4"),

    ("GAP02_OptionA_Recoil_SevarogBlock", "GAP 2 - BOSS PARRY RECOIL", "Option A - Wraith Effort Block (Preferred)", "Sevarog_Effort_Block_01"),
    ("GAP02_OptionB_Recoil_SevarogPainHeavy", "GAP 2 - BOSS PARRY RECOIL", "Option B - Heavy Pain Stumble", "Sevarog_Effort_PainHeavy_01"),
    ("GAP02_OptionC_Recoil_SevarogFrustration", "GAP 2 - BOSS PARRY RECOIL", "Option C - Frustrated Growl", "Sevarog_Effort_Frustration_01"),

    ("GAP03_OptionA_Ignite_VefectsShockwave04", "GAP 3 - PHASE 2 AURA IGNITE", "Option A - Dark Energy Burst (Preferred)", "SFX_Vefects_Shockwave_04_1s"),
    ("GAP03_OptionB_Ignite_Explosion01", "GAP 3 - PHASE 2 AURA IGNITE", "Option B - Infernal Concussion", "Explosion01"),
    ("GAP03_OptionC_Ignite_VefectsShockwave01", "GAP 3 - PHASE 2 AURA IGNITE", "Option C - Shockwave Snap", "SFX_Vefects_Shockwave_01_1s"),

    ("GAP04_OptionA_Backstep_Swoosh1", "GAP 4 - PLAYER BACKSTEP WHOOSH", "Option A - Swift Evasion Whoosh (Preferred)", "Swoosh_1"),
    ("GAP04_OptionB_Backstep_Swoosh3", "GAP 4 - PLAYER BACKSTEP WHOOSH", "Option B - Whip Whoosh", "Swoosh_3"),
    ("GAP04_OptionC_Backstep_Unsheathe1", "GAP 4 - PLAYER BACKSTEP WHOOSH", "Option C - Scabbard Slip", "Sword_Unsheathe_1"),

    ("GAP05_OptionA_StanceBreak_Collapse01", "GAP 5 - BOSS STANCE BREAK", "Option A - Rubble and Poise Collapse (Preferred)", "Collapse01"),
    ("GAP05_OptionB_StanceBreak_GuardianImpact", "GAP 5 - BOSS STANCE BREAK", "Option B - Iron Guardian Clatter", "A_Guardian_Impact01"),
    ("GAP05_OptionC_StanceBreak_SevarogDizzy", "GAP 5 - BOSS STANCE BREAK", "Option C - Disorientation Drone", "Sevarog_ProfileDizzy_010"),
]


def get_duration(audio_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except Exception:
        return 2.0


def build_reel():
    if not RAW_DIR.exists():
        print(f"ERROR: Raw WAV directory missing: {RAW_DIR}")
        return False

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    concat_list = TEMP_DIR / "concat_list.txt"
    segment_files = []

    for idx, (stem, title, subtitle, asset_name) in enumerate(CARDS):
        wav_file = RAW_DIR / f"{stem}.wav"
        if not wav_file.exists():
            print(f"WARNING: WAV missing for {stem}, skipping.")
            continue

        dur = get_duration(wav_file)
        card_dur = max(2.5, dur + 1.0)
        seg_mp4 = TEMP_DIR / f"seg_{idx:02d}_{stem}.mp4"

        # Generate titled segment video with no unescaped colons
        filter_str = (
            f"drawtext={FONT}:text='ONE BOSS FIGHT - AUDIO AUDITION REEL':fontcolor=0x888888:fontsize=32:x=(w-text_w)/2:y=120,"
            f"drawtext={FONT}:text='{title}':fontcolor=0xE0A938:fontsize=52:x=(w-text_w)/2:y=240,"
            f"drawtext={FONT}:text='{subtitle}':fontcolor=0xFFFFFF:fontsize=44:x=(w-text_w)/2:y=340,"
            f"drawtext={FONT}:text='Asset - {asset_name}':fontcolor=0xAAAAAA:fontsize=28:x=(w-text_w)/2:y=440,"
            f"drawtext={FONT}:text='Audio Duration - {dur:.2f}s':fontcolor=0x66AAFF:fontsize=28:x=(w-text_w)/2:y=500"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x121318:s=1920x1080:d={card_dur}:r=30",
            "-i", str(wav_file),
            "-filter_complex",
            f"[0:v]{filter_str}[v];[1:a]apad=whole_dur={card_dur}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k",
            str(seg_mp4)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and seg_mp4.exists():
            segment_files.append(seg_mp4)
            print(f"Rendered segment {idx+1}/{len(CARDS)}: {stem} ({card_dur:.2f}s)")
        else:
            print(f"Error rendering {stem}: {res.stderr[-300:] if res.stderr else 'no stderr'}")

    if not segment_files:
        print("ERROR: No segments were successfully rendered.")
        return False

    with open(concat_list, "w") as f:
        for seg in segment_files:
            f.write(f"file '{seg.name}'\n")

    out_mp4 = SFX_DIR / "SFX_Audition_Reel.mp4"
    out_mp3 = SFX_DIR / "SFX_Audition_Reel.mp3"

    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy", str(out_mp4)
    ]
    subprocess.run(concat_cmd, check=True)

    mp3_cmd = [
        "ffmpeg", "-y", "-i", str(out_mp4),
        "-vn", "-c:a", "libmp3lame", "-q:a", "2",
        str(out_mp3)
    ]
    subprocess.run(mp3_cmd, check=True)

    print(f"SUCCESS: Audition reel created at:")
    print(f"  MP4: {out_mp4} ({out_mp4.stat().st_size:,} bytes)")
    print(f"  MP3: {out_mp3} ({out_mp3.stat().st_size:,} bytes)")
    return True


if __name__ == "__main__":
    ok = build_reel()
    sys.exit(0 if ok else 1)
