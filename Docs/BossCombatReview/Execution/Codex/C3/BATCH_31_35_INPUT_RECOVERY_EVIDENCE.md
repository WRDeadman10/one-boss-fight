# Queue F-C C3 tasks 31–35: refusal, evidence, and recovery

## Refusal behavior

The destination collision guard runs before any attack-table write. Config loading now converts file/encoding/JSON errors to an explicit `[NEWWEAPON_FATAL]` message and rejects non-object roots. The offline validator also rejects non-string arrays for `style_aliases` and `build.aliases`, along with the existing required-field/catalog-path failures. `fixtures/malformed_config_cases.json` records the malformed-input matrix.

## Evidence and runtime boundary

`C3_RUNTIME_EVIDENCE_TEMPLATE.json` records dry-run/apply logs, the native startup catalog compile, expected/observed package changes, and prerequisite hashes. It is explicitly `NOT_RUN`: Codex did not launch Unreal or PIE. `capture_prerequisite_hashes.py` and its example baseline provide the unchanged pack-dependency control. Lead must populate an execution receipt from the actual isolated run before treating C3 as runtime accepted.

## Usage and recovery

`Documentation/Boss/C3_NEW_WEAPON_HOWTO.md` retains the dry-run and apply commands, explains the delayed native compile, and now gives a non-destructive recovery path. After a partial apply, preserve assets, capture logs/package state, verify catalog references, and have the asset owner/Lead choose a reference-safe restoration. The guide no longer recommends blanket checkout or deleting/recreating assets.

Pure Python checks requested by Claude C-786 passed after two review-driven hotfixes: validator 28/28, config re-open 4/4, how-to re-open 13/13, catalog design re-open 12/12, and weapon design re-open 18/18. Static AST/JSON checks pass. No Unreal Editor, PIE, or build was run; live execution evidence remains pending Lead.
