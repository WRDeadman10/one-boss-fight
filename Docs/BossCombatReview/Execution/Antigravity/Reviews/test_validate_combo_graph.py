#!/usr/bin/env python3
"""
test_validate_combo_graph.py
============================
Comprehensive test suite for Boss Combo Graph DAG validation and step simulator.
Runs 100% offline with zero engine dependency.

Verifies:
- All validation tokens in exact precedence order:
  Combo.Empty, Combo.MaxDepth, Combo.Root, Combo.DuplicateNode,
  Combo.UnknownNode, Combo.EdgeDomain, Combo.Cycle, Combo.Depth.
- Step simulator semantics:
  COM-003: Fresh context per decision gate.
  COM-004: Outcome-based branching (Hit/Whiff/Guarded/Parried).
  COM-005: Single-use gate (duplicate GateId ignored without touching state).
  COM-006: MaxDepth bounding and terminal node finishing.
  COM-007: Default recovery when no edge matches.
- 100% line-by-line parity with Claude's C++ tests in Source/OneBossFight/Tests/RPGBossComboTests.cpp
  (FBossComboValidate 17 assertions, FBossComboStep all scenarios).
"""

import sys
import unittest
from pathlib import Path
import copy
from typing import Dict, Any, List

cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from validate_combo_graph import (
    validate_combo_graph,
    step_combo,
    longest_path,
    ComboState,
    ComboGate,
    StepResult
)


def make_valid_3node_graph() -> Dict[str, Any]:
    """Produces a minimal valid 3-node linear chain (Root -> N1 -> N2)."""
    return {
        "Root": "Node_Root",
        "MaxDepth": 3,
        "Nodes": [
            {
                "Id": "Node_Root",
                "MoveId": "Move_Swing1",
                "Edges": [
                    {
                        "ToNode": "Node_FollowUp",
                        "MinRangeCm": 50.0,
                        "MaxRangeCm": 250.0,
                        "MaxAbsYawDegrees": 90.0,
                        "Outcome": "AnyOutcome"
                    }
                ]
            },
            {
                "Id": "Node_FollowUp",
                "MoveId": "Move_Swing2",
                "Edges": [
                    {
                        "ToNode": "Node_Finisher",
                        "MinRangeCm": 50.0,
                        "MaxRangeCm": 200.0,
                        "MaxAbsYawDegrees": 60.0,
                        "Outcome": "Hit"
                    }
                ]
            },
            {
                "Id": "Node_Finisher",
                "MoveId": "Move_HeavySlam",
                "Edges": []  # Terminal node
            }
        ]
    }


def claude_valid_fixture() -> Dict[str, Any]:
    """
    Exact replica of BossComboFixture::Valid() in RPGBossComboTests.cpp:14-21.
    A (root): Hit within 0..250 cm and 60 deg -> B; Whiff -> C; Guarded -> D.
    B: anything within 0..300 cm -> E.
    C, D, E terminal. Longest path A-B-E = 3 nodes.
    """
    def edge(to: str, min_r: float, max_r: float, yaw: float, any_out: bool, out: str = "Hit"):
        return {
            "To": to,
            "ToNode": to,
            "MinRangeCm": min_r,
            "MaxRangeCm": max_r,
            "MaxAbsYawDegrees": yaw,
            "bAnyOutcome": any_out,
            "Outcome": out
        }

    def node(nid: str, move: str, edges: List[Dict[str, Any]] = None):
        return {
            "Id": nid,
            "MoveId": move,
            "Edges": edges if edges is not None else []
        }

    return {
        "Root": "A",
        "MaxDepth": 3,
        "Nodes": [
            node("A", "MoveA", [
                edge("B", 0.0, 250.0, 60.0, False, "Hit"),
                edge("C", 0.0, 1.0e6, 180.0, False, "Whiff"),
                edge("D", 0.0, 1.0e6, 180.0, False, "Guarded")
            ]),
            node("B", "MoveB", [
                edge("E", 0.0, 300.0, 180.0, True, "Hit")
            ]),
            node("C", "MoveC"),
            node("D", "MoveD"),
            node("E", "MoveE")
        ]
    }


class TestClaudeFixtureParity(unittest.TestCase):
    """
    1-to-1 Line-by-Line Parity with RPGBossComboTests.cpp.
    Matches all 17 assertions in FBossComboValidate and all branches in FBossComboStep.
    """

    def test_cpp_validate_17_assertions_line_by_line(self):
        """Line-by-line mirror of FBossComboValidate::RunTest lines 28-45."""
        def token(edit_fn) -> str:
            g = copy.deepcopy(claude_valid_fixture())
            edit_fn(g)
            res = validate_combo_graph(g)
            return res[0] if res else ""

        # Line 28: TestTrue(TEXT("valid graph"),Validate(Valid()).IsEmpty());
        self.assertEqual(validate_combo_graph(claude_valid_fixture()), [])

        # Line 29: TestEqual(TEXT("longest path in nodes"),LongestPath(Valid()),3);
        self.assertEqual(longest_path(claude_valid_fixture()), 3)

        # Line 31: TestEqual(TEXT("no nodes"),Validate(FComboGraph()),FString(TEXT("Combo.Empty")));
        empty_g = {"Root": "", "MaxDepth": 3, "Nodes": []}
        self.assertEqual(validate_combo_graph(empty_g), ["Combo.Empty"])

        # Line 32: TestEqual(TEXT("root missing"),Token([](FComboGraph& G){G.Root=TEXT("Zed");}),FString(TEXT("Combo.Root")));
        def edit_root_missing(g): g["Root"] = "Zed"
        self.assertEqual(token(edit_root_missing), "Combo.Root")

        # Line 33: TestEqual(TEXT("duplicate node"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("C"),TEXT("Other")));}),FString(TEXT("Combo.DuplicateNode")));
        def edit_dup_node(g): g["Nodes"].append({"Id": "C", "MoveId": "Other", "Edges": []})
        self.assertEqual(token(edit_dup_node), "Combo.DuplicateNode")

        # Line 34: TestEqual(TEXT("unknown edge target"),Token([](FComboGraph& G){G.Nodes[1].Edges[0].To=TEXT("Zed");}),FString(TEXT("Combo.UnknownNode")));
        def edit_unknown_target(g): g["Nodes"][1]["Edges"][0]["ToNode"] = "Zed"; g["Nodes"][1]["Edges"][0]["To"] = "Zed"
        self.assertEqual(token(edit_unknown_target), "Combo.UnknownNode")

        # Line 35: TestEqual(TEXT("node without a move"),Token([](FComboGraph& G){G.Nodes[2].MoveId=NAME_None;}),FString(TEXT("Combo.UnknownNode")));
        def edit_no_move(g): g["Nodes"][2]["MoveId"] = ""
        self.assertEqual(token(edit_no_move), "Combo.UnknownNode")

        # Line 36: TestEqual(TEXT("range band reversed"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MinRangeCm=300.f;}),FString(TEXT("Combo.EdgeDomain")));
        def edit_range_reversed(g): g["Nodes"][0]["Edges"][0]["MinRangeCm"] = 300.0
        self.assertEqual(token(edit_range_reversed), "Combo.EdgeDomain")

        # Line 37: TestEqual(TEXT("yaw above 180"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MaxAbsYawDegrees=181.f;}),FString(TEXT("Combo.EdgeDomain")));
        def edit_yaw_above_180(g): g["Nodes"][0]["Edges"][0]["MaxAbsYawDegrees"] = 181.0
        self.assertEqual(token(edit_yaw_above_180), "Combo.EdgeDomain")

        # Line 38: TestEqual(TEXT("NaN range"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MaxRangeCm=std::numeric_limits<float>::quiet_NaN();}),FString(TEXT("Combo.EdgeDomain")));
        def edit_nan_range(g): g["Nodes"][0]["Edges"][0]["MaxRangeCm"] = float("nan")
        self.assertEqual(token(edit_nan_range), "Combo.EdgeDomain")

        # Line 39: TestEqual(TEXT("cycle E -> A"),Token([](FComboGraph& G){G.Nodes[4].Edges.Add(Edge(TEXT("A"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Cycle")));
        def edit_cycle_e_a(g):
            g["Nodes"][4]["Edges"].append({
                "To": "A", "ToNode": "A", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 180.0, "bAnyOutcome": True, "Outcome": "Hit"
            })
        self.assertEqual(token(edit_cycle_e_a), "Combo.Cycle")

        # Line 40: TestEqual(TEXT("self loop"),Token([](FComboGraph& G){G.Nodes[2].Edges.Add(Edge(TEXT("C"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Cycle")));
        def edit_self_loop(g):
            g["Nodes"][2]["Edges"].append({
                "To": "C", "ToNode": "C", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 180.0, "bAnyOutcome": True, "Outcome": "Hit"
            })
        self.assertEqual(token(edit_self_loop), "Combo.Cycle")

        # Line 41: TestEqual(TEXT("four nodes deep with max depth 3"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("F"),TEXT("MoveF")));G.Nodes[4].Edges.Add(Edge(TEXT("F"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Depth")));
        def edit_four_nodes_deep(g):
            g["Nodes"].append({"Id": "F", "MoveId": "MoveF", "Edges": []})
            g["Nodes"][4]["Edges"].append({
                "To": "F", "ToNode": "F", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 180.0, "bAnyOutcome": True, "Outcome": "Hit"
            })
        self.assertEqual(token(edit_four_nodes_deep), "Combo.Depth")

        # Line 42: TestEqual(TEXT("max depth 4 is outside 1..3"),Token([](FComboGraph& G){G.MaxDepth=4;}),FString(TEXT("Combo.MaxDepth")));
        def edit_max_depth_4(g): g["MaxDepth"] = 4
        self.assertEqual(token(edit_max_depth_4), "Combo.MaxDepth")

        # Line 43: TestEqual(TEXT("max depth 0 is outside 1..3"),Token([](FComboGraph& G){G.MaxDepth=0;}),FString(TEXT("Combo.MaxDepth")));
        def edit_max_depth_0(g): g["MaxDepth"] = 0
        self.assertEqual(token(edit_max_depth_0), "Combo.MaxDepth")

        # Line 44: TestTrue(TEXT("max depth 3 with three nodes is exactly enough"),Token([](FComboGraph& G){G.MaxDepth=3;}).IsEmpty());
        def edit_max_depth_3(g): g["MaxDepth"] = 3
        self.assertEqual(token(edit_max_depth_3), "")

        # Line 45: TestEqual(TEXT("max depth 2 is too small for a three node path"),Token([](FComboGraph& G){G.MaxDepth=2;}),FString(TEXT("Combo.Depth")));
        def edit_max_depth_2(g): g["MaxDepth"] = 2
        self.assertEqual(token(edit_max_depth_2), "Combo.Depth")

    def test_cpp_step_scenarios_line_by_line(self):
        """Line-by-line mirror of FBossComboStep::RunTest lines 53-94."""
        g = claude_valid_fixture()

        # COM-001/006: walk longest path A -> B -> E, then terminal finishes (lines 53-59)
        s = ComboState(node="A", depth=1)
        r = step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=1))
        self.assertEqual(r.action, "Continue")
        self.assertEqual(r.next_node, "B")
        self.assertEqual(s.depth, 2)

        r = step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=170.0, outcome="Hit", gate_id=2))
        self.assertEqual(r.action, "Continue")
        self.assertEqual(r.next_node, "E")
        self.assertEqual(s.depth, 3)

        r = step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=3))
        self.assertEqual(r.action, "Finished")

        # COM-005: a gate id is consumed once; duplicate ignored and state untouched (lines 60-66)
        s = ComboState(node="A", depth=1)
        step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=7))
        after_node = s.node
        after_depth = s.depth
        after_gate = s.last_gate_id

        r = step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=7))
        self.assertEqual(r.action, "Ignored")
        self.assertEqual(r.reason, "Combo.GateConsumed")
        self.assertEqual(s.node, after_node)
        self.assertEqual(s.depth, after_depth)
        self.assertEqual(s.last_gate_id, after_gate)

        # Gate id 0 is refused
        r0 = step_combo(g, s, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=0))
        self.assertEqual(r0.action, "Recover")
        self.assertEqual(r0.reason, "Combo.GateId")

        # COM-003: only snapshot of THIS gate counts: in front continue, behind recover (lines 67-72)
        front = ComboState(node="A", depth=1)
        self.assertEqual(step_combo(g, front, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=1)).action, "Continue")

        behind = ComboState(node="A", depth=1)
        r_behind = step_combo(g, behind, ComboGate(range_cm=100.0, signed_yaw_deg=170.0, outcome="Hit", gate_id=1))
        self.assertEqual(r_behind.action, "Recover")
        self.assertEqual(r_behind.reason, "Combo.DefaultRecovery")

        # COM-004: whiff, guard and parry branch differently (lines 73-78)
        s_whiff = ComboState(node="A", depth=1)
        r = step_combo(g, s_whiff, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Whiff", gate_id=1))
        self.assertEqual(r.action, "Continue")
        self.assertEqual(r.next_node, "C")

        s_guard = ComboState(node="A", depth=1)
        r = step_combo(g, s_guard, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Guarded", gate_id=1))
        self.assertEqual(r.action, "Continue")
        self.assertEqual(r.next_node, "D")

        s_parry = ComboState(node="A", depth=1)
        r = step_combo(g, s_parry, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Parried", gate_id=1))
        self.assertEqual(r.action, "Recover")
        self.assertEqual(r.reason, "Combo.DefaultRecovery")

        # COM-007: out of range recovers cleanly (hit at 300 cm, band is 0..250) (lines 79-83)
        s_oor = ComboState(node="A", depth=1)
        r = step_combo(g, s_oor, ComboGate(range_cm=300.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=1))
        self.assertEqual(r.action, "Recover")
        self.assertEqual(r.reason, "Combo.DefaultRecovery")

        s_edge = ComboState(node="A", depth=1)
        r = step_combo(g, s_edge, ComboGate(range_cm=250.0, signed_yaw_deg=60.0, outcome="Hit", gate_id=1))
        self.assertEqual(r.action, "Continue")

        # Bad gates: invalid target and non-finite snapshot recover without branch (lines 84-89)
        s_bad = ComboState(node="A", depth=1)
        r = step_combo(g, s_bad, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", target_valid=False, gate_id=1))
        self.assertEqual(r.reason, "Combo.Target")

        s_nan = ComboState(node="A", depth=1)
        r = step_combo(g, s_nan, ComboGate(range_cm=float("nan"), signed_yaw_deg=10.0, outcome="Hit", gate_id=1))
        self.assertEqual(r.reason, "Combo.Target")

        s_unk = ComboState(node="Zed", depth=1)
        r = step_combo(g, s_unk, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=1))
        self.assertEqual(r.reason, "Combo.UnknownNode")

        # COM-006: depth guard stops path longer than MaxDepth (lines 90-94)
        short_g = copy.deepcopy(claude_valid_fixture())
        short_g["MaxDepth"] = 2
        s_depth = ComboState(node="A", depth=1)
        step_combo(short_g, s_depth, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=1))
        r_depth = step_combo(short_g, s_depth, ComboGate(range_cm=100.0, signed_yaw_deg=10.0, outcome="Hit", gate_id=2))
        self.assertEqual(r_depth.action, "Recover")
        self.assertEqual(r_depth.reason, "Combo.Depth")


class TestComboGraphValidation(unittest.TestCase):
    """Verifies graph structural and domain validation rules."""

    def test_valid_3node_chain(self):
        graph = make_valid_3node_graph()
        self.assertEqual(validate_combo_graph(graph), [])

    def test_empty_nodes_refused(self):
        # 1. Combo.Empty
        graph = {"Root": "Node_A", "MaxDepth": 3, "Nodes": []}
        self.assertEqual(validate_combo_graph(graph), ["Combo.Empty"])

    def test_max_depth_bounds(self):
        # 2. Combo.MaxDepth: must be 1..3
        for bad_depth in [0, 4, 5, -1, None, "3", 2.5]:
            graph = make_valid_3node_graph()
            graph["MaxDepth"] = bad_depth
            self.assertEqual(validate_combo_graph(graph), ["Combo.MaxDepth"], f"Failed for MaxDepth={bad_depth}")

        # Valid depths
        for good_depth in [1, 2, 3]:
            g1 = {
                "Root": "RootNode",
                "MaxDepth": good_depth,
                "Nodes": [{"Id": "RootNode", "MoveId": "Move_Solo", "Edges": []}]
            }
            self.assertEqual(validate_combo_graph(g1), [])

    def test_root_missing_refused(self):
        # 3. Combo.Root
        graph = make_valid_3node_graph()
        graph["Root"] = "NonExistentRoot"
        self.assertEqual(validate_combo_graph(graph), ["Combo.Root"])

        graph_empty_root = make_valid_3node_graph()
        graph_empty_root["Root"] = ""
        self.assertEqual(validate_combo_graph(graph_empty_root), ["Combo.Root"])

    def test_duplicate_node_refused(self):
        # 4. Combo.DuplicateNode
        graph = make_valid_3node_graph()
        graph["Nodes"].append({
            "Id": "Node_FollowUp",  # Duplicate Id
            "MoveId": "Move_Extra",
            "Edges": []
        })
        self.assertEqual(validate_combo_graph(graph), ["Combo.DuplicateNode"])

    def test_unknown_node_refused(self):
        # 5. Combo.UnknownNode: edge target not in graph
        graph = make_valid_3node_graph()
        graph["Nodes"][0]["Edges"][0]["ToNode"] = "GhostNode"
        self.assertEqual(validate_combo_graph(graph), ["Combo.UnknownNode"])

        # 5b. Combo.UnknownNode: MoveId empty or None
        graph2 = make_valid_3node_graph()
        graph2["Nodes"][0]["MoveId"] = ""
        self.assertEqual(validate_combo_graph(graph2), ["Combo.UnknownNode"])

        graph3 = make_valid_3node_graph()
        graph3["Nodes"][0]["MoveId"] = "None"
        self.assertEqual(validate_combo_graph(graph3), ["Combo.UnknownNode"])

    def test_edge_domain_refused(self):
        # 6. Combo.EdgeDomain: min > max range
        g1 = make_valid_3node_graph()
        g1["Nodes"][0]["Edges"][0]["MinRangeCm"] = 300.0
        g1["Nodes"][0]["Edges"][0]["MaxRangeCm"] = 100.0
        self.assertEqual(validate_combo_graph(g1), ["Combo.EdgeDomain"])

        # Negative range
        g2 = make_valid_3node_graph()
        g2["Nodes"][0]["Edges"][0]["MinRangeCm"] = -10.0
        self.assertEqual(validate_combo_graph(g2), ["Combo.EdgeDomain"])

        # Yaw > 180 or negative
        g3 = make_valid_3node_graph()
        g3["Nodes"][0]["Edges"][0]["MaxAbsYawDegrees"] = 181.0
        self.assertEqual(validate_combo_graph(g3), ["Combo.EdgeDomain"])

        g4 = make_valid_3node_graph()
        g4["Nodes"][0]["Edges"][0]["MaxAbsYawDegrees"] = -5.0
        self.assertEqual(validate_combo_graph(g4), ["Combo.EdgeDomain"])

        # NaN / inf
        g5 = make_valid_3node_graph()
        g5["Nodes"][0]["Edges"][0]["MinRangeCm"] = float("nan")
        self.assertEqual(validate_combo_graph(g5), ["Combo.EdgeDomain"])

        # Invalid outcome string
        g6 = make_valid_3node_graph()
        g6["Nodes"][0]["Edges"][0]["Outcome"] = "InvalidOutcome"
        self.assertEqual(validate_combo_graph(g6), ["Combo.EdgeDomain"])

    def test_cycle_refused(self):
        # 7. Combo.Cycle: direct or indirect cycle
        graph = make_valid_3node_graph()
        graph["Nodes"][2]["Edges"].append({
            "ToNode": "Node_Root",
            "MinRangeCm": 50.0,
            "MaxRangeCm": 200.0,
            "MaxAbsYawDegrees": 90.0,
            "Outcome": "AnyOutcome"
        })
        self.assertEqual(validate_combo_graph(graph), ["Combo.Cycle"])

        # Self loop
        graph_self = make_valid_3node_graph()
        graph_self["Nodes"][0]["Edges"].append({
            "ToNode": "Node_Root",
            "MinRangeCm": 50.0,
            "MaxRangeCm": 200.0,
            "MaxAbsYawDegrees": 90.0,
            "Outcome": "AnyOutcome"
        })
        self.assertEqual(validate_combo_graph(graph_self), ["Combo.Cycle"])

    def test_depth_exceeded_refused(self):
        # 8. Combo.Depth: 4-node chain exceeds MaxDepth=3
        graph4 = {
            "Root": "N1",
            "MaxDepth": 3,
            "Nodes": [
                {"Id": "N1", "MoveId": "M1", "Edges": [{"ToNode": "N2", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 90.0, "Outcome": "AnyOutcome"}]},
                {"Id": "N2", "MoveId": "M2", "Edges": [{"ToNode": "N3", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 90.0, "Outcome": "AnyOutcome"}]},
                {"Id": "N3", "MoveId": "M3", "Edges": [{"ToNode": "N4", "MinRangeCm": 0.0, "MaxRangeCm": 100.0, "MaxAbsYawDegrees": 90.0, "Outcome": "AnyOutcome"}]},
                {"Id": "N4", "MoveId": "M4", "Edges": []}
            ]
        }
        self.assertEqual(validate_combo_graph(graph4), ["Combo.Depth"])


class TestComboStepSimulator(unittest.TestCase):
    """Verifies runtime Step execution semantics against fresh gates."""

    def test_duplicate_gate_id_ignored(self):
        # COM-005: GateId equal to State.LastGateId is ignored without touching state
        graph = make_valid_3node_graph()
        state = ComboState(node="Node_Root", depth=1, last_gate_id=101)
        gate = ComboGate(range_cm=100.0, signed_yaw_deg=0.0, outcome="Hit", gate_id=101)

        res = step_combo(graph, state, gate)
        self.assertEqual(res.action, "Ignored")
        self.assertEqual(res.reason, "Combo.GateConsumed")
        self.assertEqual(state.node, "Node_Root")
        self.assertEqual(state.depth, 1)
        self.assertEqual(state.last_gate_id, 101)
        self.assertFalse(state.finished)

    def test_target_invalid_recovers(self):
        # Target invalid -> Recover Combo.Target
        graph = make_valid_3node_graph()
        state = ComboState(node="Node_Root", depth=1, last_gate_id=10)
        gate = ComboGate(range_cm=100.0, signed_yaw_deg=0.0, outcome="Hit", target_valid=False, gate_id=11)

        res = step_combo(graph, state, gate)
        self.assertEqual(res.action, "Recover")
        self.assertEqual(res.reason, "Combo.Target")
        self.assertTrue(state.finished)
        self.assertEqual(state.last_gate_id, 11)

    def test_behind_the_boss_differs_from_in_front(self):
        # COM-003: Yaw cone branch discrimination
        graph = {
            "Root": "Root",
            "MaxDepth": 3,
            "Nodes": [
                {
                    "Id": "Root",
                    "MoveId": "Move_Slash",
                    "Edges": [
                        {
                            "ToNode": "Front_FollowUp",
                            "MinRangeCm": 0.0,
                            "MaxRangeCm": 300.0,
                            "MaxAbsYawDegrees": 60.0,  # Front cone
                            "Outcome": "AnyOutcome"
                        },
                        {
                            "ToNode": "Back_Spin",
                            "MinRangeCm": 0.0,
                            "MaxRangeCm": 300.0,
                            "MaxAbsYawDegrees": 180.0,  # Behind / wide cone
                            "Outcome": "AnyOutcome"
                        }
                    ]
                },
                {"Id": "Front_FollowUp", "MoveId": "Move_Front", "Edges": []},
                {"Id": "Back_Spin", "MoveId": "Move_Spin", "Edges": []}
            ]
        }

        state_front = ComboState(node="Root", depth=1, last_gate_id=1)
        gate_front = ComboGate(range_cm=150.0, signed_yaw_deg=15.0, outcome="Hit", gate_id=2)
        res_front = step_combo(graph, state_front, gate_front)
        self.assertEqual(res_front.action, "Continue")
        self.assertEqual(res_front.next_node, "Front_FollowUp")
        self.assertEqual(state_front.depth, 2)

        state_back = ComboState(node="Root", depth=1, last_gate_id=1)
        gate_back = ComboGate(range_cm=150.0, signed_yaw_deg=150.0, outcome="Hit", gate_id=2)
        res_back = step_combo(graph, state_back, gate_back)
        self.assertEqual(res_back.action, "Continue")
        self.assertEqual(res_back.next_node, "Back_Spin")
        self.assertEqual(state_back.depth, 2)

    def test_outcome_branching_hit_whiff_guarded_parried(self):
        # COM-004: Outcome-based branching
        graph = {
            "Root": "Root",
            "MaxDepth": 3,
            "Nodes": [
                {
                    "Id": "Root",
                    "MoveId": "Move_Swing",
                    "Edges": [
                        {"ToNode": "On_Hit", "MinRangeCm": 0.0, "MaxRangeCm": 300.0, "MaxAbsYawDegrees": 180.0, "Outcome": "Hit"},
                        {"ToNode": "On_Whiff", "MinRangeCm": 0.0, "MaxRangeCm": 300.0, "MaxAbsYawDegrees": 180.0, "Outcome": "Whiff"},
                        {"ToNode": "On_Guarded", "MinRangeCm": 0.0, "MaxRangeCm": 300.0, "MaxAbsYawDegrees": 180.0, "Outcome": "Guarded"},
                        {"ToNode": "On_Parried", "MinRangeCm": 0.0, "MaxRangeCm": 300.0, "MaxAbsYawDegrees": 180.0, "Outcome": "Parried"}
                    ]
                },
                {"Id": "On_Hit", "MoveId": "Move_Chaser", "Edges": []},
                {"Id": "On_Whiff", "MoveId": "Move_ResetStep", "Edges": []},
                {"Id": "On_Guarded", "MoveId": "Move_KickShield", "Edges": []},
                {"Id": "On_Parried", "MoveId": "Move_StumbleBack", "Edges": []}
            ]
        }

        cases = [
            ("Hit", "On_Hit"),
            ("Whiff", "On_Whiff"),
            ("Guarded", "On_Guarded"),
            ("Parried", "On_Parried")
        ]

        for outcome, expected_node in cases:
            state = ComboState(node="Root", depth=1, last_gate_id=10)
            gate = ComboGate(range_cm=100.0, signed_yaw_deg=0.0, outcome=outcome, gate_id=11)
            res = step_combo(graph, state, gate)
            self.assertEqual(res.action, "Continue", f"Outcome {outcome} failed")
            self.assertEqual(res.next_node, expected_node, f"Outcome {outcome} routed to wrong node")
            self.assertEqual(state.node, expected_node)

    def test_no_match_recovers_default(self):
        # COM-007: No edge matches -> Recover Combo.DefaultRecovery
        graph = make_valid_3node_graph()

        # Target out of range
        state1 = ComboState(node="Node_Root", depth=1, last_gate_id=1)
        gate1 = ComboGate(range_cm=400.0, signed_yaw_deg=0.0, outcome="Hit", gate_id=2)
        res1 = step_combo(graph, state1, gate1)
        self.assertEqual(res1.action, "Recover")
        self.assertEqual(res1.reason, "Combo.DefaultRecovery")
        self.assertTrue(state1.finished)

        # Target outside yaw cone
        state2 = ComboState(node="Node_Root", depth=1, last_gate_id=1)
        gate2 = ComboGate(range_cm=100.0, signed_yaw_deg=120.0, outcome="Hit", gate_id=2)
        res2 = step_combo(graph, state2, gate2)
        self.assertEqual(res2.action, "Recover")
        self.assertEqual(res2.reason, "Combo.DefaultRecovery")
        self.assertTrue(state2.finished)

    def test_terminal_node_finishes(self):
        # COM-006: Stepping a terminal node (0 edges) -> Finished
        graph = make_valid_3node_graph()
        state = ComboState(node="Node_Finisher", depth=3, last_gate_id=5)
        gate = ComboGate(range_cm=100.0, signed_yaw_deg=0.0, outcome="Hit", gate_id=6)

        res = step_combo(graph, state, gate)
        self.assertEqual(res.action, "Finished")
        self.assertTrue(state.finished)
        self.assertEqual(state.last_gate_id, 6)

    def test_depth_guard_prevents_exceeding_max_depth(self):
        # If stepping would cause depth + 1 > MaxDepth -> Recover Combo.Depth
        graph = make_valid_3node_graph()
        state = ComboState(node="Node_FollowUp", depth=3, last_gate_id=1)
        gate = ComboGate(range_cm=100.0, signed_yaw_deg=0.0, outcome="Hit", gate_id=2)

        res = step_combo(graph, state, gate)
        self.assertEqual(res.action, "Recover")
        self.assertEqual(res.reason, "Combo.Depth")
        self.assertTrue(state.finished)


if __name__ == "__main__":
    unittest.main()
