"""
Read-only probe for Ember Warden animation assets under /Game/OneBossFight/Boss01/Animations/.
Prints play_length, num_sections, section names, and notifies for montages and sequences.

Authority: Claude Lead Directive [C-1235] (2026-11-10).
Discipline:
  - Strictly read-only; saves zero assets.
  - Can be run headless:
    UnrealEditor.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/probe_ember_montages.py -unattended -nosound -nosplash -nullrhi
"""

import unreal

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


def probe_montages():
    log("=== EMBER MONTAGES ===")
    for name in MONTAGES:
        path = f"{ANIM_ROOT}/{name}"
        m = unreal.EditorAssetLibrary.load_asset(path)
        if m is None:
            log(f"MISSING {name}")
            continue

        length = m.get_play_length()
        num_sections = m.get_num_sections()
        log(f"MONTAGE {name}: play_length={length:.6f} sections={num_sections}")

        for sec_idx in range(num_sections):
            sec_name = m.get_section_name(sec_idx)
            sec_start = m.get_section_start_time(sec_idx)
            sec_len = m.get_section_length(sec_idx)
            log(f"  section[{sec_idx}] '{sec_name}': start={sec_start:.4f} len={sec_len:.4f}")

        # List all notifies
        notifies = m.get_editor_property("notifies")
        log(f"  notifies count={len(notifies) if notifies else 0}")
        if notifies:
            for i, ev in enumerate(notifies):
                cls = ev.get_editor_property("notify_state_class") or ev.get_editor_property("notify")
                cls_name = cls.get_name() if cls else "None"
                # Display / trigger time
                time_val = None
                for tprop in ("link_value", "trigger_time_offset"):
                    try:
                        time_val = ev.get_editor_property(tprop)
                        break
                    except Exception:
                        pass
                dur_val = None
                try:
                    dur_val = ev.get_editor_property("duration")
                except Exception:
                    pass
                log(f"    notify[{i}] cls={cls_name} time={time_val} dur={dur_val}")


def probe_sequences():
    log("=== EMBER SEQUENCES ===")
    for name in SEQUENCES:
        path = f"{ANIM_ROOT}/{name}"
        s = unreal.EditorAssetLibrary.load_asset(path)
        if s is None:
            log(f"MISSING {name}")
            continue

        try:
            length = s.get_play_length()
            log(f"SEQUENCE {name}: play_length={length:.6f}")
        except Exception as ex:
            log(f"SEQUENCE {name}: error reading length ({ex})")


def main():
    log("Starting read-only Ember animation asset audit probe...")
    probe_montages()
    probe_sequences()
    log("Audit probe complete.")


if __name__ == "__main__":
    main()
