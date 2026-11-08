# AU-C11–C15 — aura capture diagnosis and evidence boundary

**Status:** AU-C11–C14 complete offline; AU-C15 remains Lead PIE pending. Codex did not launch Unreal or edit either aura asset.

## What the existing evidence shows

- C-1075 reports the DATA-route approved capture at mean gray 0.1 and the legacy candidate readback inactive. C-1077 reports the hotfixed paired rerun rendered black on both routes. These are separate facts: pixel darkness and runtime candidate readback do not establish each other's cause. See `AO_C01_C05_CAMERA_AURA_DODGE_READINESS.md` and `AO_C16_C20_AURA_COMPARISON_AUDIT.md`.
- The checked-in Lead logs under `Docs/BossCombatReview/Execution/Claude/P_C1072_AURACOMPARE/` show the DATA route reached `FRAME_BRIGHTNESS` and decoded three warmup frames plus the approved frame at mean gray 0.000; the retained approved frame then stopped at the brightness floor. The manifest in those older logs confirms the approved Niagara asset readback and FollowCamera/pivot values. It does not prove a candidate comparison or a cause for black output.
- The current driver serializes HighResShot requests, waits for a stable file, decodes pixel data and rejects retained frames below mean gray 5. The decoder previously accepted valid pixel payloads with a missing IEND terminator; this is now rejected. Runtime visibility and owner visual disposition remain unproven.

## AU-C11–C14 offline changes

- `aura_png_metrics.mean_gray` now requires a zero-length IEND chunk. Missing files, truncated chunks, malformed payloads, black frames, valid dark frames, and usable frames have distinct test coverage. Brightness remains a capture-quality gate; it is not treated as a gameplay or exposure fix.
- Aura frame manifests now identify run, route, phase, unique capture ID, health, camera/pivot, PNG existence, mean gray, and SHA-256. Request markers carry the same run/route/phase/capture identity. Request timeout, unreadable/incomplete PNG, and below-floor retained image emit `CAPTURE_FAILURE` with the stopping reason.
- The approved-only mode exits after the approved frame before loading or swapping the candidate. Paired mode retains its transient swap. `finish()` restores the original asset and verifies the runtime readback; restore mismatch is an explicit error. No editor-property mutation or asset save was introduced.
- Verification: `python -m unittest Scripts.Editor.test_aura_png_metrics Scripts.Editor.test_pie_aura_comparison_contract -q` — 13 tests passed; `py_compile` passed; `git diff --check` passed (only existing LF/CRLF notices).

## AU-C15 Lead return

Run `pie_aura_comparison.py` on the DATA-default route with `AURA_COMPARE_APPROVED_ONLY=1` and a fresh `AURA_COMPARE_RUN`. Return the run log, manifest, each PNG and SHA-256, route witness, health fraction, camera/pivot, and explicit stop reason. If no retained frame clears the brightness floor or PNG decoding fails, stop there; do not run the paired candidate comparison. Owner visual judgment remains separate from all numeric capture metrics.
