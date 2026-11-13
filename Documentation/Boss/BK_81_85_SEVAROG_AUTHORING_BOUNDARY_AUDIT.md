# BK-81..85: Sevarog authoring boundary, fail-closed audit

Assigned by X-1998 (lead Codex) to C (implementer), 2026-11-11. New files only; no existing author, runner, driver, helper or validator file edited; no Unreal, build, PIE, asset access or writes, or locks.

## BK-81: every path that can create or mutate the encounter or the draft's Phase_1

| Script | Can write | Gate | Routes through the hardened helper? | Write before validation? |
|---|---|---|---|---|
| `ensure_bk56_60_sevarog_initial_phase.py` (hardened helper) | Appends `Phases[Phase_1]` to `DA_Boss_Sevarog_Draft` and saves (`:73-74`) | `BK56_AUTHOR_PHASE_WRITE=1` (`:13`, `require(WRITE)` `:64`) and four explicit `BK56_PHASE_*` env values (`approved_inputs` `:40-50`) | it is the guard | No. An existing row is validated and the script returns without writing (`:58-62`); a new row is validated (`:49`) before `set_editor_property("phases")` (`:73`) and the save (`:74`) |
| `run_bk56_60_deferred_selection.ps1` | Calls the helper (`:119-123`) and the encounter author | Locks, backups | yes | It sets `BK56_AUTHOR_PHASE_WRITE=1` but never supplies `BK56_PHASE_*`, so creating a row fails closed until the values are provided explicitly |
| `author_framework_encounter_definition.py` | Creates and saves `DA_Sevarog_Framework_Encounter` (`:104-124`) | `--write` / `FRAMEWORK_ENCOUNTER_WRITE=1` (`:18`); refuses an existing target (`:103`) | n/a: it never mutates the boss definition (only `asset` and a local `guid` are written) | **Yes, for its dependency.** The write branch creates and saves the encounter without checking that the boss definition has a valid `Phase_1` row or valid Stats; `Phase_1` presence is checked only in `--readback` (`:63`), after the save |
| `author_sevarog_draft_cards.py` | Creates `DA_Boss_Sevarog_Draft` with the cards and profile (`:857-912`) | **Writes by default**; only `--dry-run` / `SEVAROG_DRY_RUN=1` suppresses (`:1059`); refuses any existing target (`:1035-1036`) | n/a: `DRAFT_DEFINITION_FIELDS` has no `phases` or `stats` keys | Creates the draft with no Phase_1 row and zero Stats, the X-1988 state; the helper is then required |
| `replace_sevarog_draft_assets.py` | Deletes the draft set, `DA_Boss_Sevarog_Draft` included (`:53`) | `--write` on the command line (`:31`); refuses referenced assets | n/a | Deletion, then re-creation by the card author, would recreate the zero-Stats / no-Phase_1 draft; refused while the encounter references it |

### Bypass verdict

No script writes a `Phase_1` row except the hardened helper, and the helper cannot write a zero threshold, an assumed multiplier, or over an invalid existing row. **The Phase_1 guard has no bypass.**

Three boundary gaps remain (not bypasses):
1. **Encounter author writes before validating its dependency.** `author_framework_encounter_definition.py:103-124` saves the encounter whatever the state of the boss definition's Phase_1 and Stats. The encounter that exists today was created this way (Run_072640) while the draft had no Phase_1.
2. **No sanctioned repair path for an existing invalid row.** The current draft's Phase_1 (`0.0` threshold, unapproved `1.0` multipliers) is refused by the helper on every run, and no script may replace an existing row; repair would need a new explicit, owner-value-driven step. Delete-and-recreate is not allowed (CLAUDE.md: never delete and recreate referenced assets).
3. **No Stats writer exists.** No script authors `Stats` on the draft, so the owner's X-1991 Stats choices currently have no authoring path.

## BK-82: source contract (new: `Scripts/Tools/test_bk81_85_sevarog_authoring_boundary_contract.py`, 12 tests, AST only)

Helper:
- No phase field is set from a literal, and no numeric literal is written through `set_editor_property`.
- No zero-threshold or identity-default pattern appears.
- `os.environ.get` is never given a default.
- `INPUTS` covers exactly the four phase fields, each from a `BK56_PHASE_*` env var.
- `approved_inputs` requires presence and a numeric value, and validates.
- `validate_values` enforces a finite value with `0 < fraction <= 1` and positive finite multipliers.
- The existing-row branch validates and returns with no save and no phases write.
- On the new-row path the WRITE gate comes before the inputs, the inputs before the phases write, and the phases write before the single save.

Others:
- The runner never injects `BK56_PHASE_*` values.
- The card author's definition fields contain no `phases` or `stats`, and it never overwrites.
- The encounter author writes only its new asset (plus the local Guid).
- The encounter author's missing dependency pre-validation is pinned (gap 1), so a change is noticed.
- The replacer deletes only with `--write` and refuses referenced assets.

## BK-83: initial adversarial validator snapshot (historical pre-hotfix; new: `Scripts/Tools/test_validate_pending_definition_inputs_adversarial.py`, 14 tests)

**Defenses that hold (9):**
- Path traversal variants are refused: backslash `..`, `Docs/../x`, UNC paths, drive-relative paths, `./../x`, absolute paths and the empty path. A benign `./` segment is allowed.
- Source drift on the cited line, and an excerpt on the wrong line, are refused under `--verify-sources`.
- Bad line-number shapes are refused: 0, -1, bool, str, None and float.
- Unknown top-level approval claims are refused.
- Status case and whitespace variants are refused.
- Uppercase, padded and short hashes are refused.
- Non-object manifests and non-list rows are refused.

**At this initial snapshot, five gaps were pinned as `expectedFailure`.** They were accepted at that time and needed refusal; all were in `validate_pending_definition_inputs.py`:
1. **Non-finite values.** NaN and ±Infinity pass the float check. The `float value must be a number` branch needs `math.isfinite`; note that `json.loads` accepts `NaN` and `Infinity` by default.
2. **Truncated excerpts.** A fragment such as `0.6` passes because the line check is a substring test (`excerpt not in lines[line_no - 1]`). It should compare against the stripped cited line exactly.
3. **Unknown `field_path` rows.** A row such as `Owner.Approval` with a value is accepted. Only `REQUIRED_FIELDS` coverage is enforced, so the field set should be checked exactly.
4. **Duplicate JSON keys.** `{"manifest_state": "APPROVED", "manifest_state": "PENDING"}` exits 0 because `main` uses `json.loads` without an `object_pairs_hook` that rejects duplicates.
5. **Unchecked candidate.** A string, NaN, bool or None candidate passes.

## BK-84: validation at the initial snapshot

- From `Scripts/Tools`:
  - `discover -p "test_bk81_85_sevarog_authoring_boundary_contract.py"` → `Ran 12 ... OK`.
  - `discover -p "test_validate_pending_definition_inputs_adversarial.py"` → `Ran 14 ... OK (expected failures=5)`.
  - `discover -p "test_validate_pending_definition_inputs.py"` (existing) → `Ran 15 ... OK`.
- `python -I Scripts/Tools/validate_pending_definition_inputs.py Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json --verify-sources` → `VALID counts={'SOURCE_BACKED': 1, 'SOURCE_BACKED_AWAITING_OWNER': 3, 'OWNER_DECISION_REQUIRED': 5}`.
- `py_compile` on both new files → OK.
- `git diff --check` → clean.

## Changed files

- `Scripts/Tools/test_bk81_85_sevarog_authoring_boundary_contract.py` (new).
- `Scripts/Tools/test_validate_pending_definition_inputs_adversarial.py` (new).
- This report (new).

## Limits

- All checks are static, plus the manifest validator. Live behavior of the helper and the authors still needs a C-1155 run after the owner's choices.
- The card author writing by default is a sharp edge; its refuse-if-exists guard makes it safe while the draft exists.

## Remaining owner decisions (X-1991, unchanged)

1. Approve 1500 / 100 from SevarogEnemyInfo, including the poise-to-posture mapping.
2. Posture regen: 6 s / 13 per s, or other values.
3. Phase_1 threshold 0.6, plus the three multipliers.

Before authoring, gap 2 (no repair path for the existing invalid row) and gap 3 (no Stats writer) need a lead-designed step.

## Lead review and hotfix

Codex accepted the path audit and found five confirmed validator gaps in the independent test-first cases: non-finite numbers, truncated excerpt matches, unknown `field_path` rows, duplicate JSON keys, and untyped candidates. The validator now rejects all five, rejects path resolutions escaping the selected repository root, and handles extremely large integers without raising. Excerpt evidence must equal the cited line after trimming outer whitespace. The tests are now ordinary passing tests (15/15); original validator tests pass 15/15 and the live pending manifest's exact source/hash/line verification is VALID. Added regressions also confirm unhashable unknown field paths fail closed without raising.

Codex also closed boundary gap 1: `author_framework_encounter_definition.py` now checks the referenced boss Stats and exactly one valid Phase_1 before creating the encounter asset or claiming readback. The new AST guard passes 2/2. Validator `py_compile` and scoped `git diff --check` pass. No Unreal, build, asset access/write, or lock operation was performed. The existing draft row still needs a non-destructive approved repair path and a Stats authoring path; Owner choices in X-1991 remain required before authoring or C-1155.
