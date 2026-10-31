#!/usr/bin/env python3
"""contact_sheet.py - Generates indexed contact sheets from reference combat footage.

Extracts a time window from combat video, burns original video timestamps and
canonical frame indices into every frame using FFmpeg's drawtext filter, samples
every Nth frame, scales to tile width, and tiles them into a single contact sheet PNG.

FFmpeg Drawtext & Scaling Rules:
1. Windows Font Escaping: Escapes drive colon (e.g. 'C\\:/Windows/Fonts/arial.ttf')
   to avoid FFmpeg "Fontconfig error: Cannot load default config file".
2. Filtergraph Ordering: Places drawtext BEFORE decimation (select) and scaling
   so that frame counter 'n' and PTS evaluate against true source frames.
3. Scale-Relative Font Sizing: Because drawtext runs on the 3840-px source before
   downscaling, fontsize is dynamically scaled:
     fontsize = round(label_px * source_width / scale_width)
   This ensures that the burned label is rendered at ~label_px height on output tiles
   (e.g. fontsize=80 for 960px tiles, fontsize=160 for 480px tiles when label_px=20).
4. HUD-Avoiding Placement: Labels are positioned at the bottom-left of each frame
   (x=margin, y=h-th-margin) with a black box and yellow text to avoid player HUD.
5. Timestamp & Frame Offset: Seeking with '-ss <start>' before '-i' resets stream
   PTS to 0. Passes start time to '%{pts:hms:<start>}' and offsets frame numbering
   formula: frame = round((start_sec - 105.0) * fps) + 1 + n.
6. Repo Cleanliness: Strictly enforces that output images are saved OUTSIDE the
   git repository (e.g. /tmp, C:/temp, or outside repo root).

Usage:
  python -I contact_sheet.py --start 112.0 --duration 2.0 --out C:/temp/sheet_112_114.png
  python -I contact_sheet.py --start 110.95 --duration 0.5 --step 1 --width 480 --out C:/temp/test.png
  python -I contact_sheet.py --start 112.0 --duration 2.0 --out C:/temp/sheet.png --dry-run
"""

import argparse
import math
import os
import subprocess
import sys

DEFAULT_VIDEO = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "..",
        "Documentation", "Boss", "Morgott_82_Point_Combat_Reference",
        "Elden Ring - Morgott, The Omen King Boss Fight.webm"
    )
)
DEFAULT_FPS = 59.9401
DEFAULT_COMBAT_ZERO = 105.0
DEFAULT_STEP = 3
DEFAULT_WIDTH = 960
DEFAULT_COLUMNS = 5
DEFAULT_LABEL_PX = 20
DEFAULT_SOURCE_WIDTH = 3840
DEFAULT_FONTFILE = "C:/Windows/Fonts/arial.ttf"


def escape_filter_path(path: str) -> str:
    """Escapes Windows path colons and backslashes for FFmpeg filtergraph strings."""
    norm = path.replace("\\", "/")
    return norm.replace(":", r"\:")


def compute_tile_layout(total_frames: int, columns: int) -> str:
    """Computes grid layout string 'CxR' for FFmpeg tile filter."""
    if total_frames <= 0:
        total_frames = 1
    rows = math.ceil(total_frames / columns)
    return f"{columns}x{rows}"


def build_ffmpeg_command(
    video_path: str,
    start_sec: float,
    duration_sec: float,
    out_path: str,
    step: int = DEFAULT_STEP,
    scale_width: int = DEFAULT_WIDTH,
    columns: int = DEFAULT_COLUMNS,
    fps: float = DEFAULT_FPS,
    combat_zero: float = DEFAULT_COMBAT_ZERO,
    fontfile: str = DEFAULT_FONTFILE,
    label_px: int = DEFAULT_LABEL_PX,
    source_width: int = DEFAULT_SOURCE_WIDTH,
    ffmpeg_bin: str = "ffmpeg"
) -> list:
    """Constructs the ffmpeg argument list for contact sheet generation."""
    # Compute starting canonical frame index per D1 formula:
    # frame = round((t_orig - 105.0) * fps) + 1
    t_start_combat = start_sec - combat_zero
    start_frame = round(t_start_combat * fps) + 1

    # Approximate total decoded frames and sampled tiles
    total_decoded = round(duration_sec * fps)
    total_sampled = math.ceil(total_decoded / step)
    layout = compute_tile_layout(total_sampled, columns)

    # Escape fontfile path for Windows filtergraph
    escaped_font = escape_filter_path(fontfile)

    # Relative font size and margins scaled to source resolution
    # Formula: fontsize = round(label_px * source_width / scale_width)
    fontsize = round(label_px * source_width / scale_width)
    margin_x = round(20 * source_width / scale_width)
    margin_y = round(20 * source_width / scale_width)
    box_border = max(2, round(4 * source_width / scale_width))

    # Construct filtergraph:
    # 1. drawtext: bottom-left placement (x=margin_x, y=h-th-margin_y) avoiding HUD
    # 2. select: decimate by step (every Nth frame)
    # 3. scale: tile frame width with preserved aspect ratio
    # 4. tile: assemble into contact sheet grid
    drawtext_str = (
        f"drawtext=fontfile='{escaped_font}':"
        f"text='t=%{{pts\\:hms\\:{start_sec:.3f}}} | morgott_c0_%{{eif\\:{start_frame}+n\\:d\\:5}}.png (f=%{{eif\\:{start_frame}+n\\:d}})':"
        f"fontsize={fontsize}:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw={box_border}:"
        f"x={margin_x}:y=h-th-{margin_y}"
    )
    select_str = f"select='not(mod(n\\,{step}))'"
    scale_str = f"scale={scale_width}:-1"
    tile_str = f"tile=layout={layout}"

    filtergraph = f"{drawtext_str},{select_str},{scale_str},{tile_str}"

    cmd = [
        ffmpeg_bin,
        "-ss", f"{start_sec:.3f}",
        "-t", f"{duration_sec:.3f}",
        "-i", video_path,
        "-vf", filtergraph,
        "-frames:v", "1",
        "-update", "1",
        "-y",
        out_path
    ]
    return cmd


def validate_out_path(out_path: str, repo_root: str):
    """Enforces that output media files are never written inside the repository."""
    abs_out = os.path.abspath(out_path)
    abs_repo = os.path.abspath(repo_root)
    try:
        common = os.path.commonpath([abs_out, abs_repo])
        if common == abs_repo:
            raise ValueError(
                f"SAFETY VIOLATION: Output path '{out_path}' is inside repository '{repo_root}'. "
                f"Contact sheets must strictly be written outside the repository (e.g. C:/temp/ or /tmp)."
            )
    except ValueError as e:
        if "SAFETY VIOLATION" in str(e):
            raise
        pass


def run_contact_sheet(cmd: list, out_path: str, dry_run: bool = False) -> int:
    """Executes or prints the FFmpeg command."""
    if dry_run:
        print("[DRY-RUN] FFmpeg command:")
        print(" ".join(f'"{arg}"' if " " in arg or "=" in arg else arg for arg in cmd))
        return 0

    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    print(f"Running contact sheet generation -> {out_path}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FFmpeg failed with exit code {res.returncode}:")
        print(res.stderr[-2000:] if res.stderr else "No stderr output.")
        return res.returncode

    if os.path.exists(out_path):
        size_bytes = os.path.getsize(out_path)
        print(f"Successfully generated contact sheet: {out_path} ({size_bytes:,} bytes)")
    else:
        print(f"Error: FFmpeg succeeded but output file '{out_path}' was not created.")
        return 1

    return 0


def main():
    repo_root = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
    )

    parser = argparse.ArgumentParser(
        description="Generates indexed contact sheets from reference combat footage."
    )
    parser.add_argument(
        "--video", default=DEFAULT_VIDEO,
        help="Path to source video file."
    )
    parser.add_argument(
        "--start", type=float, required=True,
        help="Start time in original video seconds."
    )
    parser.add_argument(
        "--duration", type=float, default=None,
        help="Window duration in seconds."
    )
    parser.add_argument(
        "--end", type=float, default=None,
        help="End time in original video seconds (alternative to --duration)."
    )
    parser.add_argument(
        "--out", default=None,
        help="Output PNG path (must be outside repository)."
    )
    parser.add_argument(
        "--step", type=int, default=DEFAULT_STEP,
        help="Sample every Nth frame (default: 3)."
    )
    parser.add_argument(
        "--width", type=int, default=DEFAULT_WIDTH,
        help="Tile frame width in pixels (default: 960)."
    )
    parser.add_argument(
        "--columns", type=int, default=DEFAULT_COLUMNS,
        help="Number of columns in contact sheet grid (default: 5)."
    )
    parser.add_argument(
        "--label-px", type=int, default=DEFAULT_LABEL_PX,
        help="Desired label text height in pixels on output tile (default: 20)."
    )
    parser.add_argument(
        "--source-width", type=int, default=DEFAULT_SOURCE_WIDTH,
        help="Source video width in pixels for font scaling calculation (default: 3840)."
    )
    parser.add_argument(
        "--fontfile", default=DEFAULT_FONTFILE,
        help="Path to TTF font file for drawtext."
    )
    parser.add_argument(
        "--ffmpeg", default="ffmpeg",
        help="Path to ffmpeg executable (default: 'ffmpeg')."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print FFmpeg command without executing."
    )

    args = parser.parse_args()

    if args.duration is not None:
        duration = args.duration
    elif args.end is not None:
        duration = args.end - args.start
        if duration <= 0:
            print("Error: --end must be greater than --start.")
            sys.exit(1)
    else:
        print("Error: Either --duration or --end must be provided.")
        sys.exit(1)

    if not args.out:
        if args.dry_run:
            args.out = os.path.normpath("C:/temp/contact_sheet_dryrun.png")
        else:
            print("Error: --out path is required when not in --dry-run mode.")
            sys.exit(1)

    try:
        validate_out_path(args.out, repo_root)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    cmd = build_ffmpeg_command(
        video_path=args.video,
        start_sec=args.start,
        duration_sec=duration,
        out_path=args.out,
        step=args.step,
        scale_width=args.width,
        columns=args.columns,
        fontfile=args.fontfile,
        label_px=args.label_px,
        source_width=args.source_width,
        ffmpeg_bin=args.ffmpeg
    )

    rc = run_contact_sheet(cmd, args.out, dry_run=args.dry_run)
    sys.exit(rc)


if __name__ == "__main__":
    main()
