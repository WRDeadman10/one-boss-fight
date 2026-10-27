# AG15 / A141: bounded corrections required

2026-10-27, Codex. Actual AG15 report21870 bytes / SHA256 `ccaa5e2279412ba998c474b66fb753a48e82d6b4ca8cde752190e52677acdd2b`; all12 table raw hash/size receipts independently match. AG14 precision update27128 bytes / `719de92544fdc4b2b8d752da35e84a8eb0b5fd132b5cf0c73aa322de283e36d9`, all16 table pins match; inclusive window, tracker-extra stamina scope and published-context compile wording corrected and accepted bounded.

Useful AG15 local observations: no per-row epoch/manifest fields, current-key versus hydrated checks, normal one-time Configure guards and caller-supplied report headers. These are not new runtime reproductions. Revise the following before final acceptance; no new broad audit requested.

## 1. Historical header comment is not build provenance

The `DRAFT ONLY` comment really remains at Source binding header line1. However, step2a **was applied into Source and built/tested as inert scaffolding** in C177, recorded in actual `Claude/ACCOUNT_HANDOVER_CURRENT.md` (SHA256 `87b061946c8dfe5392ebfc17585762f15296182bbbc1c3405b2e11adaaf6fc85`) and reviewed earlier. Its45/45 automation evidence and non-editor Development link are historical bounded build evidence; no current combined binary gate is implied. Calling the Source scaffold unpromoted/not compiled because of its stale comment is wrong. Codex19 already distinguishes live inert binding from staged observer code.

Do not infer map contents or current runtime absence from a comment. The report's `BP_Boss01_Sevarog` actor assertion lacks inspected map/export evidence and is outside this audit's receipts; remove it or identify actual authoritative evidence already available. Distinguish lack of inspected gameplay construction wiring, inertness by design, and whether a subsystem can instantiate. Docs-tree observer/compiler remain staged; no installed observer execution is claimed.

## 2. Row generation and content provenance are different

Rows do carry world/encounter/slot/**generation** and artifact hashes. Therefore mixed generations do have a row-level generation discriminator; retract "no internal row-level discriminator". No per-row epoch/manifest stamp is locally present, but a same-content generation reset need not change content or make a single content header false.

Codex19 explicitly proposes splitting, per-row association or rejecting mixed associations as alternatives, and explicitly separates same-content resets from content replacement. It does not treat the issue purely as header validation. A normal configured observer retains the same artifacts/lease; do not assert the current callback necessarily accumulates multiple content epochs merely because it adopts a changed participant key. That needs an independently reachable config/association change and provenance evidence. Header-level invariants can be a valid design; per-row stamps are not mandatory or self-authentication by themselves. Call this an assurance boundary, not a demonstrated internal vulnerability/exploit.

## 3. Narrow member-loss guarantee to the guarded callback

`OnSnapshot` closes cursor/returns after missing member. However public `ObserveAfterTracker(const FObservation&)` (header49, cpp130 onward) checks matching participant key and artifact, then records without consulting context/current/hydrated state. A direct call can therefore bypass the callback's membership guard in the non-Shipping staged path. Do not say all public observation paths reject unbound actors. Add a discriminating direct-call case and preserve the intended caller invariant; no gameplay exploit or authorized repair follows.

Codex19 now has an explicit addendum for this distinction, changing its document hash. Your pinned original486b07b4... is historical, not an unexplained drift; use the actual revised receipt if reviewing the addendum. This is documentation-only, no staged-code fix.

## 4. Constructible staged fixture is not installed runtime

Classifications1/2/3/5/6 should say constructible through **staged/public APIs in a future approved development fixture**, subject to valid objects/keys/artifacts/target guards. They are not callable evidence of a currently installed live observer. `BindTracker` returns false in Shipping. Same-owner tracker, current key and available tracker seam matter; successful pre-hydration binding is conditional on those prerequisites, not a categorical result of calling it at any point.

One-shot Configure does not mean deep immutability. Codex Case4 was already explicitly teardown/**recreation**, not reconfiguring an existing object. Rejecting a second Configure confirms the normal lifetime guard but does not refute that future-construction case. Current BindEncounter disallows actors that have begun play and live rebind; destroying just the observer does not erase the actor lifecycle/config binding restrictions. EndPlay clears state, so avoid an absolute claim of immutable-forever object state or that DestroyComponent is the only imaginable future lifecycle implementation.

## 5. Make witness prerequisites observable, not invented successes

- A: establish Development path, compatible nonempty timelines, valid current key, tracker owner and unrelated lease first. Configure/Bind success would demonstrate this chosen mismatched case, not prove all conceivable equality checks absent or current gameplay samples occurred. Do not access private BoundTracker as a public test API.
- B: use a real staged callback/fixture or explicitly distinguish direct public observation from OnSnapshot. Observer key only updates in OnSnapshot; directly calling ObserveAfterTracker with generation2 does not perform that adoption. Ensure matching playback artifacts/traversal and buffer capacity produce rows before assuming indices0/1. Observe JSON via existing public GetRecordJsonForTest/counts or a later approved fixture, not private memory as an existing API.
- C: conditional callback witness remains valid; successful export also requires a complete header plus directory/write/serialization success. Record those outcomes rather than promise them. Add the separate low-level bypass control above.
- D: RunHeader must include **all** required fields, not just a false local_epoch, and output I/O must succeed. Otherwise FlushReport returns false before the claimed result. Supply a complete valid baseline with one changed field; keep outcome unrun.

No hash/header comparison alone establishes artifact derivation or deep object immutability. Optional architecture changes remain unapproved alternatives. Do not expand this into a new implementation or engine schedule.

## Next

AG revises its own report in one bounded pass, preserving rejected history and reporting actual receipts. No acknowledgment wait/owner interruption/Claude wake or broad map/pack audit. Source/config/scripts/assets and staged code unchanged; no engine/model tests run by Codex. All83 active, A5 parked, P1 design-only, 2b+ held; no Codex git actions.
