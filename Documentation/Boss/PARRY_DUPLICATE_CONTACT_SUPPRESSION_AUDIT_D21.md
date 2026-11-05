# Parry duplicate-contact suppression audit (Queue D D21, 2026-11-03)

## Runtime path

`URPGDamageResolver::KeyOf` identifies a swing contact by `MoveId|AttackInstance|HitKey`; `SyncGeneration` clears `Spent` and overlap coalescing when encounter generation changes (`RPGDamageResolver.cpp:36–78`). `Resolve` computes `bDuplicate` before invulnerability/parry checks and passes it to `RPGDamageRules::Decide`; duplicate takes precedence over `Parried` (`:141–158`, `RPGDamageResolver.h`). For the first valid parry it inserts the key into `Spent` and calls `URPGPlayerParry::NotifyParried` once (`.cpp:180–184`). A repeat with the same key is `RejectedDuplicate`, does not notify the parry component, and cannot spend/refund stamina a second time. An accepted health hit also enters `Spent` only after a successful health write (`:160–174`); rejected or failed contacts remain retryable. Distinct `HitKey` values intentionally represent authored stages that may hit again (`RPGDamageResolver.h` payload comment).

`NoteOverlap` coalesces only diagnostic overlap notes within `OverlapEpisodeGapSeconds`; it does not suppress `Resolve` calls. Each resolver outcome is recorded, so repeated contact episodes remain visible as duplicate outcomes even when the preceding overlap note is coalesced (`RPGDamageResolver.cpp:102–124,196–214`).

## Existing proof and gap

- `OneBossFight.Combat.DamageResolver.Decide` in `RPGAutomationTests.cpp:159–184` exercises the pure decision truth table, including duplicate before parry; `RPGParryTests.cpp:31–39` repeats the key parry/duplicate precedence assertions.
- `RPGBossParryFeedbackRulesTests.cpp` checks first-only feedback logic, but the helper is explicitly marked unwired in `RPGBossParryFeedbackRules.h`; it does not exercise the resolver or suppress duplicate resource effects.
- No inspected test constructs a stateful resolver/target and submits the same payload twice while parrying. The pure tests do not prove the `Spent` mutation, exact health invariance, one `NotifyParried`, one stamina refund, or generation-reset clearing as an integration contract. No pack boss's own hit-branch test is present; see D16/KI-153.

## Bounded fixture follow-up

Using a transient world with a player parry component and resolver owner, submit one valid parried payload twice with identical move/instance/key/generation. Assert first outcome `Parried`, second `RejectedDuplicate`, health unchanged across both, one parry notification/refund at most, one entry per `Resolve` outcome, and any overlap notes only according to the configured episode gap. Then change only `HitKey` to prove an authored distinct stage remains eligible, advance generation to prove spent-key state resets, and submit an old-generation payload to prove stale rejection does not notify or mutate health/resource. Setup/attribute-read failures must fail the fixture, not become a pass. This is a proposed test only; do not claim it ran.

## Verification boundary

Static source and test inventory review only. No test/build/Editor run or code change.
