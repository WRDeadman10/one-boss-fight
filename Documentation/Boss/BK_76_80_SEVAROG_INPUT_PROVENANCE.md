# BK-76..80: Sevarog deferred-definition input provenance (PENDING)

Assigned by X-1996 (lead Codex) to C (implementer), 2026-11-11. New files only. No edits to the BK-56..60 author, runner or driver; no Unreal, build, PIE, asset writes or locks. Nothing here authorizes authoring.

## BK-76: field audit

The definition needs `Stats` (4 fields) and the initial phase record `Phases[Phase_1]` (5 fields). The selected record's `EntryHealthFraction` feeds `PhaseTwoHealthFraction` (`RPGBossPhaseAdapters.cpp:171`). Every row below is in `BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json`, with excerpt and file hashes.

| Field | Value | Status | Source |
|---|---|---|---|
| `Stats.MaxHealth` | 1500 | SOURCE_BACKED_AWAITING_OWNER | `SevarogEnemyInfo.uasset` (file SHA-256) + `DECISIONS.md:249`. The value comes from the doc row; the authoring run must read it back from the asset. |
| `Stats.MaxPosture` | 100 | SOURCE_BACKED_AWAITING_OWNER | Same sources. The pack field is "poise"; mapping it to the project's posture pool is an interpretation the owner must confirm. |
| `Stats.PostureRegenDelay` | none (candidate 6.0) | OWNER_DECISION_REQUIRED | Only `RPGBossPosture.h:35` (design-freeze default); C-1239 bars native defaults as authored choices (`C1239...md:21`). |
| `Stats.PostureRegenRate` | none (candidate 13.0) | OWNER_DECISION_REQUIRED | Only `RPGBossPosture.h:39`; same C-1239 bar. |
| `Phases[Phase_1].PhaseId` | Phase_1 | SOURCE_BACKED (structural) | `author_framework_encounter_definition.py:14` and the C-1280 card phase sets. |
| `Phases[Phase_1].EntryHealthFraction` | 0.6 | SOURCE_BACKED_AWAITING_OWNER | C-1280 Decision 2 (mailbox excerpt), `author_sevarog_draft_cards.py:79`, adapter `:171`. |
| `Phases[Phase_1].SpeedMultiplier` | none (candidate 1.0) | OWNER_DECISION_REQUIRED | No Sevarog source; 1.0 is not assumed approved. |
| `Phases[Phase_1].RateMultiplier` | none (candidate 1.0) | OWNER_DECISION_REQUIRED | As above. |
| `Phases[Phase_1].AttackMultiplier` | none (candidate 1.0) | OWNER_DECISION_REQUIRED | As above. |

Finding: the prior `ensure_bk56_60_sevarog_initial_phase.py` version wrote the draft's Phase_1 row with `entry_health_fraction 0.0` and all three multipliers at `1.0`. C-1307 preserves this finding in the append-only mailbox (and the PENDING manifest cites that record). 0.0 is the invalid zero threshold behind the X-1988 rejection (validation needs 0 < x <= 1, `RPGBossPhaseAdapters.cpp:122`). The 1.0 multipliers are unapproved values already in the asset. Lead changed the helper to refuse missing/unvalidated inputs instead of generating defaults; a later approved authoring step must still repair the existing row.

## BK-77: PENDING manifest

`Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json`, schema `onebossfight.pending-definition-inputs/v1`. It declares `manifest_state=PENDING`, `authoring_evidence=false`, `executable=false`, `decision_request=X-1991`, and a warning not to author from it.

Each row records field path, type, units, status, value (`null` for pending rows, with an optional labelled `candidate`), note, and citations. Each citation has a repo-relative path, a scope (`excerpt` with the exact line text, or `file`) and a SHA-256. Mailbox and DECISIONS citations use excerpt hashes, so they stay stable as those files grow; the asset uses a file hash.

## BK-78: validator

`Scripts/Tools/validate_pending_definition_inputs.py` is read-only. Exit 0 means a valid PENDING manifest, 1 means invalid.

It always checks:
- Schema, state and both flags.
- Coverage of the 9 required fields, with no duplicates and no unknown keys.
- Status is one of SOURCE_BACKED, SOURCE_BACKED_AWAITING_OWNER or OWNER_DECISION_REQUIRED. Any other status (APPROVED, OWNER_APPROVED, AUTHORED) is refused.
- Valued rows have a typed value and no candidate; pending rows have value `null`, since a value there would be a premature promotion.
- Every row has at least one citation, with a repo-relative path and a 64-hex SHA-256, and every excerpt's hash matches its text.

`--verify-sources` additionally re-hashes cited files and confirms each excerpt still occurs in its file.

## BK-79: tests

`Scripts/Tools/test_validate_pending_definition_inputs.py`, 14 tests (in-memory manifests and temp files; the real manifest is checked schema-only, so no `.uasset` is hashed in tests). Covered cases:
- **Valid:** supported plus pending rows, the real BK-76 manifest, and `--verify-sources` with matching excerpt and file.
- **Tampering:** a tampered excerpt hash, a tampered file hash, an excerpt missing from its source, and a missing cited file.
- **Citations:** a missing citation, a missing citations key, and bad citation shapes (absolute path, `..` path, short SHA, bad scope, empty excerpt).
- **Premature approval:** APPROVED, OWNER_APPROVED and AUTHORED statuses, and a pending row given a value.
- **Manifest claims:** claiming evidence or executability, state APPROVED, or a wrong schema.
- **Row schema:** a missing required field, a duplicate field, a wrong value type, a missing value, a candidate on a valued row, unknown keys, and empty rows.
- **Other:** CLI exit codes and the read-only source check.

## BK-80: validation (exact)

- From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_validate_pending_definition_inputs.py"` → `Ran 14 tests ... OK`.
- `python -I Scripts/Tools/validate_pending_definition_inputs.py Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json --verify-sources` → `VALID counts={'SOURCE_BACKED_AWAITING_OWNER': 3, 'SOURCE_BACKED': 1, 'OWNER_DECISION_REQUIRED': 5}`.
- `python -I -m py_compile` on both Python files → OK.
- JSON parse of the manifest → OK.
- `git diff --check` on the three new data and code files → clean.

## Unresolved owner choice (unchanged from X-1991)

1. Approve 1500 / 100 from SevarogEnemyInfo, including the poise-to-posture mapping.
2. Posture regen: 6 s / 13 per s (design freeze), or other values.
3. Phase_1 threshold 0.6, and multipliers 1.0 / 1.0 / 1.0 or other values.

After the answer, a separate APPROVED manifest (out of scope here) should cite the owner's reply; the authoring step must then also correct the 0.0 threshold and unapproved multipliers now in the draft asset.

## Lead review and safety hotfix

Codex accepted the pending-only provenance manifest and source audit. Review found two safety gaps and corrected them: the manifest validator now rejects unknown top-level keys that could carry a conflicting approval claim and verifies excerpt line numbers when rechecking sources; the phase prerequisite helper no longer inserts zero threshold/identity multipliers. It requires explicit numeric inputs when creating a missing phase and validates any existing row as finite, with the threshold in `(0,1]` and multipliers positive. The pending manifest's historical asset-state citation now points to C-1307's append-only mailbox finding instead of helper lines that changed. Focused manifest tests pass 15/15, deferred source contracts 9/9, source hash/line verification is VALID, and Python compilation passes. No asset was authored or changed. The existing draft row remains unapproved and invalid pending the Owner decision; helper now refuses it. A later approved repair under C-1155 is still required.
