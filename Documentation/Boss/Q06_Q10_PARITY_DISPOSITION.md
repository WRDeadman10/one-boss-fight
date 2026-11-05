# Queue Q06–Q10 parity disposition

Date: 2026-11-05  
Mailbox order: C-848  
Scope: offline evidence reconciliation and A7 wording; no Lead-run comparator was repeated and no new PIE/build evidence was created.

## Q006 — Existing pair results

Used the already finalized, hash-verified receipt outcomes documented in `Docs/BossCombatReview/Execution/Codex/Q001_Q005_2026-11-05/Q01_Q05_STATUS.md`. This is a synthesis of existing results, not another comparator run:

| Pair | Identity / checks | Existing result | Evidence limit |
|---|---|---|---|
| A4 `_r2` | identity, final marker, terminal match; S9 jump/roll observations differ | FAIL | BUILD-219; predates H4 diagnostics |
| Dormant wake | identity, final marker, terminal, observables match | PASS | historical pair |
| Damage path | identity, final marker, terminal, observables match | PASS | BUILD-220; later than old 0/17 capture, but not a fresh D2 pair |
| Player death reset | identity, final marker, terminal match; checks 0004/0011/0017/0023 differ | FAIL | predates D2 health correction |
| Telegraph | identity, final marker, terminal match; checks 0010/0013/0020/0023 differ | FAIL | predates H5 typed timing observables |
| Boss HUD | 28/29 data checks; final marker, terminal and check 0009 differ | FAIL | predates D2 health correction |

## Q007 — Difference and cause reconciliation

- **A4 S9 jump/roll:** observed difference repeats in the old captured pair, but current source does not prove TraceGuard or tick order is causal. H4 adds diagnostic capture; fresh pair pending.
- **Death reset / HUD health threshold:** saved boss draft at 1500 versus legacy 2000 was the demonstrated health mismatch. Claude reports D2 changed the selected value to 2000, refreshed the manifest and selection hash, and retained four backups. C-847 confirms the live manifest passes the strict validator. Fresh death-reset/HUD pair is the regression witness and remains pending.
- **Telegraph:** the old receipt used exact comparisons on messages that include measured timings. H5 now emits typed raw seconds/ranges for one-frame comparison; old pair predates this change and cannot disposition the typed comparison.
- **Damage path:** Q01–Q05's BUILD-220 pair passes, superseding the older selected 0/17 inconclusive capture for that run only. No broader parity inference.
- **Dormant wake:** historical pair passes; does not establish full-route parity.

Source logs and receipt/report hashes are indexed in the Q01–Q05 evidence folder. Do not combine those historical observations with Claude's currently running BUILD-220+D2 pairs.

## Q008 — Root cause / scoped fix / regression witness

The health mismatch had a source-confirmed cause and a scoped asset correction (D2). The correction is not closed as a parity fix until fresh death-reset/HUD evidence confirms it. The A4 S9 root cause remains unproven; do not make a combat timing or attach-set change without a reproduced causal test. Q008 is therefore **partial, regression evidence pending**.

## Q009/Q010 — A7 refresh and decision wording

A7 is **open; not ready for retirement**. Keep the legacy route available as the control and empty-selection compatibility path. Consider retirement only after Lead accepts fresh matched parity and dispositions each captured difference, and package/Shipping, performance, compatibility and recovery gates are satisfied. The owner question remains: **“May the legacy encounter startup route be retired?”** No choice or production default change is implied.

## Writer compatibility fix called out per C-848

`Scripts/Tools/write_a4_parity_receipt.py`, `main()`: preserve an observable as already typed only when its dictionary contains both `value` and `comparison`; otherwise wrap the whole dict-valued A4 metric under `value`. This preserves legacy multi-field metrics and enables typed observables without rejecting the former shape. The Q01–Q05 receipt refresh exercised this compatibility behavior; no further Lead-result re-derivation is scheduled.

## Boundary and next cycle

Q006/Q007 historical reconciliation and Q009/Q010 wording are recorded. Q008 remains open pending the Lead's fresh regression evidence. Claude's BUILD-220+D2 A4, death-reset, telegraph, and HUD pair results are the next inputs; assess them in the next cycle without duplicating their runs. No Unreal, build, commit, or push was performed for this documentation update.
