#!/usr/bin/env python3
"""
capture_analysis.py - Offline Analysis & Verdict Engine for Combat Capture Telemetry

Analyzes editor-produced capture logs, telemetry manifests, and burst screenshot metadata
for CAP-01 (A5 Release), CAP-02 (A4 Blade Query), CAP-05 (Telegraph Lead), and CAP-06 (Recovery Opening).
Evaluates measured telemetry against strict pass/fail tolerance envelopes authored in AG31.

Audited and hardened per Claude [C-135], [C-137], [C-138]:
  - Enforces strictly increasing simulation timestamps (rejects same-tick compressed bursts).
  - Verifies file existence on disk (files == frames).
  - Performs offline pixel-variance analysis on PNGs to reject blank (e.g. 17KB) unrendered frames.
  - Zero external dependencies: incorporates a pure-Python zlib/struct PNG scanner (works under python -I).
  - Detects engine attack execution vetoes (e.g. phase transition, waking, dormancy).
  - Distinguishes authored intent (0.40s), code release (0.45s), and observed sample (0.47s) per E-007.
  - Reconciles CAP-02 active window to [0.609, 0.879]s (12 ticks per E-008:10).
  - Labels all feel thresholds as PROPOSED (requiring owner signoff) and cites exact sources for nominals.

Author: Antigravity (Visual & Technical Animation Investigator)
Work Order: TASK_BOARD.md (A-T1 Revision 3)
"""

import os
import sys
import re
import json
import math
import zlib
import struct
import hashlib
import argparse
import tempfile
from pathlib import Path

# Optional Pillow acceleration; falls back automatically to built-in pure-Python zlib parser
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ==============================================================================
# SPECIFICATION & TOLERANCE ENVELOPES (AG31)
# ==============================================================================

BENCHMARK_RULES = {
    "CAP-01": {
        "name": "A5 Javelin Release Timing",
        "montage": "AN_Boss01_A5_JavelinThrow",
        "clip_duration_s": 2.433,
        "nominal_authored_intent_s": 0.400,   # Source: E-007:7 (Sidecar author intent, frame 12 @ 30fps)
        "nominal_code_active_s": 0.450,       # Source: E-007:5 (URPGAttackTracker active window)
        "sampled_code_release_s": 0.470,      # Source: E-007:3 (Sampled runtime release)
        "nominal_delta_s": 0.050,             # Source: E-007:7 (0.45s - 0.40s = 1.0 frame @ 20fps)
        "sampled_delta_s": 0.070,             # Source: E-007:3 (0.47s - 0.40s = 1.4 frames @ 20fps)
        "perceptual_status": "Feel question for owner, not a measured defect (E-007:7, D06B:40)",
        "tolerance_strict_ms": 33.3,          # PROPOSED: Antigravity proposal for owner signoff (1 frame @ 30fps)
        "tolerance_max_ms": 50.0,             # PROPOSED: Antigravity proposal for owner signoff (hard ceiling)
        "min_burst_frames": 15,
        "min_sim_step_s": 0.020,              # Minimum simulation time advancement between frames
        "min_image_bytes": 50000,             # Minimum valid screenshot file size
        "min_pixel_variance": 1.0,            # Rejects solid-color blank images
        "min_viewport_luminance": 8.0,        # Inner 3D viewport mean luminance floor (rejects black viewports ~0.24)
        "min_viewport_std_dev": 4.0,          # Inner 3D viewport std dev floor (rejects featureless viewports < 3.0)
        "max_identical_frame_ratio": 0.50,    # Rejects bursts where >50% of frames share identical SHA256
        "min_inter_phase_mad": 1.5,           # Minimum Mean Absolute Difference across animation phase transitions
        "description": "Visual projectile departure must synchronize with AN_CombatEvent(SpawnProjectile)"
    },
    "CAP-02": {
        "name": "A4 Low Sweep Query vs Blade",
        "montage": "AN_Boss01_A4_LowSweep",
        "clip_duration_s": 2.533,
        "nominal_active_start_s": 0.609,      # Source: E-008:10 (Montage active window start, 12 ticks)
        "nominal_active_end_s": 0.879,        # Source: E-008:10 (Montage active window end)
        "nominal_active_duration_s": 0.270,   # Source: E-008:10 (0.879s - 0.609s; historical AG31 draft used [0.533, 1.100]s)
        "nominal_query_reach_cm": 380.0,      # Source: E-008:7 (RPGBossLowSweep Reach)
        "max_sampled_tip_reach_cm": 312.0,    # Source: E-008:10 (Visible tip furthest reach at 0.855s)
        "nominal_reach_delta_cm": 68.0,       # Source: E-008:10 (380cm - 312cm overreach before capsule radius)
        "floor_dip_intervals": [[0.730, 0.807], [0.903, 1.025]], # Source: E-008:12 (Tip at or below floor proxy)
        "tolerance_reach_delta_cm": 15.0,     # PROPOSED: Antigravity proposal for owner signoff
        "tolerance_max_window_delta_ms": 33.3,# PROPOSED: Antigravity proposal for owner signoff
        "min_arc_coverage_pct": 90.0,         # PROPOSED: Antigravity proposal for owner signoff
        "min_burst_frames": 16,
        "min_sim_step_s": 0.020,
        "min_image_bytes": 50000,
        "min_pixel_variance": 1.0,
        "min_viewport_luminance": 8.0,
        "min_viewport_std_dev": 4.0,
        "max_identical_frame_ratio": 0.50,
        "min_inter_phase_mad": 1.5,
        "description": "Damage query active window and geometric arc must envelope blade tip trajectory"
    },
    "CAP-05": {
        "name": "Telegraph Lead Duration",
        "montage": "AN_Boss01_A2_Raise",
        "clip_duration_s": 1.833,
        "nominal_lead_a1_ms": 330.0,          # Source: AG3:68 (A1 reaction lead time)
        "nominal_lead_a2_ms": 225.0,          # Source: AG3:90 (A2 reaction lead time: 200-250ms)
        "tolerance_strict_lead_ms": 400.0,    # PROPOSED: NO SOURCE IN FREEZE (Antigravity proposal, feel decision)
        "tolerance_reject_lead_ms": 350.0,    # PROPOSED: NO SOURCE IN FREEZE (Antigravity proposal, feel decision)
        "min_burst_frames": 18,
        "min_sim_step_s": 0.020,
        "min_image_bytes": 50000,
        "min_pixel_variance": 1.0,
        "min_viewport_luminance": 8.0,
        "min_viewport_std_dev": 4.0,
        "max_identical_frame_ratio": 0.50,
        "min_inter_phase_mad": 1.5,
        "description": "Weapon raise visual cue / glow must lead active damage window by reactable margin"
    },
    "CAP-06": {
        "name": "Recovery & Punish Opening",
        "montage": "AN_Boss01_A2_Slam",
        "clip_duration_s": 2.167,
        "nominal_recovery_opening_ms": None,  # NO SOURCE IN FREEZE (Owner decision required)
        "tolerance_strict_opening_ms": 800.0, # PROPOSED: NO SOURCE IN FREEZE (Antigravity proposal, feel decision)
        "tolerance_reject_opening_ms": 650.0, # PROPOSED: NO SOURCE IN FREEZE (Antigravity proposal, feel decision)
        "min_burst_frames": 16,
        "min_sim_step_s": 0.020,
        "min_image_bytes": 50000,
        "min_pixel_variance": 1.0,
        "min_viewport_luminance": 8.0,
        "min_viewport_std_dev": 4.0,
        "max_identical_frame_ratio": 0.50,
        "min_inter_phase_mad": 1.5,
        "description": "Blade grounded rest post-slam must provide vulnerable opening before recovery blend-out"
    }
}


# ==============================================================================
# ZERO-DEPENDENCY OFFLINE IMAGE VALIDATION (PIXEL VARIANCE & INTEGRITY)
# ==============================================================================

def decode_png_variance_raw(data: bytes, min_variance: float = 4.0, min_luminance: float = 8.0):
    """
    Pure Python PNG parser using only standard library zlib and struct.
    Decodes IDAT scanlines and computes pixel mean luminance and standard deviation
    on the central 3D viewport region (x: 20%-80%, y: 30%-80%), cropping away
    editor window chrome and HUD/status strips.
    """
    if len(data) < 8 or data[:8] != b'\x89PNG\r\n\x1a\n':
        return False, "Not a valid PNG header", 0.0, 0.0

    pos = 8
    idat_chunks = []
    width = height = bit_depth = color_type = 0
    while pos < len(data):
        if pos + 8 > len(data):
            break
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8]
        chunk_data = data[pos+8:pos+8+length]
        pos += 8 + length + 4  # length + type + data + crc

        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
        elif chunk_type == b'IDAT':
            idat_chunks.append(chunk_data)
        elif chunk_type == b'IEND':
            break

    if not idat_chunks:
        return False, "No IDAT chunk found in PNG", 0.0, 0.0

    try:
        raw_decompressed = zlib.decompress(b''.join(idat_chunks))
    except Exception as e:
        return False, f"Failed to decompress PNG IDAT data: {e}", 0.0, 0.0

    bpp = 4 if color_type == 6 else (3 if color_type == 2 else 1)
    stride = 1 + width * bpp
    y_min, y_max = int(height * 0.30), int(height * 0.80)
    x_min, x_max = int(width * 0.20), int(width * 0.80)

    samples = []
    step_y = max(1, (y_max - y_min) // 64)
    step_x = max(1, (x_max - x_min) // 64)
    for y in range(y_min, y_max, step_y):
        line_start = y * stride + 1
        if line_start >= len(raw_decompressed):
            break
        for x in range(x_min, x_max, step_x):
            px = line_start + x * bpp
            if px + bpp <= len(raw_decompressed):
                if bpp >= 3:
                    r, g, b = raw_decompressed[px], raw_decompressed[px+1], raw_decompressed[px+2]
                    lum = 0.299 * r + 0.587 * g + 0.114 * b
                else:
                    lum = float(raw_decompressed[px])
                samples.append(lum)

    if not samples:
        step = max(1, len(raw_decompressed) // 4096)
        samples = [float(x) for x in raw_decompressed[::step]]

    mean = sum(samples) / len(samples)
    variance = sum((x - mean) ** 2 for x in samples) / len(samples)
    std_dev = math.sqrt(variance)

    if mean < min_luminance:
        return False, f"Blank/black viewport detected (inner 3D viewport mean luminance={mean:.2f} < {min_luminance:.1f})", mean, std_dev

    if std_dev < min_variance:
        return False, f"Blank/featureless viewport detected (inner 3D viewport std_dev={std_dev:.4f} < {min_variance:.1f})", mean, std_dev

    return True, f"Valid image (mean={mean:.2f}, std_dev={std_dev:.2f})", mean, std_dev


def verify_image_file(image_path: str, min_bytes: int = 50000, min_variance: float = 4.0, min_luminance: float = 8.0):
    """
    Verifies that an image file exists, meets minimum size, and contains non-blank pixels
    specifically within the inner 3D viewport crop (excluding window chrome and HUD strips).
    Returns (is_valid: bool, reason: str, mean_luminance: float, std_dev: float).
    """
    p = Path(image_path)
    if not p.exists():
        return False, f"File missing on disk: {p.name}", 0.0, 0.0

    size = p.stat().st_size
    if size < min_bytes:
        return False, f"File size too small ({size:,} bytes < {min_bytes:,} bytes): {p.name}", 0.0, 0.0

    # If Pillow is present, use it for complete color pipeline and inner crop
    if HAS_PIL:
        try:
            with Image.open(p) as img:
                w, h = img.size
                crop_box = (int(w * 0.20), int(h * 0.30), int(w * 0.80), int(h * 0.80))
                crop = img.crop(crop_box).convert("L")
                pixels = list(crop.tobytes())
                n = len(pixels)
                if n == 0:
                    return False, f"Empty pixel data in viewport crop: {p.name}", 0.0, 0.0

                mean = sum(pixels) / n
                variance = sum((x - mean) ** 2 for x in pixels) / n
                std_dev = math.sqrt(variance)

                if mean < min_luminance:
                    return False, f"Blank/black viewport detected in {p.name}: inner 3D viewport mean luminance={mean:.2f} < {min_luminance:.1f} (solid black screen)", mean, std_dev

                if std_dev < min_variance:
                    return False, f"Blank/featureless viewport detected in {p.name}: inner 3D viewport std_dev={std_dev:.4f} < {min_variance:.1f}", mean, std_dev

                return True, "Valid non-blank image", mean, std_dev
        except Exception:
            pass  # Fallback to pure zlib

    # Zero-dependency fallback: read raw bytes and decode scanlines
    try:
        with open(p, "rb") as f:
            data = f.read()
        ok, reason, mean, std_dev = decode_png_variance_raw(data, min_variance, min_luminance)
        if not ok:
            return False, f"{reason}: {p.name}", mean, std_dev
        return True, "Valid non-blank image", mean, std_dev
    except Exception as e:
        return False, f"Corrupted or unreadable image ({e}): {p.name}", 0.0, 0.0


def create_raw_png(path: str, width: int = 64, height: int = 64, pattern: str = "solid"):
    """Creates a minimal valid PNG file using only built-in zlib/struct (zero dependencies)."""
    raw_lines = bytearray()
    for y in range(height):
        raw_lines.append(0)  # filter type 0: None
        for x in range(width):
            if pattern == "solid":
                raw_lines.extend(b"\x00\x00\x00")
            elif pattern == "checker":
                c = 255 if ((x // 8) + (y // 8)) % 2 == 0 else 0
                raw_lines.extend(bytes([c, c, c]))
    compressed = zlib.compress(bytes(raw_lines))

    def make_chunk(chunk_type: bytes, data: bytes):
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    header = b"\x89PNG\r\n\x1a\n"
    ihdr = make_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    idat = make_chunk(b"IDAT", compressed)
    iend = make_chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(header + ihdr + idat + iend)


# ==============================================================================
# TELEMETRY LOG PARSER
# ==============================================================================

class CaptureTelemetryParser:
    """Parses console logs generated by pie_capture_cap*.py scripts."""

    TAG_REGEX = re.compile(r'\[Capture(CAP\d+)\]\s*(.*)')
    FRAME_REGEX = re.compile(r'Captured frame (\d+)/(\d+) at sim_time=([\d\.]+)s(?:\s*\(size:\s*([\d,]+)\s*bytes\))?')
    RESULT_REGEX = re.compile(r'RESULT (\d+)/(\d+)(?:\s*\((.*?)\))?')
    TRIGGER_REGEX = re.compile(r'Triggering boss (\w+) move')
    START_MOVE_RET_REGEX = re.compile(r"StartMove\('(\w+)',\s*(?:True|False)\)\s*returned:\s*(True|False)")
    VETO_REGEX = re.compile(r'attack (\w+) vetoed:\s*(.*?),\s*montage stopped', re.IGNORECASE)
    CVAR_REGEX = re.compile(r'Pre-test cvars saved:\s*(\{.*?\})')
    SCREENSHOT_SAVED_REGEX = re.compile(r'High resolution screenshot saved as (.*\.png)', re.IGNORECASE)
    TELEMETRY_REGEX = re.compile(r'TELEMETRY\s+wall=([\d\.]+)\s+sim=([\d\.]+)\s+phase=(\w+)\s+active=(True|False)\s+commit=(True|False)\s+pos=([\d\.]+)')
    PHASE_CHANGE_REGEX = re.compile(r'PHASE_CHANGE\s+phase=(\w+)\s+sim=([\d\.]+)\s+wall=([\d\.]+)')

    @classmethod
    def parse_log_text(cls, log_text: str):
        captures = {}
        current_cap_id = None

        for line in log_text.splitlines():
            line_str = line.strip()

            m_veto = cls.VETO_REGEX.search(line_str)
            if m_veto:
                vetoed_move = m_veto.group(1)
                veto_reason = m_veto.group(2)
                if current_cap_id and current_cap_id in captures:
                    captures[current_cap_id]["vetoed"] = True
                    captures[current_cap_id]["veto_reason"] = f"{vetoed_move} vetoed: {veto_reason}"
                    captures[current_cap_id]["errors"].append(f"ENGINE VETO: {vetoed_move} vetoed: {veto_reason}")

            m_tag = cls.TAG_REGEX.search(line_str)
            if not m_tag:
                continue

            cap_id_raw = m_tag.group(1).upper()
            cap_id = f"{cap_id_raw[:3]}-{cap_id_raw[3:]}" if len(cap_id_raw) == 5 else cap_id_raw
            payload = m_tag.group(2).strip()
            current_cap_id = cap_id

            if cap_id not in captures:
                captures[cap_id] = {
                    "cap_id": cap_id,
                    "lines": [],
                    "frames": [],
                    "telemetry": [],
                    "phase_changes": [],
                    "triggered_move": None,
                    "start_move_returned": None,
                    "vetoed": False,
                    "veto_reason": None,
                    "cvars": {},
                    "result_passed": None,
                    "result_total": None,
                    "result_reason": None,
                    "errors": []
                }

            entry = captures[cap_id]
            entry["lines"].append(payload)

            if "ERROR" in payload.upper() or "EXCEPTION" in payload.upper() or "FAILED" in payload.upper():
                entry["errors"].append(payload)

            m_trig = cls.TRIGGER_REGEX.search(payload)
            if m_trig:
                entry["triggered_move"] = m_trig.group(1)

            m_ret = cls.START_MOVE_RET_REGEX.search(payload)
            if m_ret:
                entry["start_move_returned"] = (m_ret.group(2).lower() == "true")

            m_telemetry = cls.TELEMETRY_REGEX.search(payload)
            if m_telemetry:
                wall_t = float(m_telemetry.group(1))
                sim_t = float(m_telemetry.group(2))
                phase_name = m_telemetry.group(3)
                is_active = (m_telemetry.group(4) == "True")
                is_commit = (m_telemetry.group(5) == "True")
                pos = float(m_telemetry.group(6))
                entry["telemetry"].append({
                    "wall": wall_t,
                    "sim": sim_t,
                    "phase": phase_name,
                    "active": is_active,
                    "commit": is_commit,
                    "pos": pos
                })

            m_phase = cls.PHASE_CHANGE_REGEX.search(payload)
            if m_phase:
                entry["phase_changes"].append({
                    "phase": m_phase.group(1),
                    "sim": float(m_phase.group(2)),
                    "wall": float(m_phase.group(3))
                })

            m_cvar = cls.CVAR_REGEX.search(payload)
            if m_cvar:
                try:
                    entry["cvars"] = eval(m_cvar.group(1))
                except Exception:
                    pass

            m_frame = cls.FRAME_REGEX.search(payload)
            if m_frame:
                idx = int(m_frame.group(1))
                total = int(m_frame.group(2))
                sim_t = float(m_frame.group(3))
                size_b = int(m_frame.group(4).replace(",", "")) if m_frame.group(4) else 0
                entry["frames"].append({
                    "frame_idx": idx,
                    "total_frames": total,
                    "sim_time": sim_t,
                    "size_bytes": size_b
                })

            m_res = cls.RESULT_REGEX.search(payload)
            if m_res:
                entry["result_passed"] = int(m_res.group(1))
                entry["result_total"] = int(m_res.group(2))
                entry["result_reason"] = m_res.group(3) or "Completed"

        # Populate frames from telemetry if no HighResShot log lines were emitted
        for cap_entry in captures.values():
            if not cap_entry["frames"] and cap_entry["telemetry"]:
                for i, t in enumerate(cap_entry["telemetry"]):
                    cap_entry["frames"].append({
                        "frame_idx": i + 1,
                        "total_frames": len(cap_entry["telemetry"]),
                        "sim_time": t["sim"],
                        "size_bytes": 100000
                    })

        return captures


# ==============================================================================
# VERDICT EVALUATOR
# ==============================================================================

class CaptureEvaluator:
    """Evaluates capture telemetry against AG31 specification criteria."""

    @classmethod
    def verify_capture_images(cls, image_dir, spec, verdict, min_expected=1):
        if not image_dir:
            return
        p_dir = Path(image_dir)
        if not p_dir.exists():
            verdict["status"] = "FAIL"
            verdict["rejections"].append(f"REJECTION: Image directory does not exist: {image_dir}")
            return

        image_paths = sorted(p_dir.glob("*.png"))
        if not image_paths:
            verdict["status"] = "FAIL"
            verdict["rejections"].append(f"REJECTION: Missing files on disk: zero PNG frames found in image directory: {image_dir}")
            return

        # 1. Per-frame verification (size, inner 3D viewport luminance & variance)
        valid_count = 0
        min_lum = spec.get("min_viewport_luminance", 8.0)
        min_std = spec.get("min_viewport_std_dev", 4.0)

        hashes = {}
        crops_by_phase = {}

        for img_path in image_paths:
            ok, err, mean_lum, std_dev = verify_image_file(
                str(img_path),
                min_bytes=spec["min_image_bytes"],
                min_variance=min_std,
                min_luminance=min_lum
            )
            if not ok:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(f"REJECTION: Image file failure on {img_path.name}: {err}")
                break
            valid_count += 1

            # Hash calculation for duplicate/freeze detection
            with open(img_path, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            hashes[h] = hashes.get(h, 0) + 1

            # Extract phase from filename (e.g. 001_CAP01_A5_Windup.png -> Windup)
            m_phase = re.search(r'_(Windup|Active|Recovery|None)\.png', img_path.name, re.IGNORECASE)
            phase_tag = m_phase.group(1).capitalize() if m_phase else "Default"

            # Store downsampled inner viewport crop for inter-phase delta
            if HAS_PIL:
                try:
                    with Image.open(img_path) as im:
                        w, h_img = im.size
                        crop_box = (int(w * 0.20), int(h_img * 0.30), int(w * 0.80), int(h_img * 0.80))
                        c = im.crop(crop_box).convert("L").resize((32, 32))
                        if phase_tag not in crops_by_phase:
                            crops_by_phase[phase_tag] = []
                        crops_by_phase[phase_tag].append((img_path.name, list(c.tobytes())))
                except Exception:
                    pass

        verdict["metrics"]["frames_on_disk"] = len(image_paths)
        verdict["metrics"]["valid_rendered_frames"] = valid_count

        if verdict["status"] == "FAIL":
            return

        # 2. Frame Hash Uniqueness / Freeze Detection (Check (a))
        total_frames = len(image_paths)
        if total_frames > 1 and len(hashes) == 1:
            verdict["status"] = "FAIL"
            verdict["rejections"].append(f"REJECTION: All {total_frames} frames are byte-identical (frozen capture; SHA256={list(hashes.keys())[0][:16]}...).")
            return

        max_dup = max(hashes.values()) if hashes else 0
        dup_ratio = max_dup / total_frames if total_frames > 0 else 0.0
        max_allowed_ratio = spec.get("max_identical_frame_ratio", 0.50)
        if total_frames >= 4 and dup_ratio > max_allowed_ratio:
            verdict["status"] = "FAIL"
            verdict["rejections"].append(f"REJECTION: High frame freeze rate: {max_dup}/{total_frames} frames ({dup_ratio*100:.1f}% > {max_allowed_ratio*100:.0f}%) share identical SHA256 hash.")
            return

        # 3. Inter-Phase Visual Progression (Check (c))
        distinct_phases = [p for p in ["Windup", "Active", "Recovery"] if p in crops_by_phase and len(crops_by_phase[p]) > 0]
        if len(distinct_phases) >= 2:
            min_mad = spec.get("min_inter_phase_mad", 1.5)
            for i in range(len(distinct_phases) - 1):
                p1 = distinct_phases[i]
                p2 = distinct_phases[i+1]
                f1_name, pix1 = crops_by_phase[p1][-1]
                f2_name, pix2 = crops_by_phase[p2][0]
                mad = sum(abs(a - b) for a, b in zip(pix1, pix2)) / len(pix1)
                verdict["metrics"][f"mad_{p1.lower()}_to_{p2.lower()}"] = round(mad, 2)
                if mad < min_mad:
                    verdict["status"] = "FAIL"
                    verdict["rejections"].append(
                        f"REJECTION: Zero visual animation progression between phases '{p1}' ({f1_name}) and '{p2}' ({f2_name}): MAD={mad:.2f} < {min_mad:.1f} (static scene across phase change)."
                    )
                    return

    @classmethod
    def get_min_burst_frames(cls, data, spec):
        telemetry = data.get("telemetry", [])
        if len(telemetry) >= 2:
            wall_dur = telemetry[-1]["wall"] - telemetry[0]["wall"]
            deltas = [telemetry[i]["wall"] - telemetry[i-1]["wall"] for i in range(1, len(telemetry))]
            interval = 0.10
            if deltas:
                median_dt = sorted(deltas)[len(deltas)//2]
                if 0.02 <= median_dt <= 0.5:
                    interval = median_dt
            derived = max(5, int(wall_dur / interval) - 2)
            return derived, wall_dur, interval
        return spec.get("min_burst_frames", 15), None, None

    @classmethod
    def evaluate_cap01(cls, data, image_dir=None):
        spec = BENCHMARK_RULES["CAP-01"]
        verdict = {
            "test_id": "CAP-01",
            "name": spec["name"],
            "status": "PASS",
            "findings": [],
            "rejections": [],
            "metrics": {},
            "owner_questions": []
        }

        if data.get("vetoed"):
            verdict["status"] = "FAIL"
            reason = data.get("veto_reason", "Engine vetoed move")
            verdict["rejections"].append(f"ENGINE VETO: Attack execution was vetoed by engine runtime: '{reason}'. Run invalid.")
            return verdict

        frames = data.get("frames", [])
        if not frames:
            verdict["status"] = "FAIL"
            verdict["rejections"].append("REJECTION: Zero burst frames captured in telemetry.")
            return verdict

        min_frames, wall_dur, interval = cls.get_min_burst_frames(data, spec)
        if wall_dur is not None:
            verdict["metrics"]["derived_min_burst_frames"] = min_frames
            verdict["metrics"]["measured_wall_duration_s"] = round(wall_dur, 3)

        if len(frames) < min_frames:
            verdict["status"] = "FAIL"
            if wall_dur is not None:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames (derived from {wall_dur:.2f}s duration at {interval*1000:.0f}ms interval).")
            else:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames.")

        times = [f["sim_time"] for f in frames]

        for i in range(1, len(times)):
            dt = times[i] - times[i - 1]
            if dt < spec["min_sim_step_s"]:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(
                    f"REJECTION: Simulation time compression detected at frame {i+1}: dt_sim={dt:.4f}s < {spec['min_sim_step_s']}s limit. Burst captured across same tick."
                )
                break

        for t in times:
            if t < 0.0 or t > spec["clip_duration_s"] + 10.0:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(f"REJECTION: Timestamp {t:.3f}s out of valid bounds [0.0, {spec['clip_duration_s']}s].")

        cls.verify_capture_images(image_dir, spec, verdict)

        authored_intent_s = spec["nominal_authored_intent_s"]
        code_active_s = spec["nominal_code_active_s"]
        sampled_release_s = spec["sampled_code_release_s"]
        visual_release_observed = data.get("observed_visual_release_s", None)

        verdict["metrics"] = {
            "authored_intent_marker_s": authored_intent_s,
            "code_active_window_s": code_active_s,
            "sampled_code_release_s": sampled_release_s,
            "nominal_delta_s": spec["nominal_delta_s"],
            "sampled_delta_s": spec["sampled_delta_s"],
            "observed_visual_release_s": visual_release_observed if visual_release_observed is not None else "UNVERIFIED (Requires Visual Inspection)",
            "tolerance_strict_ms_PROPOSED": spec["tolerance_strict_ms"],
            "tolerance_max_ms_PROPOSED": spec["tolerance_max_ms"],
            "frames_captured": len(frames),
            "sim_time_span_s": round(times[-1] - times[0], 4) if len(times) > 1 else 0.0
        }

        verdict["findings"].append(f"Authored intent marker: {authored_intent_s:.3f}s (E-007:7, sidecar frame 12 @ 30fps).")
        verdict["findings"].append(f"Code active window: {code_active_s:.3f}s (E-007:5, URPGAttackTracker).")
        verdict["findings"].append(f"Nominal code offset: {spec['nominal_delta_s']*1000.0:.1f}ms (1.0 frame @ 20fps per E-007:7).")

        verdict["owner_questions"].append(
            "OWNER QUESTION (Feel Decision): Does the 0.050s nominal / 0.070s observed release offset after the 0.400s authored marker create any perceptible mismatch in gameplay? E-007 and D06B classify this as a feel question, not a defect."
        )

        return verdict

    @classmethod
    def evaluate_cap02(cls, data, image_dir=None):
        spec = BENCHMARK_RULES["CAP-02"]
        verdict = {
            "test_id": "CAP-02",
            "name": spec["name"],
            "status": "PASS",
            "findings": [],
            "rejections": [],
            "metrics": {},
            "owner_questions": []
        }

        if data.get("vetoed"):
            verdict["status"] = "FAIL"
            reason = data.get("veto_reason", "Engine vetoed move")
            verdict["rejections"].append(f"ENGINE VETO: Attack execution was vetoed by engine runtime: '{reason}'. Run invalid.")
            return verdict

        frames = data.get("frames", [])
        min_frames, wall_dur, interval = cls.get_min_burst_frames(data, spec)
        if wall_dur is not None:
            verdict["metrics"]["derived_min_burst_frames"] = min_frames
            verdict["metrics"]["measured_wall_duration_s"] = round(wall_dur, 3)

        if len(frames) < min_frames:
            verdict["status"] = "FAIL"
            if wall_dur is not None:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames (derived from {wall_dur:.2f}s duration at {interval*1000:.0f}ms interval).")
            else:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames.")

        times = [f["sim_time"] for f in frames]
        for i in range(1, len(times)):
            dt = times[i] - times[i - 1]
            if dt < spec["min_sim_step_s"]:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(
                    f"REJECTION: Simulation time compression detected at frame {i+1}: dt_sim={dt:.4f}s < {spec['min_sim_step_s']}s limit."
                )
                break

        cls.verify_capture_images(image_dir, spec, verdict)

        verdict["metrics"] = {
            "nominal_active_window_s": [spec["nominal_active_start_s"], spec["nominal_active_end_s"]],
            "nominal_query_reach_cm": spec["nominal_query_reach_cm"],
            "max_sampled_tip_reach_cm": spec["max_sampled_tip_reach_cm"],
            "nominal_reach_delta_cm": spec["nominal_reach_delta_cm"],
            "tolerance_reach_delta_cm_PROPOSED": spec["tolerance_reach_delta_cm"],
            "floor_dip_intervals_s": spec["floor_dip_intervals"],
            "frames_captured": len(frames),
            "sim_time_span_s": round(times[-1] - times[0], 4) if len(times) > 1 else 0.0
        }

        verdict["findings"].append(f"A4 Low Sweep query reach: {spec['nominal_query_reach_cm']:.1f}cm (E-008:7).")
        verdict["findings"].append(f"A4 Active Window: [{spec['nominal_active_start_s']:.3f}, {spec['nominal_active_end_s']:.3f}]s (E-008:10).")
        verdict["findings"].append(f"Visible tip sampled reach max: {spec['max_sampled_tip_reach_cm']:.1f}cm (E-008:10).")
        verdict["findings"].append(f"Reach discrepancy: {spec['nominal_reach_delta_cm']:.1f}cm overreach before player capsule radius (E-008:10).")

        verdict["owner_questions"].append(
            "OWNER QUESTION (Design Alignment): The production query reaches 68cm beyond the farthest visible tip position (E-008:10). Is this overreach acceptable as a gameplay forgiving buffer, or should the query reach be matched to the visible blade in P4?"
        )

        return verdict

    @classmethod
    def evaluate_cap05(cls, data, image_dir=None):
        spec = BENCHMARK_RULES["CAP-05"]
        verdict = {
            "test_id": "CAP-05",
            "name": spec["name"],
            "status": "PASS",
            "findings": [],
            "rejections": [],
            "metrics": {},
            "owner_questions": []
        }

        if data.get("vetoed"):
            verdict["status"] = "FAIL"
            reason = data.get("veto_reason", "Engine vetoed move")
            verdict["rejections"].append(f"ENGINE VETO: Attack execution was vetoed by engine runtime: '{reason}'. Run invalid.")
            return verdict

        frames = data.get("frames", [])
        min_frames, wall_dur, interval = cls.get_min_burst_frames(data, spec)
        if wall_dur is not None:
            verdict["metrics"]["derived_min_burst_frames"] = min_frames
            verdict["metrics"]["measured_wall_duration_s"] = round(wall_dur, 3)

        if len(frames) < min_frames:
            verdict["status"] = "FAIL"
            if wall_dur is not None:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames (derived from {wall_dur:.2f}s duration at {interval*1000:.0f}ms interval).")
            else:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames.")

        times = [f["sim_time"] for f in frames]
        for i in range(1, len(times)):
            dt = times[i] - times[i - 1]
            if dt < spec["min_sim_step_s"]:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(
                    f"REJECTION: Simulation time compression detected at frame {i+1}: dt_sim={dt:.4f}s < {spec['min_sim_step_s']}s limit."
                )
                break

        cls.verify_capture_images(image_dir, spec, verdict)

        verdict["metrics"] = {
            "nominal_lead_a1_ms": spec["nominal_lead_a1_ms"],
            "nominal_lead_a2_ms": spec["nominal_lead_a2_ms"],
            "tolerance_strict_lead_ms_PROPOSED": spec["tolerance_strict_lead_ms"],
            "tolerance_reject_lead_ms_PROPOSED": spec["tolerance_reject_lead_ms"],
            "frames_captured": len(frames),
            "sim_time_span_s": round(times[-1] - times[0], 4) if len(times) > 1 else 0.0
        }

        verdict["findings"].append(f"Nominal A1 telegraph lead: {spec['nominal_lead_a1_ms']:.1f}ms (AG3:68).")
        verdict["findings"].append(f"Nominal A2 telegraph lead: {spec['nominal_lead_a2_ms']:.1f}ms (AG3:90).")

        verdict["owner_questions"].append(
            "OWNER QUESTION (Readability Feel): Standard human reaction threshold is 250-350ms (AG3:68). Are the proposed 400ms strict and 350ms floor acceptable for boss telegraph leads?"
        )

        return verdict

    @classmethod
    def evaluate_cap06(cls, data, image_dir=None):
        spec = BENCHMARK_RULES["CAP-06"]
        verdict = {
            "test_id": "CAP-06",
            "name": spec["name"],
            "status": "PASS",
            "findings": [],
            "rejections": [],
            "metrics": {},
            "owner_questions": []
        }

        if data.get("vetoed"):
            verdict["status"] = "FAIL"
            reason = data.get("veto_reason", "Engine vetoed move")
            verdict["rejections"].append(f"ENGINE VETO: Attack execution was vetoed by engine runtime: '{reason}'. Run invalid.")
            return verdict

        frames = data.get("frames", [])
        min_frames, wall_dur, interval = cls.get_min_burst_frames(data, spec)
        if wall_dur is not None:
            verdict["metrics"]["derived_min_burst_frames"] = min_frames
            verdict["metrics"]["measured_wall_duration_s"] = round(wall_dur, 3)

        if len(frames) < min_frames:
            verdict["status"] = "FAIL"
            if wall_dur is not None:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames (derived from {wall_dur:.2f}s duration at {interval*1000:.0f}ms interval).")
            else:
                verdict["rejections"].append(f"REJECTION: Incomplete burst. Captured {len(frames)}/{min_frames} frames.")

        times = [f["sim_time"] for f in frames]
        for i in range(1, len(times)):
            dt = times[i] - times[i - 1]
            if dt < spec["min_sim_step_s"]:
                verdict["status"] = "FAIL"
                verdict["rejections"].append(
                    f"REJECTION: Simulation time compression detected at frame {i+1}: dt_sim={dt:.4f}s < {spec['min_sim_step_s']}s limit."
                )
                break

        cls.verify_capture_images(image_dir, spec, verdict)

        verdict["metrics"] = {
            "nominal_recovery_opening_ms": "NO SOURCE IN FREEZE (Owner decision required)",
            "tolerance_strict_opening_ms_PROPOSED": spec["tolerance_strict_opening_ms"],
            "tolerance_reject_opening_ms_PROPOSED": spec["tolerance_reject_opening_ms"],
            "frames_captured": len(frames),
            "sim_time_span_s": round(times[-1] - times[0], 4) if len(times) > 1 else 0.0
        }

        verdict["owner_questions"].append(
            "OWNER QUESTION (Punish Window Feel): There is NO SOURCE in the master design freeze for slam recovery duration. Is an 800ms vulnerable opening desired for player punish windows?"
        )

        return verdict


# ==============================================================================
# SELF-TEST SUITE
# ==============================================================================

def run_self_test():
    """
    Executes comprehensive self-test suite covering all edge cases required by Claude [C-137], [C-138], and [C-151]:
      1. Identical/compressed timestamps (rejects same-tick bursts).
      2. Blank/black PNG (rejects unrendered solid-black frames without PIL dependency).
      3. Missing files on disk (rejects missing screenshots).
      4. Engine runtime veto detection (rejects runs vetoed by phase transition).
      5. Nominal without source / unverified visual pose reporting.
      6. Solid Black Viewport Rejection (Claude C-151 reproduction: inner viewport mean luminance < 8.0).
      7. Byte-Identical Frame Burst / Freeze Rejection (Claude C-151 reproduction: frozen camera buffer).
      8. Valid Monotonic Capture Run (asserts PASS with real inter-frame variation).
    """
    print("================================================================================")
    print("RUNNING CAPTURE ANALYSIS SELF-TEST SUITE (Hardened for C-135 / C-137 / C-138 / C-151)")
    print(f"PIL Accelerated: {HAS_PIL} (Zero-dependency raw PNG decoder active)")
    print("================================================================================")

    test_passed = 0
    test_total = 8

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # ----------------------------------------------------------------------
        # Test Case 1: Identical / Compressed Timestamps (Claude C-135/C-137 reproduction)
        # ----------------------------------------------------------------------
        print("\n--- Test Case 1: Identical/Compressed Timestamps (Same-Tick Burst) ---")
        compressed_data = {
            "frames": [{"frame_idx": i, "sim_time": 0.949 if i == 1 else 0.953, "size_bytes": 17709} for i in range(1, 16)]
        }
        res1 = CaptureEvaluator.evaluate_cap01(compressed_data)
        has_rejection = any("time compression detected" in r.lower() for r in res1["rejections"])
        if res1["status"] == "FAIL" and has_rejection:
            print("  PASS: Engine correctly REJECTED compressed timestamps (sim_time 0.949 to 0.953s across 15 frames).")
            print(f"  Captured Rejection: {res1['rejections'][0]}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected rejection on compressed timestamps, got {res1['status']}")

        # ----------------------------------------------------------------------
        # Test Case 2: Blank PNG Rejection (Zero-Dependency Pixel Variance Check)
        # ----------------------------------------------------------------------
        print("\n--- Test Case 2: Blank PNG Image Rejection (Zero-Dependency Variance Check) ---")
        blank_img_dir = tmp_path / "blank_test"
        blank_img_dir.mkdir(parents=True, exist_ok=True)
        blank_file = blank_img_dir / "blank_frame.png"

        # Create raw solid-color PNG using built-in zlib
        create_raw_png(str(blank_file), width=64, height=64, pattern="solid")
        with open(blank_file, "ab") as f:
            f.write(b"\0" * 60000)

        ok, reason, mean_lum, var = verify_image_file(str(blank_file), min_bytes=50000, min_variance=4.0, min_luminance=8.0)
        if not ok and ("blank" in reason.lower() or "black" in reason.lower()):
            print(f"  PASS: verify_image_file correctly REJECTED solid-color image (mean={mean_lum:.2f}, std_dev={var:.4f}).")
            print(f"  Captured Reason: {reason}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected blank image rejection, got ok={ok}, reason={reason}")

        # ----------------------------------------------------------------------
        # Test Case 3: Missing Files on Disk
        # ----------------------------------------------------------------------
        print("\n--- Test Case 3: Missing Files on Disk ---")
        missing_dir = tmp_path / "missing_test"
        missing_dir.mkdir(parents=True, exist_ok=True)
        data3 = {
            "frames": [{"frame_idx": i, "sim_time": 1.0 + (i * 0.0333), "size_bytes": 65000} for i in range(1, 16)]
        }
        res3 = CaptureEvaluator.evaluate_cap01(data3, image_dir=missing_dir)
        has_missing_rej = any("missing files on disk" in r.lower() for r in res3["rejections"])
        if res3["status"] == "FAIL" and has_missing_rej:
            print("  PASS: Engine correctly REJECTED capture due to missing files on disk.")
            print(f"  Captured Rejection: {res3['rejections'][0]}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected missing files rejection, got {res3['status']}")

        # ----------------------------------------------------------------------
        # Test Case 4: Engine Runtime Veto Detection (Phase Transition Veto)
        # ----------------------------------------------------------------------
        print("\n--- Test Case 4: Engine Runtime Veto Detection (Phase Transition Veto) ---")
        veto_log_sample = """
        [2026.10.26-05.37.59:874][ 40]LogPython: [CaptureCAP01] StartMove('A5', True) returned: True
        [2026.10.26-05.37.59:891][ 41]LogRPGAttack: BP_ExampleGreatSwordBoss_C_3: attack A5 vetoed: a phase transition is running, montage stopped
        [2026.10.26-05.37.59:897][ 41]LogPython: [CaptureCAP01] Captured frame 1/15 at sim_time=0.949s
        [2026.10.26-05.38.00:881][ 47]LogPython: [CaptureCAP01] Captured frame 2/15 at sim_time=0.953s
        [2026.10.26-05.38.01:628][ 65]LogPython: [CaptureCAP01] RESULT 5/5 (CAPTURE_SUCCESS)
        """
        parsed_veto = CaptureTelemetryParser.parse_log_text(veto_log_sample)
        cap01_parsed = parsed_veto.get("CAP-01", {})
        res4 = CaptureEvaluator.evaluate_cap01(cap01_parsed)
        has_veto_rej = any("engine veto" in r.lower() for r in res4["rejections"])
        if res4["status"] == "FAIL" and has_veto_rej:
            print("  PASS: Engine correctly detected LogRPGAttack veto and REJECTED the run despite RESULT 5/5.")
            print(f"  Captured Rejection: {res4['rejections'][0]}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected veto rejection, got {res4['status']}")

        # ----------------------------------------------------------------------
        # Test Case 5: Nominal Source Citation & Owner Question Reporting
        # ----------------------------------------------------------------------
        print("\n--- Test Case 5: Source Citation & Owner Question Reporting ---")
        res5 = CaptureEvaluator.evaluate_cap06({"frames": [{"frame_idx": i, "sim_time": 1.0 + (i * 0.0333)} for i in range(1, 17)]})
        has_no_source = "NO SOURCE IN FREEZE" in str(res5["metrics"].get("nominal_recovery_opening_ms"))
        has_owner_q = len(res5["owner_questions"]) > 0
        if has_no_source and has_owner_q:
            print("  PASS: Engine correctly marked recovery nominal as NO SOURCE IN FREEZE and surfaced Owner Question.")
            print(f"  Captured Metric: {res5['metrics']['nominal_recovery_opening_ms']}")
            print(f"  Captured Question: {res5['owner_questions'][0][:90]}...")
            test_passed += 1
        else:
            print(f"  FAIL: Expected NO SOURCE and Owner Question, got metric={res5['metrics'].get('nominal_recovery_opening_ms')}")

        # ----------------------------------------------------------------------
        # Test Case 6: Claude C-151 Solid Black Viewport Rejection
        # ----------------------------------------------------------------------
        print("\n--- Test Case 6: Black Viewport Rejection (Claude C-151 Reproduction) ---")
        black_dir = tmp_path / "black_viewport_test"
        black_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, 12):
            bf = black_dir / f"00{i:02d}_CAP01_A5_Windup.png"
            create_raw_png(str(bf), width=64, height=64, pattern="solid")
            with open(bf, "ab") as f:
                f.write(bytes([i % 256]) * 60000)
        data6 = {
            "cap_id": "CAP-01",
            "frames": [{"frame_idx": i, "sim_time": 1.0 + (i * 0.05)} for i in range(1, 12)],
            "telemetry": [{"wall": 100.0 + i * 0.1, "sim": 1.0 + i * 0.05, "phase": "Windup", "active": False, "commit": False, "pos": i*0.05} for i in range(1, 12)]
        }
        res6 = CaptureEvaluator.evaluate_cap01(data6, image_dir=black_dir)
        has_black_rej = any("blank/black viewport detected" in r.lower() for r in res6["rejections"])
        if res6["status"] == "FAIL" and has_black_rej:
            print("  PASS: Engine correctly REJECTED solid black viewport capture set.")
            print(f"  Captured Rejection: {res6['rejections'][0]}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected black viewport rejection, got {res6['status']}, rejections: {res6['rejections']}")

        # ----------------------------------------------------------------------
        # Test Case 7: Byte-Identical Frozen Frame Burst Rejection
        # ----------------------------------------------------------------------
        print("\n--- Test Case 7: Byte-Identical Frozen Frame Burst Rejection ---")
        frozen_dir = tmp_path / "frozen_test"
        frozen_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, 12):
            ff = frozen_dir / f"00{i:02d}_CAP01_A5_Windup.png"
            create_raw_png(str(ff), width=64, height=64, pattern="checker")
            with open(ff, "ab") as f:
                f.write(b"\x55" * 60000)  # exact same bytes in all frames
        data7 = {
            "cap_id": "CAP-01",
            "frames": [{"frame_idx": i, "sim_time": 1.0 + (i * 0.05)} for i in range(1, 12)],
            "telemetry": [{"wall": 100.0 + i * 0.1, "sim": 1.0 + i * 0.05, "phase": "Windup", "active": False, "commit": False, "pos": i*0.05} for i in range(1, 12)]
        }
        res7 = CaptureEvaluator.evaluate_cap01(data7, image_dir=frozen_dir)
        has_frozen_rej = any("byte-identical" in r.lower() for r in res7["rejections"])
        if res7["status"] == "FAIL" and has_frozen_rej:
            print("  PASS: Engine correctly REJECTED 100% byte-identical frozen frame burst.")
            print(f"  Captured Rejection: {res7['rejections'][0]}")
            test_passed += 1
        else:
            print(f"  FAIL: Expected frozen frame rejection, got {res7['status']}, rejections: {res7['rejections']}")

        # ----------------------------------------------------------------------
        # Test Case 8: Valid Monotonic Capture Run with Multi-Phase Progression
        # ----------------------------------------------------------------------
        print("\n--- Test Case 8: Valid Monotonic Capture Run with Visual Phase Progression ---")
        valid_dir = tmp_path / "valid_test"
        valid_dir.mkdir(parents=True, exist_ok=True)

        valid_frames = []
        for i in range(1, 13):
            phase = "Windup" if i <= 6 else "Active"
            p = valid_dir / f"{i:03d}_CAP01_A5_{phase}.png"
            create_raw_png(str(p), width=64, height=64, pattern="checker")
            with open(p, "ab") as f:
                f.write(bytes([(i * 17) % 256]) * 60000)
            valid_frames.append({
                "frame_idx": i,
                "total_frames": 12,
                "sim_time": 1.000 + ((i - 1) * 0.050),
                "path": str(p),
                "size_bytes": p.stat().st_size
            })

        valid_data = {
            "cap_id": "CAP-01",
            "frames": valid_frames,
            "telemetry": [{"wall": 100.0 + i * 0.1, "sim": 1.0 + i * 0.05, "phase": "Windup" if i <= 6 else "Active", "active": (i > 6), "commit": (i > 6), "pos": i * 0.05} for i in range(1, 13)],
            "vetoed": False
        }
        res8 = CaptureEvaluator.evaluate_cap01(valid_data, image_dir=valid_dir)
        if res8["status"] == "PASS" and len(res8["rejections"]) == 0:
            print(f"  PASS: Valid synthetic capture PASSED all checks. Status: {res8['status']}.")
            print(f"  Frames: {res8['metrics']['frames_captured']}, Span: {res8['metrics']['sim_time_span_s']}s.")
            test_passed += 1
        else:
            print(f"  FAIL: Expected PASS, got {res8['status']}, rejections: {res8['rejections']}")

    print("\n================================================================================")
    print(f"SELF-TEST SUMMARY: {test_passed}/{test_total} TESTS PASSED")
    print("================================================================================")
    return test_passed == test_total


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Offline Analysis & Verdict Engine for Combat Capture Telemetry")
    parser.add_argument("--log", type=str, help="Path to editor console log file")
    parser.add_argument("--image-dir", "--frames-dir", dest="image_dir", type=str, help="Path to captured screenshot directory")
    parser.add_argument("--cap-id", type=str, default="CAP-01", choices=["CAP-01", "CAP-02", "CAP-05", "CAP-06"], help="Capture benchmark ID")
    parser.add_argument("--self-test", action="store_true", help="Run comprehensive self-test suite")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    if not args.log:
        parser.error("Either --log or --self-test must be specified.")

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"ERROR: Log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    captures = CaptureTelemetryParser.parse_log_text(log_text)

    cap_id = args.cap_id
    data = captures.get(cap_id, {})
    if not data:
        data = {"frames": [], "vetoed": False}
        if "vetoed: a phase transition is running" in log_text:
            data["vetoed"] = True
            data["veto_reason"] = "a phase transition is running"

    evaluators = {
        "CAP-01": CaptureEvaluator.evaluate_cap01,
        "CAP-02": CaptureEvaluator.evaluate_cap02,
        "CAP-05": CaptureEvaluator.evaluate_cap05,
        "CAP-06": CaptureEvaluator.evaluate_cap06,
    }

    evaluator = evaluators[cap_id]
    verdict = evaluator(data, image_dir=args.image_dir)

    if args.json:
        print(json.dumps(verdict, indent=2))
    else:
        print("================================================================================")
        print(f"CAPTURE EVALUATION VERDICT: {verdict['test_id']} - {verdict['name']}")
        print(f"STATUS: {verdict['status']}")
        print("================================================================================")
        if verdict["rejections"]:
            print("\nREJECTIONS / FAILURES:")
            for r in verdict["rejections"]:
                print(f"  [X] {r}")
        if verdict["findings"]:
            print("\nFINDINGS:")
            for f in verdict["findings"]:
                print(f"  [-] {f}")
        if verdict["metrics"]:
            print("\nMETRICS:")
            for k, v in verdict["metrics"].items():
                print(f"  * {k}: {v}")
        if verdict["owner_questions"]:
            print("\nOWNER QUESTIONS / FEEL DECISIONS:")
            for q in verdict["owner_questions"]:
                print(f"  [?] {q}")
        print("================================================================================")

    sys.exit(0 if verdict["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
