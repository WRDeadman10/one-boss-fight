# Observer content association: proposed integration contract

2026-10-27, Codex. Source-only follow-up to AG13/X211 for the replacement operator. Supplements packets F/G in `04_REPLACEMENT_IMPLEMENTATION_PACKETS.md`; does not release them. No implementation, Unreal run or new invalidation policy is approved here.

## Source boundary

Repository-relative raw-file pins read for this review:

| File | SHA256 |
|---|---|
| Source/OneBossFight/Player/RPGEncounterBinding.h | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` |
| Source/OneBossFight/Player/RPGEncounterBinding.cpp | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` |
| Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp | `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924` |

This combines live inert binding scaffolding with a **staged** observer. It does not establish that the observer is installed or these components execute together in the game.

## Existing checks establish different claims

Binding header: `FRPGParticipantConfig` holds shared const `Content`, copied configuration and strong object leases. `URPGCombatParticipant::Config()` exposes the snapshot. The participant key contains world session, encounter, slot and generation, **not content identity**.

Binding cpp: `BindEncounter` rejects already-bound encounter identity and actors that have begun play. Non-synthetic validation checks definition ID/schema, skeleton compatibility and current world-content epoch ID. This is not a general hot-rebinding API. `IsCurrent` checks live/unpoisoned actor/key membership; `IsHydrated` adds the per-record hydration flag. `OnGenerationChanged` updates encounter record/component keys while retaining configs. `UnbindActor` removes the whole encounter's records.

Staged observer cpp92â€“116: `Configure` requires a nonnull content lease, structurally valid key and nonempty/non-null uniquely keyed artifacts before registration. It does not compare the lease with a participant config. `BindTracker` checks owner and `InContext.IsCurrent(Participant)`, not hydration or content equality. Successful staged binding alone would not prove artifacts were compiled for that participant's content.

Staged observer cpp119â€“128: `OnSnapshot` finds the current key by owner. Missing context/member closes the cursor. Changed key closes the cursor and adopts the new key, retaining timelines and content lease. Same-content generation continuity is possible and not automatically stale; key adoption alone cannot certify a new content/artifact association.

Staged observer cpp236â€“269: `FlushReport` requires named header fields including `local_epoch` and `content_hash`, then copies the caller header and serializes buffered records. This method does not compare those supplied fields with `ContentLease` or the participant config. This local producer limitation is not evidence every caller supplies false provenance. EndPlay removes the callback and clears state; it does not retroactively validate buffered records.

## Proposed obligations before association integration

Record participant key, config/snapshot identity, lease epoch, artifact identity/provenance, hydration/publication state and report-header association separately. Lifetime GUID and content digest answer different questions; neither alone proves artifact derivation, dependency closure or peer agreement. An agreed construction path may establish provenance without hashing every sample, but must be specified and tested.

Decide where association is established and rechecked: initial bind, same-content generation change, content replacement, member loss and report flush. Do not interpret every key change as a content change. Do not silently label rows spanning different associations with the final epoch. Splitting reports, preserving per-row association or rejecting a mixed batch are design alternatives, not approved schema changes.

## Discriminating witnesses â€” NOT RUN

| Controlled case | Current local source implication | Required observation for a future approved contract |
|---|---|---|
| Same config/epoch/artifacts, legitimate generation advance | Config retained; observer closes cursor/adopts key | No old cursor continuation; compatible artifacts remain usable if chosen; emitted association identities agree |
| Current participant key, unrelated nonnull epoch lease supplied | Configure guards do not establish equality | Approved construction/bind path rejects or explicitly classifies mismatch before covered observations, without default/first-boss substitution |
| Observer survives member loss | Whole encounter unbound; snapshot member lookup fails | No covered observation attributed to removed member; exported queued rows retain original provenance |
| Teardown/recreation with new definition/content epoch | Future construction scenario; current API is pre-BeginPlay/no-live-rebind | New lease/config/artifacts explicitly associated; old callback/cursor cannot be relabelled to replacement |
| Correct rows, incorrect caller `local_epoch`/`content_hash` | Flush checks presence, not lease equality | Producer/checker detects disagreement; JSON serialization alone is not acceptance |
| Same deterministic content, separate lifetime epochs | Different GUID need not mean different content | Both identities reported honestly; digest alone justifies neither automatic rejection nor aliasing |

An approved fixture/operator session must control inputs and observe callback order, config/lease identities and serialized bytes. Keep negative controls and rejected records. These are acceptance candidates, not tests that passed, reproduced runtime failures, repair instructions or a Claude schedule.

## Assumptions and handover

### X220 source follow-up: key adoption does not guarantee a stop row

Staged `RPGShadowCompare.cpp:53–86` shows two distinct adapter paths. A positioned sample constructs a new observation with the supplied participant Key; Same includes Last.Participant==Key, so a generation change breaks playback continuity and advances the diagnostic ordinal. An idle/no-position sample instead copies Last into Stop, updates sample/time/legacy/stopped state, and does **not** replace Stop.Participant with the supplied key.

Consequently, if OnSnapshot first adopts a changed generation while the next adapter sample has no Position and Last belongs to the old key, the returned stop observation retains that old key. ObserveAfterTracker then returns on participant mismatch before adding a row (and without incrementing Dropped at that guard). If Last is unset/already stopped, the adapter returns no observation instead. The cursor was already closed by OnSnapshot's key-change branch. This is a source-derived boundary, not evidence of an observed runtime failure or stale row being accepted.

Future same-content reset witnesses must separate active positioned continuation, first idle sample after adoption and subsequent idle samples. Inspect current key, row count/JSON, ordinal and drop count; do not assume every tracker callback emits a row or that absence of a stop row proves no engine stop/reset occurred. A positioned midclip restart/new ordinal also does not imply inferred traversal from time0: FCursor::Advance marks uncertain/midclip paths inconclusive under its existing guards. No relabelling of old observations, adapter reset or change to row/drop policy is approved by this note. Actual staged source remains at the existing pinned hashes; no engine/model test ran.

### A141 review addendum: callback guard versus public low-level entry

The member-loss row above describes **OnSnapshot's tracker-callback path** only. Public `ObserveAfterTracker` (staged header49; cpp130 onward) accepts a matching participant key/artifact without consulting Context, IsCurrent or IsHydrated. A direct caller can bypass the callback's membership check in non-Shipping code. Add an unrun negative-control case: after UnbindActor, compare the tracker callback with a direct low-level observation retaining the old key/artifact. Observe record count/payload using existing public getters; do not assume both paths reject. Whether the intended adapter construction invariant is sufficient or the low-level entry needs a guard is an explicit future design question, not an approved repair or reproduced runtime exploit.

Rows already include generation and artifact hashes, but not lease epoch/manifest fields. Same-content generation changes can share a truthful content header; missing per-row epoch fields alone does not prove ambiguity or require a schema change. Establish a real association change before claiming mixed-content mislabelling. Normal Configure lifetime guards reject a second configuration; teardown/recreation was explicitly a future-construction case, not an assertion that an existing begun-play actor can be rebound by destroying its observer.

This addendum changes the document receipt intentionally after AG's original486b07b4... snapshot. Staged source unchanged. The stale DRAFT ONLY comment in Source binding does not override the historically applied/built inert step2a evidence; no new current-binary/runtime claim is made.

Only the pinned methods were inspected; pack ownership and hidden caller invariants remain unproved. No model or engine test run: source inspection establishes local guards, while abstract tests cannot prove Unreal registration, GC or observer wiring. Before implementation reconcile with the chosen publication/teardown design and fresh hashes. All83 required; 2b+/coordinator/adapters/step3/P1 gameplay held, A5 parked, P1 design-only.
