# Queue BE Batch 1 — framework health and encounter lifecycle

**Scope:** source mapping and acceptance boundary for native framework health, pack HUD/encounter assumptions, proof versus production ownership, and generation guards. The initial mapping below was read-only; implementation is now in progress under X-1855 and has not yet had a native build/full-suite run.

## BE-X01 — health mutation and death transition

`ARPGFrameworkBossCharacter` implements `IRPGNativeBossHealth`; `ReadNativeHealth` only answers while `bHittable` and returns its private `Health`/`MaxHealth` fields (`Boss/RPGFrameworkBossCharacter.h:17,71–72`). Player attacks reach `ApplyHit`, which validates initialized/hittable/nonterminal state, subtracts from the native field, logs before/after values, and calls `Die()` on depletion (`Boss/RPGFrameworkBossCharacter.cpp:751–777`). Channel healing is also capped against `MaxHealth` and returns applied delta (`:757–764`). These are a native provider/mutator path; they do not write the pack `Attribute.Health` value.

`Die()` is locally idempotent, stops owned movement, disables character movement, aborts the executor and emits proof result logs (`Boss/RPGFrameworkBossCharacter.cpp:1008–1017`). The function does not broadcast an encounter-level death event in the inspected body.

## BE-X02 — HUD binding assumptions

The regular attachment path creates `URPGBossHud` only when `IsPackBoss(Pawn)` is true (`Player/RPGPlayerMovesSubsystem.cpp:888–892`). The HUD polls pack `Attribute.Health` current/max values and uses them to determine alive/dead, victory, health bar fraction, and banner behavior (`UI/RPGBossHud.cpp:415–452,469–472`). It also derives generation and retry reset behavior from `URPGBossEncounter` (`:390–413`). A framework boss exposing `IRPGNativeBossHealth` does not, by that interface alone, satisfy these pack component/attribute assumptions.

**Integration seam to decide:** one encounter-owned provider/binding should supply health, max health, generation and terminal state to presentation, while preserving a pack adapter for existing bosses. This is a design proposal; no HUD integration exists by this source review.

## BE-X03 — encounter completion and retry ownership

The framework death path aborts its own executor and prints `[FrameworkProof] RESULT outcome=BossDefeated` (`Boss/RPGFrameworkBossCharacter.cpp:1015–1017`). By contrast, the existing HUD victory path detects pack health <= 0 after observing the boss alive, latches once per participant generation, can lock player input, enables retry, and broadcasts `OnVictory` (`UI/RPGBossHud.cpp:415–453`). `URPGBossEncounter` and the selection subsystem own pack participant generation/reset/binding state; selection currently counts a pack boss and possessed player (`Player/RPGEncounterSelectionSubsystem.cpp:185–204`). No inspected edge forwards framework `Die()` into that pack encounter/HUD event chain.

Unassigned integration decisions: encounter owner and completion signal; music/victory presentation owner; player lock and retry/reset authority; cleanup/replacement policy. This mapping cannot establish whether unrelated Blueprint/map scripts supply a separate path.

## BE-X04 — reset/generation guards and route boundary

The proof bridge initializes a framework character through `InitializeProofInternal` with explicit fixture/profile/target/encounter/generation (`Boss/RPGFrameworkBossCharacter.cpp:62–73,90+`). Restart requires a terminal success/death and a strictly newer generation (`Boss/RPGFrameworkBossCharacter.h:78–80`); the restart body validates target state, rearms the executor, updates generation, restores actor-owned health/state, relocates and asks its controller to walk (`Boss/RPGFrameworkBossCharacter.cpp:988–1006`). The proof fixture checks `CanRestart` before rewriting target health (`Boss/RPGFrameworkProofFixture.cpp:99–107`).

Production selection follows a separate binding route: it validates game-world/subsystem ownership and generation, resolves selected definitions, and requires exactly one pack boss and one possessed local player (`Player/RPGEncounterSelectionSubsystem.cpp:161–204`). These checks show proof-local restart safety and pack binding preconditions; they do not establish framework actor spawn, production retry ownership, player restoration, HUD rebinding, actor replacement, or generation coordination across those systems.

## BE-X05 — Lead acceptance matrix

| Acceptance case | Required observation |
|---|---|
| Same-generation health binding | HUD displays framework native current/max health from the active encounter generation |
| Terminal event idempotence | One death event produces one completion/victory signal and one presentation transition |
| Reset/retry ownership | Explicit authority advances generation once, restores the chosen participants, and disables stale retry callbacks |
| Actor replacement | Old actor/HUD/executor/callbacks are detached before the replacement binding becomes current |
| Pack regression | Existing pack health, HUD, victory, retry, and reset route remains intact |
| Teardown/failure | Missing provider, failed spawn, or destroyed participant fails closed and releases owned resources |

Lead should choose the owner/event contract and capture live evidence for both existing pack and framework route. This table does not authorize implementation or claim acceptance.

## Implementation checkpoint (not READY)

- `IRPGNativeBossHealth` now exposes a generation-tagged native terminal delegate and phase-two query in addition to current/max health and active state.
- `ARPGFrameworkBossCharacter::Die()` broadcasts the current generation after its existing idempotence guard. `URPGBossHud` binds/unbinds that delegate with component lifetime and refuses stale, duplicate, invalid-health, or nonterminal events before its existing once-per-generation victory path.
- The selected native participant gets `URPGBossHud` and `URPGBossMusic`; the pack legacy attachment branch is unchanged. Native music reads native health/active/phase state and retains the shared retry widget's existing level-reload authority.
- `RPGNativeBossHealthTests.cpp` now covers finite/max-health validity, victory guards, and current/duplicate/stale/future completion generations. C++ automation tests have not yet run.
- `test_check_shipping_guards.py`: 4/4 PASS; targeted `git diff --check` has no whitespace errors. These checks do not substitute for UHT, C++ compilation, or the full suite.
- C-1155 run `Docs/BossCombatReview/Execution/Codex/BE_X01_X05_FRAMEWORK_INTEGRATION/Run_20261110_171659/`: Development build 0; pinned suite 507/507, 0 failed, complete; DD27j hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`; no assets; both locks released. `OneBossFight.BossHealth.PresentationSnapshot` completed successfully.

## Verification and limits

- Native build/full-suite passed. Lead's live selected-framework-route acceptance remains pending; no asset authoring or commit/push is claimed.
- Existing prior reports identify the same HUD/death integration as open; this batch adds source integration but not runtime acceptance evidence.
- Relevant existing maps: `BD_X01_X05_FRAMEWORK_INTEGRATION_MAP.md`, `BC_X11_X15_FRAMEWORK_LIFECYCLE.md`, and `BB_X26_X30_FRAMEWORK_BINDING_AUDIT.md`.
