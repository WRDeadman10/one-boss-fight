# D02 — Data model, migration and canary proposal

2026-10-25. CI-P0-D-01/T2; Codex; REVIEW-REQUESTED. Proposal for Claude's DATA_DRIVEN_ARCHITECTURE_GATE, not approval to change code/content. Current behavior and owner numbers remain the migration baseline. The owner asks for reusable combat driven by data; this document makes no factual claim about Elden Ring's internal implementation.

## Smallest ownership model

Use the existing UPrimaryDataAsset pattern in RPGWeaponAttackTable.h:59 as the precedent. Six content definitions plus one shared runtime catalog are sufficient; nested structs can stay embedded instead of becoming a class/asset per number. Stable IDs identify bosses, moves, weapons, builds, phases, windows and cues. IDs do not require C++ enum additions. A finite shared executor kind (weapon sweep, planar sweep, projectile, radial wave, paired action) is code behavior; parameters and composition are data. The canary guarantees new content within those supported capabilities. Entirely new physical mechanics may require extending the shared capability library through a later approved change; do not promise an arbitrary scripting language.

Relationship:
EncounterDefinition -> BossDefinition -> BossMoveDefinition[] / phases / lifecycle;
BossDefinition -> PresentationDefinition;
BuildDefinition -> WeaponDefinition -> existing attack-table rows + action bindings;
RuntimeCatalog -> definitions, pack adapter version, shared player combat/HUD profiles.

One generic encounter context owns participant identity and generation. One combat runtime owns accepted action identity, timeline, cancellation and next-selection gates. Shared effect executors consume that context. Per-instance mutable HP/posture/cooldowns/history/targets/hitsets/phase/rate state never lives in a data asset or a global singleton keyed only by move name. Two actors may share an immutable definition safely.

## Field contract

Each table row defines a field group and explicitly lists its members. All lengths cm, angles degrees, angular speeds deg/s; real seconds and animation-local seconds use distinct names/types. Optional values are explicit, not magic negatives in the canonical model. Existing -1 conventions stay only in the compatibility reader.

### RuntimeCatalog / adapter / player profile

| Fields and type | Current source replaced | Animation source? / validation |
|---|---|---|
| SchemaVersion integer; CatalogId; registered Boss/Move/Weapon/Build/Encounter/Presentation soft refs; DefaultEncounter; legacy aliases | WeaponAttackTable.h:84 singleton path; BuildRules.h:8/23/107 fixed enum/count/parse | No. Unique stable IDs, registered cook dependencies; explicit missing-data policy |
| PackAdapterVersion; pack class/interface refs; attribute/tag bindings; function/property/enum bindings; ability config descriptors | PlayerMovesSubsystem.cpp:80/93; BuildRules.h:26; Pack/RPGPackTrace.cpp:211/221/238; BuildLoadout.cpp:876+ | No. Shared integration ABI, validated against installed pack once; not arbitrary names authored independently per boss |
| PlayerCombatProfile: input action refs; Dodge quick/full playback/rates/doubleTap/backward-turn policy; iframe intervals; camera profile; consumable activity/item binding | DodgeTiming.cpp:27 and h:42-86; CameraRig.h:33-54; HealPunish.cpp:236; FlaskHud integration | Dodge/iframe windows may be animation-derived, command timing stays data; keep .30 double tap, 3.2m roll and owner-kept effective iframe windows |
| EquipmentPolicy: apply gates, retry/verify timeout/max attempts; slot lock policy; actual-equipment display binding | BuildLoadout.h:32-48 and BuildRules decision functions | No. State machine/safety invariants remain shared code; content profile supplies tunables, not custom callbacks |

The catalog is loaded/prevalidated before encounter activation. Prefer soft references plus explicit preload/cook closure and pinned runtime references. Loading on first hit/release/phase change is unacceptable. No constructor fallback can silently turn a new boss into Boss01. Development can support an explicitly selected LegacyCompatibility profile with loud diagnostics; canary/Shipping acceptance requires complete selected definitions.

### BossDefinition

| Fields and type | Current source replaced | Animation source? / validation |
|---|---|---|
| BossId, localized DisplayName; pack pawn/controller/style/BT/BB refs; skeleton/animation profile; default presentation ref | IsPackBoss class string, Subsystem.cpp:143-281; live E-002 route | No. Boss registration supplied by encounter binding; no asset-name discovery |
| Stats: MaxHealth, base attribute values; Posture {max, regenDelayRealSec, regenPerRealSec, packPoiseIntegration}; StatusResponses.Bleed {enabled, initialThreshold, perProcIncrease, maxThreshold, maxHpFraction, cue} | Encounter.h:40; Posture.h:31-43; Bleed.h:30-53 | No. Initial Boss01 values 2000, 100/6/13, bleed100/+20/cap200/.03; retain exact owner behavior |
| MoveRefs[]; AbilityBindings[] {bindingId, classRef, tags, granted order, configured move refs, slot/index mapping, cooldown owner}; selector policy ref | Tracker.cpp:24-103, StartMove map at241, CloseClipSwapRules.h:12-14; E-002 grants | No. Include MidRange/Sprint/Retaliation and death/lifecycle grants; reject ambiguous move resolution |
| Phases[] {PhaseId, entry predicate on normalized HP, one-shot transition, transition playback, interruption/queue policy, persistent modifiers, enabled moves, cue override} | BossPhases.h:31-113; cpp:56-59 | Transition duration can be animation-derived; threshold/modifiers cannot. Boss01 phase2 .60, move/rate1.2, attack1.25, leap gate retained. Apply/reverse modifiers once using owned handles/baselines, never multiply repeatedly |
| Lifecycle {dormant playback, wake playback/gate, death playback/mode/freeze point, timeout, ragdoll policy, remains cue, cleanup policy} | DormantWake.cpp:20/21/86/109; Death.h:51-93 | Playback timing from specific variant animation; no global 9999/40-loop magic as content. Bounded abort/watchdog remains code |
| Stagger {threshold response, duration, fall/down/getup playback, immunity policy, cooldown, posture hold}; RiposteSpec {range, facing/cone, paired playbacks, align/exit policy, impact marker, damage, input-lock policy} | Stagger.h:36-91/129-225; cpp:138/624 | Windows/impact from animation, geometry/damage from data. Preserve reversed Fall getup and 40*2.5=100 impact; do not substitute standalone GetUp FBX silently |
| ConflictPolicy reference; readiness predicate; recovery/next-selection policy | BossRules.h; Interrupt; Tracker.CanStartMove/Tick | Shared validated priority code; data selects supported policy, cannot disable death/reset safety |

All phase counts are arrays, not a boolean IsPhaseTwo for new content. Legacy IsPhaseTwo diagnostic/UI getters can map to the Boss01 phase alias. The owner policy (death/reset, phase queued behind break, accepted riposte, break, committed attack, selection) remains a shared invariant until explicitly changed.

### BossMoveDefinition

| Fields and type | Current source replaced | Animation source? / validation |
|---|---|---|
| MoveId; family tags; semantic roles; enabled; activation {bindingId, entry section, request channel}; compatible skeleton/profile | Tracker MoveId/name map; CloseClipSwap; hard-coded A2/A6 feedback | No. Role tags trigger feedback; no MoveId switch in executor |
| Eligibility {phase set, min/max planar range, root/surface distance convention, yaw cone, height interval, target validity, LOS/current-lastseen policy, resource requirements, cooldownGroup}; ReactionTrigger {observed activity tag, detection binding, minimum delay, expiry, feasibility and budget} | BranchRange/Cone; HealPunish.h:37-80 / cpp:236; phase locks; BT constants in E-002 | No. Gates evaluate fresh context at request and branch; no future-input knowledge. Heal trigger records detection on potion montage edge today |
| Selection {weight, range preference curve, family/history penalties, seeded tie policy, adaptation profile, fallback action}; cooldown {duration, start policy, failure refund, phase/reset policy} | Pack BT weights/bands and ability cooldowns, HealPunish.Cooldown | No. One selector owns attempts and successful-start accounting. Existing pack cooldown may remain authority per binding; never count twice |
| Variants[] {VariantId, montage OR sequence ref, slot, section, rate, blendIn/Out, motion mode, loop/hold section policy, TimelineSource}; explicit missing-variant policy | Tracker.cpp:150-169/205, FallbackMontageName and ClipPath, BossClips.h | Yes for asset/section timing; rate/blend/motion policy content data. Authored and fallback have distinct timelines, never merely names on one row |
| TimelineSource {AnimationCompiled or ExplicitCompatibility}; compiled artifact {asset hash/version, segment/section mapping, marker IDs, windows}; compatibility timeline source citation | Constructor commit/active/recovery duplication | Animation is canonical in final design. Compatibility timeline explicitly preserves old code values until approved migration; mismatches cannot be auto-overwritten from sidecar |
| Tracking {target snapshot policy, allowed yaw window, cap curve, postCommit policy}; Motion {None/Nav/Root/Manual/Warp capability, handoff boundaries, path/landing safety, caps} | Tracker.TrackTurnRate/commit lock; pack rotation/movement notifies; leap movement | Windows from animation; mode/caps from data. Exactly one translation/rotation owner at a time. Root motion allowed when declared/path-safe; no universal in-place mandate |
| Effects[] {EffectId, trigger marker/window, executor kind, ShapeSpec, DamageSpec, DefensePolicyRef, HitGroupId, contact policy, lifetime/cleanup}; see next table | LowSweep/HealPunish/Javelin/Shockwave bespoke components | Release/active endpoints from animation; physics and damage data. More than one window/effect supported |
| Followups[] {GateId, source marker/window, target MoveId, prerequisites, range/cone/LOS/hit outcome policy, max uses/depth/time, consume rule, default recovery}; EarliestNextSelection marker | bBranchStage/global branch check, AN_PerformFollowUp | Gate location from animation; graph/predicates from data. Strict source instance/gate token, once-only; cannot authorize earlier selection than configured active closure |
| Presentation {telegraph cue refs, sound/VFX/shake/rumble/hitstop events, effect scale/radius bindings, low-effects alternative} | Legend A2/A6 condition; flipbook switch, debug ring | Cue interval/placement animation; cue definition and damage-volume linkage data. Cue must remain correct with debug drawing disabled |
| Safety {maximum action real duration, holdMin/Max and prechosen sampled duration, interrupt profile, release terminal policy, root/motion restore}; evidence refs | component grace/timeout checks and per-class cleanup | Animation duration can seed bound, but watchdog uses real time. Loss of notify must never strand offense/movement/input |

Do not use data-defined arbitrary Blueprint code per move to evade the no-new-combat-code canary. Supported effect/predicate composition is declarative and bounded. New move ID strings need no code change; a new capability is an explicit architecture extension.

### Shared effect, shape, damage and defense structs

| Fields | Replaces / evidence | Behavior contract |
|---|---|---|
| ShapeSpec.WeaponSweep {production component role, socket list or curve samples, radius, sample spacing/error bounds, collision channels, blockers}; optional visible correspondence map | PackTrace::FTarget GetMesh/GetSockets/radius; TraceGuard; E-002-10 notify tracks | Hidden driver or visible mesh may own queries if world-space agreement is measured. Names/identical local sockets do not prove parity across transforms. No universal 20cm radius or mandated BladeEnd tip change |
| ShapeSpec.PlanarSweep {origin role, inner/outer radius, height/vertical tolerance, from/to angle, curve/time mapping, capsule convention, blocker policy} | LowSweep.h:37-55, BossMath/SweepTouches | Shared swept interval query; preserve Boss01 20 damage, 60..380cm,40cm height,+90..-90. Changing geometry is later approval |
| ShapeSpec.Projectile {spawn attachment roles/fallback policy, orientation offset, targeting snapshot, speed/range/radius/flight policy, spawn penetration grace, lifetime, homing flag} | HealPunish.h:48-76; Javelin.cpp:25/38 | Spawn/release validated against originating action; no tracking after commitment unless explicitly approved. Boss0112 damage,radius25,max3000; speed bounded450..2500 from flight1.2 today |
| ShapeSpec.RadialWave {origin/ground binding, initial/max radius, speed/thickness/height, terrain/LOS rule} | Shockwave.h:39-57 | Boss01 48 damage,200..1100cm,1000cm/s,180cm thickness,50cm clearance retained. Sweep prior-to-current annular region so large steps cannot skip; this correctness change needs approved implementation/test, not migration-by-stealth |
| DamageSpec {baseHp, posture, stamina/guard, status buildup, phase scaling, impact reaction, hitstop cue}; HitPolicy {hitgroup, perTarget cap, rehit interval, reset boundary, central-vs-wave priority} | HP-only specials vs pack outcome path; DamageResolver payload; HP-delta central priority | Shared resolver attributes actual contact/result to source action/effect/target/generation; no HP delta inference or late refund for new path. Existing compatibility path remains explicitly labeled until parity proven |
| DefensePolicy {dodge/iframe, jump clearance, block/parry/unblockable, armor/flinch/posture rules, simultaneous outcome precedence} | BossDamage.h, resolver and pack attack-data policies | Common resolver verifies alive/generation and defense at resolution; data cannot bypass required validity/safety. Hyperarmor resists flinch; it must not automatically grant full posture-break immunity |
| Material/cue binding {asset ref, attachment, offsets, lifetime, parameters, volume->visual mapping} | FlipbookEffect; Look/Remains slots; Javelin art | Shared event owner cleans cues on terminal/reset; particles never constitute damage authority |

### WeaponDefinition

| Fields | Replaces | Animation source? |
|---|---|---|
| WeaponId; item asset; style asset; spawned actor class; granted ability refs; accepted style aliases; equipment slot binding; name/icon | BuildRules rows50-52/69; BuildLoadout.CallEquip; UI icon arrays | No. Prefer object refs/stable IDs over asset base names |
| Visible mesh/materials/attachments; ProductionQueryProfile; skeleton/socket compatibility | look sword and hidden weapon coupling | Skeleton/socket topology inspected as assets; offsets explicitly data |
| Actions[] {ActionId, kind, pack binding/montage variant, attack-table row ref, followups}; row {posture, stamina policy/amount, HP multiplier, bleed, hyperarmor window} | RPGWeaponAttackTable rows and HitIntake action inference | Active/hyperarmor windows can come from actual montage; retain exact row behavior during migration |
| Status/defense/movement modifiers and presentation ref, optional spare/offhand associations | fixed archetype assumptions / dual/twin aliases | No. Validation prevents two weapons sharing one mutable swing identity |

Keep URPGWeaponAttackTable as the compatibility view of WeaponDefinition rows. Remove constructor-authored balance values only after authored assets and cook validation exist. New consumers key by WeaponId/ActionId; old (style name,ERPGAttackKind) lookups map through the registry until migrated. Enum attack-kind categories can remain shared; weapon identities cannot require enum cases.

### BuildDefinition

| Fields | Replaces | Animation source? |
|---|---|---|
| BuildId, display name, aliases, icon, UI order/visibility | ERPGBuild/BuildCount/Parse/three UI rows | No; registry driven UI supports fourth entry |
| Equipment[] {slot binding, WeaponId/item ref, offhand}; initial stat profile/ref; accepted actual-equipment states | BuildRules table and style->build special cases | No. Current builds only choose equipment; preserve current stats rather than introducing archetype buffs |
| HUD description template and actual equipped weapon name; encounter-change policy | BuildLine/DescribeStyle, equip/defer suffix logic | No. Shared pending/failed/deferred status displayed independently of requested build |
| PlayerCombatProfile ref and permitted customization refs | fixed dodge/input/player settings | Shared kept defaults; data does not silently retune iframe/roll |

### EncounterDefinition and PresentationDefinition

| Fields | Replaces | Animation source? |
|---|---|---|
| EncounterId; participant actor/definition bindings, player target binding; spawn/home transforms; arena bounds/nav/landing constraints; trigger radius/predicate | IsPackBoss and first-boss iteration; Encounter.h:28; FogGate actor search | No. Level instance binds placed actors to stable participant slots; second instance must not resolve first boss |
| Reset/death/victory policy, generation lifecycle, startup readiness; gate actor binding/collision policy; persistence | Encounter.h:36/104; Hud.bLockPlayerOnVictory; FogGate | No. Runtime owns reset; persistence semantics must be explicit |
| Look {driver/followers/pieces, leader-pose binding, mesh scale, socket attachments, hidden component roles, material parameter mapping} | BossLook.cpp:17-23/93/131 | Asset skeleton/attachments validated; no Boss01 strings in runtime |
| Phase presentation entries {music track, volume, start offset, crossfade, phase subtitle/cues}; death/remains FX | Subsystem.cpp:150/156, BossMusic.h, Remains | Phase animation events can trigger cues; references/scales data |
| HUD {widget/style ref, localized boss/phase text, prompts, banners, retry delays, flash/trail}; footsteps/surface map; camera/shake profile | BossHud.h:142-172/cpp layout; footstep set; Legend | No. Shared widget construction remains generic and data-bound |

## Timing authority and smallest marker set

Current pack notifies in E-002-10 already carry collision/rotation/followup/end information. Their payload semantics must be read from graphs, not assumed from AG's proposed catalog. Pack assets stay unchanged. Compile/read animation metadata at authoring/load validation into an immutable TimelineSpec mapped to animation version/sections/segments; evaluate crossed intervals and events in runtime with actual previous/current position and playback instance, not only poll IsActive. The compiled artifact is a cache of animation data, never a second hand-maintained gameplay timeline.

Propose **one generic project-owned AN_CombatEvent marker** with EventKind and stable EventId payload: Commit, EffectRelease/Impact, BranchGate (when existing pack notify cannot be safely adapted), RecoveryEnd. Telegraph and hyperarmor/iframe intervals can use **one generic ANS_CombatWindow** with WindowKind and WindowId if existing states do not expose them. Thus two reusable notify types cover missing semantics; do not create a class per move or insist all moves carry eight new notifies. Existing collision/rotation/end/followup states can be adapted into the normalized timeline where their semantics match. For project-owned montages future content may add these markers; immutable pack montages use project-owned wrappers/copies or explicit compatibility manifests pending owner gate, never save pack assets.

Commitment restricts targeting/cancellation according to priority, not permanent rotation or invulnerability. Death/reset/stance break and queued phase rules must still terminate. RecoveryEnd denotes legal selection only after active windows/cues/safety gates and default recovery requirements; pack EndAnimatingAbility can otherwise select early. Missing End/Commit/Release never creates damage: compiler rejects malformed required markers; runtime aborts by watchdog and cleans all tokens. Effect release crossed in one large tick fires once only if action remained legal; an aborted action never catches up damage afterward. Reverse playback, seeks, loops and section jumps carry explicit traversal events and loop/gate IDs; no naive previous<marker<=current for every transition. Endpoints ordered deterministically (close active, resolve outcome, branch/recovery gate) with a documented boundary rule.

A2 hold: stable authored hold remains approved intent; variable delay is an owner N/A decision candidate. If used, duration is chosen before commitment, bounded min/max and watchdog, then exits at a validated seam. No indefinite AI jump-to-Slam hold. A2 stable apex need not share a universal4Hz tremor for every future boss.

## Pack integration feasibility gate

Existing pack BT/abilities/montages remain the execution backbone. The native observer cannot meet identity-before-play or legal-request-before-start by observing playback afterward. The migration must install a **shared project-owned request adapter** once, so every natural pack task and native reaction obtains an accepted action token before ability playback. Generic selector data must drive bands/weights/phase/history rather than leave fixed BT250/800/1000 bands in control while claiming they are data.

Two feasible bindings need Claude evidence: (a) project-owned generic BT task/selector reads definitions, requests shared runtime then invokes existing pack abilities; (b) an existing supported pack preactivation hook supports veto/token/configuration without editing pack graphs. Either is a one-time shared framework change after approval. Do not grant both adapter and unmodified autonomous pack BT independent selection authority. Pack-owned death/hitstun states remain routed through shared lifecycle arbitration. If no hook/configuration API exists, document project-owned adapter/wrapper scope in the gate; moving rows alone does not pass.

Before implementation, export/configure/readback evidence must establish per-instance montage/attack-data/ability-set replacement and phase gate behavior without changing pack assets, including duplicate FarRare tags and returned ability order. Data-only new boss cannot depend on newly authored bespoke ability Blueprint code. A generic projectile actor/class is shared once; each projectile mesh/shape/damage/flight is a profile. Existing per-move components can remain diagnostic compatibility facades temporarily, with production side effects disabled under the new runtime. Exactly one path may damage/move/unlock at each migration boundary.

## Migration order, regression and rollback

C-91 arrived while D02 was being drafted and settles delivery order: P0 closes, owner approves the architecture gate, behavior-identical DD-1 foundation precedes P1-P7, then P8 proves the canary and all83 final dispositions. In the table below, steps1-3 are the behavior-identical foundation; steps4-6 describe dependency order for later approved P1-P7 correctness/features, not permission to put behavior fixes in DD-1. Data adapter scaffolding may be built in DD-1 only if observable behavior remains identical. Step7 is P8. If request-adapter replacement is needed in foundation, preserve legacy selection/eligibility/timing semantics first and prove parity before activating corrected policies. The full schema can be specified now without implementing every feature during foundation.

All steps are proposed for the owner's architecture gate. No step starts in P0. Before each step pin current code + project asset manifest/source hashes, preserve the user's dirty work, record engine config and baseline. Rollback means switching the encounter's versioned binding/profile back to the preceding complete path and restoring only the change-owned recoverable artifacts; never reset/clean the user's tree or overwrite referenced assets. Never live-switch during an active action/PIE; reset/restart first.

| Step | Change after approval | Driver compatibility and required proof | Rollback boundary |
|---|---|---|---|
| 0 baseline/validation | Read actual current serialized values/variants; pin Boss01 gold definition, schema version/cook closure and complete active inventory | Claude's current registered automation/RunDrivers table, targeted known flakes/config labels; archive unmodified source + result manifests. Historic pass totals alone insufficient | Docs/data draft only; keep existing runtime |
| 1 weapon/build/catalog | Add authored catalog/Weapon/Build assets and registry reader behind legacy facade; no value/behavior changes | existing builds/build HUD/hyperarmor/stamina/bleed/loadout/selector/flask checks; old aliases and style lookups preserved. New fourth entry via data, no test weakening | profile chooses legacy table/three-build adapter; assets remain referenced/recoverable |
| 2 boss/encounter/presentation hydration | Populate current components from immutable definition before registration; explicit participant binding; keep old runtime state algorithms | encounter/wake both configurations, phase/reset, look/death/music/HUD, cook coverage; no fallback to Boss01 for unknown boss | encounter chooses whole legacy component bundle; no mixed partially hydrated state |
| 3 timeline parity/shadow | Compile animation variant timelines and run side-effect-free comparison against current tracker | close/A2/A4/A5/leap/clip drivers with actual rates/notifies; mismatch report is a finding, not an auto-tune. Assertions keep current agreed behavior | shadow off, original tracker authoritative |
| 4 shared request/identity/arbitration | Generic data selector/request adapter gates all pack/native starts; lifecycle tokens before play; public diagnostics retain compatible names/outputs | attack rules, transitions/interrupts, reset/riposte, natural move inventory, same-name restart, failed play, empty pool/cooldown. Update/add assertions only for owner-approved corrected behavior | select entire legacy request path at encounter initialization, no dual selectors |
| 5 reusable effects/resolver | Move planar/projectile/wave/weapon queries to shared capability/resolver with data params | trace/damage/iframe/A4/A5/wave/jump/block/guard/walls plus bounded hitches/multiple windows/central priority/generation. Maintain diagnostic facades for existing driver calls | effect-family path switched only between encounters; previous complete resolver/query ownership restored |
| 6 phases/lifecycle/followups/recovery | Generic phase array/stagger/riposte/cleanup/presentation; data edges/history/recovery | phase reset once-only, victory/death, paired abort/geometry/input cleanup, legal branch/default recovery, next-action/punish tests; approved source of truth for each route | restore complete prior lifecycle adapter, including modifier reversal; no mid-phase rollback |
| 7 canary + package gate | Add content-only second boss/new weapon/fourth build; data-driven parameterized test adapter; retire legacy hardcoded production defaults only after parity | full registered Boss01 gate unchanged in invocation; same meaningful scenario suite parameterized by definition for canary; cook/shipping debug-off cues/soak/perf and owner feel acceptance | retain LegacyCompatibility for diagnostics until owner accepts; rollback catalog bindings/version as a unit |

“Every driver valid” means its public hooks/legacy IDs continue to resolve and assertions retain meaning through each step. Existing hard-coded geometry/health tests may be Boss01-specific; keep them running on Boss01 and use a shared parameterized harness for the canary. Do not pretend a canary with different damage should pass Boss01's literal20/48 assertions. Required correctness fixes change expected behavior only after explicit scope approval and documented test update. A step with known blocking regression is not ready for the next step.

## Second-boss, weapon and build canary

Pin a single already-approved shared runtime build. Then the author changes only new project data/animation/visual assets and a level's encounter binding (content data), using existing pack pawn/abilities and shared executor types; no cpp/h, new component/ability/task class, Blueprint combat logic, script code, or pack asset change. Preexisting test runner supports any definition and emits definitions/version/hashes.

Minimal content:
- BossCanary uses a different registered BossId and look/name/music binding; no string containing Boss01 required for resolution. Reusing a compatible skeleton is sufficient, so new retargeting technology is not smuggled into the test.
- At least three differently parameterized moves exercise weapon sweep with two windows or explicit followup, projectile release, and radial/planar effect; at least one branch with success/failure/default recovery. Declare natural eligibility rather than forcing all starts.
- Two distinct HP-threshold phases differing from Boss01 threshold/modifiers (values are canary-only test data proposed to owner), with a transition and changed move eligibility. Dormant/wake/reset/posture break/riposte/death/cleanup/presentation configured entirely by data.
- NewWeaponId uses an existing supported pack weapon actor/ability capability with new art/action table values and a distinct action/lookup binding. If the requirement demands a novel skeleton/animation style, treat that as additional content validation, not necessary to prove registry extensibility.
- Fourth BuildId points to NewWeaponId with new display/icon/UI order and optional stat-profile reference. It appears, equips, defers during fight, resets and displays actual equipment without adding a fourth switch/row in code.

Pass record:
1. Version control/diff/content manifest proves the shared runtime code and pack assets unchanged between pinned build and content canary.
2. Definitions validate: IDs/refs/skeleton/socket/sections/timeline/cook reachability, no constructor/missing-data fallback, no Boss01 constant leakage. Reject malformed missing marker/socket/followup target before activation with actionable field path.
3. Natural samples record eligibility/attempts/starts and phase gating for all configured moves; forced diagnostic starts separately exercise boundaries and aborts. Counts are not arbitrary success percentages.
4. Same shared tests verify identity-before-play, exactly-once effect/branch, failure rollback, interrupt priority, one motion owner, source-attributed damage/defenses, hitches/crossings, visible query alignment, recovery before next damage, phase modifier once/reset, player respawn, death/victory/gate/cleanup.
5. Run Boss01 then Canary then Boss01 again, plus two canary instances in diagnostic context, to expose static MoveId/global cvar/hitset/first-actor leakage. Concurrent fights are a diagnostic isolation requirement, not multiplayer scope.
6. NewWeapon/NewBuild equip and attack costs/HP/posture/status/armor reflect their own data; original three builds remain unchanged.
7. Packaged cold load includes all soft dependencies; debug-off telegraphs/contact visible and matched; no missing-path log fallback; accepted hardware performance and existing regression/soak gate remain applicable. Captures, hashes and raw results retained; owner feels/accepts design.
8. All 83 IDs have IMPLEMENTED evidence or explicitly owner-confirmed N/A per D03. Passing one canary cannot substitute for per-ID proof or owner approval.

## A-44 authoring-contract review needed for the gate

AUTHORING_CONTRACT.md is a proposal, not binding: its section1 calls itself definitive/binding and section9 guarantees integration before the runtime exists. Correct that status. Sections4.1/5/6/7 introduce unapproved behavior: permanent uncancelable commitment; poise-break immunity from hyperarmor; tip-socket snap and default20cm radius; universal zero root motion/dedicated bone rule; indefinite hold; and section8 suggests modifying pack montages/releasing A5 at .40. These conflict with current evidence limits, priority rules or pack-edit prohibition. Retain geometry validation, explicit motion ownership, bounded hold, existing50cm trace radius and current .45 A5 release until approved evidence-backed scope.

The JSON validator checks hashes/bytes/fps/duration/root assumptions/frame-offset string, not notify coverage, runtime refs, curve/shape/defense/followup graph, missing root provenance, timing order or canary integration. 17/17 is a limited source-sheet check; the17 clips also omit A1b/A6 and the three pack moves as full MoveDefinitions. Its missing-bound default0 may pass absent kinematic evidence. Accept those JSON files as provenance/author-intent input, not engine-ready combat assets. Machine schema should separate declared intent, measured extraction, exported engine timeline and approved runtime definition; conflicts become validation diagnostics for review.

Decisions for Claude's owner gate: N/A list in D03; shared request-adapter approach after graph proof; exact approved future damage/defense/motion contract; scope of animation-notify authoring/project wrappers; staged regression and rollback criteria. No need to ask the owner piecemeal before those concrete choices are assembled.

