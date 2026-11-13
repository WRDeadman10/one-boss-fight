# BQ-51..55: Queue BQ batch 11, Greystone notify readback, combat-trace and parry gate, F4b checklist

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Static only.** Nothing was run in the Editor or PIE. No asset was written, and no build or commit. All validation is in-process: 9/9 plus 4/4.

| Task | Result | Files |
|---|---|---|
| **BQ-51** (B5) notify readback validation | **new, awaiting review.** `verify_greystone_saved_wrapper_notifies.py` is a read-only Editor script for the **saved** `_Fit_Greystone` wrappers. C-1275a's `verify_greystone_wrapper_readback.py` only proves the copy into a transient montage. For each of the four wrappers it iterates `author_greystone_player.MONTAGES` directly, so there is no copied list to drift. Steps: (1) run the author's `source_readback`; (2) reload the saved package from disk (`reload_packages` with `ASSUME_POSITIVE`), failing closed if the API is missing, which applies the X-2359 lesson; (3) check that the wrapper references the Fit sequence; (4) compare the native notify rows (class, trigger, duration, track, slots, segment path@length) through the author's `compare_wrapper_notify_rows`. A failure in one wrapper does not stop the others, so the receipt is complete. It prints `WRAPPER PASS/FAIL` and `RESULT=PASS wrappers=4 saves=0` | `Scripts/Editor/verify_greystone_saved_wrapper_notifies.py` (new) |
| **BQ-52/53** (B6) combat-trace and parry confirmation on Greystone | **gate helper new; Lead wired both drivers (X-2362).** Finding: hit and parry drivers always used the mannequin, so Greystone hit/parry remained unproven. `greystone_pawn_gate.py` is a pure gate using `C1257_PLAYER_TARGET`, unset meaning mannequin and invalid meaning refuse. Both `pie_er_default_wiring_hits.py` and `pie_tier2_parry.py` now set the Development CVar before PIE, require the exact requested pawn class before counting the run, include `target=` in results, restore the CVar on exit, and store parry frames under a target-specific folder. The mannequin class is pinned to the class recognized by `RPGPlayerMovesSubsystem`. Static contract covers both integrations; no PIE run has occurred | `Scripts/Editor/greystone_pawn_gate.py`, `pie_er_default_wiring_hits.py`, `pie_tier2_parry.py` |
| **BQ-54** (B15) F4b checklist automation | **new, awaiting review.** `Scripts/Tools/f4b_checklist.py` is a library only. It maps each F4b item to its native test names and PIE drivers and verifies statically that they still exist. On the real tree, 6 of 7 items are static-ok: i-frame rejection, dead/stale, block/parry, selector, combo graph and phases. **F4b-7 Greystone visuals is a gap by design**: there is no native test, and it needs an ART/owner review. `summary()` always reports `live_verified=0`. It does not prove the live checks; it only proves nothing was renamed or lost | `Scripts/Tools/f4b_checklist.py` (new), `Scripts/Tools/test_f4b_checklist.py` (new, 4/4) |
| **BQ-55** | this report | |

**Contracts:** `Scripts/Editor/test_bq51_55_greystone_contracts.py`, **10/10 in-process** (includes the Lead integration hotfix); `Scripts/Tools/test_f4b_checklist.py`, **4/4 in-process**:
- **Readback:** read-only (no setter, save, delete, duplicate, wrapper create or create calls); the reload comes before the compare; the fail-closed refusal text; it covers the author's four wrappers through `author.MONTAGES`; `unreal` is imported only inside functions; the markers.
- **Gate:** env parsing, commands, possession cases, and that it matches the existing switch (the RM4 driver's env name and child class, and the C++ CVar name).

## Lead run (ENG, C-1155)

1. Editor with `-nosound`: `py Scripts/Editor/verify_greystone_saved_wrapper_notifies.py`. Expect `RESULT=PASS wrappers=4 saves=0`.
2. Run the wired hit and parry drivers twice, with `C1257_PLAYER_TARGET=mannequin` and `=greystone`. Compare the RESULT lines by target tag; each run must pass the exact possession guard.
3. Owner: the Greystone visual review (F4b-7, O4 context).

## Limits

- The F4b mapping is my judgement of which existing tests and drivers cover each item; the Lead may want to adjust it.
- `pie_phase_reset.py` covers dead/stale only partly: it exercises reset, but I did not confirm it asserts `RejectedStale` in PIE.

## Lead source-review follow-up (X-2362)

The initial gate allowed any non-Greystone class to count as the mannequin, which could false-pass if an unrelated pawn were possessed. The gate now requires the exact `BP_CombatPlayerCharacter_C` class identified by `RPGPlayerMovesSubsystem`, with an unexpected-class regression. Lead also wired the helper into both lead-run combat drivers so BQ-52/53 produce target-specific checks. The source contract covers target parsing, CVar set/restore, possession refusal, and result tagging in both drivers. Focused static suites passed 10/10 and 4/4. AG accepted the hotfix/integration in A-972; PIE proof still needs the C-1155 engine gate.
