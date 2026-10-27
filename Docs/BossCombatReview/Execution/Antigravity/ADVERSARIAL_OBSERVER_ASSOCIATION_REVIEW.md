# AG15: Adversarial Review of Observer Content Association Contract (Rev 02)

**Document Date:** 2026-10-27  
**Author:** Antigravity (Pair Programming AI Assistant)  
**Task Classification:** Work Order 15 (AG15) — Adversarial Challenge of Codex `19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md` (Revision 02)  
**Governing Inputs:**
- Proposal under Review: [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md) (Rev 02 post-addendum: `SHA256: eddb5ac7b739e740aff22dc8221386e63894711a3d8c03ce6a49c7c87f2276e5`, 7,995 bytes; historical pre-addendum pin: `486b07b40625b99ecdc81883e9daecd842347063c9183715a28a904128e69ed7`, 6,245 bytes)
- Review Directives: [`Docs/BossCombatReview/Execution/Codex/AG15_A141_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG15_A141_REVIEW.md) (`SHA256: 6379ae96324993a7d10217c2019f407685b7e363c243150cec2a5588631c340b`, 7,059 bytes)
- Mailbox Directives: `[X-214]` and `[X-215]` (2026-10-27 06:23:54 +05:30)

---

## 1. Executive Summary & Review Scope (Rev 02)

Per Codex directives `[X-214]`, `[X-215]`, and [`AG15_A141_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG15_A141_REVIEW.md), Antigravity conducted an independent, adversarial source-level challenge of Codex's proposed observer content-association contract ([`19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md)), incorporating the A141 review addendum.

### Core Review Conclusions & Grounded Invariants (Rev 02):
1. **Three-Way Codebase Architecture Distinctions:**
   - **Live Shipped Duel Code:** The actual duel in `L_SevarogArena` runs on [`RPGBossEncounter`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h), [`RPGBossPhases`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h), and [`RPGBossPosture`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.h).
   - **Inert Scaffolding (Step 2a):** [`RPGEncounterBinding.h/.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h) is built into the engine module and linked in Development targets (validated by historical 45/45 C177 automation tests, recorded in `Claude/ACCOUNT_HANDOVER_CURRENT.md` `87b06194...`). While line 1 retains a historical `DRAFT ONLY` comment, it is compiled code; it remains **inert by design**, lacking active gameplay construction wiring in the shipped duel level.
   - **Staged Observer Drafts:** [`RPGShadowCompare.h/.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h) and [`RPGTimelineCompiler.h/.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h) reside in `Docs/BossCombatReview/Execution/Codex/Drafts/` and are offline prototype drafts, not currently compiled or installed in runtime binaries.
2. **Row Generation vs Content Epoch Provenance:**
   - Individual buffered rows (`Records[i]`) serialized by `ObserveAfterTracker` ([`RPGShadowCompare.cpp:140-163`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L140-L163)) **do carry an internal generation discriminator** (`Participant.Generation`), alongside `world_session`, `encounter_instance`, `participant_slot`, `asset_sha256`, and `adapter_sha256`.
   - Rows do **not** carry a per-row `local_epoch` GUID or `content_hash` manifest stamp.
   - For a same-content generation reset, sharing a single truthful file header is valid design; it does not constitute a mixed-epoch failure. The absence of per-row epoch fields is an **assurance boundary and design choice**, not a demonstrated runtime exploit.
3. **Member-Loss Guard Scope (Callback vs Direct Entry):**
   - In `URPGCombatTimelineShadow::OnSnapshot` ([`RPGShadowCompare.cpp:121-127`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L121-L127)), the tracker-callback path explicitly checks `Context->FindParticipant(*GetOwner())`. If the member was removed (e.g. via `UnbindActor`), it closes the cursor and returns, successfully preventing new observations.
   - However, the public method `ObserveAfterTracker(const FObservation&)` ([`RPGShadowCompare.cpp:130-134`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L130-L134)) checks matching participant key and artifact, but **does not consult Context, `IsCurrent`, or `IsHydrated`**. A direct caller in non-Shipping code can bypass the callback's membership guard.
4. **Hydration Verification Bypass in `BindTracker`:**
   - `URPGCombatTimelineShadow::BindTracker` ([`RPGShadowCompare.cpp:111`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L111)) checks `InContext.IsCurrent(Participant)`, which verifies unpoisoned actor presence, but **does not check `InContext.IsHydrated(Participant)`**. An observer can successfully bind in a staged Development fixture before component plan hydration is complete.
5. **One-Shot `Configure` Lifetime Guard:**
   - `URPGCombatTimelineShadow::Configure` ([`RPGShadowCompare.cpp:95`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L95)) enforces a standard one-shot configuration lifetime guard: `if (!Timelines.IsEmpty() || IsRegistered()) return false;`.
   - Codex Case 4 was explicitly framed as a **teardown / recreation** scenario in future construction, not a second call to `Configure`. In current APIs, destroying an observer does not erase `BindEncounter`'s ban on begun-play actors or live re-binding.
6. **Constructibility Bounded to Staged Future Fixtures:**
   - Constructibility of Cases 1, 2, 3, 5, and 6 applies strictly to **staged / public APIs in a future approved Development test fixture** (`!UE_BUILD_SHIPPING`), conditional upon valid prerequisite objects, keys, and tracker ownership. They do not constitute evidence of an installed live observer in the shipping game.

---

## 2. Inspected Input Receipts

All inspected files were verified on disk via exact SHA256 hashing and byte counts:

| File Path | SHA256 Hash | Bytes | Role / Architectural Boundary |
|:---|:---|:---:|:---|
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md) | `eddb5ac7b739e740aff22dc8221386e63894711a3d8c03ce6a49c7c87f2276e5` | 7,995 | Revised contract under review (with A141 addendum) |
| *Historical pre-addendum pin:* `19_OBSERVER_CONTENT_ASSOCIATION_CONTRACT.md` | `486b07b40625b99ecdc81883e9daecd842347063c9183715a28a904128e69ed7` | 6,245 | Historical pre-addendum contract pin cited in A141 |
| [`Docs/BossCombatReview/Execution/Codex/AG15_A141_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG15_A141_REVIEW.md) | `6379ae96324993a7d10217c2019f407685b7e363c243150cec2a5588631c340b` | 7,059 | Codex A141 review and correction instructions |
| [`Source/OneBossFight/Player/RPGEncounterBinding.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h) | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` | 7,338 | Step 2a inert scaffold; participant config & context declarations |
| [`Source/OneBossFight/Player/RPGEncounterBinding.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp) | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` | 14,964 | `BindEncounter`, `IsCurrent`, `IsHydrated`, `OnGenerationChanged`, `UnbindActor` |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h) | `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab` | 2,690 | Staged `URPGCombatTimelineShadow` component declaration |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp) | `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924` | 15,190 | `Configure`, `BindTracker`, `OnSnapshot`, `ObserveAfterTracker`, `FlushReport` |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h) | `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e` | 3,137 | Staged `RPGTimeline::FKey` & compiler declarations |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.cpp) | `c3c8f9073806e6bee7d6bb507c241f2f3ea5ba027af21b55e27ee337d8e19f22` | 8,581 | Staged timeline compilation implementation |
| [`Source/OneBossFight/Player/RPGCombatCatalog.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.h) | `e7d5296833cfa5bec4101e608a98ab336a5b8c7a5c476e0d3b17eae57279dbb5` | 7,427 | Catalog `FEpoch`, `FContext`, `FDiagnosticLedger` |
| [`Source/OneBossFight/Player/RPGCombatCatalog.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp) | `f6f71036804f60f0e4c8b3cf455f2a04a7bc4cf379760334903a2d9d613de59d` | 23,675 | Catalog compile, asset resolution, coverage formatters |
| [`Source/OneBossFight/Player/RPGSwingRules.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingRules.h) | `cafda8dc235079bdda9ee9f9123575f81b7f7b03151a3d9bb59a9277541ec0c2` | 2,286 | `WindowOpen` inclusive interval rule (`Position >= Start && Position <= End`) |
| [`Docs/BossCombatReview/Execution/Codex/AG14_A140_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG14_A140_ACCEPTANCE.md) | `4d498c670f1a8f8b7f9d3f844780574a3d7bfee92669775d9b96a9e400efc234` | 5,591 | Codex AG14 acceptance & AG15 assignment terms |
| [`Docs/BossCombatReview/Execution/Antigravity/CATALOG_COVERAGE_CONSUMER_AUDIT.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/CATALOG_COVERAGE_CONSUMER_AUDIT.md) | `719de92544fdc4b2b8d752da35e84a8eb0b5fd132b5cf0c73aa322de283e36d9` | 27,128 | AG14 report with precision note updates applied |

---

## 3. Adversarial Analysis of Local Source Mechanisms

### 3.1. Inert Scaffold (Step 2a Built) vs Staged Observer Prototype
- **Inert Step 2a Scaffolding (`Source/OneBossFight/Player/RPGEncounterBinding.h/.cpp`):**
  - Applied and built in Step 2a (C177, validated by 45/45 automation tests in `ACCOUNT_HANDOVER_CURRENT.md` `87b06194...`).
  - It is linked into Development targets, but is **inert by design**: in the shipped duel level, no level actors invoke `BindEncounter`, and combat runs on the unadapted `RPGBossEncounter` / `RPGBossPhases` pipeline.
- **Staged Observer Prototype (`RPGShadowCompare.h/.cpp`):**
  - Unpromoted draft residing in `Docs/BossCombatReview/Execution/Codex/Drafts/`.
  - `#if UE_BUILD_SHIPPING return false; #endif` protects `BindTracker` and `FlushReport`.
  - It is an offline evaluation component designed for future integration testing, not a live production actor component.

---

### 3.2. Detailed Analysis of Codex Contract Assertions

#### 1. Row Generation Metadata vs Content Epoch Provenance
- In `ObserveAfterTracker` (`RPGShadowCompare.cpp:140-163`):
  ```cpp
  auto Row = MakeShared<FJsonObject>();
  Row->SetStringField(TEXT("world_session"), Participant.WorldSession.ToString());
  Row->SetStringField(TEXT("encounter_instance"), Participant.EncounterInstance.ToString());
  Row->SetStringField(TEXT("participant_slot"), Participant.Slot.ToString());
  Row->SetNumberField(TEXT("generation"), Participant.Generation);
  Row->SetStringField(TEXT("source_asset"), O.Timeline.AssetPath);
  Row->SetStringField(TEXT("asset_sha256"), O.Timeline.AssetSHA256);
  Row->SetStringField(TEXT("adapter_sha256"), O.Timeline.AdapterSHA256);
  ```
- **Source Verification:**
  - Rows **do carry an internal generation discriminator** (`Participant.Generation`).
  - Rows do **not** carry `local_epoch` (the `FGuid` of the content lease) or `content_hash` (the manifest hash).
- **Assurance Boundary:**
  - For a same-content generation reset (Case 1), the participant configuration, weapon definitions, and catalog epoch remain identical. Outputting rows with differing generation numbers under a single file header is **valid continuity**, not an invalidation defect.
  - An assurance boundary arises only if a participant's content epoch is replaced while an observer retains buffered records from a prior epoch. Codex's alternatives (splitting reports, adding per-row epoch fields, or rejecting mixed batches) represent valid design choices, not mandatory fixes.

#### 2. Narrowing Member-Loss Guards (Callback vs Direct Entry)
- **Callback Path (`OnSnapshot`, `RPGShadowCompare.cpp:121-127`):**
  ```cpp
  if (!Context.IsValid() || !GetOwner()) { Cursor.Close(); return; }
  const auto CurrentKey = Context->FindParticipant(*GetOwner());
  if (!CurrentKey.IsSet()) { Cursor.Close(); return; }
  ```
  If `UnbindActor` is invoked, `FindParticipant` returns empty. `OnSnapshot` closes the cursor and returns, successfully preventing new observations via the tracker callback.
- **Direct Low-Level Entry (`ObserveAfterTracker`, `RPGShadowCompare.cpp:130-134`):**
  ```cpp
  void URPGCombatTimelineShadow::ObserveAfterTracker(const RPGTimeline::FObservation& O)
  {
  #if !UE_BUILD_SHIPPING
      if (!(Participant == O.Participant)) { return; }
  ```
  `ObserveAfterTracker` is a public method (header line 49). It validates `Participant == O.Participant` and artifact key, but **does not query `Context` or check `IsCurrent` / `IsHydrated`**.
  - In a future development fixture, a direct caller supplying a matching participant key can bypass the member-loss guard of `OnSnapshot`.
  - Codex's A141 addendum explicitly acknowledges this distinction as a low-level entry boundary, requiring a dedicated negative-control witness.

#### 3. Hydration Bypass in `BindTracker`
- In `RPGShadowCompare.cpp:111`:
  ```cpp
  if (Timelines.IsEmpty() || BoundTracker.IsValid() || Tracker.GetOwner() != GetOwner()
      || !InContext.IsCurrent(Participant)) { return false; }
  ```
- In `RPGEncounterBinding.cpp:204-212`:
  - `IsCurrent(Key)` verifies `!R.bPoisoned && R.Actor.IsValid() && R.Key == Key`.
  - `IsHydrated(Key)` verifies `!R.bPoisoned && R.bHydrated && R.Actor.IsValid() && R.Key == Key`.
- **Verdict:** `BindTracker` checks `IsCurrent`, but **not `IsHydrated`**. In a development fixture where `BindTracker` is called after `BindEncounter` but before component plan hydration (`CreateConfigureRegister`), binding succeeds prematurely.

#### 4. One-Shot `Configure` Lifetime Guard
- In `RPGShadowCompare.cpp:95`:
  `if (!Timelines.IsEmpty() || IsRegistered() || Values.IsEmpty() || !Lease || ...) { return false; }`
- Calling `Configure` a second time is rejected by design. This is a standard component lifetime guard.
- Codex Case 4 was explicitly framed as **teardown / recreation** in future construction, not re-calling `Configure` on a registered instance.
- In existing scaffold APIs, `BindEncounter` strictly rejects begun-play actors (`Actor->HasActorBegunPlay()`) and existing encounter IDs (`Binding.cpp:153`). Merely destroying an observer component does not enable live rebinding of an existing begun-play actor.

---

## 4. Trace & Classification of the Six Contract Cases (in Staged Fixtures)

The six cases are classified below regarding their construction viability in a **future approved Development test fixture** (`!UE_BUILD_SHIPPING`), subject to valid objects and prerequisites:

| Case # | Scenario Description | Constructibility in Staged Dev Fixture | Transition Trace Across Component Lifecycle | Invariant Classification |
|:---:|:---|:---:|:---|:---|
| **1** | Same config/epoch/artifacts, legitimate generation advance | **Constructible** (via staged public APIs) | `Context->OnGenerationChanged` updates generation. On next tracker tick, `OnSnapshot` detects key change, closes cursor, updates `Participant = CurrentKey.GetValue()`, and retains existing `Timelines` and `ContentLease`. Emits generation 2 rows. | **Locally Enforced Continuity.** Same-content reset retains valid timeline artifacts. Buffered records carry generation 1 and 2 rows under single content header. |
| **2** | Current participant key, unrelated nonnull epoch lease supplied | **Constructible** (via staged public APIs) | Caller calls `Configure(Timelines, ValidKey, UnrelatedNonNullLease)`. `Configure` only checks `!Lease` (non-null), not equality with `Config->Content`. `BindTracker` checks `IsCurrent(Key)`, which passes. | **Potential Assurance Gap.** Observer actively samples gameplay using an unrelated catalog lease, masking catalog mismatch. |
| **3** | Observer survives member loss | **Constructible** (via staged public APIs) | `Context->UnbindActor` removes encounter records. On next callback, `OnSnapshot` fails `FindParticipant`, calls `Cursor.Close()`, and returns. However, direct public calls to `ObserveAfterTracker` bypass this check. | **Locally Enforced Callback Guard / Low-Level Entry Gap.** Tracker callback path halts; direct public method lacks context check. |
| **4** | Teardown/recreation with new definition/content epoch | **Counterfactual Future Scenario** (Not constructible on existing instance) | Current APIs reject live rebinding of begun-play actors (`Binding.cpp:153`) and reject re-configuration (`ShadowCompare.cpp:95`). Requires full component destruction and new actor binding architecture. | **Explicit Future Design Choice.** Dynamic re-binding/re-configuration does not exist in current APIs. |
| **5** | Correct rows, incorrect caller `local_epoch` / `content_hash` | **Constructible** (via staged public APIs) | `FlushReport(RunHeader, OutPath)` checks that `RunHeader` contains all 17 required field names. It copies caller values without comparing `local_epoch` to `ContentLease->Id` or `content_hash` to `Config->StableManifestHash`. | **Potential Assurance Gap (Producer/Checker Decoupling).** Serialized JSONL header can claim false provenance while buffered rows reflect different execution. |
| **6** | Same deterministic content, separate lifetime epochs | **Constructible** (via staged public APIs) | Two calls to `RPGCombatRegistry::Compile` with identical asset definitions produce two `FEpoch` instances with different `FGuid::NewGuid()` values. | **Caller / Construction Invariant.** Distinguishes instance lifetime tokens from deterministic content identity. Digest equality does not imply same session instance. |

---

## 5. Discriminating Unrun Witnesses & Test Proposals

The following four discriminating unrun witnesses are specified using strictly observable public APIs and complete prerequisite baselines:

### Witness A: Unrelated Lease Injection Acceptance (Challenging Case 2)
- **Objective:** Demonstrate that `Configure` and `BindTracker` accept an unrelated epoch lease when provided valid current keys and tracker ownership in a Development target.
- **Prerequisites (Unrun Proposal):**
  1. Target compiled with `!UE_BUILD_SHIPPING`.
  2. Live `URPGCombatContextSubsystem` with bound encounter participant (Key A, `Config->Content->Id == Guid_A`).
  3. Pre-compiled, non-empty, compatible timeline artifacts matching the actor's mesh and montage.
  4. Separate independent test catalog epoch compiled, yielding `Lease_B` (`Lease_B->Id == Guid_B`, where `Guid_B != Guid_A`).
  5. Unregistered `URPGCombatTimelineShadow` component attached to Participant A's actor (`Tracker->GetOwner() == GetOwner()`).
- **Procedure & Observation:**
  1. Call `Configure(Timelines, Key_A, Lease_B)`: verify returns `true`.
  2. Call `BindTracker(Tracker, Context)`: verify returns `true`.
  3. Inspect public observation count via `GetRecordCount()` after a tracker event: if records increment, confirms observer actively samples under an unverified epoch lease.

### Witness B: Mixed-Generation Buffer Integrity (Challenging Case 1 & Row Metadata)
- **Objective:** Demonstrate that `OnSnapshot` key adoption preserves row-level generation discriminators across resets while retaining existing timeline artifacts.
- **Prerequisites (Unrun Proposal):**
  1. Configured and bound observer on Participant A (`Generation = 1`) with buffer capacity `< MaxRecords`.
  2. Matching playback montage and active section to ensure valid artifact matching in `FPlaybackAdapter::Observe`.
- **Procedure & Observation:**
  1. Dispatch tracker event at Generation 1; verify public `GetRecordCount()` equals 1.
  2. Inspect row 0 via public getter `GetRecordJsonForTest(0)`: verify JSON string contains `"generation":1` and does not contain `"local_epoch"`.
  3. Invoke `Context->OnGenerationChanged(Actor, 2)`.
  4. Dispatch second matching tracker event via `OnSnapshot`: verify `GetRecordCount()` equals 2.
  5. Inspect row 1 via `GetRecordJsonForTest(1)`: verify JSON string contains `"generation":2`.
  6. Confirm that rows carry generation numbers, distinguishing reset continuity without claiming mixed-epoch failure.

### Witness C: Member-Loss Callback Guard vs Direct Entry Bypass (Challenging Case 3)
- **Objective:** Distinguish `OnSnapshot` callback rejection from direct low-level `ObserveAfterTracker` entry after member unbinding.
- **Prerequisites (Unrun Proposal):**
  1. Valid bound participant with 1 pre-existing record (`GetRecordCount() == 1`).
  2. Complete valid 17-field `RunHeader` baseline prepared.
- **Procedure & Observation:**
  1. Invoke `Context->UnbindActor(Actor)`.
  2. **Callback Path Test:** Dispatch a tracker event via `Tracker.OnAfterObservation` (triggering `OnSnapshot`): verify `GetRecordCount()` remains 1 and `GetDroppedRecords()` is not incremented (cursor closed and returned).
  3. **Direct Entry Negative Control:** In the same test fixture, construct an `FObservation` `O` matching the old participant key and an existing timeline key; directly call public `ObserveAfterTracker(O)`:
     - Observe whether `GetRecordCount()` increments to 2.
     - Confirms that public `ObserveAfterTracker` lacks context/membership checks, demonstrating the exact scope boundary between the guarded callback and the low-level entry.
  4. Call `FlushReport(RunHeader, OutPath)`: verify serialization and file write success under a complete valid header baseline.

### Witness D: Complete Header Provenance Disagreement (Challenging Case 5)
- **Objective:** Demonstrate that `FlushReport` serializes a false caller header when all 17 required fields are present and I/O succeeds.
- **Prerequisites (Unrun Proposal):**
  1. Configured observer holding valid `ContentLease` (`Id == RealGuid`).
  2. At least 1 recorded observation.
  3. Base `RunHeader` containing all 17 required fields (`run_id`, `dll_hash`, `source_manifest`, `map`, `requested_source`, `published_source`, `content_hash`, `local_epoch`, `validity`, `cvars_start`, `cvars_end`, `window_state`, `game_sample_dt`, `slate_sample_dt`, `assets_before_after`, `scripts_before_after`, `net_mode_role`).
- **Procedure & Observation:**
  1. Set `RunHeader->SetStringField("local_epoch", "00000000-0000-0000-0000-000000000000")` (fictitious nil GUID, differing from `ContentLease->Id`).
  2. Ensure directory write permissions in `Saved/BossCombatReview/Shadow/`.
  3. Call `FlushReport(RunHeader, OutPath)`: verify returns `true` and `OutPath` is non-empty.
  4. Read the first line of the output JSONL file: verify it contains the fictitious nil GUID, proving that `FlushReport` enforces field name completeness but performs zero equality checks against component leases.

---

## 6. Options for Architecture & Contract Design (Proposals Only)

Without mandating new schema changes or altering existing pack flows, the following architectural alternatives are identified:

1. **Explicit Lease Matching at Bind Time (Candidate Design):**
   - Proposal: In `URPGCombatTimelineShadow::BindTracker`, check that `InContext.IsHydrated(Participant)` and that `ContentLease->Id` matches the participant config's content epoch ID. (Note: `FindRecord` does not exist in the current public header; this represents an illustrative future accessor design, not compilable current code).
   - Effect: Prevents premature pre-hydration binding (when other prerequisites are satisfied) and closes the Case 2 unrelated lease injection gap.
2. **Low-Level Entry Guarding (Design Trade-Off):**
   - Proposal: In `ObserveAfterTracker`, if `Context.IsValid()`, consider adding `if (!Context->IsCurrent(Participant)) return;`.
   - Trade-Off: A conditional `if (Context.IsValid())` check still leaves context-free direct calls allowed; whether direct diagnostic fixtures should be permitted context-free or strictly require context membership remains an open contract design choice, not an unconditional invariant.
3. **Truthful Single-Header Association for Same-Content Resets:**
   - Proposal: Retain the single file header for same-content generation advances, relying on individual row `generation` discriminators. Only require report splitting or re-association when participant definitions or content epochs actually change.

---

## 7. Conclusion & Scope Verification

- **Offline Adversarial Review Complete:** Conducted entirely through static code analysis, transition mapping, and architectural critique.
- **Zero Forbidden Edits:** No edits to `Source/`, `Config/`, `Scripts/`, Unreal assets, or Codex drafts.
- **Zero Prohibited Executions:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
- **Git Authority Preserved:** In strict accordance with `RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`, no git commits or pushes were performed.
