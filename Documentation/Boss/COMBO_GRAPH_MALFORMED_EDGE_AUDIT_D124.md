# Queue D124 — combo graph malformed-edge test audit

Date: 2026-11-03  
Method: static comparison of `RPGBossComboRules.h` and `RPGBossComboTests.cpp`; no tests run.

## Validation contract and coverage

`Validate` has stable first-failure order: empty graph, MaxDepth outside 1..3, unknown root, empty/duplicate node ID, missing MoveId or unknown edge destination, invalid edge domain, any cycle (including disconnected nodes), then root longest path exceeding MaxDepth. Tokens are `Combo.Empty`, `Combo.MaxDepth`, `Combo.Root`, `Combo.DuplicateNode`, `Combo.UnknownNode`, `Combo.EdgeDomain`, `Combo.Cycle`, and `Combo.Depth`.

Tests cover unknown edge destination as `Combo.UnknownNode`; reversed range, yaw >180, NaN range, and invalid pause as `Combo.EdgeDomain`; root cycle, disconnected two-node cycle, self-loop as `Combo.Cycle`; valid orphan node; and exact/overlong depth. `LongestPathFrom` returns -1 for missing references or a revisited visiting node. The graph validator rejects missing references before calling it, so `Combo.Cycle` denotes cycles for validated graphs, not missing edges. Traversal recurses through the node graph; accepted graphs are limited to depth 3 from the root, but disconnected acyclic orphan chains have no global length cap beyond finite authored node count.

## Terminal/no-edge behavior

A node with no edges is valid and is terminal by contract. `Step` returns `Finished` from it. The existing A→B→E scenario exercises a terminal node; an orphan terminal node is also accepted by validation. There is no separate “terminal edge” marker or edge-required rule.

## Result

Requested malformed-edge, cycle, and terminal cases are represented by tests. No specific missing-node/cycle/terminal validation defect found. Current test gaps are exact token-precedence combinations (multiple simultaneous defects) and large disconnected acyclic graph scale/recursion, neither of which is promised by the acceptance wording. Static audit only.
