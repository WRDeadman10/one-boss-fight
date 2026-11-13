# Queue BC Batch 3: X11–X15 framework lifecycle and integration map

## X11 — spawn ownership and teardown

`ARPGFrameworkBossCharacter::SpawnFrameworkBossForTest` is a transient, non-Shipping helper that validates subclass and game-world context before spawning (`RPGFrameworkBossCharacter.cpp:76–88`). The actor owns `URPGFrameworkMoveExecutor` as a default subobject (`:45–55`). `InitializeProofInternal` resolves the profile, checks the explicit same-world target, writes/validates test target health only for the authorized standalone test route, then spawns its AI controller and begins the initial band walk (`:90–158`). `EndPlay` stops owned movement, aborts the executor, stops the F11 clip, and drops profile/target/fixture references (`:1027–1030`).

The helper does not establish a production encounter owner or default map binding; the inspected use remains transient proof setup. If controller creation or the initial walk fails, `Fail` makes the actor inactive; cleanup otherwise follows PIE/world teardown or explicit actor destruction.

## X12 — possession and controller path

The actor constructor sets `AutoPossessAI=Disabled` while selecting `ARPGFrameworkBossController` as `AIControllerClass` (`RPGFrameworkBossCharacter.cpp:45–46`). Test/proof initialization explicitly calls `SpawnDefaultController` and validates the cast (`:137`). The controller's movement completion routes successful arrival to `WalkArrived` and failed movement to the boss failure path (`RPGFrameworkBossController.cpp:51–70`). I found no custom `PossessedBy`/`UnPossessed` override in this actor; teardown explicitly stops the owned walk in both death and EndPlay.

## X13 — health, death, and repeat calls

`ARPGFrameworkBossCharacter` implements `IRPGNativeBossHealth` (`RPGFrameworkBossCharacter.h:17,71–75`). `ApplyHit` owns the health subtraction and calls `Die` on depletion (`RPGFrameworkBossCharacter.cpp:771–798`). `Die` is idempotent via the `bDead` early return, stops movement and aborts the executor once (`:1008–1018`). `Fail` is separately idempotent via `bFailed` (`:1019–1025`). This is source evidence of repeated-call guards; no new runtime claim is made.

## X14 — HUD integration option

The existing `URPGBossHud` is constructed only on `IsPackBoss` actors (`RPGPlayerMovesSubsystem.cpp:888–892`). Its bar/victory path reads `Attribute.Health` through pack attribute helpers and detects death only after first seeing positive health (`RPGBossHud.cpp:407–452`). The framework interface can provide current/max native health, but does not currently expose a health-changed or death event (`RPGNativeBossHealth.h`; framework implementation `RPGFrameworkBossCharacter.h:71–75`).

Smallest reusable path: make HUD health sampling consume `IRPGNativeBossHealth` when implemented and retain the existing pack adapter otherwise; add an explicit native-death/generation signal or a clearly scoped polling contract for victory. Bind/reset retry must be tied to a real encounter generation/owner. Do not infer that the current `IRPGNativeBossHealth` interface supplies display name, encounter state, or retry policy.

## X15 — encounter completion and retry

Framework death emits `[FrameworkProof] boss_dead` and `RESULT outcome=BossDefeated`, but the audited `Die()` path does not notify `URPGBossEncounter`, HUD victory, music, or a retry controller (`RPGFrameworkBossCharacter.cpp:1008–1018`). Its explicit proof `RestartEncounter` requires a newer generation after death/success and resets actor/executor state (`:988–1006`); this method is not wired to `URPGBossHud`'s retry/reload behavior. The missing integration is therefore a real source gap for using the framework actor as a production encounter.

## Acceptance and scope

X11–X15 are static lifecycle and integration audits. No Source changes, build, tests, Unreal, PIE, HUD authoring, or encounter route changes were made. The existing X29/X30 audit remains the concise blocker record; this report adds ownership/interface detail and a minimal integration option for a future separately approved task.
