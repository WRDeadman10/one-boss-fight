"""Build the Owner SFX Batch 3 Audition Reel (C-1204) using ffmpeg.

Takes exported WAVs from D:/FightVideo/SFX_audition/RawWavs/ (off-repo per C-1181),
generates 1080p visual cards with labels, waveforms/timings, and concatenates
into D:/FightVideo/SFX_audition/Batch3_Audition_Reel.mp4 and Batch3_Audition_Reel.mp3 for Owner review.
"""

import os
import subprocess
import sys
from pathlib import Path

SFX_DIR = Path(r"D:/FightVideo/SFX_audition")
RAW_DIR = SFX_DIR / "RawWavs"
TEMP_DIR = SFX_DIR / "_temp_batch3"

FONT = "fontfile='C\\:/Windows/Fonts/arial.ttf'"

CARDS = [
    # SFX-11: A1 Horizontal Slash
    ("SFX11_OptionA_A1_Attack1", "SFX-11 - BOSS A1 HORIZONTAL SLASH", "Option A - Medium Blade Cleave (Preferred)", "Sword_Attack_1"),
    ("SFX11_OptionB_A1_Swoosh1", "SFX-11 - BOSS A1 HORIZONTAL SLASH", "Option B - Swift Velocity Swoosh", "Swoosh_1"),
    ("SFX11_OptionC_A1_SwordSwing01", "SFX-11 - BOSS A1 HORIZONTAL SLASH", "Option C - Pack Standard Sword Swing", "A_Sword_Swing01"),

    # SFX-12: A2 Overhead Cleave
    ("SFX12_OptionA_A2_Attack3", "SFX-12 - BOSS A2 OVERHEAD CLEAVE", "Option A - Heavy Vertical Cleave (Preferred)", "Sword_Attack_3"),
    ("SFX12_OptionB_A2_AxeSwing01", "SFX-12 - BOSS A2 OVERHEAD CLEAVE", "Option B - Weighted Downward Drag", "A_Axe_Swing01"),
    ("SFX12_OptionC_A2_Attack5", "SFX-12 - BOSS A2 OVERHEAD CLEAVE", "Option C - Deep Wind Drag", "Sword_Attack_5"),

    # SFX-13: A3 Ground Stomp
    ("SFX13_OptionA_A3_Shockwave01", "SFX-13 - BOSS A3 GROUND STOMP", "Option A - Shockwave Concussion (Preferred)", "SFX_Vefects_Shockwave_01_1s"),
    ("SFX13_OptionB_A3_Explosion01", "SFX-13 - BOSS A3 GROUND STOMP", "Option B - Detonation Rumble", "Explosion01"),
    ("SFX13_OptionC_A3_GuardianImpact01", "SFX-13 - BOSS A3 GROUND STOMP", "Option C - Stone Guardian Thud", "A_Guardian_Impact01"),

    # SFX-14: Mid01 Forward Thrust
    ("SFX14_OptionA_Mid01_AttackShort1", "SFX-14 - BOSS MID01 FORWARD THRUST", "Option A - Piercing Air Wake (Preferred)", "Sword_Attack_Short_1"),
    ("SFX14_OptionB_Mid01_Swoosh4", "SFX-14 - BOSS MID01 FORWARD THRUST", "Option B - Directional Air Cut", "Swoosh_4"),
    ("SFX14_OptionC_Mid01_Attack7", "SFX-14 - BOSS MID01 FORWARD THRUST", "Option C - Linear Slicing Thrust", "Sword_Attack_7"),

    # SFX-15: Sprint Gap-Closer
    ("SFX15_OptionA_Sprint_Attack2", "SFX-15 - BOSS SPRINT GAP-CLOSER", "Option A - Sweeping Momentum Whoosh (Preferred)", "Sword_Attack_2"),
    ("SFX15_OptionB_Sprint_HammerSwing01", "SFX-15 - BOSS SPRINT GAP-CLOSER", "Option B - Heavy Velocity Displacement", "A_Hammer_Swing01"),
    ("SFX15_OptionC_Sprint_Attack8", "SFX-15 - BOSS SPRINT GAP-CLOSER", "Option C - High-Speed Wide Edge", "Sword_Attack_8"),
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
    clip_paths = []

    print(f"Generating {len(CARDS)} visual audition clips...")

    for i, (stem, title, subtitle, asset_name) in enumerate(CARDS, start=1):
        audio_file = RAW_DIR / f"{stem}.wav"
        if not audio_file.exists():
            print(f"WARNING: Missing audio file {audio_file}")
            continue

        clip_out = TEMP_DIR / f"clip_{i:02d}.mp4"
        duration = max(get_duration(audio_file) + 0.5, 2.0)

        title_esc = title.replace("'", "").replace(":", "-")
        sub_esc = subtitle.replace("'", "").replace(":", "-")
        asset_esc = f"Asset- {asset_name}".replace("'", "")
        index_str = f"Candidate {i}/{len(CARDS)}"

        drawtext_filters = (
            f"drawtext={FONT}:text='ONE BOSS FIGHT - QUEUE SFX BATCH 3':x=(w-text_w)/2:y=180:fontsize=48:fontcolor=0xE07A5F,"
            f"drawtext={FONT}:text='{title_esc}':x=(w-text_w)/2:y=340:fontsize=56:fontcolor=white:box=1:boxcolor=0x1E1E24@0.8:boxborderw=20,"
            f"drawtext={FONT}:text='{sub_esc}':x=(w-text_w)/2:y=480:fontsize=42:fontcolor=0x81B29A,"
            f"drawtext={FONT}:text='{asset_esc}':x=(w-text_w)/2:y=620:fontsize=36:fontcolor=0xA0A0A0,"
            f"drawtext={FONT}:text='{index_str}':x=(w-text_w)/2:y=760:fontsize=32:fontcolor=0x606060"
        )

        filter_complex = f"[0:a]showwaves=s=1200x200:mode=line:colors=0x81B29A[wave];[1:v][wave]overlay=(W-w)/2:840[vbg];[vbg]{drawtext_filters}[vout]"

        cmd = [
            "ffmpeg", "-y",
            "-i", str(audio_file),
            "-f", "lavfi", "-i", f"color=c=0x0D0D11:s=1920x1080:d={duration}:r=30",
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "0:a",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", str(duration),
            "-c:a", "aac", "-b:a", "192k",
            str(clip_out)
        ]

        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            print(f"ERROR rendering clip {i}: {p.stderr}")
            return False

        clip_paths.append(clip_out)
        print(f"Rendered clip {i:02d}: {title} ({duration:.2f}s)")

    with open(concat_list, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.name}'\n")

    final_mp4 = SFX_DIR / "Batch3_Audition_Reel.mp4"
    final_mp3 = SFX_DIR / "Batch3_Audition_Reel.mp3"

    print("Concatenating into final MP4...")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(final_mp4)
    ]
    p_concat = subprocess.run(concat_cmd, capture_output=True, text=True)
    if p_concat.returncode != 0:
        print(f"ERROR concatenating: {p_concat.stderr}")
        return False

    print("Exporting MP3 audio reel...")
    mp3_cmd = [
        "ffmpeg", "-y",
        "-i", str(final_mp4),
        "-vn", "-c:a", "libmp3lame", "-b:a", "192k",
        str(final_mp3)
    ]
    p_mp3 = subprocess.run(mp3_cmd, capture_output=True, text=True)
    if p_mp3.returncode != 0:
        print(f"ERROR creating MP3: {p_mp3.stderr}")
        return False

    mp4_mb = final_mp4.stat().st_size / (1024 * 1024)
    mp3_kb = final_mp3.stat().st_size / 1024
    print("SUCCESS: Batch 3 SFX Audition Reel generated successfully!")
    print(f"  MP4: {final_mp4} ({mp4_mb:.2f} MB)")
    print(f"  MP3: {final_mp3} ({mp3_kb:.1f} KB)")
    return True


if __name__ == "__main__":
    ok = build_reel()
    if not ok:
        sys.exit(1)
