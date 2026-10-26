# WP9 — compiled timeline and read-only shadow draft

2026-10-25. NOT BUILT / NOT RUN. Staged `Boss/RPGTimelineCompiler.*`, `RPGShadowCompare.*` and `Drafts/TRACKER_OBSERVATION_SEAM.md`. No production tracker edit, asset write or gameplay repair.

## Assumptions and implemented contracts

Inputs are verified montage-local metadata exports, not guessed sidecar timing. Unsupported/unverified segment mappings fail compilation; no automatic animation segment conversion is claimed. Artifacts include schema/full asset path/content and adapter hashes/variant/slot/section; caller supplies precompiled assets and same-GI epoch lease. Native compiler value-copies metadata and publishes const shared artifacts. Adapter reads engine montage instance ID, position, actual rate, section, slot and first animation segment without playing/stopping/retiming animation. No hit-time asset load.

One actor shadow has an immutable artifact set, passive playback identity adapter and diagnostic cursor. Cursor validates participant generation, sequence, playback/engine identity, monotone forward path and exact continuity. `(previous,current]`, initial zero once, deterministic ties and both boundaries of skipped windows are implemented. Reverse/loop/section jumps/unknown path/midclip first observation remain explicitly INCONCLUSIVE, not invented event histories. Reverse and loop traversal are supported as *diagnostic inputs*, not replayed production semantics. Exact engine instance ID prevents same-asset index reuse being accepted as a continuous move. There is no authoritative action ID unless a real authority supplies it.

Review update C118/C119: a VERIFIED single-loop traversal now supports explicit loop bounds and exactly-next ordinal, emitting edges once per loop with chronological loop tags; unverified wraps/reverse/jump/gap stay INCONCLUSIVE. Passive engine adapter cannot infer an actual loop count from position, so it still emits Unknown at a backwards wrap until a verified traversal feed is supplied. Compiler supports flagged overhang projection preserving RawEnd/ClampedFrom in output; no observed blend-out cleanup inferred. Synthetic key factory exists only with automation enabled; production64hex validation unchanged. Current segment is selected with AnimTrack.GetSegmentAtTime, not segment0.

Scope choice requested by C118: this step3 draft covers **flat, already-mapped per-variant/section timelines**. True branch graph/section-transition traversal and composite local-to-montage conversion remain an OPEN later integration slice, not guessed from section counts. A3a/A3b can be distinct variants; that does not prove a composite A2 asset is live. Coverage is exactly the returned GetCurrentActiveMontage and its first slot track/current segment; other slots/additive sequences/inactive blend-outs are UNCOVERED in every row. No blanket full-animation-coverage claim.

Bounded4096-record JSONL sink serializes uint64 ordinals as strings, null authority/instance metadata explicitly, legacy state/counters and compiled crossings. Header needs externally recorded source/DLL/map/mode/cvars/window/timing/before-after hashes; unavailable provenance is not guessed. Output is constrained to a GUID-named file under Saved/BossCombatReview/Shadow. Empty coverage isn't a MATCH. EndPlay unsubscribes, closes local cursor and releases leases without touching another actor/world.

Expected-difference registry retains all six D07 evidence categories with the corrected A2/E008/E007 wording. They are possible explanations with boundaries, **not blanket suppressions**. Automatic comparison only covers sampled active state. A mismatch stays REGRESSION_CANDIDATE until independently reconciled with its actual raw evidence; labels never turn a mismatch into acceptance. No source here calls montage play/stop/rate/rotation/trace/damage/ability APIs.

## D07/spec coverage and limits

| Requirement | Symbol / file | Boundary |
|---|---|---|
| compile/hash/variant immutable | RPGTimeline::Compile / FCompiled | No live notify export importer/cache invalidation worker yet; structural hash validation only |
| cursor identity/crossings | FCursor::Advance | Inconclusive non-forward paths rather than fictitious loop/section traversal |
| after-tracker hook including returns | TRACKER_OBSERVATION_SEAM.md | Exact scoped insertion draft; NOT applied to live source |
| passive untracked observer | CaptureAfterTracker / FPlaybackAdapter | Only active montage; blend-out/multiple simultaneous instances not claimed covered; first segment is source attribution, not universal map conversion |
| same-tick subscribe/lifetime | BindTracker / OnSnapshot / EndPlay | Requires promoted tracker delegate seam and hydrated explicit association |
| report/registry | ObserveAfterTracker / FlushReport / ExpectedDifferences | Full declared-intent/extraction/runtime reference enrichment and accepted evidence-specific automatic classifications remain open |
| unchanged gameplay | no tick/play/effect APIs | Static property only until Claude runs observer off/on parity |

No A4 geometry pass, natural occurrence frequency, cancellation cause, future A2 cut ratio or new hit path is inferred. D06/D08 source-domain, strict-context and fixture boundaries preserved. Full integration remains gated on WP8 adapters and step1 acceptance. This is a substantive draft core, not a claim the entire D07 architecture is complete.

## Claude build/test and API ledger

Promote reviewed files and the entire tracker seam together, after preimages and baseline acceptance. With editor closed: `powershell -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. Then WP10 focused drivers and unchanged full RunDrivers gate. Record exact DLL/source/artifact hashes and observer off/on presets. Never run a half-promoted file set.

Engine declarations read: `Animation/AnimInstance.h` GetCurrentActiveMontage, Montage_GetCurrentSection/Position/PlayRate, GetActiveInstanceForMontage; `Animation/AnimMontage.h` FAnimMontageInstance::GetInstanceID; existing tracker public getters; `Misc/ScopeExit.h`; `Dom/JsonObject.h`, `Serialization/JsonSerializer.h`, `Serialization/JsonWriter.h`; `Misc/FileHelper.h`, `Misc/Paths.h`, `HAL/FileManager.h`. Modules Engine/Core/CoreUObject/Json already declared; WP11 checks actual signatures. Header/static inspection is NOT an engine test.
