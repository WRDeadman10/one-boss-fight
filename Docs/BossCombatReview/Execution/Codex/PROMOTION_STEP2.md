# Step2 promotion set: binding scaffold

2026-10-26, X-T6. **HOLD for product promotion.** `PROMOTION_STEP2_SCAFFOLD.patch` is a concrete one-pass patch for the existing staged core + standalone tests, NOT a complete Boss01 data hydration implementation. Never apply it merely because git apply --check succeeds. Owner step1 acceptance and exact promotion scope are prerequisites. No live files changed by Codex.

## Exact files and seam status

Patch adds Player/RPGEncounterBinding.h/.cpp and Tests/RPGEncounterBindingTests.cpp under Source/OneBossFight. No Config, module rules, pack assets, map, live attachment code or runtime behavior path replaced. Existing Build.cs already lists AIModule/Json/UMG/Slate; new reflection classes require UHT + complete restart build, not Live Coding.

| Live seam | Required integration | Present in patch? |
|---|---|---|
| Player/RPGPlayerMovesSubsystem.cpp:195-282 | One explicit encounter batch before old NewObject/RegisterComponent calls; suppress entire old boss bundle only after validated new batch; no partial fallback | NO. Existing attachment occurs late relative to draft pre-BeginPlay rule. Requires reviewed startup coordinator, not Binding actor BeginPlay (ordering unspecified). |
| Encounter + phases + stagger + dormant + posture + bleed + effects + death/look/music/HUD | Typed config records and ConfigureBeforeRegistration adapters for every actual content field/private constructor read | NO. Core accepts native callback plans but does not implement these adapters. WP13 unresolved records must first distinguish content from state/invariant. |
| Actor lookup/target consumers | Replace IsPackBoss/first iterator/player0 assumptions with associated context target, retaining legacy test facades | NO. ResolveTarget/ResolveEncounter API exists; consumers not rewired. |
| Reset / respawn / travel | Existing reset owner supplies generation once, deferred spawn transaction before BeginPlay, unbind/restore on teardown | PARTIAL API only. Existing non-deferred respawn path is intentionally rejected by core; cannot silently retrofit it. |
| Definition + binding authoring | New project definition with full hashes/typed closure; placed participant refs and distinct encounter ids | NO fixture/assets. Owner/Claude content scope required; do not edit referenced map or pack as a shortcut. |

This is a material incomplete implementation, not merely an editor test blocker. Claude should NOT apply this expecting complete step2 parity. Complete the seams in staged code and review first. A generic reflection ImportText loop over WP13 is explicitly forbidden.

## Apply / verify procedure (Claude only, after approval)

1. Snapshot exact current touched files and SHA256/dirty state to a NEW versioned preimage directory. Patch adds3 files; ensure none exists or overlaps other work. Source pins and staged hashes are in WP6Support/promotion_pins.json.
2. From project root: `git apply --check Docs/BossCombatReview/Execution/Codex/PROMOTION_STEP2_SCAFFOLD.patch`. Only after explicit approval: `git apply` the same exact file. No blanket copy of Drafts/ and no reset/checkout/clean.
3. Close editor; `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. Record actual discovered automation names/count; do not assume41+N from files alone.
4. Standalone Binding.DraftWorldIsolation is a synthetic unit proof. It is NOT real GI travel, skeleton animation, player respawn or two actual duels. Keep it out of product-complete claims.
5. After full adapters/fixtures are separately completed: run explicit two-encounter character fixture with actual meshes/animations, wrong skeleton, duplicate slots/ids, missing required config, wrong epoch/world, invalid/destroyed target, callback failure/reentrancy/GC, generation rollback, travel/respawn, no-first-actor fallback. Compare before/after effective fields from WP13.
6. Existing full `Scripts/RunDrivers.ps1` invocation and presets unchanged; run WakeClip0 AND enabled authored wake, phases/riposte/death/look/music/HUD/reset/cook. Do not add draft fixture-dependent drivers to the arena gate until a real fixture exists.

## Compile/design risk table

| Risk | Required check |
|---|---|
| UHT generated includes / forward-declared strong object leases | Full UHT/compiler pass on UE5.5.4, including noneditor target |
| Automatic world subsystem creation without bindings | Empty records must not attach/activate or suppress old path |
| Arbitrary plan callback behavior / registration side effects | Native-only adapter allowlist; validate whole batch first; reject registered/late components |
| Actor destruction during callbacks | IsValid checks before and after callbacks, no dereference after owner invalidation; partial pre-register rollback test |
| Registration fails after callbacks start | Poison context, prevent gameplay; not a claimed undo transaction |
| Immutable content versus mutable world state | No shared HP/cooldown/target mirrors in assets; generation-qualified identities |

Rollback only newly added unreferenced scaffold or precisely reverse approved owned hunks after reviewing intervening edits. No restoration of an entire shared preimage over newer work. NOT BUILT / NOT RUN by Codex.
