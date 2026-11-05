# Temporary-directory cleanup audit (S172)

Static review of Python scratch fixtures and scripts that create or remove temporary files. No scripts, tests, Unreal Editor, or build were run.

## Scoped temporary roots

| File:lines | Cleanup behavior |
|---|---|
| `Scripts/blender_exec.py:46-81` | Fallback runner creates its script and result JSON inside a `TemporaryDirectory` context; cleanup targets that unique root after the subprocess and result read complete. |
| `Scripts/Tests/test_build_fight_policy.py:18-19` | Each test case owns a `TemporaryDirectory` and registers its `cleanup` with unittest, including teardown on failure. |
| `Scripts/Tools/test_*.py` | All `TemporaryDirectory` occurrences found in the offline tool fixtures are context-managed. Files are created beneath that returned root; no fixture recursively removes a repository or caller-supplied path. |
| `Scripts/Tools/atomic_io.py:12,28,50,54,70,74` | Atomic write helpers create sibling temporary files in the target directory and unlink only that helper-created path after publication or failure. These are temporary files, not directory roots. Abrupt process termination can leave a `.tmp` sibling; no startup scavenger deletes unrelated files. |

## Cleanup outside owned temporary roots

| File:line | Finding |
|---|---|
| `Scripts/MakeBenchKit.ps1:24` | Recursively deletes the pre-existing `$OutDir\OneBossFight_BenchKit` before assembling a new kit. This output directory is not a temporary root created by the current invocation; an existing kit can be lost. Require an explicit overwrite policy or stage into a unique temporary directory and publish after success. |
| `Scripts/stitch_contact_sheets.py:50` | Deletes each matching `temp_cs_*` frame from a fixed former-user `Import/Boss01/Animations` directory after reading it. The script did not create or establish ownership of the frame in this invocation. |
| `Scripts/stitch_g2_g3_sheets.py:46` | Deletes matched `temp_cs_*` frames from the project animation directory without proving they belong to this run. |
| `Scripts/stitch_topdown_sheet.py:54` | Deletes fixed-name `temp_topdown_*.png` inputs from the animation directory without proving this invocation created them. |
| `Scripts/stitch_two_row_sheets.py:65` | Deletes matched frame inputs from the shared animation directory without an invocation-owned temp root. |

## Disposition

Python `TemporaryDirectory` uses and atomic-I/O temporary sibling cleanup are scoped to paths created by the operation. The broader cleanup acceptance is **not met**: the benchmark-kit builder removes a persistent output directory, and four legacy image stitchers consume and delete shared input frames. Lead recorded these as low-severity KI-158–KI-162; this audit makes no behavioral changes. No tests/build/Editor/runtime were run.
