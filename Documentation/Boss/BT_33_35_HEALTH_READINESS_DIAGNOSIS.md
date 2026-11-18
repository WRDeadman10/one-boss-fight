# BT-33 / BT-35: Sevarog player-health readiness diagnosis

Date: 2026-11-16
Route: C-1619 Sevarog arena

## Evidence reviewed

The Smoke run `Saved/SevarogArenaRoute/Run_20261116_122821_e45f89f1` ended with `FAILED`, `accepted=false`, and `runtime_acceptance_status=BLOCKED` because the arena route refused with `PlayerHealthTimeout`. Its log advanced through retries 1–100 and ended with `BossCount=0 PlayerCount=1 CompetingPackBossCount=0`. The pack boss was suppressed before BeginPlay and had no active montage. The framework boss was never spawned or bound; HUD count, Sevarog health, and production-card selection were not exercised. The runner restored config, closed Editor, released both locks, and saved no assets.

Antigravity's independent receipt review (A-1026, accepted by the lead) confirms those observations. The current retry log records `health=0`, but does not reveal whether `RPGPack::ReadAttribute` returned false or returned an actual zero.

## Supported cause and bounded correction

The project already records the pack startup lifecycle in `Documentation/KNOWN_ISSUES.md` (KI-150) and `Documentation/TEST_PLAN.md`: `BP_CombatPlayerCharacter` can initially have no combat style, with health remaining uninitialized until the default style/equipment setup completes, measured around 9–14 seconds in the documented probe. The current gate allows only 100 retries at 50 ms, approximately five seconds. This is consistent with the observed timeout before health initialization. This is a source-backed diagnosis; the exact attribute read result in the failed Smoke remains unknown.

The approved implementation scope is to extend the bounded wait to 600 retries at 50 ms (30 seconds), retain local-player possession and readable, finite, positive health as prerequisites, preserve fail-closed refusal and timer cleanup, and report unreadable health separately from readable-but-invalid health. No asset workaround is approved.

## Task sequence and current status

- BT-33 receipt audit: accepted and done.
- BT-35 lifecycle diagnosis: accepted and done.
- BT-37 implementation: complete; source reviewed by Codex.
- BT-36 source review: complete and accepted.
- BT-40 C-1155 build and pinned suite: complete, 573/573 passing.
- BT-38 Smoke: complete attempt; failed closed at retry 600.
- BT-39 independent receipt audit: Antigravity, in progress; verify reflected output-property contract and actual health evidence.
- BT-34 closeout remains open until the post-fix evidence is reviewed.

At the time this diagnosis was written, no implementation, test, build, Editor/PIE run, asset edit, commit, or push had occurred. Subsequent progress: Antigravity completed BT-37; Codex reviewed and accepted the source as BT-36. The C-1155 Development build and complete pinned suite then passed under BT-40 (build exit 0, 573/573 passed, 0 failed; both locks released; no PIE/package/assets). Exact receipt: `Saved/C1619RouteBuild/Run_20261116_124737_874f4cc7/route_lead_approval.json`.

The fresh BT-38 Smoke `Saved/SevarogArenaRoute/Run_20261116_124914_d40365e8` still refused at retry 600. Its helper telemetry logs `hp=0`, but actual player Health is not yet proven. `RPGPack::ReadAttribute` delegates to `CallBlueprintFunction`, which returns true when it invokes the reflected function; its read callback uses `ReadNumber`, which defaults to 0 if the named output property is absent or nonnumeric (`RPGBlueprintCall.h:95-116,141-149,210-230`). Config was restored, Editor closed, both locks released, and no assets were saved. Antigravity's BT-39 independent read-only audit is in progress, focused on the getter output contract, retry timing/event call sites, and any logged player style/equipment initialization.

The route is still **not accepted**. There is **no playable packaged build** from this gate. Boss-death acceptance and raw BehaviorTree attack-task tick evidence remain separate open criteria.
