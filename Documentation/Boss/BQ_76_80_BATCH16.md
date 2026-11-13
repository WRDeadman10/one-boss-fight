# BQ-76..80: Queue BQ batch 16, performance attribution, benchmark triage and shader-failure triage plans

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Plans only.** Nothing was run, packaged or benchmarked. Performance is parked (owner 2026-11-05), with DLSS as the planned fix. These plans make the next round decisive when the owner reopens it. Hardware is O6. The target is the RTX 2060 Super; all existing evidence is from the RTX 3060 proxy.

## BQ-76 (D3): performance attribution test plan

**What we know** (`PERFORMANCE_LOG.md`, BQ-24): the frame is GPU bound (game and render threads 3-4 ms).
- **Round 2 ProfileGPU, one Development frame of 22.4 ms:** VSM 8.2, deferred lights 6.6, volumetric clouds 5.3, post 4.1 (TSR 3.5). These reported pass values total 24.2 ms, exceeding the 22.4 ms frame; treat them as non-additive/unreconciled attribution labels until a fresh capture establishes nesting and total accounting. Do not use their sum as a frame budget.
- **Round 2 trusted block:** brazier lights off gave +30 fps; their shadows off gave +23 fps; the other arena content was within noise.
- **Round 6 (BUILD-240, data route):** TSR 26.7 fps / 45.7 ms p99; DLSS Performance 35.2 / 35.9.

**Goal:** a per-pass cost table measured in **Shipping-like** conditions on the target class. Every number must carry a BQ-21 `run_identity` block, and each run's receipt must pass the BQ-22 validator.

| Step | Run (existing tools) | Pass/keep criteria |
|---|---|---|
| A1 | Anchor: `RunBenchmark.ps1`, fight mode, 3x baseline, same build | Anchor drift ≤ 5% (Round 5 reached 4.1%); otherwise the session is invalid (Round 2 lesson) |
| A2 | `-RPGBenchmarkProfileGPUAt` at two fixed fight times | Pass table recorded; VSM, lights, clouds and post each as a share of GPU ms |
| A3 | One-change arms through `-RPGBenchmarkCvars`: `rpg.Perf.FireShadows=4`, `=0`, `rpg.Perf.FireRadiusScale=0.65`, cloud sample counts (only after the runtime `help` confirms the CVar names, per the Round 6 note) | Each arm against the bracketing anchors; keep an arm only if its effect is larger than the anchor drift |
| A4 | Each A3 arm repeated with DLSS Performance | Shows whether DLSS and the light cut add up or overlap |
| A5 | **Pre-step:** `Package.ps1 -Configuration Shipping` | The **pass split is unmeasured in Shipping** today, so take one ProfileGPU or Insights capture in Shipping (or Test) to confirm the Development split carries over |

**Done when:** the table names the passes that must change to reach ≤ 16.67 ms p99, each with a measured delta. Recommendation stays with the Lead and owner.

## BQ-77/78 (D1): benchmark triage plan, for when a run looks wrong

Check these in order and stop at the first failure:
1. **Session:** `run_identity.session_type` must be `console`. Remote or unknown sessions are invalid for target claims (BQ-21/22; the Remote Display Adapter run is the precedent).
2. **Identity:** build stamp `OBF-<CONFIG>-<stamp>-<hash>` (`check_stage_identity.py`); the same build across the anchor and the treatment.
3. **Fight actually started:** `fight_started=true`; a false value means an idle-arena run (a summary field).
4. **Settings persisted:** compare the applied CVar values between runs and record the readback used for each arm. Round 2's suspected `GameUserSettings.ini` persistence is the known failure mode. Keep the owner's settings intact; use an isolated disposable profile if the runner supports one, or explicitly set/read back the test CVars and invalidate any run whose applied values differ. Never delete or reset the owner's persistent settings as part of triage.
5. **Thermal or clock state:** GPU clocks from the `smi_*.csv` logs (Round 3 method); anchor drift over 5% means the machine state changed.
6. **Shader cache cold:** see BQ-79. The first run after a build is a warm-up and is never kept.
7. **Only then** treat a regression as real, and bisect with the A3 one-change arms.

## BQ-79 (D10): shader-failure triage plan (KI-080, KI-081)

**KI-080:** the second machine showed failed shader compiles for pack materials (`M_Greystone_*`, a GideonVFX swirl, replenishment dust, a HealthPotion material) plus two missing pack textures. The cause was not checked.
- **Step 1, static, cheap: DONE, corrected finding.** A recursive filename search of `Content/` on this checkout found no `T_Water_N_2`, but found `T_WispySmoke_V2_OCC+Alpha` in both `Content/ParagonSteel/FX/Textures/Heroes/` and `Content/ParagonGrux/FX/Textures/Smoke/`. Their presence does not establish which assets the failing materials reference, whether the same files exist on the reported second machine, or whether either texture caused those shader errors. Preserve both copies. Compare material references and machine-specific cook errors in ENG Step 2 before proposing any copy or re-pointing action.
- **Step 2, ENG:** in the cook log, search for `Failed to compile Material` and `ShaderCompileWorker` errors. Map each failing material to the missing textures through `inventory`-style dependency reads.
- **Step 3:** only if cook/reference evidence identifies a genuinely missing package path and the source machine has that exact asset, use the approved asset-copy procedure; do not overwrite either existing WispySmoke copy or re-download the ignored pack. If no exact source asset exists, stop for an owner decision before re-pointing materials. For unrelated failures, open each remaining material with `-nosound` and read its compile error.
- **Accept:** a cook with 0 material compile errors, and `CheckPackagedLog.ps1` clean.

**KI-081:** a cold shader cache makes the first PIE and benchmark runs slow. This is a procedure, not a bug.
- Benchmark rule: one discarded warm-up per build per machine (already practice).
- Driver rule: render the arena once before `RunDrivers.ps1`.

**Shipping-only risk:** a material that compiles in the Editor can still fail at cook for a Shipping shader permutation. A5's Shipping capture doubles as that check.

## BQ-80: this report

**Lead review correction:** the benchmark triage plan now preserves the owner's settings and requires actual CVar readback; the initial draft's instruction to delete/reset user settings was unsafe. The filename finding above is corrected from an independent recursive search.

**Gates:**
- OWN: O6 hardware and the reopening of the performance lane.
- ENG: every run above, all under C-1155.
- Lead: adopt the BQ-22 receipt schema so attribution numbers are comparable.

**No code changed in this batch.**
