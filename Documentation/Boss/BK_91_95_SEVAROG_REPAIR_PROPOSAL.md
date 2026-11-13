# BK-91..95: non-destructive Sevarog data repair and authoring — PROPOSAL

Assigned by X-2002 (lead Codex) to C (implementer), 2026-11-11. Design input for lead review. New files only; no existing author, runner, driver, helper or validator edited; no Unreal, build, PIE, asset or lock operations; no project values.

**No owner response to X-1991 exists. Nothing here authors data or unblocks C-1155.**

## BK-91: the reflected target and its rules

| Item | Declaration | Python property | Native validation |
|---|---|---|---|
| Definition | `URPGBossDefinition`, `RPGEncounterBinding.h:352` | — | — |
| `Stats` | `FRPGBossStatsConfig Stats` (`:361`); struct at `:26` | `stats.max_health`, `.max_posture`, `.posture_regen_delay`, `.posture_regen_rate` | finite; MaxHealth > 0 (`RPGBossStatsAdapters.cpp:74`) and above the native override floor 1 (`RPGBossStatsAdapters.h:38`); MaxPosture > 0; delay and rate >= 0 (`:84`) |
| `Phases` | `TArray<FRPGPhaseConfig> Phases` (`:381`); struct at `:322` | `phase_id`, `entry_health_fraction`, `speed_multiplier`, `rate_multiplier`, `attack_multiplier` | finite; threshold in (0, 1] (`RPGBossPhaseAdapters.cpp:122`); multipliers > 0 (`:131`). The selected record's threshold feeds `PhaseTwoHealthFraction` (`:171`) |
| `Fields` | `TArray<FRPGParityField> Fields` (`:385`); struct at `:334` (FieldPath, Value, Type, Units, SourcePath, SourceSHA256, SourceSite, Origin, Precedence, Destination, …) | `fields[]` | The hydration preflight requires a record for every required path (`RPGBossHydrationPreflight.cpp:214-231`). X-1988's "no field manifest" refusal |

Field paths: `Stats.*` (`RPGBossStatsAdapters.h:41-44`), `Phases[Phase_1].*` (`RPGBossPhaseAdapters.cpp:102-105`). Precedent for the record format: the accepted G044 Ember manifest (`Stats.MaxHealth` with destination, origin, precedence, source_path/sha256/site, type, units, value, witness).

Readback needs: all four Stats; exactly one Phase_1 row with its four numbers; the other phase rows unchanged; a `Fields` record for each of the 9 paths; the asset path unchanged; the file hash changed by the save.

## BK-92: in-place repair design

- **Target:** the existing `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft`, which the framework encounter references. Only `operation=in_place_update` is allowed; create, replace, delete-and-recreate and copy targets are refused (CLAUDE.md: never delete and recreate referenced assets).
- **Values:** taken only from a valid owner approval envelope (BK-86..90, as hardened by the lead, X-2002) with no unresolved fields, no rejected field lacking an approved alternative, and approvals for all 9 fields. Each value is re-checked against the native range (defense in depth), and PhaseId must be `Phase_1`. No default is ever supplied.
- **Phase_1:** if exactly one row exists, update it in place (`update_existing_row`, which fixes today's `0.0` threshold and unapproved `1.0` multipliers). If none exists, append one (`append_row`). If two or more exist, refuse (ambiguous target). Other phase rows are never touched.
- **Stats:** set all four properties in place. This closes the BK-81..85 "no Stats writer" gap once implemented.
- **Provenance:** one `Fields` record per written path, with `origin=OwnerApproval`, `precedence=typed-record`, `source_path=Documentation/TEAM_MAILBOX.md`, `source_site=<owner message id>`, `source_sha256=<reply hash>`.

## BK-93: gated sequence

**Dry run (default):** `load_existing_asset` → `diff_only`. No locks or backup are needed; nothing is saved. It emits the planned from/to diffs.

**Write** requires all of the following:
- `explicit_write=true`.
- Both C-1155 locks held under one owner token.
- A file backup whose SHA-256 equals the asset file's before-hash.

It then runs `verify_locks` → `verify_backup` → `load_existing_asset` → `apply_stats` → `apply_phase_1` → `upsert_field_records` → `save_in_place` → `readback_verify` → `release_locks`.

**Readback** (after the save) checks:
- The asset path is unchanged.
- The file hash differs from the before-hash.
- There is exactly one Phase_1 row.
- The other phase rows are unchanged.
- Every written property equals the plan within float32 tolerance (1e-5).
- Every written path has a `Fields` record.

On any mismatch the next step is `restore_backup_then_release_locks`; on success it is `release_locks`. Locks are released on every path (the executor must use try/finally, as the BK-56..60 runner does).

A separate locked readback (as `author_framework_encounter_definition.py --readback` does today) and a fresh pinned suite would follow, before any C-1155 PIE.

## BK-94: synthetic gate and plan (proposal code, not an executor)

- `Scripts/Tools/plan_sevarog_definition_repair.py` is pure Python: no `unreal` import, no file or path access, no locks; it never executes a step. `plan_repair(envelope_result, snapshot, context, owner_source)` returns a refusal or a data-only plan, and `verify_readback(plan, after)` checks a synthetic after-snapshot.
- `Scripts/Tools/test_plan_sevarog_definition_repair.py` has 12 tests, all with in-memory synthetic values:
  - **Accepted plans:** a complete approval gives an in-place write plan (9 writes: all four Stats fields plus PhaseId and four Phase_1 values; update of the existing row, Phase_2 untouched, provenance records citing the owner message, `release_locks` last); a missing row is appended rather than recreated; a dry run needs no locks or backup and has no save step.
  - **Refused approvals:** absent, invalid or empty, partial, unresolved, rejected-without-alternative, and unknown-field approvals.
  - **Refused values:** out of range, NaN, bool or string, and a wrong PhaseId, even when the envelope result claims `valid`.
  - **Refused operations:** replace, delete-and-recreate, create or missing operation; a non-existent or different target; two Phase_1 rows.
  - **Refused write prerequisites:** missing backup, backup hash mismatch, a missing lock or token, no explicit write flag, a bad before-hash, and an unknown mode.
  - **Readback:** success releases the locks; an unsaved value, an unchanged hash, a moved asset, missing provenance, a removed other row or a duplicate Phase_1 each lead to restore-then-release; float32 rounding is tolerated and a real difference is not; readback is refused for a dry-run plan.
  - **Static contract:** the planner never touches Unreal, files or locks.

## BK-95: validation (exact)

- From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_plan_sevarog_definition_repair.py"` → `Ran 12 tests ... OK`.
- `python -I -m py_compile Scripts/Tools/plan_sevarog_definition_repair.py Scripts/Tools/test_plan_sevarog_definition_repair.py` → OK.
- `git diff --check` on both files → clean.
- Property lines re-verified: `RPGEncounterBinding.h:361/:381/:385`.

## Lead review and hotfix (2026-11-11)

Review of C-1310 found the proposal planner omitted the `Phases[Phase_1].PhaseId` assignment even though it required that approval and created a `Phase_1` row. That could have appended an unnamed row and left the provenance record incomplete. Fixed the planner and synthetic fixture to include the ninth write and a typed `name` provenance record; readback now checks the saved PhaseId and exact provenance values/types/source identity. Input validation also fails closed for malformed lists/paths/values and oversized numbers.

Focused post-hotfix validation: 12/12 tests, `py_compile` OK, scoped `git diff --check` clean. These results apply to the pure planner/tests only; the module remains a data-only proposal and is not an editor executor. The future executor must validate the same raw Owner envelope used to derive `owner_source`, in one bound operation, and must derive the source metadata from that validated message; accepting a separately supplied validation result and source object is not sufficient proof of binding. No Owner reply to X-1991 has arrived; no asset authoring or C-1155 run is authorized.

## Dependencies before implementation (lead)

1. The owner's X-1991 reply, captured as an approval envelope that validates with `--verify-source`.
2. An editor-side executor that implements exactly this plan: dry-run by default; write only with the gates; backup and hashes; property-level readback; restore on mismatch; try/finally lock release. It needs its own source contract (as BK-82 does for the helper) and a locked dry-run first.
3. A decision on the existing helper: either retire `ensure_bk56_60_sevarog_initial_phase.py` for this flow or keep it as the append-only path; the executor above supersedes it for repair.
4. After the write: encounter readback, pinned suite, then the BK-59 deferred C-1155 PIE.

## Owner responses still required (X-1991)

1. Approve or reject MaxHealth 1500 and MaxPosture 100, including the poise-to-posture mapping.
2. Regen delay and rate: 6 / 13, or alternatives.
3. Threshold 0.6, and Speed / Rate / Attack multipliers: 1.0 each, or alternatives.

Answers must use plain numbers; anything not stated explicitly stays unresolved.
