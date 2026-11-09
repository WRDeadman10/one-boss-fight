"""Build Parry SFX Addendum Audition Reel (C-1186).

Extracts and compiles short metallic parry clash/clang candidates (0.2-0.6s)
into D:/FightVideo/SFX_audition/Parry_Addendum_Reel.mp4 and .mp3.
"""
import os
import subprocess
import sys
from pathlib import Path

SFX_DIR = Path(r"D:/FightVideo/SFX_audition")
RAW_DIR = SFX_DIR / "RawWavs"
TEMP_DIR = SFX_DIR / "_temp_addendum"

FONT = "fontfile='C\\:/Windows/Fonts/arial.ttf'"

CANDIDATES = [
    {
        "stem": "GAP01_Addendum_Opt1_SwordAttackShort2",
        "title": "PARRY ADDENDUM - CANDIDATE 1",
        "subtitle": "Sword_Attack_Short_2 (Trimmed Transient)",
        "source": "RealisticSwordSoundEffects / Sword_Attack",
        "desc": "Fast biting metallic clash - 0.40s duration",
        "trim": (0.20, 0.40) # start, duration
    },
    {
        "stem": "GAP01_Addendum_Opt2_SwordImpact1",
        "title": "PARRY ADDENDUM - CANDIDATE 2",
        "subtitle": "SwordImpact1 (Sharp Blade Ping)",
        "source": "AdvancedARPGCombat / SwordImpacts",
        "desc": "Crisp high-frequency deflection ping - 0.35s duration",
        "trim": (0.00, 0.45)
    },
    {
        "stem": "GAP01_Addendum_Opt3_SwordImpact3",
        "title": "PARRY ADDENDUM - CANDIDATE 3",
        "subtitle": "SwordImpact3 (Heavy Iron Deflect)",
        "source": "AdvancedARPGCombat / SwordImpacts",
        "desc": "Resonant heavy iron blade clang - 0.40s duration",
        "trim": (0.00, 0.50)
    },
]

def build_addendum():
    if not RAW_DIR.exists():
        print(f"ERROR: Raw directory {RAW_DIR} missing.")
        return False

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    concat_list = TEMP_DIR / "concat_list.txt"
    segment_files = []

    for idx, c in enumerate(CANDIDATES):
        raw_wav = RAW_DIR / f"{c['stem']}.wav"
        if not raw_wav.exists():
            print(f"ERROR: Missing {raw_wav}")
            continue

        trimmed_wav = TEMP_DIR / f"trimmed_{c['stem']}.wav"
        start_t, dur_t = c["trim"]
        # Trim using ffmpeg with a quick 0.05s fade out at end
        trim_cmd = [
            "ffmpeg", "-y", "-ss", str(start_t), "-i", str(raw_wav),
            "-t", str(dur_t),
            "-af", f"afade=t=out:st={dur_t-0.05}:d=0.05",
            str(trimmed_wav)
        ]
        subprocess.run(trim_cmd, capture_output=True)

        card_dur = 3.5  # comfortable listening card duration
        seg_mp4 = TEMP_DIR / f"seg_{idx:02d}.mp4"

        filter_str = (
            f"drawtext={FONT}:text='ONE BOSS FIGHT - PARRY SFX ADDENDUM':fontcolor=0x888888:fontsize=32:x=(w-text_w)/2:y=120,"
            f"drawtext={FONT}:text='{c['title']}':fontcolor=0xE0A938:fontsize=52:x=(w-text_w)/2:y=240,"
            f"drawtext={FONT}:text='{c['subtitle']}':fontcolor=0xFFFFFF:fontsize=44:x=(w-text_w)/2:y=340,"
            f"drawtext={FONT}:text='Source - {c['source']}':fontcolor=0xAAAAAA:fontsize=28:x=(w-text_w)/2:y=440,"
            f"drawtext={FONT}:text='{c['desc']}':fontcolor=0x66AAFF:fontsize=28:x=(w-text_w)/2:y=500"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x121318:s=1920x1080:d={card_dur}:r=30",
            "-i", str(trimmed_wav),
            "-filter_complex",
            f"[0:v]{filter_str}[v];[1:a]adelay=300|300,apad=whole_dur={card_dur}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "192k",
            str(seg_mp4)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and seg_mp4.exists():
            segment_files.append(seg_mp4)
            print(f"Segment {idx+1}/{len(CANDIDATES)} rendered: {c['stem']}")
        else:
            print(f"Error rendering segment: {res.stderr[-300:] if res.stderr else 'unknown'}")

    if not segment_files:
        print("ERROR: No segments rendered.")
        return False

    with open(concat_list, "w", encoding="utf-8") as f:
        for s in segment_files:
            f.write(f"file '{s.name}'\n")

    out_mp4 = SFX_DIR / "Parry_Addendum_Reel.mp4"
    out_mp3 = SFX_DIR / "Parry_Addendum_Reel.mp3"

    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(out_mp4)
    ]
    subprocess.run(concat_cmd, capture_output=True)

    mp3_cmd = [
        "ffmpeg", "-y", "-i", str(out_mp4),
        "-vn", "-c:a", "libmp3lame", "-b:a", "192k",
        str(out_mp3)
    ]
    subprocess.run(mp3_cmd, capture_output=True)

    print(f"SUCCESS: Assembled Parry Addendum Reel:")
    print(f"  MP4: {out_mp4} ({out_mp4.stat().st_size:,} bytes)")
    print(f"  MP3: {out_mp3} ({out_mp3.stat().st_size:,} bytes)")
    return True

if __name__ == "__main__":
    ok = build_addendum()
    sys.exit(0 if ok else 1)
