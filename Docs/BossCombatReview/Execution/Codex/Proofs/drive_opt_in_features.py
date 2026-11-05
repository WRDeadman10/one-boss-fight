"""Plan or run one/several opt-in proof cases through Claude's F4 PIE wrapper.

Default is plan-only. Use --case NAME --execute to run one isolated case;
Codex does not execute this driver. Feature reports check telemetry presence
only; numeric/gameplay relations remain manual. Fatigue needs a calibrated
target-shift schedule derived from the selected card's active/recovery timings.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN_PIE = ROOT / "Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1"
PROOF_REPORT = ROOT / "Scripts/Tools/proof_report.py"
BASE = "/Game/OneBossFight/FrameworkProof"
HERE = Path(__file__).resolve().parent


def case(name, map_name, console="", overlay="", expected=()):
    return {"name": name, "map": BASE + "/" + map_name,
            "console": console, "overlay": overlay, "expected": expected}


CASES = [
    case("warp-linear-control", "L_SevarogFrameworkProofANM006"),
    case("warp-ease", "L_SevarogFrameworkProofWarpEaseR1", expected=("WARP_EASE_EXPECTED.md",)),
    case("strafe-stuck", "L_SevarogFrameworkProofStrafeEdgeR3c", expected=("STRAFE_STUCK_EXPECTED.md",)),
    case("yaw-control", "L_SevarogFrameworkProofF5", "rpg.BossProofYawProbe 5"),
    case("yaw-hysteresis", "L_SevarogFrameworkProofYawConeR6A8", "rpg.BossProofYawProbe 5", expected=("YAW_CONE_EXPECTED.md",)),
    case("guard-chip", "L_SevarogFrameworkProofGuardChipR7",
         "rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 6", expected=("GUARD_CHIP_EXPECTED.md",)),
    case("parry-recovery", "L_SevarogFrameworkProofParryRecoveryR9",
         "rpg.BossProofPlayerGuard 4;rpg.BossProofPlayerGuardSeconds 6", expected=("PARRY_RECOVERY_EXPECTED.md",)),
    case("telegraph-scale", "L_SevarogFrameworkProofTelegraphScaleR11", expected=("TELEGRAPH_SCALE_EXPECTED.md",)),
    case("aggro-close", "L_SevarogFrameworkProofAggroSwitchR13",
         "rpg.BossProofPlayerDodge 0.2,0.7,1.2", expected=("AGGRO_SWITCH_EXPECTED.md",)),
    case("aggro-far", "L_SevarogFrameworkProofAggroSwitchR13",
         "rpg.BossProofTargetShift 0.1:0,800,0;rpg.BossProofPlayerDodge 0.2,0.7,1.2", expected=("AGGRO_SWITCH_EXPECTED.md",)),
    case("fatigue", "L_SevarogFrameworkProofFatigueR15A6", expected=("FATIGUE_EXPECTED.md",)),
    case("stamina-and-overlay", "L_SevarogFrameworkProofF5",
         "rpg.BossProofPlayerGuard 4;rpg.BossProofPlayerGuardSeconds 6", "2",
         ("PARRY_STAMINA_EXPECTED.md", "OVERLAY_PARRY_EXPECTED.md")),
]


def command_for(item, fatigue_console=""):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(RUN_PIE), "-Map", item["map"],
           "-OutDir", str(ROOT / "Saved/Proofs/OptIn" / item["name"] / run_id),
           "-Task", "QUEUE_200_C/" + item["name"]]
    console = fatigue_console if item["name"] == "fatigue" else item["console"]
    if console:
        cmd += ["-Console", console]
    if item["overlay"]:
        cmd += ["-Overlay", item["overlay"]]
    return cmd


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="run each independent proof map using run_pie.ps1")
    parser.add_argument("--case", choices=[item["name"] for item in CASES],
                        help="plan/run one named case; default is all cases")
    parser.add_argument("--fatigue-console", default="",
                        help="rpg.BossProofTargetShift schedule for fatigue whiff calibration")
    args = parser.parse_args()
    if not RUN_PIE.is_file():
        raise SystemExit("F4 wrapper not found: " + str(RUN_PIE))
    selected = [item for item in CASES if args.case is None or item["name"] == args.case]
    if args.execute and any(item["name"] == "fatigue" for item in selected) and not args.fatigue_console:
        raise SystemExit("fatigue execution needs --fatigue-console after card-timing calibration")
    overall = 0
    for i, item in enumerate(selected, 1):
        if item["name"] == "fatigue" and not args.fatigue_console:
            print("%02d %-24s INCOMPLETE: calibrate rpg.BossProofTargetShift from selected card timing first" % (i, item["name"]))
            overall = max(overall, 2)
            continue
        cmd = command_for(item, args.fatigue_console)
        print("%02d %-24s PLAN: %s" % (i, item["name"], subprocess.list2cmdline(cmd)))
        if args.execute:
            result = subprocess.run(cmd, cwd=str(ROOT), check=False)
            if result.returncode != 0:
                print("%02d %-24s FAIL: PIE wrapper exit=%d" % (i, item["name"], result.returncode))
                return result.returncode or 1
            print("%02d %-24s PIE: PASS (wrapper exit=0; feature criteria still require report/review)" % (i, item["name"]))
            log = Path(cmd[cmd.index("-OutDir") + 1]) / "editor_raw.log"
            if not log.is_file():
                print("%02d %-24s FAIL: missing log %s" % (i, item["name"], log))
                return 1
            if not item["expected"]:
                print("%02d %-24s RESULT: MANUAL (no case-specific expected sheet)" % (i, item["name"]))
                overall = max(overall, 2)
            for expected_name in item["expected"]:
                expected = HERE / expected_name
                report = subprocess.run([sys.executable, str(PROOF_REPORT), str(log), str(expected)],
                                        cwd=str(ROOT), check=False)
                label = "PASS" if report.returncode == 0 else "FAIL" if report.returncode == 1 else "INCOMPLETE"
                print("%02d %-24s %s: telemetry report (%s)" % (i, item["name"], label, expected.name))
                overall = max(overall, report.returncode)
    if args.execute:
        print("RESULT: %s" % ("FAIL" if overall == 1 else "INCOMPLETE" if overall == 2 else "PASS"))
    return overall


if __name__ == "__main__":
    sys.exit(main())
