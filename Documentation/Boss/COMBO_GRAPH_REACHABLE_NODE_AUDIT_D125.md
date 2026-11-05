# Queue D125 — combo graph reachable-node audit

Date: 2026-11-03  
Method: static trace of graph validation, profile resolution, and runtime lookup; no assets or tests run.

## Validation and resolution

`RPGBossCombo::Validate` validates every node, not only the root-reachable subset: IDs must be nonempty/unique, every MoveId nonempty, every edge destination present, every edge in domain, and every component acyclic. It checks `MaxDepth` against the longest path from the root; a disconnected acyclic node chain is not included in this root-depth calculation. `ValidateProfile` runs this when combo data exists and only permits it in F5.

`ResolveProfile` then iterates every authored combo node and requires its MoveId to match one of the resolved profile candidates (`Framework.Profile.Combo.UnknownMove`). Thus unreachable nodes still need valid references and resolvable cards; a structurally valid orphan node is not ignored at profile load.

## Runtime lookup

At encounter start, runtime copies the built graph. Selector-driven combo entry occurs only when the selected card MoveId matches the graph root's MoveId. On a branch, `Step` selects a node ID from the current node's authored edges. Runtime finds that node by ID, then scans resolved candidates for a matching MoveId before attempting `StartCard`. The test suite covers pure root-to-terminal Step traversal and profile validation errors, but no focused profile-resolution/runtime test demonstrates behavior for a valid unreachable node or duplicate MoveId across distinct nodes.

## Findings / limits

- Unreachable nodes undergo structural validation and card-resolution checks despite being unreachable from root in combo traversal.
- Runtime lookup is by node ID followed by MoveId; the loop overwrites `CardIndex` for every matching candidate, so duplicate candidate MoveIds resolve to the last matching entry. Distinct graph nodes can name the same MoveId without a graph-rule rejection; profile card uniqueness/selector candidate behavior is a separate concern and was not proven here.
- The audit confirms the requested distinction between validator coverage and runtime reachability. It does not claim authored asset state or runtime graph execution.
