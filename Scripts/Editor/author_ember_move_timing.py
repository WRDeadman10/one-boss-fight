"""
Authors URPGANS_BossMoveTiming anim notify state on Ember Warden close montages:
  - AM_Boss01_A1 (A1)
  - AM_Boss01_A2 (A2)
  - AM_Boss01_A3a (A3a)
  - AM_Boss01_A3b (A3b)

Authority: Claude Lead Directives [C-1231], [C-1232], [C-1234] (2026-11-10).
Discipline:
  - Saves ONLY those 4 assets under /Game/OneBossFight/Boss01/Animations/.
  - Refuses /Game/AdvancedARPGCombat/ fail-closed.
  - Pre-mutation safety: verifies 'BossMoveTiming' track contains no unrelated notifies.
  - Idempotent: replaces its own state on dedicated track 'BossMoveTiming' and never duplicates it.
  - Preserves all other notifies untouched (using C-1233 Lead ev_prop/ev_signature helpers).
  - Resolves UClass via unreal.RPGANS_BossMoveTiming.static_class() (fallback load_class).
  - Prints verified readback after reload.
  - Exits non-zero on any failure.
  - Run ONLY by Lead under C-1155 engine lock.
"""

import sys
import unreal

AL = unreal.AnimationLibrary

DEST_ROOT = "/Game/OneBossFight/Boss01/Animations"
FORBIDDEN_ROOT = "/Game/AdvancedARPGCombat"
TRACK_NAME = "BossMoveTiming"

SPECS = {
    f"{DEST_ROOT}/AM_Boss01_A1": {
        "move_id": "A1",
        "commit_time": 0.330,
        "window_start_time": 0.350,
        "window_end_time": 0.500,
        "recovery_end_time": 1.200,
        "track_turn_rate": 360.0,
        "b_branch_stage": False,
        "branch_range": 0.0,
        "branch_cone_degrees": 120.0,
        "b_authored_windup": True,
        "span_start": 0.000,
        "span_dur": 1.200,
    },
    # C-1235 Lead: A2 removed. AM_Boss01_A2 is a 0.600 s single-section clip (the raise only; see
    # Claude/B_C1235_EMBERA2/probe_a2_length.log), not the 3.134 s composite the inventory assumed, so the table times
    # 1.68-3.14 cannot be annotated on it (strict audit: InvalidMontageNotifyTiming.OrderOrBounds).
    f"{DEST_ROOT}/AM_Boss01_A3a": {
        "move_id": "A3a",
        "commit_time": 0.380,
        "window_start_time": 0.400,
        "window_end_time": 0.600,
        "recovery_end_time": 0.800,
        "track_turn_rate": 360.0,
        "b_branch_stage": False,
        "branch_range": 0.0,
        "branch_cone_degrees": 120.0,
        "b_authored_windup": True,
        "span_start": 0.000,
        "span_dur": 0.800,
    },
    f"{DEST_ROOT}/AM_Boss01_A3b": {
        "move_id": "A3b",
        "commit_time": 0.130,
        "window_start_time": 0.150,
        "window_end_time": 0.400,
        "recovery_end_time": 1.3333,
        "track_turn_rate": 360.0,
        "b_branch_stage": True,
        "branch_range": 400.0,  # Corrected live tracker value per C-1231
        "branch_cone_degrees": 120.0,
        "b_authored_windup": True,
        "span_start": 0.000,
        "span_dur": 1.3333,
    },
}


def log(msg):
    unreal.log(f"[AuthorEmberTiming] {msg}")


def log_err(msg):
    unreal.log_error(f"[AuthorEmberTiming] ERROR: {msg}")


def set_prop_robust(obj, name, val):
    """Sets property using exact name, camelCase, or snake_case variants."""
    candidates = [
        name,
        name[0].lower() + name[1:] if len(name) > 1 else name.lower(),
        "".join(
            [
                "_" + c.lower()
                if c.isupper()
                and i > 0
                and (name[i - 1].islower() or (i + 1 < len(name) and name[i + 1].islower()))
                else c.lower()
                for i, c in enumerate(name)
            ]
        ),
    ]
    if name.startswith("b") and len(name) > 1 and name[1].isupper():
        candidates.append("".join(["_" + c.lower() if c.isupper() and i > 0 else c.lower() for i, c in enumerate(name[1:])]))

    for cand in candidates:
        if not cand:
            continue
        try:
            obj.set_editor_property(cand, val)
            return
        except Exception:
            continue
    raise RuntimeError(f"Unable to set property '{name}' on {obj}")


def get_prop_robust(obj, name):
    """Gets property using exact name, camelCase, or snake_case variants."""
    candidates = [
        name,
        name[0].lower() + name[1:] if len(name) > 1 else name.lower(),
        "".join(
            [
                "_" + c.lower()
                if c.isupper()
                and i > 0
                and (name[i - 1].islower() or (i + 1 < len(name) and name[i + 1].islower()))
                else c.lower()
                for i, c in enumerate(name)
            ]
        ),
    ]
    if name.startswith("b") and len(name) > 1 and name[1].isupper():
        candidates.append("".join(["_" + c.lower() if c.isupper() and i > 0 else c.lower() for i, c in enumerate(name[1:])]))

    for cand in candidates:
        if not cand:
            continue
        try:
            return obj.get_editor_property(cand)
        except Exception:
            continue
    raise RuntimeError(f"Unable to get property '{name}' from {obj}")


def validate_target_safety(paths):
    for path in paths:
        if path.startswith(FORBIDDEN_ROOT) or "AdvancedARPGCombat" in path:
            msg = f"REFUSAL: Target path '{path}' touches forbidden pack content '{FORBIDDEN_ROOT}'"
            log_err(msg)
            raise RuntimeError(msg)
        if not path.startswith(DEST_ROOT):
            msg = f"REFUSAL: Target path '{path}' is not within authorized root '{DEST_ROOT}'"
            log_err(msg)
            raise RuntimeError(msg)


def resolve_timing_class():
    """Resolves URPGANS_BossMoveTiming UClass instance using static_class() per C-1232."""
    py_type = getattr(unreal, "RPGANS_BossMoveTiming", None)
    if py_type is not None:
        if hasattr(py_type, "static_class"):
            uclass = py_type.static_class()
            if uclass is not None:
                return uclass
        elif isinstance(py_type, unreal.Class):
            return py_type

    uclass = unreal.load_class(None, "/Script/OneBossFight.RPGANS_BossMoveTiming")
    if uclass is not None:
        return uclass

    raise RuntimeError("Failed to resolve URPGANS_BossMoveTiming UClass.")


def ev_prop(ev, names, default=None):
    """C-1233 Lead fix: FAnimNotifyEvent fields differ in what UE 5.5 exposes to Python (display_time is not exposed).
    Returns the first readable field, else default, so the preservation check never aborts on a hidden field."""
    for name in names:
        try:
            return ev.get_editor_property(name)
        except Exception:
            continue
    return default


def ev_signature(ev, class_name):
    """Preservation signature of a non-timing notify: class + whichever timing fields are readable."""
    t = ev_prop(ev, ("display_time", "trigger_time_offset", "link_value"), None)
    d = ev_prop(ev, ("duration",), None)
    n = ev_prop(ev, ("notify_name",), None)
    return (class_name, str(n), round(float(t), 4) if isinstance(t, (int, float)) else str(t),
            round(float(d), 4) if isinstance(d, (int, float)) else str(d))


def author_all_timings():
    log("Validating target asset path boundaries...")
    validate_target_safety(SPECS.keys())

    notify_class = resolve_timing_class()
    log(f"Resolved timing notify UClass: {notify_class.get_name()} (class: {notify_class})")

    results = {}

    for path, spec in sorted(SPECS.items()):
        log(f"Processing montage: {path} (MoveId: {spec['move_id']})...")
        m = unreal.EditorAssetLibrary.load_asset(path)
        if not m:
            raise RuntimeError(f"Unable to load target montage asset: {path}")

        # Record pre-existing non-timing notifies to verify non-destructive update
        initial_events = AL.get_animation_notify_events(m)
        non_timing_pre = []
        for ev in initial_events:
            st = ev.get_editor_property("notify_state_class")
            no = ev.get_editor_property("notify")
            obj = st if st is not None else no
            if obj and "BossMoveTiming" not in obj.get_class().get_name():
                non_timing_pre.append(ev_signature(ev, obj.get_class().get_name()))

        # Pre-mutation safety check (Codex X-1744 catch):
        # If TRACK_NAME already exists, verify that all events on it are exclusively BossMoveTiming
        existing_tracks = list(AL.get_animation_notify_track_names(m))
        if TRACK_NAME in existing_tracks:
            # C-1235 Lead fix: UE 5.5 Python does not expose FAnimNotifyEvent.track_index, so the per-event track check
            # cannot run. Instead remove the track IN MEMORY, then verify every non-timing notify is still present before
            # anything is saved. On any loss we raise: the commandlet exits without saving, so the asset on disk is untouched.
            log(f"Removing pre-existing '{TRACK_NAME}' track (in memory) for clean idempotent re-authoring...")
            AL.remove_animation_notify_track(m, TRACK_NAME)
            after_remove = []
            for ev in AL.get_animation_notify_events(m):
                st = ev.get_editor_property("notify_state_class")
                no = ev.get_editor_property("notify")
                obj = st if st is not None else no
                if obj is None:
                    continue
                cname = obj.get_class().get_name()
                if "BossMoveTiming" in cname:
                    raise RuntimeError(f"REFUSAL: a BossMoveTiming state outside track '{TRACK_NAME}' remains on {path}; not saving")
                after_remove.append(ev_signature(ev, cname))
            if sorted(after_remove) != sorted(non_timing_pre):
                raise RuntimeError(
                    f"REFUSAL: Pre-existing track '{TRACK_NAME}' contains unrelated notify (removal changed other notifies) on {path}; not saving. "
                    f"Pre: {non_timing_pre}, After: {after_remove}"
                )

        # Add dedicated timing track
        AL.add_animation_notify_track(m, TRACK_NAME)

        # Add notify state event spanning authored active window / montage duration
        inst = AL.add_animation_notify_state_event(
            m, TRACK_NAME, float(spec["span_start"]), float(spec["span_dur"]), notify_class
        )
        if not inst:
            raise RuntimeError(f"Failed to add URPGANS_BossMoveTiming state on {path}")

        # Set properties with exact validated coordinates using robust field setter
        set_prop_robust(inst, "MoveId", unreal.Name(spec["move_id"]))
        set_prop_robust(inst, "CommitTime", float(spec["commit_time"]))
        set_prop_robust(inst, "WindowStartTime", float(spec["window_start_time"]))
        set_prop_robust(inst, "WindowEndTime", float(spec["window_end_time"]))
        set_prop_robust(inst, "RecoveryEndTime", float(spec["recovery_end_time"]))
        set_prop_robust(inst, "TrackTurnRate", float(spec["track_turn_rate"]))
        set_prop_robust(inst, "bBranchStage", bool(spec["b_branch_stage"]))
        set_prop_robust(inst, "BranchRange", float(spec["branch_range"]))
        set_prop_robust(inst, "BranchConeDegrees", float(spec["branch_cone_degrees"]))
        set_prop_robust(inst, "bAuthoredWindup", bool(spec["b_authored_windup"]))

        # Force save asset under lock
        m.modify()
        saved = unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
        if not saved:
            raise RuntimeError(f"Failed to save modified asset: {path}")
        log(f"SUCCESS: Saved {path}")

        # Reload and perform post-save readback audit
        reloaded = unreal.EditorAssetLibrary.load_asset(path)
        found_timing = False
        non_timing_post = []
        timing_summary = ""

        for ev in AL.get_animation_notify_events(reloaded):
            st = ev.get_editor_property("notify_state_class")
            no = ev.get_editor_property("notify")
            obj = st if st is not None else no
            if obj:
                cname = obj.get_class().get_name()
                if "BossMoveTiming" in cname:
                    found_timing = True
                    move_id = get_prop_robust(obj, "MoveId")
                    commit = get_prop_robust(obj, "CommitTime")
                    win_start = get_prop_robust(obj, "WindowStartTime")
                    win_end = get_prop_robust(obj, "WindowEndTime")
                    rec_end = get_prop_robust(obj, "RecoveryEndTime")
                    turn_rate = get_prop_robust(obj, "TrackTurnRate")
                    branch = get_prop_robust(obj, "bBranchStage")
                    b_range = get_prop_robust(obj, "BranchRange")
                    cone = get_prop_robust(obj, "BranchConeDegrees")
                    windup = get_prop_robust(obj, "bAuthoredWindup")
                    timing_summary = (
                        f"MoveId={move_id} "
                        f"Commit={commit:.3f}s "
                        f"Window=[{win_start:.3f}..{win_end:.3f}s] "
                        f"Recovery={rec_end:.3f}s "
                        f"TurnRate={turn_rate} "
                        f"BranchStage={branch} "
                        f"BranchRange={b_range} "
                        f"BranchCone={cone} "
                        f"AuthoredWindup={windup}"
                    )
                else:
                    non_timing_post.append(ev_signature(ev, cname))

        if not found_timing:
            raise RuntimeError(f"Audit failure: BossMoveTiming state missing upon reload of {path}")

        # Verify other notifies were preserved untouched
        if sorted(non_timing_pre) != sorted(non_timing_post):
            raise RuntimeError(
                f"Audit failure: Non-timing notifies modified on {path}! Pre: {non_timing_pre}, Post: {non_timing_post}"
            )

        log(f"READBACK [{path}]: {timing_summary}")
        log(f"PRESERVED [{path}]: {len(non_timing_post)} pre-existing notifies intact: {[p[0] for p in non_timing_post]}")
        results[path] = timing_summary

    log("================ EMBER MOVE TIMING AUTHORING COMPLETE ================")
    for path, summary in results.items():
        log(f"  {path.split('/')[-1]}: {summary}")
    log("=======================================================================")


if __name__ == "__main__":
    try:
        author_all_timings()
    except Exception as ex:
        log_err(f"Fatal exception during authoring: {ex}")
        sys.exit(1)
