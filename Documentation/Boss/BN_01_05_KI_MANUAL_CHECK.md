# BN-01..05: manual check of the heuristic-O KIs (lane BN, batch 1 of 10, per X-2213)

C (implementer), 2026-11-12.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

## BN-01: reconstructing the 49 IDs

- I re-parsed `Documentation/KNOWN_ISSUES.md`: open rows, run through the BM-46 keyword rules (`gen46.py`), class O.
- **The result is 49 IDs.** They match the order of the `BM_46_50_KI_TRIAGE_AND_CLOSEOUT.md` table (Python list equality: `True`).

The order is: KI-001, 003, 004, 005, 002, 009, 016, 020, 022, 024, 026, 029, 030, 033, 035, 036, 039, 040, 045, 050, 055, 057, 059, 063, 065, 067, 068, 070, 074, 078, 079, 080, 087, 103, 106, 101, 092, 110, 128, 134, 147, 163, 164, 165, 166, 167, 174, 176, 181. This follows the table order, which is not numeric.

## BN-02..05

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-02 | KI-001 | `KNOWN_ISSUES.md:68`: UBT warns that MSVC 14.51 is not the preferred VS2022 compiler, but the build succeeds | Toolchain message only. Removing it needs a compiler install or a build | **E** (build/toolchain) | No |
| BN-03 | KI-003 | `:69`: the benchmark PC is an RTX 3060, not the 2060 Super target | Hardware fact | **E** (needs target hardware or a GPU run) | No |
| BN-04 | KI-004 | `:70`: Lumen and VSM defaults give 94-97 FPS with an unstable p99; the fix is to "use gi_off settings via config" | `Config/DefaultEngine.ini:14,16,22` still sets `r.DynamicGlobalIlluminationMethod=1`, `r.ReflectionMethod=1` and `r.Shadow.Virtual.Enable=1`, so the fix is **not applied**. `PERFORMANCE_LOG.md:71-72` records the gi_off and gi_vsm_off measurements. DECISIONS M6 keeps this optimization parked; the later DLSS Phase 2 is also parked/not run (C-954). This does not mean all performance work is parked. | **D** (M6 optimization parked) + E (needs a perf re-run) | No (a config edit would change the shipped performance setup without current approval) |
| BN-05 | KI-005 | `:71`: look direction and sensitivity are not playtested | `bEnableLegacyInputScales=False` is still at `DefaultInput.ini:67`. Needs a human feel test | **E** (playtest) | No |

**Batch 1 result:** none of the 4 is truly O. The heuristic missed them because their rows lack the engine and owner keywords.

**Limits:** these are text and config reads only. Performance and feel were not measured.
