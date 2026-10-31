#!/usr/bin/env python3
"""
validate_combo_graph.py
=======================
Pure Python validation rules and step simulator for Boss Combo Graph DAG.
Strictly mirrors C++ rules in Source/OneBossFight/Player/RPGBossComboRules.h (namespace RPGBossCombo).

Requirements Covered:
- BOSS-COM-001: Explicit Directed Acyclic Graph (DAG) authored with validation.
- BOSS-COM-003: Fresh context per decision gate (only Gate telemetry used).
- BOSS-COM-004: Outcome-based branching (Hit / Whiff / Guarded / Parried / AnyOutcome).
- BOSS-COM-005: Single-use decision gate (duplicate GateId ignored).
- BOSS-COM-006: MaxDepth bounding (1..3 nodes maximum).
- BOSS-COM-007: Default recovery when out of range or no edge matches.

100% offline, zero engine dependency.
"""

import math
from typing import List, Dict, Any, Optional, Set

CEILING = 1.0e6
VALID_OUTCOMES = {"Hit", "Whiff", "Guarded", "Parried", "AnyOutcome", "Any"}


class ComboState:
    """Live state of the combo execution on the boss."""
    def __init__(
        self,
        node: str,
        depth: int = 1,
        last_gate_id: int = 0,
        finished: bool = False
    ):
        self.node = str(node)
        self.depth = int(depth)
        self.last_gate_id = int(last_gate_id)
        self.finished = bool(finished)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node": self.node,
            "depth": self.depth,
            "last_gate_id": self.last_gate_id,
            "finished": self.finished
        }


class ComboGate:
    """Instantaneous snapshot passed into the decision gate."""
    def __init__(
        self,
        range_cm: float,
        signed_yaw_deg: float,
        outcome: str = "Hit",
        target_valid: bool = True,
        gate_id: int = 0
    ):
        self.range_cm = float(range_cm)
        self.signed_yaw_deg = float(signed_yaw_deg)
        self.outcome = str(outcome)
        self.target_valid = bool(target_valid)
        self.gate_id = int(gate_id)


class StepResult:
    """Result of a single Step invocation."""
    def __init__(
        self,
        action: str,
        next_node: Optional[str] = None,
        reason: Optional[str] = None
    ):
        self.action = str(action)  # "Continue", "Recover", "Finished", "Ignored"
        self.next_node = next_node
        self.reason = reason

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StepResult):
            return False
        return (
            self.action == other.action and
            self.next_node == other.next_node and
            self.reason == other.reason
        )

    def __repr__(self) -> str:
        parts = [f"action='{self.action}'"]
        if self.next_node:
            parts.append(f"next_node='{self.next_node}'")
        if self.reason:
            parts.append(f"reason='{self.reason}'")
        return f"StepResult({', '.join(parts)})"


def longest_path(graph: Dict[str, Any]) -> int:
    """
    Longest root-to-terminal path counted in nodes.
    Returns -1 if a cycle or unknown node makes it undefined.
    Mirrors RPGBossCombo::LongestPath(const FComboGraph& G).
    """
    nodes = graph.get("Nodes", [])
    if not isinstance(nodes, list):
        return -1
    node_ids = [n.get("Id") for n in nodes if isinstance(n, dict) and "Id" in n]
    node_index = {nid: i for i, nid in enumerate(node_ids)}
    root = graph.get("Root")
    if root not in node_index:
        return -1

    n_count = len(nodes)
    memo = [0] * n_count
    color = [0] * n_count  # 0: new, 1: visiting, 2: done

    def visit(i: int) -> int:
        if color[i] == 2:
            return memo[i]
        if color[i] == 1:
            return -1
        color[i] = 1
        best = 1
        edges = nodes[i].get("Edges", []) if isinstance(nodes[i], dict) else []
        for e in edges:
            if not isinstance(e, dict):
                return -1
            to_id = e.get("ToNode", e.get("To"))
            if to_id not in node_index:
                return -1
            to_idx = node_index[to_id]
            sub = visit(to_idx)
            if sub < 0:
                return -1
            if 1 + sub > best:
                best = 1 + sub
        color[i] = 2
        memo[i] = best
        return best

    return visit(node_index[root])


def validate_combo_graph(graph: Dict[str, Any]) -> List[str]:
    """
    Validates a Combo Graph specification.
    First failure wins, strictly checking in this exact order:
      1. Combo.Empty
      2. Combo.MaxDepth (1..3)
      3. Combo.Root
      4. Combo.DuplicateNode (also a node with no id)
      5. Combo.UnknownNode (edge target or node without MoveId)
      6. Combo.EdgeDomain
      7. Combo.Cycle
      8. Combo.Depth (longest path in nodes > MaxDepth)
    Returns list with winning error token, or empty list if valid.
    """
    # 1. Combo.Empty
    nodes = graph.get("Nodes")
    if not nodes or not isinstance(nodes, list) or len(nodes) == 0:
        return ["Combo.Empty"]

    # 2. Combo.MaxDepth: must be integer in 1..3
    max_depth = graph.get("MaxDepth")
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 1 or max_depth > 3:
        return ["Combo.MaxDepth"]

    # 3. Combo.Root: root not a node
    root = graph.get("Root")
    node_ids = []
    node_dict = {}
    for n in nodes:
        if isinstance(n, dict) and "Id" in n and n["Id"]:
            node_ids.append(n["Id"])
            node_dict[n["Id"]] = n

    if not root or not isinstance(root, str) or root not in node_dict:
        return ["Combo.Root"]

    # 4. Combo.DuplicateNode (also a node with empty/missing id)
    seen_ids = set()
    for n in nodes:
        if not isinstance(n, dict):
            return ["Combo.DuplicateNode"]
        nid = n.get("Id")
        if not nid or not isinstance(nid, str) or nid.strip() == "" or nid == "None" or nid in seen_ids:
            return ["Combo.DuplicateNode"]
        seen_ids.add(nid)

    # 5. Combo.UnknownNode
    for n in nodes:
        move_id = n.get("MoveId")
        if not move_id or not isinstance(move_id, str) or move_id.strip() == "" or move_id == "None":
            return ["Combo.UnknownNode"]

        edges = n.get("Edges", [])
        if not isinstance(edges, list):
            return ["Combo.UnknownNode"]
        for e in edges:
            if not isinstance(e, dict):
                return ["Combo.UnknownNode"]
            to_node = e.get("ToNode", e.get("To"))
            if not to_node or not isinstance(to_node, str) or to_node not in seen_ids:
                return ["Combo.UnknownNode"]

    # 6. Combo.EdgeDomain
    for n in nodes:
        for e in n.get("Edges", []):
            min_r = e.get("MinRangeCm", 0.0)
            max_r = e.get("MaxRangeCm", CEILING)
            yaw = e.get("MaxAbsYawDegrees", 180.0)
            out = e.get("Outcome", "Hit")

            # Check numeric types and finite values
            nums = [("MinRangeCm", min_r), ("MaxRangeCm", max_r), ("MaxAbsYawDegrees", yaw)]
            for name, val in nums:
                if val is None or isinstance(val, bool) or not isinstance(val, (int, float)):
                    return ["Combo.EdgeDomain"]
                if not math.isfinite(val):
                    return ["Combo.EdgeDomain"]

            if min_r < 0.0 or min_r > max_r:
                return ["Combo.EdgeDomain"]
            if yaw < 0.0 or yaw > 180.0:
                return ["Combo.EdgeDomain"]
            if out not in VALID_OUTCOMES:
                return ["Combo.EdgeDomain"]

    # 7. Combo.Cycle & 8. Combo.Depth via LongestPath
    lp = longest_path(graph)
    if lp < 0:
        return ["Combo.Cycle"]
    if lp > max_depth:
        return ["Combo.Depth"]

    return []


def step_combo(
    graph: Dict[str, Any],
    state: ComboState,
    gate: ComboGate
) -> StepResult:
    """
    Executes a single step through the Combo Graph.
    Strictly mirrors RPGBossCombo::Step(const FComboGraph& G, FComboState& S, const FComboGate& Gate).
    Rules:
      1. Node existence check: Unknown node -> Recover Combo.UnknownNode.
      2. Gate ID == 0 check: Refused -> Recover Combo.GateId.
      3. Gate ID == State.LastGateId check: Ignored without touching state (COM-005) -> Ignored Combo.GateConsumed.
      4. Target validity & finite snapshot: Not valid -> Recover Combo.Target.
      5. Terminal node (0 edges): -> Finished (COM-006).
      6. Edge evaluation (in order): First matching range, yaw, and outcome wins.
         - Depth guard: If depth + 1 > MaxDepth -> Recover Combo.Depth.
         - Continue to next node: depth += 1, node = ToNode -> Continue.
      7. Default recovery: No edge matched -> Recover Combo.DefaultRecovery (COM-007).
    """
    nodes = graph.get("Nodes", [])
    node_dict = {n.get("Id"): n for n in nodes if isinstance(n, dict) and "Id" in n}

    # 1. Current node exists
    if state.node not in node_dict:
        return StepResult("Recover", reason="Combo.UnknownNode")

    # 2. Gate ID == 0
    if gate.gate_id == 0:
        return StepResult("Recover", reason="Combo.GateId")

    # 3. Single-use gate (COM-005)
    if gate.gate_id == state.last_gate_id:
        return StepResult("Ignored", reason="Combo.GateConsumed")

    # Latch gate ID
    state.last_gate_id = gate.gate_id

    # 4. Target validity & finite snapshot
    if not gate.target_valid or not math.isfinite(gate.range_cm) or not math.isfinite(gate.signed_yaw_deg):
        state.finished = True
        return StepResult("Recover", reason="Combo.Target")

    # 5. Terminal node (COM-006)
    current_node = node_dict[state.node]
    edges = current_node.get("Edges", [])
    if not edges:
        state.finished = True
        return StepResult("Finished")

    # 6. Edge matching (first in order)
    max_depth = graph.get("MaxDepth", 3)
    for edge in edges:
        min_r = float(edge.get("MinRangeCm", 0.0))
        max_r = float(edge.get("MaxRangeCm", CEILING))
        max_yaw = float(edge.get("MaxAbsYawDegrees", 180.0))
        out_filter = edge.get("Outcome", "Hit")
        b_any = edge.get("bAnyOutcome", False) or out_filter in ("AnyOutcome", "Any")

        # Range check
        if gate.range_cm < min_r or gate.range_cm > max_r:
            continue
        # Yaw check
        if abs(gate.signed_yaw_deg) > max_yaw:
            continue
        # Outcome check
        if not b_any and out_filter != gate.outcome:
            continue

        # Depth guard
        if state.depth + 1 > max_depth:
            state.finished = True
            return StepResult("Recover", reason="Combo.Depth")

        to_node = edge.get("ToNode", edge.get("To"))
        state.node = to_node
        state.depth += 1
        return StepResult("Continue", next_node=to_node)

    # 7. Default recovery (COM-007)
    state.finished = True
    return StepResult("Recover", reason="Combo.DefaultRecovery")
