"""Turn [FullFight] game-time frames and action markers into ffmpeg/ASS inputs.

This tool writes inputs and prints an ffmpeg command. It never runs ffmpeg.
"""

import argparse
import re
import subprocess
from pathlib import Path


FRAME = re.compile(r"\[FullFight\] FRAME (\d+) g=([0-9]+(?:\.[0-9]+)?)\b")
ACTION = re.compile(r"\[FullFight\] ACTION (\S+) t=([0-9]+(?:\.[0-9]+)?)\b")
COUNTER = re.compile(r"\[FullFight\] COUNTER t=([0-9]+(?:\.[0-9]+)?)\b")
BOSS_DEAD = re.compile(r"\[FullFight\] BOSS_DEAD at ([0-9]+(?:\.[0-9]+)?) s\b")
LABELS = {
    "light": "Light attack", "strong": "Strong attack", "backstep": "Backstep",
    "air_light": "Air light", "air_heavy": "Air heavy", "guard": "Guard",
}


def parse_log(source: str) -> tuple[list[tuple[int, float]], list[tuple[float, str]]]:
    frames = []
    events = []
    for line in source.splitlines():
        for marker, pattern in (("FRAME ", FRAME), ("ACTION ", ACTION), ("COUNTER ", COUNTER), ("BOSS_DEAD ", BOSS_DEAD)):
            if "[FullFight] " + marker in line and not pattern.search(line):
                raise ValueError(f"malformed [FullFight] {marker.strip()} marker: {line}")
        if match := FRAME.search(line):
            index, game_time = int(match[1]), float(match[2])
            if frames and (index != frames[-1][0] + 1 or game_time <= frames[-1][1]):
                raise ValueError("FRAME indices must be consecutive and game time strictly increasing")
            if not frames and index != 0:
                raise ValueError("first FRAME must be 0")
            frames.append((index, game_time))
        elif match := ACTION.search(line):
            events.append((float(match[2]), LABELS.get(match[1], match[1])))
        elif match := COUNTER.search(line):
            events.append((float(match[1]), "Guard counter"))
        elif match := BOSS_DEAD.search(line):
            events.append((float(match[1]), "Boss defeated"))
    if not frames:
        raise ValueError("no [FullFight] FRAME markers")
    if any(events[i][0] < events[i - 1][0] for i in range(1, len(events))):
        raise ValueError("ACTION/COUNTER/BOSS_DEAD times must be monotone")
    return frames, events


def _ffconcat_path(path: Path) -> str:
    # ffconcat uses backslash escapes even on Windows; quote paths with spaces/apostrophes.
    return path.resolve().as_posix().replace("'", "'\\''")


def trim_leading_frames(frames: list[tuple[int, float]], events: list[tuple[float, str]], count: int) -> tuple[list[tuple[int, float]], list[tuple[float, str]]]:
    """Drop a measured black capture lead-in and keep ASS time aligned to the first kept frame."""
    if count < 0 or count >= len(frames):
        raise ValueError("trim must retain at least one frame")
    offset = frames[count][1] - frames[0][1]
    return frames[count:], [(time - offset, label) for time, label in events if time >= offset]


def make_concat(frames: list[tuple[int, float]], frame_dir: Path) -> str:
    if not frames:
        raise ValueError("no frames")
    gaps = [b[1] - a[1] for a, b in zip(frames, frames[1:])]
    tail = sorted(gaps)[len(gaps) // 2] if gaps else 1.0 / 15.0
    lines = ["ffconcat version 1.0"]
    for offset, (index, _) in enumerate(frames):
        path = frame_dir / f"f_{index:05d}.png"
        if not path.is_file():
            raise ValueError(f"missing frame: {path}")
        lines.append(f"file '{_ffconcat_path(path)}'")
        lines.append(f"duration {(gaps[offset] if offset < len(gaps) else tail):.6f}")
    # ffmpeg's concat demuxer needs the final file repeated to honor its duration.
    lines.append(f"file '{_ffconcat_path(frame_dir / f'f_{frames[-1][0]:05d}.png')}'")
    return "\n".join(lines) + "\n"


def _ass_time(seconds: float) -> str:
    centis = max(0, round(seconds * 100))
    return f"{centis // 360000}:{centis // 6000 % 60:02}:{centis // 100 % 60:02}.{centis % 100:02}"


def _ass_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def make_ass(events: list[tuple[float, str]], duration: float) -> str:
    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 960", "PlayResY: 540",
        "[V4+ Styles]", "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Default,Arial,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,30,30,40,1",
        "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    for index, (start, label) in enumerate(events):
        if start >= duration:
            continue
        next_start = events[index + 1][0] if index + 1 < len(events) else duration
        end = min(duration, max(start + 0.01, next_start))
        lines.append(f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Default,,0,0,0,,{_ass_text(label)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--trim-leading-frames", type=int, default=0,
                        help="measured all-black lead-in PNG count; shifts subtitle times by the same game-time offset")
    args = parser.parse_args()
    frames, events = parse_log(args.log.read_text(encoding="utf-8", errors="replace"))
    frames, events = trim_leading_frames(frames, events, args.trim_leading_frames)
    concat = make_concat(frames, args.frames)
    duration = frames[-1][1] - frames[0][1] + (frames[-1][1] - frames[-2][1] if len(frames) > 1 else 1.0 / 15.0)
    args.out.mkdir(parents=True, exist_ok=True)
    concat_path = args.out / "frames.ffconcat"
    ass_path = args.out / "actions.ass"
    video_path = args.out / "fight_review.mp4"
    concat_path.write_text(concat, encoding="utf-8")
    ass_path.write_text(make_ass(events, duration), encoding="utf-8")
    # Run in the output folder so the ASS filter never has to parse a Windows drive colon or a spaced path.
    command = ["ffmpeg", "-y", "-safe", "0", "-f", "concat", "-i", concat_path.name,
               "-vf", f"ass={ass_path.name}", "-fps_mode", "vfr", "-c:v", "libx264", "-pix_fmt", "yuv420p", video_path.name]
    rendered_command = subprocess.list2cmdline(command)
    (args.out / "ffmpeg_command.txt").write_text(f"Run from: {args.out.resolve()}\n{rendered_command}\n", encoding="utf-8")
    print(f"Run from: {args.out.resolve()}")
    print(rendered_command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
