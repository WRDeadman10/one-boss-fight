# AA-C22 / AA-C23 — scalability option and hitch/PSO evidence

## AA-C22 — owner-gated scalability option

**Recommendation: prepare, but do not enable or ship a new profile yet.** The graphics preset can be exposed as **Performance** under Options → Graphics after values are measured on the current data-default build and the owner accepts image quality. Keep the current project default unchanged until then. This is a proposal only; no CVar or content default changed.

| Candidate input | Existing evidence | Proposal boundary |
|---|---|---|
| Upscaler and primary fraction | Round 5 medians on the RTX 3060 proxy: TSR 28.6 FPS / ~41.6 ms p99; DLSS Performance 38.1 / 31.9. Round 6 Phase 1 Performance treatment reports 35.19 FPS / 35.85 ms p99. | Keep as a user-selectable preference; do not make Performance the shipped default from proxy data. Phase 2 is parked and no new profile values are approved. |
| Fire-light shadow quality | Round 6 experiment plan includes FireShadows=4 and 0, each repeated three times against anchors. | Candidate quality-group input; no measured delta or value selection yet. |
| Fire-light radius scale | Round 6 experiment plan includes 0.65, repeated three times. | Candidate quality-group input; no measured delta or value selection yet. |
| Real-time reflection capture | Round 6 experiment plan includes an opt-in 0 treatment, repeated three times. | Candidate quality-group input; no measured delta or value selection yet. |

Use the R6 decision gates already defined by the owner: valid mode witnesses, anchor stability, p99 non-regression against TSR, and owner image-quality acceptance. If a profile is approved, map only measured values into the project's user-facing setting and retain the existing defaults otherwise. Do not combine several unmeasured CVar changes in one comparison. Sources: `PERFORMANCE_LOG.md` Round 5/Round 6 preparation; `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md`; C-954 (Phase 2 parked).

## AA-C23 — PSO feasibility from available hitch frames

Round 4 evidence remains as detailed in `U-C07P_ROUND4_HITCH_ANALYSIS.md` and the diagnostic proposal in `V_C009_PSO_PRECACHE_PROPOSAL.md`. Additional read-only frame inspection found:

| Capture | Highest relevant rows | Interpretation |
|---|---|---|
| Round 4 `r4_legacy_c` | Frame 1288: 310.4318 ms total / 308.7521 ms game; frame 1289: 128.2369 / 129.1022. GPU stayed ~32–35 ms. | Two adjacent game-thread stalls. RTPSO creation and async-load flushes in the log occur during startup, tens of seconds earlier; causation is not established. |
| Round 5 archive `run_20261105_213602` | Frame 4: 404.1114 ms / 392.0263 ms game; frame 5: 175.2679 / 188.3334 game; frame 13: 616.4131 ms total while game/render/GPU samples remain ordinary. | Archive label is only `run` and its summary has no build ID. The large full-frame samples do not identify a PSO cause and should not be folded into the accepted per-mode medians. |
| Round 6 Phase 1 `R6M_Performance_03_dlss_performance_t1` | Frame 1480: 346.3788 ms / 344.3714 ms game; frame 1481: 142.9715 / 144.3100 game; GPU ~24–27 ms. | Development RTX 3060 treatment, 35.19 FPS average / 35.85 ms p99. Its log has a 66.18 ms RTPSO creation and `FlushAsyncLoading(148)` during startup; CSV rows lack wall-clock timestamps, so neither log event is correlated to the later hitch. |

**Disposition:** PSO precaching is plausible for startup work but is not a proven fix for any listed outlier. The outlier evidence spans game-thread stalls and full-frame spikes without matching thread work; a startup PSO event cannot explain a later frame without timestamp correlation. Retain the existing `V_C009` diagnostic plan: add monotonic timestamps/frame indices, capture Unreal Insights frame/CPU/GPU/loading/PSO channels, and compare controlled cold and warm launches. Change PSO policy only if repeated traces identify PSO misses/late work at the affected frame and a narrowly scoped intervention improves the p99 without unacceptable load time, memory, or package cost.

No benchmark, Editor, or Unreal run was performed for this proposal. The frame summaries were read from retained local CSV/summary/log artifacts; no raw artifacts were modified.
