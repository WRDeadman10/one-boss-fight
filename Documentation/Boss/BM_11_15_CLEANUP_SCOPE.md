# BM-11..15: destructive-cleanup characterization (lane BM, batch 3 of 10; KI-158..162)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_destructive_cleanup_scope.py`. **No tool was executed:** each would delete real files in shared folders. No source change. Narrowing the delete scope stays **owner-gated** (`OWNER_DECISIONS_PENDING.md`, row KI-158–KI-162).

## BM-11: current delete scope, pinned from source

| KI | Tool | Delete (line) | Target |
|---|---|---|---|
| KI-158 | `MakeBenchKit.ps1` | `Remove-Item $Kit -Recurse -Force` (`:23`) | `$OutDir\OneBossFight_BenchKit`, recursive |
| (new) | `MakeBenchKit.ps1` | `Remove-Item $z -Force` (`:76`, `-Zip` only) | `$OutDir\OneBossFight_BenchKit.zip`, a single file. **Not listed in KI-158.** It is the same ownership risk: an older zip may not be this run's. |
| KI-159 | `stitch_contact_sheets.py` | `os.remove(frame_path)` (`:50`) | `<prefix>_NN.png` frames joined onto `anim_dir` |
| KI-160 | `stitch_g2_g3_sheets.py` | `os.remove(frame_path)` (`:46`) | same pattern |
| KI-161 | `stitch_topdown_sheet.py` | `os.remove(f_path)` (`:54`) | listed frame names joined onto `anim_dir` |
| KI-162 | `stitch_two_row_sheets.py` | `os.remove(f_path)` (`:65`) | `<prefix>_<view>_NN.png` joined onto `anim_dir` |

Every stitch tool has exactly one single-file `os.remove` and no `shutil`. The only recursive delete is `MakeBenchKit`'s kit folder.

## BM-12: additional observations

- **`anim_dir` portability:** `stitch_contact_sheets.py:4` hard-codes an absolute path under another user's Windows profile. The other three use `os.path.abspath("Import/Boss01/Animations")`, which depends on the current directory. Neither is ownership-safe, and the hard-coded one is not portable. Recorded only; it is the same owner-gated row.
- **Wider inventory, not in KI-158..162:** 15 more scripts contain delete calls, mostly Editor PIE drivers (`Scripts/Editor/pie_*.py`, `retarget_mixamo_backstep.py`, `run_c1003_under_lock.py`, `render_mixamo_backstep_strip.py`). They were found by `grep` only and are not audited in this batch. BM-46..50 (the residual KI sweep) will classify them.

## BM-13: characterization tests

`python -m unittest discover -s Scripts/Tools -p test_destructive_cleanup_scope.py -v` → **`Ran 6 tests ... OK`**:
- **stitch tools:** exactly one delete each, `os.remove` at the pinned line, on `frame_path` or `f_path` joined onto `anim_dir`, with no `shutil`;
- **`MakeBenchKit`:** exactly two `Remove-Item` calls (`:23`, `:76`); the recursive one targets only `$OutDir\OneBossFight_BenchKit`; the zip delete is a single file and not recursive.

## BM-14: proposal for the owner row (no change made)

If approved, make each stitch tool delete only frames it created in this run (a manifest of written frames), and make `MakeBenchKit` refuse an existing kit or zip unless a `-Replace` switch is given. That would also cover the new zip finding.

## BM-15: limits

- Static characterization: the tests pin the **source text**, not runtime behavior. Line-number pins fail on any edit to those lines, and that is intended.
- No temp-folder execution: running the stitchers needs their image inputs, and the scripts write to fixed directories.
