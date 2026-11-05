# Boundary, randomness, tick, and loading audit (Queue C S51–S55)

Read-only source audit, 2026-11-03. No project files or runtime behavior were changed; no editor or Unreal execution.

## S51 — float boundaries and current coverage

- Framework profile domains use explicit inclusive bounds for closed ranges (`< min` / `> max`) and strict-positive checks where zero is invalid. Examples: center bias `[0,1]`, center-bias start fraction `(0,1]`, selector tie band `[0,0.5]` (`Player/RPGBossFrameworkProfile.cpp:95,127`). Center-bias activation uses `FromCenter >= Threshold` (`Boss/RPGFrameworkBossController.cpp:27`), so equality is in the active band. Several adjacent numeric values are separately bounded by profile validation.
- MoveCard `WarpStandoffCm` has a generic finite/nonnegative/upper-bound check but no feature-specific upper bound or pure test for equality/greater-than standoff; see S50 report. Candidate boundary coverage gap, not demonstrated incorrect runtime behavior.
- Fireball hydration has tests for inverted cooldown order and NaN endpoints (`Tests/RPGBossHydrationPreflightTests.cpp:1170`; `Tests/RPGBossPhasesClusterAdaptersTests.cpp:424–425`). Existing tests exercise invalid cases; this audit did not establish exact equality coverage for every authored range. Do not infer full boundary coverage from general profile tests.

## S52 — non-finite provenance

- Validated framework profiles reject non-finite values before resolution (`Player/RPGBossFrameworkProfile.cpp:44–166`); MoveCard numeric validation rejects non-finite inputs (`Player/RPGBossMoveCard.cpp:17–21`). Runtime consumers reached through those resolved objects have validation provenance.
- Fireball cooldown hydration explicitly rejects non-finite endpoints and inverted ranges (`Player/RPGBossPhasesClusterAdapters.cpp`; `Tests/RPGBossHydrationPreflightTests.cpp:1170`; `Tests/RPGBossPhasesClusterAdaptersTests.cpp:424–430`); director lightning cooldown is a separate actor-authored `FVector2D` (`Boss/RPGSevarogDirector.h:84`) and is passed to `RandRange` at source callsites (`.cpp:38,389,421`). No finite/order check was found at those callsites in this scan; classify as trusted authored-data assumption, not a proven runtime failure.
- C-719 follow-up: the non-shipping `rpg.BossProofCenterBias` override now requires a finite value and `>= 0` before use (`Boss/RPGFrameworkBossController.cpp:23`). This is a one-line guard; no runtime test was run.
- C-719 follow-up: the non-shipping yaw probe now requires a finite amplitude and `> 0` before calling `YawAt` (`Boss/RPGFrameworkBossCharacter.cpp:431`). This is a one-line guard; no runtime test was run.

## S53 — randomness ownership

- Combat choices using global, unseeded randomness: director lightning cooldown (`Boss/RPGSevarogDirector.cpp:38,389,421`) and phase fireball cooldown (`Player/RPGBossPhases.cpp:345,518`). They have no local seed/reset contract in these call paths; playback is not deterministic from profile seed alone.
- Seeded gameplay choices: selector tie resolution uses `TieSeed + StartedCount` when a non-empty tie band yields multiple top candidates (`Player/RPGBossMoveSelector.cpp:78–81`); reaction delay uses seed plus count (`Player/RPGBossTrackRules.h:46–50`); cue and strafe rules use seed/index-derived `FRandomStream` (`RPGBossCueRules.h:29`, `RPGBossStrafeRules.h:44`). Selector history resets with its owner/reset path; per-event rule inputs are explicit. No claim that all combat randomness is seeded.
- Global random cosmetic sources: footsteps pitch and fire-source ambience (`Audio/RPGFootsteps.cpp:76,126`; `Arena/RPGFireSource.cpp:77,82,89`). Local seeded presentation generation: ember field owns an `FRandomStream` initialized from `Seed` (`Arena/RPGEmberField.cpp:91`); greybox scatter uses `FRandomStream(ScatterSeed)` (`Arena/RPGGreyboxArena.cpp:207`).

## S54 — tick-order dependencies

- Explicit prerequisites exist where correctness is directly stated: executor after boss mesh (`Boss/RPGFrameworkMoveExecutor.cpp:59,80`); trace guard after mesh (`Player/RPGTraceGuard.cpp:19,30`); death after stagger/posture/phases (`Player/RPGBossDeath.cpp:105–113`); close-clip swap and dormant wake after encounter (`Player/RPGBossCloseClipSwap.cpp:55`; `Player/RPGBossDormantWake.cpp:44`); phases after stagger (`Player/RPGBossPhases.cpp:76`).
- Several components rely on tick group and a comment describing relative ordering, without an explicit component prerequisite: footsteps `TG_PostPhysics` after pose (`Audio/RPGFootsteps.cpp:17`), iframe monitor `TG_PostUpdateWork` after notify dispatch (`Player/RPGIFrameMonitor.cpp:21`), trace audit after pack sample (`Player/RPGTraceAudit.cpp:30`), and legend after tracker/phases/stagger/HUD (`Player/RPGLegend.cpp:258`). Group membership alone does not establish relative order within a group. Treat as unverified ordering assumptions; runtime order test or explicit prerequisites would be needed to prove them.

## S55 — async asset loading

- Production-source search found no `RequestAsyncLoad`, `FStreamableHandle`, `LoadPrimaryAsset`, or equivalent asynchronous asset request/callback lifecycle in `Source/OneBossFight`.
- Asset resolution uses synchronous soft-reference loads, for example profile resolution (`Player/RPGBossFrameworkProfile.cpp:173–275`), plus synchronous component setup loads across phase, movement, and presentation components. There is therefore no production async handle cancellation/weak-owner/completion path to map in this scope. This establishes the current implementation pattern, not suitability for future streaming-heavy use.

## Disposition

No confirmed gameplay bug in S51–S55. Review candidates: test exact equality for all high-risk authored thresholds; reject non-finite values at non-shipping numeric CVar boundaries; establish ordering for same-group consumers currently documented only by comments. No async asset lifecycle exists in the scanned production source.
