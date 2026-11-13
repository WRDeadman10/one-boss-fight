# BQ-21..25: Queue BQ batch 5, benchmark receipts and Shipping hygiene

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**The C++ is written but NOT compiled or run.** Binary acceptance needs the Lead's C-1155 build and suite. The Python validator ran only as in-process temp-fixture tests. No engine, editor, PIE, benchmark, tool CLI, asset change or commit.

| Task | Result | Files |
|---|---|---|
| **BQ-21** per-run identity in the summary producer | **new, awaiting review.** `ARPGBenchmarkRunner` adds a nested `run_identity` object to `summary.json`. It is additive: the flat fields existing consumers read are unchanged. Fields: `schema_hint` ("BENCHMARK_RUN_RECEIPT_V1 (proposal)"), `run_id` (a new GUID, hex digits, matches the schema pattern), `completed_at_utc` (ISO 8601, Z), `build_version` (`FApp::GetBuildVersion`), `engine_changelist`, `build_configuration`, `session_type` and `host_fingerprint_md5`. `session_type` comes from the pure seam `RPGBenchmarkReceipt::ClassifySession` reading Windows `SESSIONNAME`: Console gives console, RDP-* gives remote, anything else gives unknown, never a guessed console. **Privacy:** the machine name is never written in clear, only an MD5 fingerprint, which tells runs on one host apart. MD5 of a short name is not anonymisation against a determined reader, but the summary is local evidence and never public. **Not included:** the binary and package hashes, which belong to intake (hashing the package mid-run would distort the measurement), and `started_at_utc`. Test `OneBossFight.Benchmark.ReceiptSessionType` | `Benchmark/RPGBenchmarkRunner.h/.cpp`, `Tests/RPGBenchmarkReceiptTests.cpp` (new) |
| **BQ-22** receipt validator with in-process fixtures | **new, awaiting review.** `Scripts/Tools/validate_benchmark_run_receipt.py` is library only: no CLI and no file writes. `validate(receipt, schema=None, root=None)` returns refusal reasons. Structural pass: a dependency-free JSON Schema subset read from `BENCHMARK_RUN_RECEIPT_V1.schema.json` itself. Any keyword it does not enforce is a refusal (fail-closed, so a rule can never be skipped silently). Semantic pass, the BI X03 negative list: UTC timestamps ending in Z, no backwards time, a target claim needs a console session, a valid verdict carries no reasons, and artifact paths stay under the root (no `..`, absolute path or symlink escape), with byte count and SHA-256 checked when a root is given. **Evidence:** `python -m unittest Scripts/Tools/test_validate_benchmark_run_receipt.py` ran 23 tests, OK with 1 skipped. The skipped one is the symlink-escape case, because creating symlinks needs extra privileges on this Windows host. That case is **unverified here**; the code path exists | `Scripts/Tools/validate_benchmark_run_receipt.py` (new), `Scripts/Tools/test_validate_benchmark_run_receipt.py` (new) |
| **BQ-23** KI-168 Shipping-visible console controls | **review done, see the table below.** Source finding: there are **seven** controls now, not six, because the BQ-17 `rpg.Boss.ProjectHitReaction` (C-1569) is also registered outside any `!UE_BUILD_SHIPPING` guard. This is a source classification only, not binary proof (KI-168 remains open for the packaged-binary check) | this report |
| **BQ-24** KI-108 GPU-cost attribution | **read-only notes, see below.** No run | this report |
| **BQ-25** | this report | |

## BQ-23: disposition of the Shipping-visible controls (source only)

| Control | Default | What it does | Player-facing? | Disposition (proposed) |
|---|---|---|---|---|
| `rpg.BossOverlay` | 0 | framework boss debug overlay and log | no, debug | **Guard** with `!UE_BUILD_SHIPPING`. Pure QA; a release build needs no overlay |
| `rpg.CloseTelegraph` | 0.4 | A1/A3 telegraph play-rate target (KI-102) | indirectly, it is live tuning | **Keep for now.** Gameplay pacing that the owner set as a default (2026-10-24). Freeze the value into data and guard it once the authored clips land |
| `rpg.Build` | empty | Gate 3 player build choice | yes, until a menu exists | **Keep.** It is the only selection route today. Replace it with UI before release |
| `rpg.CameraDebug` | 0 | draws camera debug geometry | no, debug | **Guard** with `!UE_BUILD_SHIPPING` |
| `rpg.Legend` | 1 | legend pass effects on/off | yes, a comfort option | **Keep.** Accessibility (hit stop, slow motion, shake); belongs in a settings menu later |
| `rpg.LegendShakeScale` | 1 | camera shake multiplier | yes, accessibility | **Keep.** Accessibility; belongs in a settings menu later |
| `rpg.Boss.ProjectHitReaction` (BQ-17) | 0 | A4/A5/A6 hit reaction opt-in | no, experimental | **Guard** with `!UE_BUILD_SHIPPING` until design adopts it. I did not change it, because the Lead accepted BQ-17 as is (X-2341). Lead's call |

The three "Guard" rows are proposals, not code changes. Each guard is a small source edit, but a Shipping build or package check is needed to prove it (ENG). The disposition record of C-702 and `TEST_HOOKS.md` is unchanged until the Lead decides.

## BQ-24: GPU-cost attribution from existing evidence (read-only, `PERFORMANCE_LOG.md`)

1. **Shipping-configuration evidence is thin.** The only valid Shipping capture is round 1 (2026-10-24): RTX 3060 proxy, console session, 1080p. It shows 28 to 29 fps average, p99 about 40 ms, GPU p99 about 39 to 41 ms, and game and render threads at 3 to 4 ms, so the frame is GPU bound. The empty arena alone ran at 33 fps, which points at the arena or render settings, not the fight. A later Shipping run from Remote Desktop is invalid (Remote Display Adapter) and attributes nothing.
2. **The per-pass split comes from Development, not Shipping.** Round 2 `ProfileGPU`, one frame, 22.4 ms GPU: virtual shadow maps 8.2 ms (projection mask 4.1, non-Nanite raster 2.9), deferred lights 6.6 ms (unbatched 2.0), volumetric clouds 5.3 ms, post 4.1 ms (TSR 3.5), base pass 0.4 ms, Nanite 0.3 ms, no Lumen pass visible. Treating these as Shipping costs is an inference: Shipping has the same renderer, but the split is unmeasured there.
3. **Attribution that holds across rounds.** The 12 shadow-casting brazier lights are the dominant arena cost: lights off gave +30 fps and shadows off +23 fps in round 2's trusted block. That fits the VSM-plus-deferred-lights share above (about 15 of 22 ms). Fire particles, mists, dressing and embers were each within noise. Volumetric clouds (about 5 ms) are the next distinct item; round 6 looked at the cloud sample CVars.
4. **Caveats.** Round 2's first ten experiments are not trusted (machine-state shift, noted in the log). All numbers come from the RTX 3060 proxy, not the RTX 2060 Super target. Performance is parked (owner 2026-11-05), with DLSS as the planned fix.
5. **What would close it (ENG, not requested):** one Shipping `ProfileGPU` or Insights capture on the target class with a receipt that passes BQ-22.

## Gates still open

1. **The Lead's C-1155 build plus suite** for `Benchmark.ReceiptSessionType` and the summary writer change.
2. **ENG:** a benchmark run to see `run_identity` in a real summary; the symlink-escape test on a host that allows symlinks.
3. **Lead decisions:** adopting BENCHMARK_RUN_RECEIPT_V1 (still a proposal) and the three proposed guards (BQ-23).
4. **KI-168** stays open: no packaged-binary check.

**Earlier uncommitted edits** in the touched C++ files were preserved; my edits were insertions only.
