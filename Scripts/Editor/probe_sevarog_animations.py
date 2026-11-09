"""
Read-only probe for Sevarog animation assets under /Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/.
Prints play_length, num_sections, section names, notify classes, and root motion flags for montages and sequences.

Authority: Claude Lead Directives [C-1236], [C-1238] (2026-11-10).
Discipline:
  - Strictly read-only; saves zero assets.
  - Fail-safe: every property read is guarded so an unexposed 5.5 Python property logs 'n/a' rather than aborting.
  - Sourced from confirmed 5.5 APIs:
    * AnimationLibrary.get_animation_notify_events(asset) for notifies.
    * m.get_num_sections() and m.get_section_name(i) for montage sections.
    * m.get_play_length() / s.get_play_length() for duration.
    * Guarded 'enable_root_motion' read for root motion extraction.
"""

import unreal

AL = unreal.AnimationLibrary

SEVAROG_ROOT = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations"

# Category A: Existing Montages
MONTAGES = [
    "Swing1_Medium_Montage",
    "Swing2_Medium_Montage",
    "LevelStart_Montage",
]

# Category B: Primary Melee Attack Sequences (Core Swings & Variants)
MELEE_SEQUENCES = [
    "Swing1_Medium",
    "Swing1_Slow",
    "Swing1_FAST_v2",
    "Swing1_Return2Idle",
    "Swing1_120fps",
    "Swing1_FAST_120fps",
    "Swing1_Slow_120fps",
    "Swing1Start_120fps",
    "Swing1_Return2Idle_120fps",
    "Swing2_Medium",
    "Swing2_Slow",
    "Swing2_FAST_v2",
    "Swing2_Return2Idle",
    "Swing2_120fps",
    "Swing2_FAST_120fps",
    "Swing2_Slow_120fps",
    "Swing2_Return2Idle_120fps",
    "Swing3_Medium",
    "Swing3_Slow",
    "Swing3_FAST_v2",
    "Swing3_Return2Idle",
    "Swing3_120fps",
    "Swing3_FAST_120fps",
    "Swing3_Slow_120fps",
    "Swing3_Return2Idle_120fps",
    "Swing3_Return2Idle_Medium",
    "Swing_In_Air",
    "Swing_In_Air_120fps",
]

# Category C: Signature Abilities & Specials
ABILITY_SEQUENCES = [
    "Ultimate_Swing_120fps",
    "Ultimate_Targeting",
    "Ultimate_Targeting_Loop",
    "Ultimate_Targeting_pose",
    "Subjugation",
    "Soul_Siphon",
    "Soul_Siphon_Targeting",
    "Soul_Siphon_Targeting_Loop",
    "Speedburst",
    "Cast",
    "Bound",
]

# Category D: Reactions, Staggers & Defeat
REACTION_SEQUENCES = [
    "Hitreact_Front",
    "Hitreact_Back",
    "Hitreact_Left",
    "Hitreact_Right",
    "Stun_Start",
    "Stun_Loop",
    "Stun_End",
    "Knock_back",
    "Knock_back_bwd",
    "Death_front",
]

# Category E: Soul Armor Progression
STAGE_SEQUENCES = [
    "Stage_1",
    "Stage_2",
    "Stage_3",
    "Stage_4",
]


def log(msg):
    unreal.log(f"[SevarogProbe] {msg}")


def safe_call(fn, desc, fallback="n/a"):
    """Executes fn and returns its string result, or 'n/a <desc>' if an exception occurs."""
    try:
        val = fn()
        return str(val) if val is not None else fallback
    except Exception as ex:
        return f"n/a ({desc}: {type(ex).__name__})"


def safe_prop(obj, prop_names, fallback="n/a"):
    """Reads the first matching editor property from prop_names safely, returning fallback if none exist."""
    for prop_name in prop_names:
        try:
            val = obj.get_editor_property(prop_name)
            if val is not None:
                return str(val)
        except Exception:
            continue
    return fallback


def probe_notifies(asset):
    """Safely extracts notify class names or notify_name using AnimationLibrary.get_animation_notify_events."""
    try:
        events = list(AL.get_animation_notify_events(asset))
        if not events:
            return "0 notifies"

        classes = []
        for ev in events:
            cls_name = "Unknown"
            try:
                st = ev.get_editor_property("notify_state_class")
                no = ev.get_editor_property("notify")
                obj = st if st is not None else no
                if obj is not None:
                    cls_name = obj.get_class().get_name()
                else:
                    nname = safe_prop(ev, ("notify_name", "event_name"))
                    if nname != "n/a" and nname:
                        cls_name = f"NamedNotify({nname})"
            except Exception:
                pass
            if cls_name == "Unknown":
                nname = safe_prop(ev, ("notify_name", "event_name"))
                if nname != "n/a" and nname:
                    cls_name = f"NamedNotify({nname})"
            classes.append(cls_name)
        return f"{len(events)} notifies: [{', '.join(classes)}]"
    except Exception as ex:
        return f"notifies=n/a ({type(ex).__name__})"


def probe_root_motion(asset):
    """Guarded query for root motion flag."""
    return safe_prop(asset, ("enable_root_motion", "b_enable_root_motion", "bEnableRootMotion"), fallback="n/a")


def probe_montages():
    log("=== SEVAROG CATEGORY A: MONTAGES ===")
    for name in MONTAGES:
        path = f"{SEVAROG_ROOT}/{name}"
        m = unreal.EditorAssetLibrary.load_asset(path)
        if m is None:
            log(f"MISSING {name}")
            continue

        length_str = safe_call(lambda: f"{m.get_play_length():.6f}", "play_length")
        sections_count = 0
        try:
            sections_count = m.get_num_sections()
            sections_str = str(sections_count)
        except Exception:
            sections_str = "n/a (get_num_sections)"

        rm_str = probe_root_motion(m)
        notifies_str = probe_notifies(m)

        log(f"MONTAGE {name}: play_length={length_str} sections={sections_str} root_motion={rm_str} {notifies_str}")

        if isinstance(sections_count, int) and sections_count > 0:
            for sec_idx in range(sections_count):
                sec_name = safe_call(lambda idx=sec_idx: m.get_section_name(idx), f"sec_name[{sec_idx}]")
                log(f"  section[{sec_idx}] '{sec_name}'")


def probe_sequence_group(group_label, sequences):
    log(f"=== SEVAROG {group_label} ===")
    for name in sequences:
        path = f"{SEVAROG_ROOT}/{name}"
        s = unreal.EditorAssetLibrary.load_asset(path)
        if s is None:
            log(f"MISSING {name}")
            continue

        length_str = safe_call(lambda: f"{s.get_play_length():.6f}", "seq_length")
        rm_str = probe_root_motion(s)
        notifies_str = probe_notifies(s)

        log(f"SEQUENCE {name}: play_length={length_str} root_motion={rm_str} {notifies_str}")


def main():
    log("Starting read-only Sevarog animation asset audit probe (C-1238 guarded)...")
    probe_montages()
    probe_sequence_group("CATEGORY B: MELEE SEQUENCES", MELEE_SEQUENCES)
    probe_sequence_group("CATEGORY C: SIGNATURE ABILITIES", ABILITY_SEQUENCES)
    probe_sequence_group("CATEGORY D: REACTIONS & STAGGERS", REACTION_SEQUENCES)
    probe_sequence_group("CATEGORY E: SOUL ARMOR PROGRESSION", STAGE_SEQUENCES)
    log("Sevarog audit probe complete.")


if __name__ == "__main__":
    main()
