# Queue X batch 1: Tier 1 asset-writer correction and safety spec

Offline source/API review following W-C046. No project asset was created, saved, wired, or modified. This page is a bounded implementation/review contract for the Lead; it is not proof of a working Python API sequence.

## X-C001 — UE 5.5 API evidence

The installed `AnimMontageFactory.h:23-28` describes `SourceAnimation` as the only sequence included. Its implementation `AnimMontageFactory.cpp:83-90` creates one `FAnimSegment`, adds it to the first montage slot track, and sets the montage composite length to that sequence's play length. The inherited `FAnimTrack.AnimSegments` array and segment reference/time fields are in `AnimCompositeBase.h:67-81,107-137,246-257`; montage `CompositeSections` and `AddAnimCompositeSection` are in `AnimMontage.h:673-679,881-887`. Therefore the current factory call is a single-sequence montage. Three local length variables and a summed log line do not add the Hold or Slam clips.

## X-C002 — safe execution contract

- Default invocation performs inspection/planning only; asset writes require an explicit `--execute` (or an approved equivalent) option.
- No `--force` overwrite mode. Existing destination means refuse and report the exact path.
- Validate every source path, expected class, shared skeleton, destination namespace, and planned segment/section layout before creating or saving any asset.
- Build the complete candidate in memory, validate it, then save once. On a failed pre-save condition, save none of the batch; do not delete partial assets automatically.
- Emit exact planned paths and validation results in dry run. Keep any asset authoring and visual/content approval with the Lead/owner.

## X-C003 — A2 sequence contract

Before any generated montage is called composite, verify in the candidate that its slot track contains exactly the intended ordered sequence references: Raise, ApexHold, Slam. The start positions must be contiguous and non-overlapping, each segment's animation start/end and play rate must be valid, and the composite length must equal the actual resulting track length within a documented tolerance. Add named sections at the intended Raise/ApexHold/Slam boundaries only after confirming those boundaries are meaningful to the tracker/notify contract. Compare the actual candidate's slot, skeleton, section list, segment list, and duration against the source timing requirement; never report the sum of source clip lengths as the montage's measured length unless the montage itself confirms it.

UE source establishes the available fields but this spec intentionally does not guess the exact Unreal Python property names or array mutation calls. The Lead must check those against the live Python API/Editor build before implementation. No segment timing values are prescribed by this audit.

## X-C004 — offline and runtime verification split

Static tests can require: explicit execution gating; default dry-run behavior; refusal on existing targets; namespace allowlisting; all required source references; validation occurring before every save; sequence-order and expected-boundary assertions; and no save call reachable on dry-run/refusal branches. A negative fixture should mutate each guard independently and prove the checker fails. Such checks establish source shape only.

Before an authored asset can be considered ready, Lead verifies its in-Editor segment list, section names/times, actual duration, correct skeleton/slot, notify/tracker boundary compatibility, preview playback, and no unintended referencers or wiring. Owner approval remains necessary for the look-changing montage before production use. Do not claim visual or runtime success from the offline checker.

## X-C005 — batch receipt status

Completed X-C001 through X-C004 as source/API evidence and a no-write correction specification. The source/API finding strengthens W-C046; actual script correction and Editor validation remain separate Lead-reviewed work.
