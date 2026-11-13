#!/usr/bin/env python3
"""Check a Lead PIE log against the C-1278 X26 live acceptance table.

This tool reports observed log evidence only. It does not launch Unreal or
upgrade missing/ambiguous observations into a pass.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

TABLE = Path(__file__).resolve().parents[2] / "Documentation" / "Boss" / "C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md"
S6 = "Move_Sevarog_Ultimate_Swing_120fps_C1277"
S7 = "Move_Sevarog_Subjugation_C1277"
S8 = "Move_Sevarog_Soul_Siphon_C1277"
TICKS = (0.467, 0.667, 0.867, 1.067, 1.267)


def matching(lines, pattern):
    rx = re.compile(pattern)
    return [line for line in lines if rx.search(line)]


def field(line, name):
    match = re.search(r"(?:^|\s)" + re.escape(name) + r"=([^\s]+)", line)
    return match.group(1) if match else None


def number(line, name):
    value = field(line, name)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def outcome_is(line, expected):
    """Accept both concise fixture outcomes and Unreal's scoped enum spelling."""
    value = field(line, "outcome")
    return value == expected or value == "ERPGDamageOutcome::" + expected


def vector(line, name):
    match = re.search(r"(?:^|\s)" + re.escape(name) + r"=\(([-+0-9.eE]+),([-+0-9.eE]+),([-+0-9.eE]+)\)", line)
    if not match:
        return None
    try:
        return tuple(float(value) for value in match.groups())
    except ValueError:
        return None


def engine_vector(line, name):
    match = re.search(r"(?:^|\s)" + re.escape(name) + r"=X=([-+0-9.eE]+) Y=([-+0-9.eE]+) Z=([-+0-9.eE]+)", line)
    if not match:
        return None
    try:
        return tuple(float(value) for value in match.groups())
    except ValueError:
        return None


def result(row, ok, evidence):
    return {"row": row, "status": "PASS" if ok else "FAIL", "evidence": evidence}


def verify(text, s7_case="stationary", s8_case="inside"):
    all_lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in all_lines if "[FrameworkProof]" in line]
    rows = []
    # P1: both phase-two-only cards are refused in Phase 1.
    p1 = [line for line in lines if "refusal" in line and "reason=MoveModel.Phase" in line
          and (("card=" + S6) in line or ("card=" + S8) in line)]
    p1_s6 = any("card=" + S6 in line for line in p1)
    p1_s8 = any("card=" + S8 in line for line in p1)
    transition_lines = matching(lines, r"phase_transition .*from=Phase_1 to=Phase_2")
    first_transition_index = lines.index(transition_lines[0]) if transition_lines else len(lines)
    p1_candidates = [line for line in lines[:first_transition_index]
                     if "candidate" in line and ("card=" + S6 in line or "card=" + S8 in line)]
    p1_starts = [line for line in all_lines if "CARD accepted move=" in line
                 and ("move=" + S6 in line or "move=" + S8 in line)]
    rows.append(result("X26-P1", p1_s6 and p1_s8 and not p1_candidates and not p1_starts, p1 + p1_candidates + p1_starts))

    transitions = transition_lines
    transition_index = lines.index(transitions[0]) if transitions else -1
    candidates = [line for line in lines if "candidate" in line and "card=" in line]
    after_transition = [line for line in candidates if transition_index >= 0 and lines.index(line) > transition_index]
    p2_s6 = any("card=" + S6 in line for line in after_transition)
    p2_s8 = any("card=" + S8 in line for line in after_transition)
    unique_candidates = {field(line, "card") for line in after_transition if field(line, "card")}
    # X26-IMPL-B1 T4: S6 (90-150 cm) and S8 (220-620 cm) bands are disjoint, so honest P2 evidence needs at least
    # two post-transition selector decisions (distinct seq). Any post-transition empty eligible pool fails P2.
    post_decisions = {field(line, "seq") for line in after_transition if field(line, "seq")}
    s6_seqs = {field(line, "seq") for line in after_transition if "card=" + S6 in line}
    s8_seqs = {field(line, "seq") for line in after_transition if "card=" + S8 in line}
    empty_pool = [line for line in lines if transition_index >= 0 and lines.index(line) > transition_index
                  and "autonomous_test_refusal" in line and "reason=NoCandidate" in line]
    rows.append(result("X26-P2", len(transitions) == 1 and p2_s6 and p2_s8 and len(unique_candidates) >= 3
                       and len(post_decisions) >= 2 and bool(s6_seqs) and bool(s8_seqs) and not empty_pool,
                       transitions + after_transition + empty_pool))

    s6_setup = matching(all_lines, r"SETUP .*move=" + re.escape(S6) + r" ")
    s6_request_setup = [line for line in s6_setup if field(line, "stage") == "before_request"]
    s6_initial_setup = [line for line in s6_setup if field(line, "stage") == "before_initialize"]
    # S6 can be the first forced card. In that arm the driver records its setup
    # once before boss initialization and again immediately before the request.
    # The request-stage readback is authoritative; repeated request-stage rows fail.
    s6_setup_shape_ok = len(s6_request_setup) == 1 and len(s6_initial_setup) <= 1 and len(s6_setup) == len(s6_request_setup) + len(s6_initial_setup)
    s6_distance = number(s6_request_setup[0], "actualDistanceCm") if s6_setup_shape_ok else None
    s6_band_ok = (s6_distance is not None and 110.0 <= s6_distance <= 130.0
                  and field(s6_request_setup[0], "inBand") == "1")
    s6_hits = [line for line in matching(lines, r"hit .*key=HitGroup_ScytheBlade ")
               if outcome_is(line, "Accepted")]
    s6_valid = [line for line in s6_hits if math.isclose(number(line, "hpApplied") or -1, 65.0, abs_tol=0.05)]
    rows.append(result("X26-S6", s6_setup_shape_ok and s6_band_ok and len(s6_valid) == 1 and len(s6_hits) == 1, s6_setup + s6_hits))

    release = matching(lines, r"area_effect state=Released .*card=" + re.escape(S7) + r"\b")
    s7_instance = field(release[0], "instance") if len(release) == 1 else None
    s7_events = [line for line in lines if s7_instance and field(line, "instance") == s7_instance]
    resolves = matching(s7_events, r"area_effect state=Resolve ")
    damage = matching(s7_events, r"area_effect_damage ")
    snare_start = matching(s7_events, r"area_effect_snare state=Started ")
    # The current C++ Ended receipt omits instance identity; keep it visible
    # as an uncorrelated cleanup observation instead of inventing a link.
    snare_end = matching(lines, r"area_effect_snare state=Ended ")
    release_ok = (len(release) == 1 and math.isclose(number(release[0], "release") or -1, 0.8, abs_tol=0.01)
                  and math.isclose(number(release[0], "delay") or -1, 0.75, abs_tol=0.01)
                  and math.isclose(number(release[0], "radius") or -1, 225.0, abs_tol=0.1))
    release_time_ok = (release_ok and number(release[0], "cardTime") is not None
                       and 0.8 <= number(release[0], "cardTime") <= 0.9)
    resolve_time_ok = (bool(resolves) and all(number(line, "cardTime") is not None
                        and number(line, "cardTime") >= 1.55 for line in resolves))
    sample = matching(all_lines, r"S7_RELEASE_SAMPLE ")
    sample_player = vector(sample[0], "playerGround") if len(sample) == 1 else None
    sample_boss = vector(sample[0], "bossGround") if len(sample) == 1 else None
    center = engine_vector(release[0], "center") if len(release) == 1 else None
    center_sample_ok = False
    if center and sample_player and sample_boss:
        center_to_player = math.dist(center, sample_player)
        center_to_boss = math.dist(center, sample_boss)
        center_sample_ok = center_to_player <= 10.0 and center_to_boss > 15.0
    resolve_ok = bool(resolves) and all(field(line, "inside") in ("0", "1") for line in resolves)
    resolve_geometry_ok = all(
        None not in (number(line, "distanceCm"), number(line, "radiusCm"), number(line, "targetRadiusCm"))
        and ((field(line, "inside") == "1" and number(line, "distanceCm") <= number(line, "radiusCm") + number(line, "targetRadiusCm") + 0.1)
             or (field(line, "inside") == "0" and number(line, "distanceCm") > number(line, "radiusCm") + number(line, "targetRadiusCm") - 0.1))
        for line in resolves)
    if s7_case == "stationary":
        s7a_ok = (release_time_ok and resolve_ok and resolve_geometry_ok and resolve_time_ok and center_sample_ok
                  and any(field(line, "inside") == "1" for line in resolves))
        s7b_ok = (any(field(line, "inside") == "1" for line in resolves)
                 and any(outcome_is(line, "Accepted") and math.isclose(number(line, "hpApplied") or -1, 35, abs_tol=0.05) for line in damage)
                 and any(field(line, "scale") == "0.55" and field(line, "seconds") == "2.5" for line in snare_start)
                 and any(field(line, "restored") == "1" for line in snare_end))
    else:
        s7a_ok = (release_time_ok and resolve_ok and resolve_geometry_ok and resolve_time_ok and center_sample_ok
                  and any(field(line, "inside") == "0" for line in resolves))
        s7b_ok = (any(field(line, "inside") == "0" for line in resolves)
                 and not damage and not snare_start)
    rows.append(result("X26-S7a", s7a_ok, release + sample + resolves))
    rows.append(result("X26-S7b" if s7_case == "stationary" else "X26-S7-dodge-out",
                       s7b_ok, resolves + damage + snare_start + snare_end))

    channel_start = matching(lines, r"channel state=Started .*card=" + re.escape(S8) + r"\b")
    s8_instance = field(channel_start[0], "instance") if len(channel_start) == 1 else None
    s8_events = [line for line in lines if s8_instance and field(line, "instance") == s8_instance]
    ticks = matching(s8_events, r"channel_tick ")
    channel_end = matching(s8_events, r"channel state=Ended .*ticks=5\b")
    tick_times = [number(line, "cardTime") for line in ticks]
    cadence_ok = (len(channel_start) == 1 and len(ticks) == 5 and len(channel_end) == 1
                  and field(channel_start[0], "trackFacing") == "0"
                  and all(value is not None and math.isclose(value, expected, abs_tol=0.01)
                          for value, expected in zip(tick_times, TICKS)))
    if s8_case == "inside":
        tick_ok = cadence_ok and all(field(line, "inCone") == "1" and outcome_is(line, "Accepted")
                                     and math.isclose(number(line, "hpApplied") or -1, 8, abs_tol=0.05)
                                     for line in ticks)
        observed_heals = [number(line, "bossHealed") for line in ticks]
        heal_ok = (all(value is not None and 0.0 <= value <= 4.05 for value in observed_heals)
                   and sum(observed_heals) <= 20.05)
    else:
        first_miss = next((index for index, line in enumerate(ticks) if outcome_is(line, "Miss")), len(ticks))
        tick_ok = (cadence_ok and 0 < first_miss < len(ticks)
                   and all(outcome_is(line, "Accepted") and field(line, "inCone") == "1" for line in ticks[:first_miss])
                   and all(outcome_is(line, "Miss") and field(line, "inCone") == "0"
                           and (number(line, "dot") is not None and number(line, "dot") < math.cos(math.radians(45.0)))
                           and math.isclose(number(line, "hpApplied") or 0, 0, abs_tol=0.001)
                           and math.isclose(number(line, "bossHealed") or 0, 0, abs_tol=0.001)
                           for line in ticks[first_miss:]))
        heal_ok = True
    rows.append(result("X26-S8a", cadence_ok, channel_start + ticks + channel_end))
    rows.append(result("X26-S8b" if s8_case == "inside" else "X26-S8-cone-escape",
                       tick_ok and heal_ok, ticks))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="Lead PIE log containing FrameworkProof lines")
    parser.add_argument("--s7-case", choices=("stationary", "dodge-out"), default="stationary")
    parser.add_argument("--s8-case", choices=("inside", "cone-escape"), default="inside")
    parser.add_argument("--receipt", type=Path, help="optional JSON receipt output")
    args = parser.parse_args(argv)
    if not args.log.is_file() or not TABLE.is_file():
        parser.error("log and C1278 acceptance table must both exist")
    rows = verify(args.log.read_text(encoding="utf-8", errors="replace"), args.s7_case, args.s8_case)
    payload = {"table": str(TABLE), "log": str(args.log), "s7_case": args.s7_case,
               "s8_case": args.s8_case, "rows": rows,
               "result": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL"}
    for row in rows:
        print("%s %s" % (row["status"], row["row"]))
        for line in row["evidence"]:
            print("  " + line)
    if args.receipt:
        args.receipt.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("RESULT " + payload["result"])
    return 0 if payload["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
