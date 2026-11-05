from __future__ import annotations

import ast
import json
import re
import unittest
from unittest import mock
from pathlib import Path

from write_a4_parity_receipt import DRIVERS, read_capture, read_driver_capture
from compare_encounter_parity import _observable_value_matches


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "pie_phase_reset": ("PhaseReset", 14, 420),
    "pie_boss_death": ("BossDeath", 11, 300),
    "pie_boss_death_states": ("DeathStates", 28, 600),
    "pie_victory_lock": ("VictoryLock", 9, 420),
    "pie_transition_rules": ("Transition", 28, 900),
    "pie_a5_heal_punish": ("A5", 31, 420),
    "pie_bleed": ("Bleed", 19, 900),
    "pie_leap_wave": ("Leap", 17, 420),
    "pie_posture_hits": ("Posture", 25, 1100),
    "pie_hyperarmor": ("HyperArmor", 23, 900),
    "pie_close_attacks": ("Close", 55, 420),
    "pie_authored_close_clips": ("AuthoredClose", 14, 600),
    "pie_boss_clips": ("BossClips", 14, 600),
    "pie_attack_rules": ("Rules", 13, 420),
    "pie_boss_look": ("BossLook", 14, 300),
    "pie_riposte": ("Riposte", 5, 420),
    "pie_riposte_exec": ("RipostExec", 15, 700),
    "pie_riposte_lethal": ("RipostLethal", 3, 300),
    "pie_trace_audit": ("Trace", 30, 1500),
    "pie_hit_intake": ("Intake", 36, 600),
    "pie_iframes": ("IFrame", 19, 1500),
    "pie_fog_gate": ("FogGate", 6, 420),
    "pie_remains": ("Remains", 4, 600),
    "pie_soak": ("Soak", 213, 900),
    "pie_legend": ("Legend", 25, 900),
}


def module_assignments(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, (ast.Dict, ast.Constant, ast.List, ast.Tuple))
        and node.targets[0].id in {"ALLOWED"}
    }


class A5ParityDriverRegistrationTests(unittest.TestCase):
    def test_s27_death_reset_x3_route_runs_three_cycles_on_both_arms(self) -> None:
        driver = (ROOT / "Scripts/Editor/pie_player_death_reset.py").read_text(encoding="utf-8")
        pair = (ROOT / "Scripts/RunA5ParityPair.ps1").read_text(encoding="utf-8")
        invocation = (ROOT / "Scripts/RunA5DeathResetX3.ps1").read_text(encoding="utf-8")
        self.assertIn('A5_DEATH_RESET_REPETITIONS', driver)
        self.assertIn('range(_repeat_count)', driver)
        self.assertIn('"%s (cycle %d)"', driver)
        self.assertIn('[ValidateSet(1,3)][int]$DeathResetRepetitions = 1', pair)
        self.assertIn('$env:A5_DEATH_RESET_REPETITIONS = [string]$DeathResetRepetitions', pair)
        self.assertIn("-DeathResetRepetitions 3", invocation)
        self.assertIn("-Driver 'pie_player_death_reset'", invocation)

    def test_every_registered_receipt_prefix_matches_driver_log_helper(self) -> None:
        for driver, (prefix, _) in DRIVERS.items():
            with self.subTest(driver=driver):
                source = (ROOT / "Scripts/Editor" / (driver + ".py")).read_text(encoding="utf-8")
                match = re.search(
                    r'^log\s*=\s*lambda\s+\w+\s*:\s*unreal\.log\("\[([^\]]+)\]\s*"\s*\+',
                    source,
                    re.MULTILINE,
                )
                self.assertIsNotNone(match, f"could not read {driver} log() prefix from source")
                self.assertEqual(prefix, match.group(1))

    def test_driver_prefix_minimum_and_timeout_match_run_drivers(self) -> None:
        runner = module_assignments(ROOT / "Scripts/Editor/run_a5_parity_driver_and_quit.py")["ALLOWED"]
        ps = (ROOT / "Scripts/RunDrivers.ps1").read_text(encoding="utf-8")
        for driver, (prefix, minimum, timeout) in EXPECTED.items():
            with self.subTest(driver=driver):
                match = re.search(r"\@\{ N = '" + re.escape(driver) + r"';\s+K = '([RS])'; Min = (\d+)(?:; T = (\d+))? \}", ps)
                self.assertIsNotNone(match)
                self.assertEqual(int(match.group(2)), minimum)
                self.assertEqual(int(match.group(3) or 420), timeout)
                self.assertEqual(runner[driver], float(timeout))
                self.assertEqual(DRIVERS[driver], (prefix, minimum))

    def test_pair_runner_accepts_driver_and_uses_source_prefix_and_minimum(self) -> None:
        ps = (ROOT / "Scripts/RunA5ParityPair.ps1").read_text(encoding="utf-8")
        for driver, (prefix, minimum, _) in EXPECTED.items():
            with self.subTest(driver=driver):
                self.assertIn("'" + driver + "'", ps)
                self.assertRegex(ps, re.escape(driver) + r"\s*=\s*'" + re.escape(prefix) + r"'")
                self.assertRegex(ps, re.escape(driver) + r"\s*=\s*" + str(minimum) + r"(?:;|\s*\})")

    def test_nightly_runner_covers_all_registered_drivers_and_writes_summary(self) -> None:
        ps = (ROOT / "Scripts/RunA5ParityNightly.ps1").read_text(encoding="utf-8")
        block = re.search(r"\$drivers\s*=\s*@\((.*?)\n\)", ps, re.S)
        self.assertIsNotNone(block)
        drivers = re.findall(r"'([^']+)'", block.group(1))
        self.assertEqual(len(drivers), 31)
        self.assertEqual(set(drivers), set(DRIVERS))
        self.assertIn("RunA5ParityPair.ps1", ps)
        self.assertIn("summary.md", ps)
        self.assertIn("if (-not $Execute)", ps)
        self.assertIn("each calls RunA5ParityPair.ps1", ps)

    def test_pair_harness_routes_a4_through_its_own_fresh_process_runner(self) -> None:
        ps = (ROOT / "Scripts/RunA5ParityPair.ps1").read_text(encoding="utf-8")
        self.assertIn("ValidateSet('pie_a4_low_sweep'", ps)
        self.assertIn("if ($Driver -eq 'pie_a4_low_sweep')", ps)
        self.assertIn("run_a4_parity_and_quit.py", ps)
        self.assertRegex(ps, r"pie_a4_low_sweep\s*=\s*'A4'")
        self.assertRegex(ps, r"pie_a4_low_sweep\s*=\s*14")

    def test_selector_switch_precedes_begin_play_for_each_driver(self) -> None:
        for driver in EXPECTED:
            path = ROOT / "Scripts/Editor" / (driver + ".py")
            source = path.read_text(encoding="utf-8")
            selector = source.index('os.environ.get("H019_ENCOUNTER_DEFINITION", "").strip()')
            apply = source.index('"rpg.EncounterDefinition " + selection', selector)
            begin = source.index("editor_request_begin_play()", apply)
            self.assertLess(selector, apply)
            self.assertLess(apply, begin)

    def test_phase_reset_summary_is_a_receipt_terminal(self) -> None:
        with mock.patch.object(
            Path, "read_text", return_value=(
                '[A5ParityRunner] SNAPSHOT_JSON {}\n'
                '[PhaseReset] PASS one\n'
                '[PhaseReset] FAIL two\n'
                '[PhaseReset] SUMMARY 2 checks, 1 failed [two]\n'
            ),
        ):
            payload = read_driver_capture(Path("synthetic.log"), "pie_phase_reset")
        self.assertEqual(payload["run_facts"]["final_marker"], {"kind": "R", "passed": 1, "total": 2})
        self.assertEqual(payload["run_facts"]["checks"]["minimum"], 14)
        self.assertFalse(payload["run_facts"]["terminal"]["clean"])

    def test_timing_observable_maps_to_assertion_by_name(self) -> None:
        message = "P06 the javelin arrives after the drink animation ends (dodgeable on the heal exit)"
        typed = {"value": 1.42, "comparison": {"type": "timing_seconds", "range_seconds": [1.15, 2.75]}}
        log_text = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            f"[A5] PASS {message}\n"
            f"[A5] TIMING_OBSERVABLES_JSON {json.dumps({message: typed})}\n"
            '[A5] RESULT 31/31 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("synthetic.log"), "pie_a5_heal_punish")
        self.assertEqual(payload["run_facts"]["observables"]["check-0001"],
                         {**typed, "check_status": "PASS", "check_message": message})

        telegraph = (ROOT / "Scripts/Editor/pie_telegraph.py").read_text(encoding="utf-8")
        a3a = "T1 cvar zero keeps the authored A3a windup (0.40 s since the authored clips, B10)"
        self.assertRegex(telegraph, r'record_windup\("T1 cvar zero keeps the authored A3a windup[^\n]+')
        typed_a3a = {"value": 0.426, "comparison": {"type": "timing_seconds", "range_seconds": [0.34, 0.46]}}
        telegraph_log = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            f"[Telegraph] PASS {a3a} windup 0.426\n"
            f"[Telegraph] TIMING_OBSERVABLES_JSON {json.dumps({a3a: typed_a3a})}\n"
            '[Telegraph] RESULT 1/1 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=telegraph_log):
            telegraph_payload = read_driver_capture(Path("synthetic.log"), "pie_telegraph")
        self.assertEqual(telegraph_payload["run_facts"]["observables"]["check-0001"],
                         {**typed_a3a, "check_status": "PASS", "check_message": a3a + " windup 0.426"})

    def test_health_posture_damage_check_values_are_emitted_as_typed_observables(self) -> None:
        message = "P01 hit: health 120.0 -> 72.0, posture 82 (expect 82), damage 48.0"
        log_text = (
            "[A5ParityRunner] SNAPSHOT_JSON {}\n"
            f"[A4] PASS {message}\n"
            "[A4] RESULT 1/1 passed\n"
        )
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("synthetic.log"), "pie_a4_low_sweep")
        observable = payload["run_facts"]["observables"]["gameplay-check-0001"]
        self.assertEqual(observable["value"], {
            "source_check": "check-0001",
            "fields": [
                {"field": "health_before", "value": 120.0},
                {"field": "health_after", "value": 72.0},
                {"field": "posture", "value": 82.0},
                {"field": "damage", "value": 48.0},
            ],
        })
        self.assertEqual(observable["comparison"], {"type": "exact"})
        self.assertEqual(observable["check_message"], message)

    def test_health_current_maximum_and_lethal_transition_keep_distinct_fields(self) -> None:
        log_text = (
            "[A5ParityRunner] SNAPSHOT_JSON {}\n"
            "[RipostLethal] PASS L0 boss health and poise full health 2000/2000 poise 100\n"
            "[RipostLethal] PASS L1 riposte took boss from 60.0 health to zero (health 0.0)\n"
            "[RipostLethal] RESULT 2/2 passed\n"
        )
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("synthetic.log"), "pie_riposte_lethal")
        obs = payload["run_facts"]["observables"]
        self.assertEqual(obs["gameplay-check-0001"]["value"]["fields"], [
            {"field": "health_current", "value": 2000.0},
            {"field": "health_maximum", "value": 2000.0},
        ])
        self.assertEqual(obs["gameplay-check-0002"]["value"]["fields"], [
            {"field": "health_before", "value": 60.0},
            {"field": "health_after", "value": 0.0},
        ])

    def test_typed_gameplay_capture_uses_the_registered_prefix_for_all_31_drivers(self) -> None:
        self.assertEqual(len(DRIVERS), 31)
        for driver, (prefix, _) in DRIVERS.items():
            log_text = (
                "[A5ParityRunner] SNAPSHOT_JSON {}\n"
                f"[{prefix}] PASS sample health 100 -> 90 posture 20 damage 10\n"
                f"[{prefix}] RESULT 1/1 passed\n"
            )
            with self.subTest(driver=driver), mock.patch.object(Path, "read_text", return_value=log_text):
                payload = read_driver_capture(Path("synthetic.log"), driver)
            self.assertIn("gameplay-check-0001", payload["run_facts"]["observables"])

    def test_p06_splits_exact_hit_fields_from_stochastic_world_hit_field(self) -> None:
        message = "P06 a side roll pressed on the heal exit leaves the javelin's line"
        rows = [{"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0, "world_hits": 1}]
        typed = {"value": rows, "comparison": {"type": "exact"}}
        log_text = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            f"[A5] PASS {message} [('side roll at heal+1.30', 0, 0, 1)]\n"
            f"[A5] TIMING_OBSERVABLES_JSON {json.dumps({message: typed})}\n"
            '[A5] RESULT 32/32 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("synthetic.log"), "pie_a5_heal_punish")
        observations = payload["run_facts"]["observables"]
        self.assertEqual(observations["check-0001"], {
            "value": [{"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0}],
            "comparison": {"type": "exact"}, "check_status": "PASS",
            "check_message": message + " [('side roll at heal+1.30', 0, 0, 1)]",
        })
        self.assertEqual(observations["p06-world-hits"]["comparison"]["type"], "stochastic")
        self.assertEqual(observations["p06-world-hits"]["value"]["rows"], rows)
        changed_world = dict(observations["p06-world-hits"], value={
            "scenario_ran": True, "trials": 1,
            "rows": [{"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0, "world_hits": 0}],
        })
        self.assertTrue(_observable_value_matches(observations["p06-world-hits"], changed_world))
        changed_hits = dict(observations["check-0001"], value=[{
            "trial": "side roll at heal+1.30", "hits": 1, "iframe_passes": 0,
        }])
        self.assertFalse(_observable_value_matches(observations["check-0001"], changed_hits))

    def test_closed_p06_log_rows_backfill_split_observables(self) -> None:
        message = "P06 a side roll pressed on the heal exit leaves the javelin's line"
        log_text = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            '[A5] INFO P06 side roll at heal+1.30: hits 0, i-frame pass 0, world 1\n'
            f"[A5] PASS {message} [('side roll at heal+1.30', 0, 0, 1)]\n"
            '[A5] RESULT 32/32 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("closed.log"), "pie_a5_heal_punish")
        observations = payload["run_facts"]["observables"]
        self.assertEqual(observations["check-0001"], {
            "value": [{"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0}],
            "comparison": {"type": "exact"},
            "check_status": "PASS",
            "check_message": message + " [('side roll at heal+1.30', 0, 0, 1)]",
        })
        self.assertEqual(observations["p06-world-hits"]["value"]["rows"], [
            {"trial": "side roll at heal+1.30", "hits": 0, "iframe_passes": 0, "world_hits": 1},
        ])

    def test_only_s9_roll_at_040_is_stochastic_in_a4_capture(self) -> None:
        capture = {
            "snapshot": {}, "run_facts": {"observables": {
                "S9 info roll at 0.40 s": {"hits": 1, "trials": 3, "jumped": 0,
                                            "invulnerable": 2, "scenario_checks": [True, True]},
                "S9 info roll at 0.30 s": {"hits": 1, "trials": 3, "jumped": 0,
                                            "invulnerable": 0, "scenario_checks": [True, True]},
            }}
        }
        log_text = "[A4] PARITY_CAPTURE_JSON " + json.dumps(capture) + "\n"
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_capture(Path("a4.log"))
        obs = payload["run_facts"]["observables"]
        self.assertEqual(obs["S9 info roll at 0.40 s"]["comparison"]["type"], "stochastic")
        self.assertEqual(obs["S9 info roll at 0.40 s"]["value"]["invulnerable"], 2)
        self.assertEqual(obs["S9 info roll at 0.40 s exact fields"], {
            "hits": 1, "jumped": 0, "scenario_checks": [True, True],
        })
        self.assertEqual(obs["S9 info roll at 0.30 s"]["invulnerable"], 0)
        self.assertNotIn("comparison", obs["S9 info roll at 0.30 s"])

    def test_only_c7_and_the_two_r5_checks_emit_stochastic_contracts(self) -> None:
        c7_name = "C7 the close attack hurts a player in front (90 cm): at least 1 of 5 trials (KI-106, target 4)"
        c7_value = {"scenario_ran": True, "hits": 2, "trials": 5}
        c7_comparison = {"type": "stochastic", "scenario_ran_field": "scenario_ran",
                         "threshold": {"left_field": "hits", "op": "gte", "right_value": 1}}
        r5_names = (
            "R5 the boss attacked in the fight (3 tracked attacks)",
            "R5 every tracked attack that reached its commit point committed once (3 attacks, 1 stopped in the windup)",
        )
        r5_values = (
            {"scenario_ran": True, "tracked_attacks": 3},
            {"scenario_ran": True, "tracked_attacks": 3, "commits": 2,
             "stopped_in_windup": 1, "accounted_attacks": 3},
        )
        r5_comparisons = (
            {"type": "stochastic", "scenario_ran_field": "scenario_ran",
             "threshold": {"left_field": "tracked_attacks", "op": "gte", "right_value": 1}},
            {"type": "stochastic", "scenario_ran_field": "scenario_ran",
             "threshold": {"left_field": "accounted_attacks", "op": "gte", "right_field": "tracked_attacks"}},
        )
        c7_log = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            f'[Close] PASS {c7_name} 2 of 5\n'
            f'[Close] TIMING_OBSERVABLES_JSON {json.dumps({c7_name: {"value": c7_value, "comparison": c7_comparison}})}\n'
            '[Close] RESULT 55/55 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=c7_log):
            c7 = read_driver_capture(Path("close.log"), "pie_close_attacks")
        self.assertEqual(c7["run_facts"]["observables"]["check-0001"]["comparison"], c7_comparison)
        r5_checks = [
            f'[Rules] PASS {r5_names[0]}',
            '[Rules] PASS R5 no double launch in the natural fight',
            '[Rules] PASS R5 no vetoed start in the natural fight',
            f'[Rules] PASS {r5_names[1]}',
        ]
        r5_map = {name: {"value": value, "comparison": comparison}
                  for name, value, comparison in zip(r5_names, r5_values, r5_comparisons)}
        r5_log = ('[A5ParityRunner] SNAPSHOT_JSON {}\n' + '\n'.join(r5_checks) + '\n'
                  + f'[Rules] TIMING_OBSERVABLES_JSON {json.dumps(r5_map)}\n'
                  + '[Rules] RESULT 13/13 passed\n')
        with mock.patch.object(Path, "read_text", return_value=r5_log):
            r5 = read_driver_capture(Path("rules.log"), "pie_attack_rules")
        self.assertEqual(r5["run_facts"]["observables"]["check-0001"]["comparison"], r5_comparisons[0])
        self.assertEqual(r5["run_facts"]["observables"]["check-0004"]["comparison"], r5_comparisons[1])

    def test_old_c7_and_r5_logs_backfill_only_the_declared_stochastic_rows(self) -> None:
        c7_name = "C7 the close attack hurts a player in front (90 cm): at least 1 of 5 trials (KI-106, target 4)"
        c7_lines = [f"[Close] INFO C7 trial at 90 cm: {'hit' if i < 2 else 'miss'} (health 100 -> 88)" for i in range(5)]
        c7_log = ('[A5ParityRunner] SNAPSHOT_JSON {}\n' + '\n'.join(c7_lines) + '\n'
                  + f'[Close] PASS {c7_name} 2 of 5\n[Close] RESULT 55/55 passed\n')
        with mock.patch.object(Path, "read_text", return_value=c7_log):
            c7 = read_driver_capture(Path("close-old.log"), "pie_close_attacks")
        c7_observable = c7["run_facts"]["observables"]["check-0001"]
        self.assertEqual(c7_observable["value"], {"scenario_ran": True, "hits": 2, "trials": 5})
        self.assertEqual(c7_observable["comparison"]["type"], "stochastic")

        attack = "R5 the boss attacked in the fight (3 tracked attacks)"
        commits = "R5 every tracked attack that reached its commit point committed once (3 attacks, 1 stopped in the windup) commits 2"
        r5_log = (
            '[A5ParityRunner] SNAPSHOT_JSON {}\n'
            f'[Rules] PASS {attack}\n'
            f'[Rules] PASS {commits}\n'
            '[Rules] RESULT 13/13 passed\n'
        )
        with mock.patch.object(Path, "read_text", return_value=r5_log):
            r5 = read_driver_capture(Path("rules-old.log"), "pie_attack_rules")
        attack_observable = r5["run_facts"]["observables"]["check-0001"]
        commit_observable = r5["run_facts"]["observables"]["check-0002"]
        self.assertEqual(attack_observable["value"]["tracked_attacks"], 3)
        self.assertEqual(commit_observable["value"]["accounted_attacks"], 3)
        self.assertEqual(attack_observable["comparison"]["type"], "stochastic")
        self.assertEqual(commit_observable["comparison"]["type"], "stochastic")

    def test_only_natural_soak_no_damage_rows_use_stochastic_health_check(self) -> None:
        checks = [
            "01 natural no damage after reset (84.0, 84.0)",
            "02 break no damage after reset (84.0, 84.0)",
            "03 roar no damage after reset (84.0, 84.0)",
            "04 player_death no damage after reset (84.0, 84.0)",
            "05 boss_death no damage after reset (84.0, 84.0)",
            "06 natural no damage after reset (120.0, 120.0)",
        ]
        log_text = ('[A5ParityRunner] SNAPSHOT_JSON {}\n'
                    + "\n".join(f"[Soak] PASS {check}" for check in checks)
                    + "\n[Soak] RESULT 213/213 passed\n")
        with mock.patch.object(Path, "read_text", return_value=log_text):
            payload = read_driver_capture(Path("soak.log"), "pie_soak")
        observations = payload["run_facts"]["observables"]
        for index, scenario in enumerate(("natural", "break", "roar", "player_death", "boss_death", "natural"), 1):
            with self.subTest(index=index, scenario=scenario):
                observation = observations[f"check-{index:04d}"]
                if scenario == "natural":
                    self.assertEqual(observation["comparison"]["type"], "stochastic")
                    self.assertEqual(observation["value"]["before"], observation["value"]["after"])
                else:
                    self.assertNotIn("comparison", observation)
        natural_comparison = observations["check-0001"]["comparison"]
        self.assertEqual(natural_comparison["threshold"],
                         {"left_field": "before", "op": "eq", "right_field": "after"})


if __name__ == "__main__":
    unittest.main()
