# D07 v2 — DD-1 steps 2/3, aligned with step 1 v2

Codex, 2026-10-25, C-99/C-100 follow-up. **DRAFT / REVIEW-REQUESTED, NOT STARTED.** This new revision preserves `D07_STEP2_STEP3_SPEC.md` intact. It incorporates that draft's step2/step3 goal/non-goal, field mapping, initialization, witnesses, compiler/traversal/report/proof/rollback contracts by reference, with the explicit replacements below. Where they conflict, this revision controls. Read alongside `D08_STEP1_V2_REREVIEW.md`; neither document accepts a pending baseline or authorizes implementation.

## Revision map

| Original D07 area | V2 replacement/addition |
|---|---|
| Shared precondition1 | Step1 means STEP1_SPEC_v2 plus accepted D08 clarifications; actual clean baseline supplement/results required, not the contaminated run |
| Shared epoch wording; step2 new-code1/2 | Game-instance-owned immutable content epoch; world-owned encounter runtime context; no mutable process-global registry or global restoration |
| Step2 reference readiness/ownership | Value-copied metadata is separate from strongly owned loaded runtime dependencies; no assumption that soft paths prevent GC |
| Step2 lookup/build compatibility | Stable BuildId end to end, pinned three legacy slots, context-explicit facades and non-injective style mapping |
| DD-1 networking non-goal | No new network gameplay execution in these steps, BUT authority seams/identity fields designed now; networking built and verified through later phases in parallel, not postponed to P8 |
| Step3 artifact and report identity | Content fingerprint plus context/session/world/participant/generation; authority/time provenance explicit, no fabricated accepted token |
| Rollback/source modes | Startup-isolated strict-data versus compatibility-auto policies; no Shipping source switch, no global epoch pop or asset rename |

The unchanged original sections remain normative, including: explicit participant binding, hydration before registration/first consumption, no Boss01 fallback, per-instance state, no pack writes, preserved startup/delayed setup behavior, exactly one production executor, multiwindow per-variant compiler, shadow-only observer, crossed traversal and discontinuity rules, corrected measured-behavior table, complete provenance and no leapfrogging.

## 1. Shared prerequisites and exact source policy

Before step2, Claude must have step0 accepted against the fresh-editor clean run and current automation, step1 specification accepted after D08, step1 implementation reviewed/tested/accepted and exact next file claims posted. Before step3, step2 is accepted. Clean-run absence is pending evidence, not a pass/failure. Current evidence independently supports37 recorded automation successes; the initial contaminated35/39 run is not parity. Retain all artifacts; do not discard an unexplained clean failure as “old contamination.”

Source policy is latched per new game-instance context before consumer activity:

- `auto`: complete valid data bundle or complete legacy-compatible bundle with an explicit diagnostic. This is permitted only when the release/binding deliberately allows legacy compatibility.
- `legacy`: complete legacy bundle only, Development startup rollback/proof mode; no pieces of a data bundle are read for missing fields.
- `data`: complete required data bundle or initialization failure. Missing boss/move/weapon/presentation cannot silently become an existing entry, and missing required referenced content cannot yield a partly live stack.
- Malformed fixtures and injection: isolated Development/automation contexts only, with explicit requested strict/recovery policy and expected result. No fourth production source.

Source cvar/injection entry points are compiled out of Shipping. For current DD-1 compatibility shipping, `auto` is a declared policy, not proof of data completeness. P8 new-content/canary and eventual required-data release validation must fail on fallback or required missing rows. Rollback in Shipping requires the previous supported release/binding at startup through its approved deployment procedure, not a nonexistent runtime cvar. No new deployment mechanism is implemented by this draft.

Changing a Development cvar after publication reports next-session-only; no mid-fight/equip or active-context rebinding. Boss01-first, fixture, Boss01 proofs each identify the actual selected mode, bundle source, fingerprint and fresh context; displaying three expected rows is not proof that `data` didn't fall back.

## 2. Step 2 — code/asset scope and epoch lifetime replacement

Keep the original step2 schema/types/assets/consumer closure and Claude ownership. Extend the accepted step1 `FRPGCombatEpoch` and registry rather than introducing a competing boss-only catalog/source selector. All additions remain proposed claim changes; do not assume “No other file” in step1 authorizes later step2 edits.

### Ownership layers

**Game-instance content owner:** one subsystem/context owns an immutable published `FRPGCombatEpoch` containing value-copied strings/names/numbers/soft paths, legacy-slot map and validated definition/variant references by stable identity. Publication occurs once dependencies are ready and before any build/equip/HUD/encounter consumption. Same game instance across world travel retains its content epoch; a new game instance gets a fresh one. Asset-authoring objects may be released after extraction if no consumer uses their fields/pointers. A module-global mutable current epoch and “restore previous global epoch at teardown” are prohibited.

**Loaded dependency lease:** UObject assets/classes/textures/meshes/montages needed by runtime are not kept alive by copying FSoftObjectPath. The owner/context holds strong references or explicit supported load handles for the required lifetime, separately from immutable scalar metadata. Resolve and validate required packages/class ancestry/style compatibility and cook closure before activation. Teardown releases only its leases. No constructor return pointer or FBuildEntry const TCHAR* may outlive its pinned owned storage. Existing loaded pack/equip behavior stays compatible; this is not permission to change timing by blocking the game thread at first attack.

**World encounter owner:** original D07 `RPGCombatContextSubsystem` remains per-world, references its game-instance epoch and owns weak bound actors plus independent encounter-instance state/generations. It cannot publish or swap content epochs. Two worlds/game instances can share an immutable compiled cache entry by content fingerprint but never mutable targets, choice state, HP, cooldowns, traces, delegates or timers. World teardown clears only its state; game-instance teardown never installs a previous global context.

**Pure tests:** explicit non-global registry contexts may build snapshots without a world. Scoped injection targets only an unstarted test/game-instance context, unwinds on failure and cannot modify an existing live context. Legacy no-context helpers may retain immutable baseline-only behavior; all new data-aware runtime operations receive a context/epoch. Do not use GWorld, first world, first actor or the last test context as an implicit answer.

Document exact init dependencies and first-read trace rather than asserting subsystem Initialize automatically precedes every consumer. Original D07 create->hydrate->register order and pack startup-overwrite protections still govern. A missing pre-start route for a pre-existing component is a blocker, not a post-BeginPlay data patch. Per-context readiness must not grant an extra attack hold, earlier wake or different retry cadence.

### Build/weapon/participant integration

BuildId travels through selection, requested/chosen/equipped records, deferred apply/reset, equip lookup, verification and HUD. LegacySlot0/1/2 is pinned for the original three, independent of UI order; unsupported ID-to-enum conversion returns explicit failure, while legacy invalid-enum99->Dex stays its separate old behavior. Encounter hydration must pass the same epoch as the player's selected build; no player-global chosen build leaking across contexts.

A style is equipment evidence, not always a unique BuildId. Allow multiple builds referencing one weapon where the data contract permits; preserve known chosen/equipped identity from the verified transaction, display actual equipment separately, and return Ambiguous/Unknown for underdetermined reverse lookup. Do not silently label the fourth build Starter/Dex because it shares a style, or choose the first UiOrder row. Keep original special SwordAndShield/Twinblade HUD wording and alias parity. Invalid requests leave state unchanged.

Attack-table compatibility remains unchanged for current content. Add coverage/provenance metadata per weapon/action: exact style row, any-weapon row or final fallback, declared missing-row policy and effective values. A compatibility fallback warning is not a complete new-weapon data proof. Required-data/P8 weapon fixtures require authored coverage; absent optional kinds have explicit reasons. Step2 does not edit attack rows/balance by stealth. A deliberately reduced fourth-build fixture remains labeled as such.

Optional presentation fields, including icons, may use an explicit text-only/disabled fallback; required gameplay refs fail. Distinguish absent icon from broken authored ref and emit diagnostics. Original first-three UI geometry/icons/input remain unchanged; rows hidden by overflow cannot be painted/clicked/number-key/focus-selected inconsistently. The fourth entry must be visible/selectable in the actual1080p proof. No new scrolling/art feature is implied.

## 3. Step 2 — authority/identity seams now, network mechanics through phases

C100 records owner re-confirmation of all83 including QA-008, with networking developed alongside each phase. Replace any reading of original D07 “no network execution here” as deferral to P8. DD-1 builds the following identity/authority DATA CONTRACT, without claiming new replicated gameplay or adding unauthorized mechanics:

- Stable content IDs/fingerprint are distinct from runtime instance identity. Actor names, memory addresses and local increment-only observation counters are not network actor/action identities. Store context/session/world, encounter binding/instance, participant slot and generation separately; network actor/channel identity is optional until a real network binding exists, then validated, not guessed.
- Definitions declare the supported authority-policy/version and gameplay ownership roles. Per-instance context records actual local net mode/role and authority provenance. A standalone observation is labeled standalone, never “server-authority verified.” Data cannot authorize a client to write authoritative HP/posture/cooldown/phase or a denied tool.
- Epochs are locally owned; they are not made equal across machines by reusing a process-local epoch number. Content fingerprint/manifest compatibility is the future handshake input. Local epoch IDs remain diagnostic and never substitute for replicated accepted-action identity or authoritative start time.
- Future P2 action contract reserves separate server action identity, source actor/generation, MoveId/VariantId/section, chosen target binding, authoritative start time/time domain, phase and terminal reason. Missing fields are null with an unavailable reason in DD-1, not populated from a post-play observer and advertised as pre-acceptance truth. Do not implement a second transaction authority now.

Sequenced proof ownership: DD-1 context isolation/identity and dependency scope; P1 cue metadata must support remote observation without client damage authority; P2 server-owned accepted-action/terminal transaction and playback start/section/target identity; P3 authoritative hit/defense/posture/damage; P4 geometry/contact replication implications; P5 paired/grab lifecycle and remote interruption; P6 selection/defense/adaptation/fallback authority and shared observation snapshot; P7 phase/reset authority. Add focused listen/dedicated multi-client tests as these paths become real, not first at P8. P8 performs the integrated80/150ms RTT/nonzero-packet-loss acceptance plus join/disconnect/reset cases and final83 recount. This table is sequencing, not authorization to start a P-phase before DD-1 acceptance. No bandwidth/fairness claim is inferred from scalar fields alone.

## 4. Step 3 — compiler/cache/context amendments

Retain the original step3 goal, non-goals, full variant inventory, compile contract, traversal semantics, comparison classifications and corrected symptom table unchanged. Production tracker/pack/native effects stay authoritative; no AN/ANS assets are authored merely to make comparisons pass. No blanket zero-root-motion rule or mandatory socket offsets from an AG validator becomes runtime policy.

Use two distinct keys:

1. **CompiledContentKey:** stable definition/move/variant IDs, complete source identity/hash, section/segment/slot mapping, schema/compiler/notify-adapter version and declared compatibility profile. It may be cached across contexts ONLY if fully immutable and exact fingerprint matches. A game-instance epoch references it; a local epoch number alone is not a cache/content identity.
2. **ObservedPlaybackKey:** session/world/game-instance context, encounter instance/participant/generation, local playback ordinal, actual montage object/source variant/section, optional exposed engine montage instance. Never labels itself a production accepted token. Actual authoritative action/net IDs are separate nullable fields, only filled by later true authority; no retrofit “acceptance” from a seen montage.

Observer state, previous/current positions, traversal/loop ordinals, pending events, dropped-record counts and incomplete stop reasons are per actor/generation/context. Strong dependency leases keep animation objects valid; weak actor refs and context cancellation prevent late callbacks from crossing worlds or respawns. Teardown of one game instance never resets another's cache ownership/state. Compilation is deterministic from pinned content, not whichever globally loaded test catalog was last pushed.

Source/alias resolution uses the accepted epoch: full object/class/segment identity, no base-name-first matching. Authored/fallback variants remain distinct; A2's two engine collision windows versus one tracker Active interval is an expected reported discrepancy, not permission to change active execution. A4 bounds-axis estimate and capsule-bottom proxy remain evidence limitations; no geometry rewrite. A5 stays nominal0.45 and sampled0.47; sidecar0.40 remains intent. Natural A2 sample count is not a future deterministic ratio.

### Report additions

Extend original D07's header with game-instance/context ID; latched requested source and actual published source; compatibility/strict policy; local epoch and stable content fingerprint; actual authority/net role; dependency lease/validation result; table-coverage route if relevant. Include optional authoritative server/action/target/phase/time fields as unavailable until genuinely observed, with time domain and clock source. Never compare local montage seconds directly to wall/server time or claim clock synchronization from matching epoch numbers.

Keep original per-playback provenance and classifications. `auto -> legacy` must be visible in the header and invalidates required-data/canary proof; it cannot be hidden by successful three-build rows. Unknown/ambiguous style/variant metadata is a finding, not invented identity. Standalone shadow comparisons remain local evidence; network tests later compare actual authority/remote observations with their own tolerances and clocks.

## 5. Additional proofs and unchanged acceptance boundaries

Add these to the original D07 proof lists; they are future Claude-owned tests after accepted scope, not runs by Codex:

- Two simultaneous game-instance registry contexts with different fourth-build fixtures; equip/UI/reset/teardown of one cannot alter the other. Repeated fresh PIE, world travel within one instance and a later fresh instance prove the chosen lifecycle. Pure automation injects no process-global epoch.
- `auto` valid/absent/invalid, explicit legacy, strict data absent/invalid, rejected live source changes and scoped fixture failure/unwind. Assert the actual source/fingerprint, not only row count. No Shipping switch/injection symbol accidentally reachable.
- Runtime dependency lifetime under GC versus scalar snapshot lifetime; held legacy returned references; invalid fully qualified item/class/style references; shared-style builds; missing row with explicit compatibility policy versus required coverage. Existing three builds retain exact values/call ordering/text.
- Two world/participant contexts sharing a compiled artifact, independent playback histories; reset/destroy/late callback/teardown and same-asset restart. No cached-world pointer or stale generation attribution. Dropped diagnostics are visible and do not trigger gameplay.
- Network seam schema/role/version validation and explicit unavailability of absent server identifiers. This does not count as replicated-action/server-authority runtime proof; phase-specific real tests remain required.
- Preimage and owned-delta rollback of dirty RunDrivers.ps1 preserves pre-existing owner rows; assets are never renamed/deleted for absence tests. New later schema additions preserve readable/versioned legacy compatibility without mixing epochs.

Do not change original regression meanings/totals silently. New tests add their own counts and expected results. The clean baseline and supplements pin actual command/settings/dependencies/results and file-set drift; archived contaminated failures are retained with uncertainty. No probes run during Claude's clean gate. Exact source changes, missing startup hooks, map serialization needs and API/context consumer closure are reviewed before claims become implementation.

## 6. Rollback, claims and handoff

For Development, select the prior complete source/binding before a new session; end the existing encounter/session safely first. Game-instance/context creation, not a global Pop, determines publication. Immutable content may remain cached; mutable context and loaded dependency leases are released only by their owners. Restore only owned deltas/preimages, never whole dirty files blindly. No asset rename/delete, resets/stash/checkout, commits or pushes. Shipping source-switch controls do not exist; keep deployment rollback separate.

Claude next adopts D08's bounded clarifications, supplies actual clean baseline/supplement, secures step1 acceptance and implementation proof, then reviews this D07v2 as the next-step specification. C100's scope confirmation resolves the size decision; no new owner tuning/feature choice is embedded here. G4/G5 remain denied. A50 is an unreviewed offline submission, not an approved gameplay or authoring policy. Original D07 remains provenance; this revision plus its retained clauses is the current proposal.
