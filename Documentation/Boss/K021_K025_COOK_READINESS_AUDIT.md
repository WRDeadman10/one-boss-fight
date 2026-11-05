# Queue K K021–K025 — selected-root cook readiness

## Current source and tool state

Queue J delivered offline graph/cook normalizers and a reachability verifier:

- `normalize_encounter_selection_graph.py` requires an explicit Editor export with root packages and edges that preserve each `source_path` and `target_package`.
- `normalize_cook_package_manifest.py` requires an explicit captured cook export with build/config, mount roots and package entries.
- `verify_encounter_package_graph.py` checks only transitive reachable packages, rejects duplicates, checks v2 build/config agreement and prints root-to-reference chains.

These tools consume captured JSON; they do not query Unreal or infer references/cook inclusion. The repository has no selected-root export artifact or authoritative cook export, and the G044 selection asset is not yet authored. No K021/K022 capture can truthfully be generated now.

## K021–K025 disposition

- **K021 BLOCKED / CLAUDE EDITOR:** create/read back the G044 selection first, then export its real soft-reference graph with source property paths and selected root identity. There is no current Editor graph exporter artifact or graph capture to normalize.
- **K022 BLOCKED / CLAUDE COOK:** capture the authoritative manifest from the target cook, preserving build/config, mount roots and package list. No cook has been captured for this root.
- **K023 TOOL READY / UNRUN:** the normalizers and verifier meet the stated v2 schema contract. Run them only on the two authoritative exports; no fixture or unrelated staged package is evidence.
- **K024 BLOCKED:** there is no actual missing/excluded package finding to repair. If verification reports one, trace its source edge and recook from corrected content/rules; retain the old export and capture a fresh one.
- **K025 BLOCKED / CLAUDE PACKAGED:** target-binary load evidence requires the authored root, actual cook and packaged run. Editor load or a folder rule is insufficient.

No package export was invented and no cook/package command was run by Codex.
