# BQ-46..50: Queue BQ batch 10, Greystone `_RM` roll write, repoint and RM4 driver

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Static only.** Nothing was run in the Editor. No asset was written, and no engine, PIE or commit. Contracts ran in-process only.

**Context:**
- C-1285 found that the earlier retargets baked travel into `pelvis`, because the Root chain FK mode was None.
- C-1289 then re-authored and checked the Greystone backstep: RM4 **PASS**, 99.35 cm, scaled +2.75%.
- The quick roll is still **OPEN**: the `_Grey` roll measured 0.00 cm.
- The fix chain is to write the `_RM` rolls, then repoint the child to them, then run the RM4 paired trial again.

| Task | Result | Files |
|---|---|---|
| **BQ-46** (B1) `_RM` roll write script | **reconciled, already delivered** by BK-1. `retarget_greystone_pack_rolls_rm.py` is dry-run by default and needs `--write` to change anything. It covers the two inventory rolls only, uses a duplicated target IK rig and a new retargeter with Root to Root FK `GLOBALLY_SCALED`, and writes `_RM` sequences and montages under `/Game/OneBossFight/Player/Greystone/RootMotion/`. It refuses existing outputs, proves nonzero root XY travel, writes a manifest, and never edits `_Grey` or pack assets. Contract `Scripts/Tools/test_bk1_greystone_roll_rm_contract.py` rerun in-process: **5/5** | none |
| **BQ-47** (B2) repoint script | **new.** `repoint_greystone_rolls_rm.py` points `BP_GreystoneERPlayer`'s `URPGDodgeTiming` `QuickMontage` and `FullMontage` from the `_Grey` montages to the `_RM` copies. It is a **dry run by default** (`RESULT=DRY_RUN`); write needs `-RMRepointWrite` on the Editor command line. Write mode refuses when: an `_RM` montage is missing or is not an `AnimMontage`; the child has no `URPGDodgeTiming` or has two; a current value is neither the expected `_Grey` path nor the `_RM` path (it never overwrites an unknown value). It is idempotent: already-repointed fields are a no-op. It changes only those two fields, then compiles, saves the child Blueprint once, explicitly reloads its package, and reads back. The receipt prints `READBACK ... rollback_to=<_Grey path>`. It never deletes, duplicates, renames or creates anything. The pure seam is `plan()`, which returns repoint, already or refuse | `Scripts/Editor/repoint_greystone_rolls_rm.py` (new) |
| **BQ-48** (B3) RM4 paired-trial driver | **reconciled, already delivered.** `pie_greystone_root_motion.py` runs once with `C1257_PLAYER_TARGET=mannequin` and once with `=greystone`: 5 trials each of backstep and quick roll, in-band checks, and `MONTAGE_NOT_OBSERVED` refusals. It reads the expected montage names from the possessed pawn, so after BQ-47 it measures the `_RM` quick roll with no driver change. **Pass band:** the quick roll scaled 248-334 cm, within 10% after the root ratio (C-1289 Decision 1), against the mannequin's 264.28 cm | none |
| **BQ-49** static tests | **new:** `test_repoint_greystone_rolls_rm_contract.py`, **8/8 in-process**. It checks: `unreal` is imported only inside functions; the `_RM` paths are derived exactly as the retarget script derives them (`OUT_ROOT/Montages/<kind>/<grey name>_RM`, parsed from its source); the `_Grey` paths and child path equal `author_greystone_player.py`'s `CHILD_FIELDS` and `ALLOWLIST`; the `plan()` cases (repoint, already, mixed, refuse on an unknown or missing value); the dry-run return comes before the only setter; no destructive calls, and exactly one save and one setter; the snake_case property names; the readback and rollback receipt | `Scripts/Editor/test_repoint_greystone_rolls_rm_contract.py` (new) |
| **BQ-50** | this report | |

## Lead run order (ENG, C-1155: locks, no Unreal process, `-nosound`)

1. `retarget_greystone_pack_rolls_rm.py`: dry run, then `--write`. Keep its manifest (root XY travel must be nonzero).
2. `repoint_greystone_rolls_rm.py`: dry run (expect `would_repoint=2`), then `-RMRepointWrite` (expect `RESULT=PASS repointed=2 saves=1` and two `READBACK` lines).
3. Build and run the pinned suite.
4. Run the RM4 pair, `pie_greystone_root_motion.py` with mannequin then greystone. Expect the quick roll in band in 5/5 trials and the backstep still passing.
5. On failure, roll back by setting the two `rollback_to` paths again. The `_RM` assets stay, isolated and unreferenced.

## Unverified until the Editor run

- **Property name form.** The repoint script uses `quick_montage` / `full_montage`, the documented snake_case names. `author_greystone_player.readback_child_bp` uses `quickMontage` (first letter lowercased), and C-1289's readback reportedly passed with it, which suggests UE also accepts that form. Which form is correct is unproven until step 2's dry run prints the current values.
- **The write flag.** Whether `-RMRepointWrite` reaches `get_command_line()` with the Lead's launch wrapper. It uses the same mechanism as BK-1's `--write`.
- **Root-motion flags** on the `_RM` montages are not re-checked here. They are proven by the BK-1 manifest and by RM4.

## Lead source-review follow-up (X-2358)

AG's A-969 review accepted the original Batch 10 handoff at source/planning level. Lead review then found that `load_asset()` alone may return the already-loaded in-memory Blueprint and therefore does not establish a disk-package reload. The repoint write path now requires `EditorLoadingAndSavingUtils.reload_packages()` with `ASSUME_POSITIVE` after the one save and before readback; the static contract pins the reload ordering and refusal path. AG independently accepted this hotfix in A-970, and the focused contract passed 8/8. Actual Editor execution, property-name confirmation, build/suite, and RM4 remain ENG-gated under C-1155.

**Owner/default note:** the player default stays the mannequin. This changes only the Greystone child that is used behind its switch (O4).
