# Step3 promotion set: timeline and passive shadow scaffold

2026-10-26, X-T6. **HOLD for complete step3 promotion.** Concrete `PROMOTION_STEP3_SCAFFOLD.patch` adds staged timeline/shadow/test code plus exact tracker observation seam. Depends on step2 scaffold. No patch applied; no live source/asset/config writes or Codex build/PIE.

## Exact contents and missing product pieces

New Source/OneBossFight/Boss/RPGTimelineCompiler.h/.cpp, RPGShadowCompare.h/.cpp; Tests/RPGTimelineTests.cpp. Existing Player/RPGAttackTracker.h/.cpp get observational delegate + recursion guard + scope-exit snapshot only. The patch carries current live tracker preimage hashes in WP6Support/promotion_pins.json; small insertion-only context hunks avoid CRLF whole-file churn. Check the full preimage hashes too: successful context matching is not a full-file drift check. Refresh/review, never force apply.

Timeline compiler accepts ALREADY mapped montage-local windows/markers. **Missing:** a verified importer for actual sections/segments/rates/root-motion and full notify payload, production artifact authoring/cook closure, typed observer hydration and actual paired fixtures. It cannot claim animation-canonical timeline by importing AG sidecar intent as engine facts. Source hash must match current raw export; stale hashes fail closed. AG16 unknown topology remains unknown.

CaptureAfterTracker observes selected active montage/first slot/current segment and engine instance. It does not enumerate blends/layers or identify the causal stop caller. Artifact misses are uncovered; absent action IDs serialize null, not fabricated authority. No attack forced, no damage/motion/end ownership moved. JSONL is bounded4096 per observer and debug-only writing to Saved GUID-named output. Production remains legacy-authoritative.

## Integration seams

| Site | Required action / status |
|---|---|
| AttackTracker.h before generated include | Shadow header include; non-Shipping delegate + bool recursion guard. Included in patch. |
| AttackTracker.cpp after Super::TickComponent | ON_SCOPE_EXIT snapshot broadcast after all early exits; includes ScopeExit/UnrealTemplate. Included in patch. |
| Passive snapshot | IsValid tracker/owner/mesh/anim/montage checks; included in staged shadow. No untrusted listener may tick/destroy gameplay. |
| Step2 native observer plan | Configure precompiled artifacts/content lease before registration, then BindTracker for associated actor after batch readiness. **NOT implemented as actual Boss01 adapter.** |
| Metadata provenance | Source asset + actual segment, section/slot and export/hash/policy key. Section/loop path must be verified externally; backwards position alone is inconclusive. Importer missing. |
| Test runner | Existing draft Python drivers require explicit fixture, not shipped arena. Do not install as unconditional gate rows. |

## Claude apply/build/test commands after approval

From root, with editor closed and fresh preimages: `git apply --check Docs/BossCombatReview/Execution/Codex/PROMOTION_STEP3_SCAFFOLD.patch`; only after exact scope approval `git apply` that file. Step2 added headers must exist first. `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. Tests DraftCrossings/DraftA2Golden are math/synthetic scalar proofs, not live montage observation. Record actual results, no assumed test total.

After importer + fixtures exist, Claude runs: same full Boss01 gate observerOFF and observerON, same startup config. Compare hit/miss/damage/HP/stamina/posture/generation/phase/reset/selection outcomes and timings, plus passive JSONL semantic validation. Include authored and fallback variants, actual rate changes, both collision windows, hitch edges, stop/restart same asset, reverse/seek/section jump/known loop, zero rate, missing metadata, no samples, duplicate samples, teardown/destruction/GC, buffer cap, multiple instances/worlds and stale provenance. Unknown traversal is INCONCLUSIVE, never MATCH. Expected mismatch annotations never whitelist a defect or convert coverage into acceptance.

## Compile/design risk table

| Risk | Gate |
|---|---|
| Tracker/Shadow/Binding include dependency | Promote all required headers coherently, generated include last; UHT/full noneditor compile |
| UE5.5 montage instance / segment API | Real compile, actual engine instance readback; first-slot limitation preserved |
| Reentrant delegate | Guard suppresses recursive broadcasts only; production subscription should be private/scoped; no gameplay callbacks |
| Pointer invalidation during teardown | Weak subscription removal + IsValid snapshot checks; no actor proxies kept across PIE sessions |
| Metadata-only local time | Importer must map segment notifies and actual traversal; no inferred wall-time or next-section graph |
| Fixture/JSONL superficial tests | Assert record contents/provenance/nulls/ordering, not count alone; off/on outcome parity separate |

**One-pass scaffold packaging delivered; task's one-pass complete product promotion criterion NOT met.** Missing adapters/importer remain work, not an owner decision that may be silently waived. Owner acceptance of step1 alone cannot manufacture those pieces. Stage them before asking Claude to apply. NOT BUILT / NOT RUN.
