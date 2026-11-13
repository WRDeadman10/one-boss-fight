# Queue BF X41–X45 — Performance Candidates, Niagara Limits, Owner Gates

Date: 2026-11-11  
Scope: read-only source, performance and decision-document audit, plus a successor offline queue. No Unreal, Editor, build, package, runtime, profiler, benchmark, asset, or raw-capture operation.

## X41 — Combat-path allocation and string candidates

These are source locations for later instrumentation, not measured costs or optimization findings:

| Source | Candidate | Evidence boundary |
|---|---|---|
| `Source/OneBossFight/Player/RPGDamageResolver.cpp` | Key/reason/history formatting (`FString::Printf`, name conversion) in resolution paths | Count invocations and allocations under the measured route before estimating impact. |
| `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp` | Tick/playback and sweep diagnostics convert names/vectors and emit detailed proof logs; channel ticks construct a formatted `FName` key | Mostly framework/proof paths; route and log verbosity determine whether they are active. Source cannot show packaged frequency. |
| `Source/OneBossFight/Player/RPGPackParryContact.cpp` | Attack-key generation and per-contact display diagnostics | Contact frequency and category filtering are unmeasured. |
| `Source/OneBossFight/Player/RPGAttackTracker.cpp` | Move-name formatting in lifecycle/branch diagnostics | Event-triggered paths; no allocation or frame-cost claim. |
| `Source/OneBossFight/Player/RPGSwingTracker.cpp` | Human-readable swing row formatting, formatted key, retained diagnostic lines | Some work is explicitly audit/UI oriented; no evidence establishes it runs on every shipping frame. |

Existing candidate inventory in `BD_X36_X40_OBSERVABILITY_PERFORMANCE_AUDIT.md` remains compatible. No candidate justifies code changes without profiler/call-count evidence.

## X42 — 2060 Super performance receipt schema

`PERFORMANCE_LOG.md` states the packaged 1920x1080 full-encounter gate: average >=60 FPS and whole-frame p99 <=16.67 ms; 120 FPS is stretch only. It contains 5-second discarded warm-up / 60-second captures, p95/p99/max, game/render/GPU timing and hardware context for some witnessed runs. However, the accepted Round 6 Phase 1 evidence is an RTX 3060 proxy, all modes miss the target, and Phase 2 is PARKED / NOT RUN under C-954.

The base `summary.json` writer records map/configuration/engine/hardware, timing window, sample count and frame/thread/GPU metrics, but not host/session or unique build/binary identity. D145 found these absent in 0/59 summaries it scanned (legacy and R1/R2). Later receipts add some provenance at a higher level: Round 6 v1 binds a parent `build_id` and raw archive SHA-256 to unique run IDs/source-summary paths, but its individual run rows do not carry the complete source/binary/package and host/session identity set. Round 4's custom receipt validator requires a richer per-run set including build ID/hash, session type, map/route, warm-up/duration, summary/frame paths and hashes; it is specific to that round's intake and is not the base benchmark schema. No 2060 Super result is claimed. The BD-X40 proposal and BI-X02 schema draft add explicit provenance fields; neither has been adopted by the benchmark runner.

## X43 — Niagara bounds and sprite limits

- The authored Ember BoostLite asset is a project-owned Niagara asset. C-1202 records successful editor compile/resave/readback with graph-source overrides, Sparks1 and system fixed bounds, and exposed User defaults; C-1210 records its Lead acceptance and production reference. Current authoring-plan defaults are fixed system bounds +/-175 cm, Sparks1/Sparks2 70/52.5 particles per second, and Sparks1 size min (5,50) cm / max (10,100) cm. These are spawn rates, not a hard live-sprite cap.
- Sevarog remains a different, unselected candidate. `BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md` requires fixed bounds, scalability-limited spawn and prewarm; it lists a <=60-particle idea for Cand A. Later `BC_A26_A30_SFX_AURA_COOK_PRECHECK.md` describes a proposed Sevarog system/emitter box +/-220 cm and <=120 sprites. Neither is proof that an authored Sevarog Niagara system exists or has those limits read back.
- No VFX runtime cost, culling correctness, or target performance is inferred. Keep candidate specifications separate from the accepted Ember asset and require Lead readback/capture for Sevarog.

## X44 — Pending owner choices and gated content

Current artifact state (mailbox through A-796; docs reviewed):

| Choice / gate | Owner | Unblocked after decision | Still requires Lead |
|---|---|---|---|
| SFX audition options across the listed batches, including reel-backed SFX-01..15 and spec-only later batches | Owner selects A/B/C or None (`BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, SFX manifests) | Only the exact approved cue mappings can advance to authoring/wiring plans; no unpicked cue should be wired | Asset/runtime wiring, mix and in-game verification |
| Sevarog 4-move clip and Phase-2 aura Cand A/B/C | Owner visual choice (`BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md`) | Selected motif may enter a project-owned Niagara authoring plan; Cascade sources cannot be assigned to `TSoftObjectPtr<UNiagaraSystem>` directly | Proper Niagara authoring, bounds/readback, prewarm/lifecycle and paired PIE review |
| Greystone retarget/root-motion and live X26/S1–S8 evidence | Lead, pending `[C-1286+]` | Offline audits/manifests can be prepared | Editor/PIE/save/readback are Lead-only |
| Shipping reflection/stage and packaged RTX 2060 Super performance receipt | Lead | Schema and offline intake preparation | UHT/Shipping/staging/physical target run |

No new owner decision was present in recent mailbox messages A-792 through A-796. C-1168's prior BoostLite decision concerns Ember's aura and does not select a Sevarog Cand A/B/C.

## X45 — Successor queue

Drafted `Documentation/Boss/QUEUE_BI.md`: ten batches of five offline/source tasks, scoped to residual Lead/Owner acceptance preparation, evidence tooling, integration audits, and closeout. It does not duplicate Antigravity's active `QUEUE_BH_AG.md`. Every Lead/Owner-only action remains a blocked input rather than an executable assignment. No commit or push.

## Verification boundary

Mailbox inspected through A-796; Antigravity status is enabled, unpaused, onboarding-ready; team service reports agents offline, but her receipts show active execution. Claude is currently listed offline and no new review verdict was present. No tests or doc-link scan were run in this batch.
