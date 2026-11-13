"""Turn [FullFight] game-time frames and action markers into ffmpeg/ASS inputs.

This tool writes inputs and prints an ffmpeg command. It never runs ffmpeg.
"""

import argparse
import re
import subprocess
from pathlib import Path

import os
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-17: sibling atomic_io as a script or via -m
from atomic_io import atomic_write_text


FRAME = re.compile(r"\[FullFight\] FRAME (\d+) g=([0-9]+(?:\.[0-9]+)?)\b")
ACTION = re.compile(r"\[FullFight\] ACTION (\S+) t=([0-9]+(?:\.[0-9]+)?)\b")
COUNTER = re.compile(r"\[FullFight\] COUNTER t=([0-9]+(?:\.[0-9]+)?)\b")
BOSS_DEAD = re.compile(r"\[FullFight\] BOSS_DEAD at ([0-9]+(?:\.[0-9]+)?) s\b")
PARRY_ATTEMPT = re.compile(r"\[FullFight\] PARRY_ATTEMPT instance=(\d+) active=(True|False) position=([0-9]+(?:\.[0-9]+)?) opened=(True|False) parried_before=(\d+)\b")
PARRY_CONTACT = re.compile(r"\[FullFight\] PARRY_CONTACT instance=(\d+) t=([0-9]+(?:\.[0-9]+)?) parried_delta=(\d+) boss_montage=(\S+)")
PARRY_RECOIL = re.compile(r"\[FullFight\] PARRY_RECOIL instance=(\d+) t=([0-9]+(?:\.[0-9]+)?) montage=(\S+)")
PARRY_FRAME_READY = re.compile(r"\[FullFight\] PARRY_FRAME_READY label=(\S+) instance=(\d+) frame=(\d+) t=([0-9]+(?:\.[0-9]+)?) actual_offset=([0-9]+(?:\.[0-9]+)?) path=(.+)$")
LABELS = {
    "light": "Light attack", "strong": "Strong attack", "backstep": "Backstep",
    "air_light": "Air light", "air_heavy": "Air heavy", "guard": "Guard",
}


def parse_log(source: str) -> tuple[list[tuple[int, float]], list[tuple[float, str]]]:
    frames = []
    events = []
    parry_attempts: dict[int, bool] = {}
    parry_contacts: dict[int, float] = {}
    parry_recoils: set[int] = set()
    parry_frame_labels: set[str] = set()
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
        elif "[FullFight] PARRY_ATTEMPT " in line:
            match = PARRY_ATTEMPT.search(line)
            if not match:
                raise ValueError(f"malformed [FullFight] PARRY_ATTEMPT marker: {line}")
            instance, _, _, opened, _ = match.groups()
            instance = int(instance)
            if instance in parry_attempts:
                raise ValueError(f"duplicate parry attempt for attack instance {instance}")
            parry_attempts[instance] = opened == "True"
        elif "[FullFight] PARRY_CONTACT " in line:
            match = PARRY_CONTACT.search(line)
            if not match:
                raise ValueError(f"malformed [FullFight] PARRY_CONTACT marker: {line}")
            instance, event_time, delta, _montage = match.groups()
            instance, event_time, delta = int(instance), float(event_time), int(delta)
            if parry_attempts.get(instance) is not True:
                raise ValueError(f"parry contact for instance {instance} has no opened attempt")
            if delta != 1:
                raise ValueError(f"parry contact for instance {instance} must have exactly one parried-count increment")
            if instance in parry_contacts:
                raise ValueError(f"duplicate parry contact for attack instance {instance}")
            parry_contacts[instance] = event_time
            events.append((event_time, "Successful parry"))
        elif "[FullFight] PARRY_RECOIL " in line:
            match = PARRY_RECOIL.search(line)
            if not match:
                raise ValueError(f"malformed [FullFight] PARRY_RECOIL marker: {line}")
            instance, event_time, montage = int(match[1]), float(match[2]), match[3]
            if instance not in parry_contacts:
                raise ValueError(f"parry recoil for instance {instance} has no preceding contact")
            if "ParryRecoil" not in montage:
                raise ValueError(f"parry recoil marker names unexpected montage: {montage}")
            if instance in parry_recoils:
                raise ValueError(f"duplicate parry recoil marker for attack instance {instance}")
            parry_recoils.add(instance)
            events.append((event_time, "Boss parry recoil"))
        elif "[FullFight] PARRY_FRAME_READY " in line:
            match = PARRY_FRAME_READY.search(line)
            if not match:
                raise ValueError(f"malformed [FullFight] PARRY_FRAME_READY marker: {line}")
            label, instance, frame, frame_time, offset, path = match.groups()
            instance, frame, frame_time, offset = int(instance), int(frame), float(frame_time), float(offset)
            if label in parry_frame_labels:
                raise ValueError(f"duplicate parry frame label: {label}")
            parry_frame_labels.add(label)
            if instance not in parry_contacts:
                raise ValueError(f"parry frame {label} has no preceding contact")
            if frame not in {item[0] for item in frames}:
                raise ValueError(f"parry frame {label} references missing FRAME {frame}")
            if offset < 0 or abs((frame_time - parry_contacts[instance]) - offset) > 0.02:
                raise ValueError(f"parry frame {label} has inconsistent contact offset")
            if not path.strip():
                raise ValueError(f"parry frame {label} has no image path")
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


def _platform_newlines(text: str) -> str:
    """BP-17: Path.write_text(text) without newline= translates "\n" to os.linesep; atomic_write_text writes bytes as
    given. Translating first keeps the output byte-identical to the former text-mode writes."""
    return text.replace("\n", os.linesep)


def _write_platform_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    atomic_write_text(path, _platform_newlines(text), encoding=encoding)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--frames", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--trim-leading-frames", type=int, default=0,
                        help="measured all-black lead-in PNG count; shifts subtitle times by the same game-time offset")
    args = parser.parse_args()
    if not args.log.is_file():  # BP-11: a missing input is a named usage error (exit 2), not a traceback
        parser.error(f"input file not found: {args.log}")
    frames, events = parse_log(args.log.read_text(encoding="utf-8", errors="replace"))
    frames, events = trim_leading_frames(frames, events, args.trim_leading_frames)
    concat = make_concat(frames, args.frames)
    duration = frames[-1][1] - frames[0][1] + (frames[-1][1] - frames[-2][1] if len(frames) > 1 else 1.0 / 15.0)
    args.out.mkdir(parents=True, exist_ok=True)
    concat_path = args.out / "frames.ffconcat"
    ass_path = args.out / "actions.ass"
    video_path = args.out / "fight_review.mp4"
    atomic_write_text(concat_path, _platform_newlines(concat))  # BP-17: atomic; same bytes as text-mode write_text
    _write_platform_text(ass_path, make_ass(events, duration), encoding="utf-8")
    # Run in the output folder so the ASS filter never has to parse a Windows drive colon or a spaced path.
    command = ["ffmpeg", "-y", "-safe", "0", "-f", "concat", "-i", concat_path.name,
               "-vf", f"ass={ass_path.name}", "-fps_mode", "vfr", "-c:v", "libx264", "-pix_fmt", "yuv420p", video_path.name]
    rendered_command = subprocess.list2cmdline(command)
    atomic_write_text(args.out / "ffmpeg_command.txt", _platform_newlines(f"Run from: {args.out.resolve()}\n{rendered_command}\n"))
    print(f"Run from: {args.out.resolve()}")
    print(rendered_command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
