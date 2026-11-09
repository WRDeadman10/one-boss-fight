"""
Read-only probe for Ember Warden animation assets under /Game/OneBossFight/Boss01/Animations/.
Prints play_length, num_sections, section names, and notifies for montages and sequences.

Authority: Claude Lead Directives [C-1235], [C-1236] (2026-11-10).
Discipline:
  - Strictly read-only; saves zero assets.
  - Fail-safe: every property read is guarded so an unexposed 5.5 Python property logs 'n/a' rather than aborting.
  - Uses confirmed 5.5 APIs:
    * AnimationLibrary.get_animation_notify_events(asset) for notifies.
    * m.get_num_sections() and m.get_section_name(i) for montage sections.
    * m.get_play_length() / s.get_play_length() for duration.
"""

import unreal

AL = unreal.AnimationLibrary

ANIM_ROOT = "/Game/OneBossFight/Boss01/Animations"

MONTAGES = [
    "AM_Boss01_A1",
    "AM_Boss01_A2",
    "AM_Boss01_A3a",
    "AM_Boss01_A3b",
    "AM_Boss01_DeathLegend",
    "AM_Boss01_ParryRecoil",
]

SEQUENCES = [
    "AN_Boss01_A1_QuickSlash",
    "AN_Boss01_A2_Raise",
    "AN_Boss01_A2_ApexHold",
    "AN_Boss01_A2_Slam",
    "AN_Boss01_A3a_Combo1",
    "AN_Boss01_A3b_Combo2",
    "AN_Boss01_A4_LowSweep",
    "AN_Boss01_A5_JavelinThrow",
    "AN_Boss01_DeathLegend",
    "AN_Boss01_DormantIdle",
    "AN_Boss01_ParryRecoil",
    "AN_Boss01_PhaseRoar",
    "AN_Boss01_StaggerDown",
    "AN_Boss01_StaggerFall",
    "AN_Boss01_Wake",
    "AN_Riposte_Boss_Reaction",
    "AN_Riposte_Player_Front",
]


def log(msg):
    unreal.log(f"[EmberProbe] {msg}")


def safe_call(fn, desc, fallback="n/a"):
    """Executes fn and returns its string result, or 'n/a <desc>' if an exception occurs."""
    try:
        val = fn()
        return str(val) if val is not None else fallback
    except Exception as ex:
        return f"n/a ({desc}: {type(ex).__name__})"


def safe_prop(obj, prop_name, fallback="n/a"):
    """Reads an editor property safely, returning fallback if not exposed in UE 5.5."""
    try:
        val = obj.get_editor_property(prop_name)
        return str(val) if val is not None else fallback
    except Exception:
        return fallback


def probe_montages():
    log("=== EMBER MONTAGES ===")
    for name in MONTAGES:
        path = f"{ANIM_ROOT}/{name}"
        m = unreal.EditorAssetLibrary.load_asset(path)
        if m is None:
            log(f"MISSING {name}")
            continue

        length_str = safe_call(lambda: f"{m.get_play_length():.6f}", "play_length")
        num_sections_val = 0
        try:
            num_sections_val = m.get_num_sections()
            sections_str = str(num_sections_val)
        except Exception:
            sections_str = "n/a (get_num_sections)"

        log(f"MONTAGE {name}: play_length={length_str} sections={sections_str}")

        if isinstance(num_sections_val, int) and num_sections_val > 0:
            for sec_idx in range(num_sections_val):
                sec_name = safe_call(lambda idx=sec_idx: m.get_section_name(idx), f"sec_name[{sec_idx}]")
                sec_start = safe_call(lambda idx=sec_idx: f"{m.get_section_start_time(idx):.4f}", f"sec_start[{sec_idx}]")
                sec_len = safe_call(lambda idx=sec_idx: f"{m.get_section_length(idx):.4f}", f"sec_len[{sec_idx}]")
                log(f"  section[{sec_idx}] '{sec_name}': start={sec_start} len={sec_len}")

        # Rule 2: Use AnimationLibrary.get_animation_notify_events(m)
        notifies = []
        try:
            notifies = list(AL.get_animation_notify_events(m))
            log(f"  notifies count={len(notifies)}")
        except Exception as ex:
            log(f"  notifies count=n/a (get_animation_notify_events: {type(ex).__name__})")

        for i, ev in enumerate(notifies):
            cls_name = "None"
            try:
                st = ev.get_editor_property("notify_state_class")
                no = ev.get_editor_property("notify")
                obj = st if st is not None else no
                if obj is not None:
                    cls_name = obj.get_class().get_name()
            except Exception:
                pass

            time_val = "n/a"
            for tfield in ("trigger_time_offset", "link_value"):
                try:
                    val = ev.get_editor_property(tfield)
                    if val is not None:
                        time_val = f"{float(val):.4f}"
                        break
                except Exception:
                    pass

            dur_val = safe_prop(ev, "duration", fallback="n/a")
            track_val = safe_prop(ev, "track_index", fallback="n/a")
            log(f"    notify[{i}] cls={cls_name} time={time_val} dur={dur_val} track={track_val}")


def probe_sequences():
    log("=== EMBER SEQUENCES ===")
    for name in SEQUENCES:
        path = f"{ANIM_ROOT}/{name}"
        s = unreal.EditorAssetLibrary.load_asset(path)
        if s is None:
            log(f"MISSING {name}")
            continue

        length_str = safe_call(lambda: f"{s.get_play_length():.6f}", "seq_length")
        log(f"SEQUENCE {name}: play_length={length_str}")


def main():
    log("Starting read-only Ember animation asset audit probe (C-1236 guarded)...")
    probe_montages()
    probe_sequences()
    log("Audit probe complete.")


if __name__ == "__main__":
    main()
