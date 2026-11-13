# BK-186..190: lock acquisition scope, New-Item error handling and release-failure visibility (plus BK-181..185 corrections)

Assigned by X-2041 (lead Codex) to C (implementer), 2026-11-11. This is batch 4 of 20. New files only:
- `Scripts/Tools/test_bk186_190_c1155_lock_scope.py`
- this report

The BK-181..185 module and report keep their original evidence. The report only gains an append-only correction section that points here.

**Source-only. No PowerShell was executed, and no lock, log, temp file or asset was touched. All classes describe code, not observed runtime. X-1991 is still open.**

## Corrections to BK-181..185 (X-2041 / A-847)

1. **Unique tokens: 9 lock writers, not 10.** The 10th `NewGuid` hit is `Scripts/Tests/TestRunLeadPieDryRun.ps1`, which uses it only for a `__dry_run_<guid>` temp folder name and writes no lock. Test: `test_unique_tokens_are_nine_lock_writers`.
2. **`Scripts/RunLeadPie.ps1` acquires before its cleanup try.**
   - **Where:** `CreateNew` opens at `:59`, and the payload is written inside an inner `try` (`:61-66`) whose `finally` only disposes the stream. The `try` whose `finally` deletes the lock opens at `:69`, with the release at `:156-157`.
   - **Effect:** a serialization or write exception between `:59` and `:69` leaves the lock stranded.
   - **Status:** **documented only.** It is not edited, not run, and not separately assigned. It is up to the lead whether to assign a fix.
   - **Test:** `test_runleadpie_acquires_before_its_cleanup_try`.
3. **New-Item exclusivity now requires a hard failure.** `new_item_exclusivity()` returns:
   - `checked` only when the lock `New-Item` carries `-ErrorAction Stop` (also `-EA Stop`, `-ErrorAction:Stop`, or a quoted `'Stop'`), or when a global `$ErrorActionPreference='Stop'` is set **before** it;
   - `unchecked` when it can fail without stopping;
   - `forced` with `-Force`.

   All **15** current lock `New-Item` writers are `checked`. Test: `test_new_item_exclusivity_now_requires_error_stop`.

## BK-186: inventory re-verification

A second, independent method finds the same files: `os.walk` plus a raw-bytes search for `ENGINE_LOCK` or `C-1155`, where BK-181 used `Path.rglob` plus a text regex. It finds the **same 63** scripts and the **same 34** `owner_token` scripts.

The split is **63 = 34 (subset) + 28 (other lock writers) + 1 (test, non-writer)**, which gives **62 lock writers**.

## BK-187: New-Item error handling (adversarial cases)

- **11 single-line forms**, each classified as expected:
  - Stop as a parameter, as `-EA`, as `-ErrorAction:Stop`, or quoted;
  - none at all;
  - `SilentlyContinue`, `Continue` or `Ignore`;
  - `-Force`, alone or with Stop;
  - a `-Value` form.
- **Global Stop:** it counts only when it is set **before** the `New-Item`, and a per-call `SilentlyContinue` overrides it.
- **Several sites:** the worst site decides the result.
- **Not lock files:** directory or evidence `New-Item` calls are ignored.

## BK-188: lock acquisition vs the cleanup try (all 62 lock writers)

`cleanup_scope()` finds:
- the first lock write;
- the first lock `Remove-Item`;
- the `finally` that holds it;
- that `finally`'s own `try`, matched by equal indentation.

| Class | Count | Scripts |
|---|---|---|
| Acquire **inside** the cleanup try | **54** | includes all 34 subset runners |
| Acquire **before** the cleanup try (an exception in between leaves the lock behind) | **8** | `run_author_aura_boostlite_production` (`:30` / try `:34`), `run_author_boss01_heavyswordsocket` (`:30` / `:33`), `run_export_sfx_batch3` (`:30` / `:34`), `run_pie_ember_sword_probe_ag` (`:29` / `:32`), `run_restore_pack_heavyswordsocket` (`:30` / `:33`), `run_verify_aura_boostlite_roundtrip` (`:30` / `:34`), `Scripts/RunLeadPie.ps1` (`:59` / `:69`), `Scripts/Tools/run_c1249_editor_validation.ps1` (`:11` / `:12`) |

None of the 8 is in the `owner_token` subset.

## BK-189: release-failure visibility and stranded-lock implications

| Visibility of a failed release | Count | Implication |
|---|---|---|
| **Warned** (`catch` plus `Write-Warning`) | 34 | The lock may stay behind, but it is reported. A plain token mismatch is still silent (BK-149). |
| **Silenced** (`-ErrorAction SilentlyContinue`) | **6** | `c1230b`, `c1231b`, `c1232a`, `c1233a`, `c1237a`, `RunLeadPie`. **The lock can stay with no signal.** In the 5 `c123x` runners, `LOCKS_RELEASED=$created.Count` still reports it released. |
| **Terminating** (bare `Remove-Item`) | **22** | The error ends the `finally` block, skipping any later lock release in that block, such as the second lock. |

Other stranded-lock paths:
- **Unguarded ownership reads (4 scripts):** `run_aura_graph_authoring`, `run_aura_graph_commandlet`, `run_c1210_build_suite`, `run_c1210_ember_aura_definition`. `Get-Content | ConvertFrom-Json` runs in `finally` outside any `try`, so a bad or foreign first lock aborts the release loop.
- **False release count:** 34 runners report the created count as released. In the 5 `c123x` runners this combines with a silenced failure.

**Other gaps the agents found (documented, not tested):**
- In the `be`/`bf`-style runners, a lock created by `CreateNew` whose content write then fails never reaches `$created.Add`, so it is left behind with empty or partial content.
- A hard process kill skips any `finally`.

## Cross-check

Each of the 62 lock writers was also read by its own independent read-only agent, using written definitions for acquisition placement, write line, cleanup-try line, release visibility and New-Item exclusivity. **They agreed with the classifier on all 310 checks** (62 scripts × 5 fields).

## BK-190: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk186_190_c1155_lock_scope.py" -v` → **`Ran 12 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk181Corrections` (3) | 9 tokens; the RunLeadPie scope; New-Item checked 15 / unchecked or forced 0. |
| `Bk186InventoryReverification` (2) | Independent re-derivation of 63 and 34; the 63 / 34 / 28 / 1 split; 62 writers. |
| `Bk187NewItemAdversarial` (3) | 11 forms; global-Stop ordering and override; the worst site wins; non-lock `New-Item` ignored. |
| `Bk188AcquisitionScope` (2) | 8 before / 54 inside; none in the subset; synthetic inside, before and no-release cases. |
| `Bk189FailureVisibility` (2) | 34 / 6 / 22 with the silenced list frozen; 4 unguarded ownership reads; 34 created-count reports; 5 silenced and counted. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- The BK-181..185 suite still passes, unchanged.

## Limits and scope caveats

- The try/finally pairing uses indentation; these scripts are consistently formatted, and the agents confirmed every pairing. An unusually formatted script could be misread, and a frozen-table failure would flag it.
- `Scripts/**/*.ps1` only. A-847 notes 32 non-`.ps1` files under `Scripts/` (for example `.py`) that mention `ENGINE_LOCK`; they are out of scope here.
- No runtime claims: interruption windows, delete failures and hard kills are code paths, not observed events.

## Correction (append-only, X-2043, 2026-11-12)

The BK-189 "terminating" row above, with 22 bare `Remove-Item` releases, was wrong for 11 of them. The original text and tests are kept as published. Regressions: `Scripts/Tools/test_bk186_190_hotfix_error_semantics.py` (`Ran 7 tests ... OK`).

- **Terminating (effective `$ErrorActionPreference = 'Stop'`), 11 scripts:**
  - **Release both C-1155 locks (7):** `run_aura_graph_authoring`, `run_aura_graph_commandlet`, `run_author_aura_boostlite_production`, `run_c1210_build_suite`, `run_c1210_ember_aura_definition`, `run_export_sfx_batch3`, `run_verify_aura_boostlite_roundtrip`. **Only for these 7 does the claim hold that a failed release ends `finally` and skips the later lock release.**
  - **Release one lock (4):** `run_author_boss01_heavyswordsocket`, `run_pie_ember_sword_probe_ag`, `run_restore_pack_heavyswordsocket`, `Scripts/Tools/run_c1249_editor_validation`. A failure strands only that lock.
- **Non-terminating (no preference set, so PowerShell's default `Continue`), 11 scripts:** `run_apply_notifies`, `run_author_boss01_greatsword_sockets`, `run_create_phase_two_aura_boost`, `run_create_phase_two_aura_boost_lite`, `run_export_sfx_candidates`, `run_export_sfx_parry_addendum`, `run_inspect_boss01_attach_transforms`, `run_inspect_props`, `run_reauthor_guard_counter_c1046`, `run_rebuild_ppm`, `run_verify_notifies`. A failed `Remove-Item` writes an error record and **`finally` continues**; the lock may stay, but no later release is skipped.
- **Corrected BK-189 counts:** warned 34, silenced 6, **terminating 11**, **non-terminating 11**.
- **Unchanged:** the 4 unguarded-ownership-read scripts are all in the Stop group, so their "aborts the release loop" claim stands. The "34 report the created count as released" and "5 c123x silenced and counted" claims are unaffected.
- **Method:** `effective_preference_at()` takes the last script-level `$ErrorActionPreference` assignment before the release line, and otherwise the default `Continue`. This was checked for both groups and on synthetic text. It does not model runtime callers that set a preference before invoking the script.
