"""Validate that approved/candidate aura captures followed a bright warmup in the same run."""
import json
import hashlib
import math
import os
import re
from pathlib import Path


BRIGHTNESS_FLOOR = 5.0
MAX_WARMUP_FRAMES = 20
MAX_WARMUP_SECONDS = 4.0
ASSETS = {
    "approved": "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura",
    "candidate": "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost.NS_Boss_PhaseTwoAura_Boost",
}
CANDIDATE_ASSET_RE = re.compile(
    r"/Game/OneBossFight/VFX/(NS_Boss_PhaseTwoAura_[A-Za-z0-9_]+)\.\1\Z")
MANIFEST_SCHEMA = 1
SAFE_COMPONENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")


def validate_warmup_receipt(records, run_id, route, verify_png_files=False):
    if not isinstance(records, list) or not records:
        raise ValueError("manifest is empty")
    seen_frames = set()
    png_paths = set()
    previous_time = None
    manifest_provenance = None
    for row in records:
        if not isinstance(run_id, str) or not SAFE_COMPONENT_RE.fullmatch(run_id):
            raise ValueError("unsafe run id")
        if row.get("run") != run_id or row.get("route") != route:
            raise ValueError("run/route mismatch")
        if type(row.get("schema")) is not int or row["schema"] != MANIFEST_SCHEMA:
            raise ValueError("unsupported manifest schema")
        if (not isinstance(row.get("build_id"), str) or
                row["build_id"].strip() in ("", "UNKNOWN")):
            raise ValueError("missing or unknown build_id")
        if not isinstance(row.get("map"), str) or row["map"].strip() in ("", "UNKNOWN"):
            raise ValueError("missing or unknown map")
        if row.get("route") not in ("legacy", "data"):
            raise ValueError("invalid route")
        row_provenance = (row["build_id"], row["map"], row["route"])
        if manifest_provenance is None:
            manifest_provenance = row_provenance
        elif row_provenance != manifest_provenance:
            raise ValueError("manifest provenance drift")
        frame = row.get("frame")
        if not isinstance(frame, str) or not frame:
            raise ValueError("manifest row lacks frame label")
        if not SAFE_COMPONENT_RE.fullmatch(frame):
            raise ValueError("unsafe frame label")
        if frame in seen_frames:
            raise ValueError("duplicate frame label")
        seen_frames.add(frame)
        if row.get("capture_id") != "%s:%s" % (run_id, frame):
            raise ValueError("capture identity does not match run/frame")
        if not isinstance(row.get("phase"), str) or "game_time_s" not in row:
            raise ValueError("manifest row lacks phase/time")
        phase = row["phase"]
        if phase == "approved" and frame != "approved":
            raise ValueError("phase/label mismatch for approved capture")
        if phase == "candidate" and frame != "boost_candidate":
            raise ValueError("phase/label mismatch for candidate capture")
        if phase == "warmup" and not re.fullmatch(r"(?:warmup_discard|candidate_discard)_\d+", frame):
            raise ValueError("phase/label mismatch for warmup capture")
        if phase not in ("warmup", "approved", "candidate"):
            raise ValueError("unknown manifest phase")
        target_phase = ("candidate" if frame.startswith("candidate_discard_") or phase == "candidate"
                        else "approved")
        asset = row.get("asset")
        valid_asset = (asset == ASSETS["approved"] if target_phase == "approved" else
                       isinstance(asset, str) and CANDIDATE_ASSET_RE.fullmatch(asset) is not None)
        if not valid_asset:
            label = target_phase + (" warmup" if phase == "warmup" else " target")
            raise ValueError("%s asset identity mismatch" % label)
        if row.get("active") != "True":
            raise ValueError("%s is not active" % (target_phase + " target" if phase != "warmup"
                                                     else target_phase + " warmup"))
        png = row.get("png")
        if png is not None:
            if not isinstance(png, str) or not png:
                raise ValueError("invalid PNG path")
            canonical_png = os.path.normcase(os.path.abspath(os.path.normpath(png)))
            if canonical_png in png_paths:
                raise ValueError("duplicate PNG path across frame captures")
            png_paths.add(canonical_png)
        if verify_png_files:
            png = row.get("png")
            expected_hash = row.get("png_sha256")
            if row.get("png_exists") is not True or not isinstance(png, str) or not Path(png).is_file():
                raise ValueError("PNG file missing for %s" % frame)
            if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                raise ValueError("invalid PNG hash for %s" % frame)
            actual_hash = hashlib.sha256(Path(png).read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError("PNG hash mismatch for %s" % frame)
        try:
            game_time = float(row["game_time_s"])
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid game_time_s") from exc
        if not math.isfinite(game_time):
            raise ValueError("non-finite game_time_s")
        if previous_time is not None and game_time < previous_time:
            raise ValueError("manifest game_time_s time regression")
        previous_time = game_time

    candidate_indexes = [i for i, row in enumerate(records) if row["phase"] == "candidate"]
    approved_indexes = [i for i, row in enumerate(records) if row["phase"] == "approved"]
    if candidate_indexes and (not approved_indexes or approved_indexes[0] > candidate_indexes[0]):
        raise ValueError("candidate capture precedes approved capture")
    approved_index = approved_indexes[0] if approved_indexes else None
    candidate_index = candidate_indexes[0] if candidate_indexes else None
    for index, row in enumerate(records):
        if row["phase"] != "warmup":
            continue
        frame = row["frame"]
        if frame.startswith("warmup_discard_") and approved_index is not None and index > approved_index:
            raise ValueError("warmup phase order places approved warmup after target")
        if frame.startswith("candidate_discard_") and (
                approved_index is None or index < approved_index or
                (candidate_index is not None and index > candidate_index)):
            raise ValueError("warmup phase order does not match candidate target")

    ready_rows = []
    for index, target in enumerate(records):
        if target.get("phase") not in ("approved", "candidate"):
            continue
        warmups = []
        cursor = index - 1
        while cursor >= 0 and records[cursor].get("phase") == "warmup":
            warmups.insert(0, records[cursor])
            cursor -= 1
        if not warmups:
            raise ValueError("capture lacks same-run warmup")
        prefix = "candidate_discard" if target["phase"] == "candidate" else "warmup_discard"
        labels = [row["frame"] for row in warmups]
        expected = ["%s_%d" % (prefix, n) for n in range(1, len(labels) + 1)]
        if labels != expected:
            raise ValueError("non-sequential warmup labels for target capture")
        if len(warmups) > MAX_WARMUP_FRAMES:
            raise ValueError("warmup exceeds 20 frames")
        def finite(row, field):
            try:
                value = float(row[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("invalid warmup %s" % field) from exc
            if not math.isfinite(value):
                raise ValueError("non-finite warmup %s" % field)
            return value

        ready = next((row for row in warmups if finite(row, "mean_gray") >= BRIGHTNESS_FLOOR), None)
        if ready is None:
            raise ValueError("no bright warmup before target capture")
        if any(row.get("asset") != target.get("asset") for row in warmups):
            raise ValueError("warmup asset differs from target capture")
        if any(row.get("active") != target.get("active") for row in warmups):
            raise ValueError("warmup active state differs from target capture")
        elapsed = finite(ready, "game_time_s") - finite(warmups[0], "game_time_s")
        if elapsed < 0.0 or elapsed > MAX_WARMUP_SECONDS:
            raise ValueError("warmup exceeds 4 game seconds")
        target_elapsed = finite(target, "game_time_s") - finite(warmups[0], "game_time_s")
        if target_elapsed < elapsed or target_elapsed > MAX_WARMUP_SECONDS:
            raise ValueError("target capture exceeds 4 game seconds from warmup start")
        if finite(target, "mean_gray") < BRIGHTNESS_FLOOR:
            raise ValueError("target capture below brightness floor")
        ready_rows.append({"phase": target["phase"], "target_frame": target.get("frame"),
                           "ready_frame": ready.get("frame"), "warmup_frames": len(warmups),
                           "ready_elapsed_s": elapsed})
    if not ready_rows:
        raise ValueError("no approved or candidate target frame")
    return ready_rows


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--route", choices=("legacy", "data"), required=True)
    parser.add_argument("--verify-png-files", action="store_true",
                        help="verify each manifest PNG exists and matches its recorded SHA-256")
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    targets = validate_warmup_receipt(rows, args.run, args.route, args.verify_png_files)
    print(json.dumps({"run": args.run, "route": args.route, "manifest_schema": MANIFEST_SCHEMA,
                      "verified_png_files": len(rows) if args.verify_png_files else 0,
                      "png_verification": "sha256" if args.verify_png_files else "not_requested",
                      "targets": targets}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
