# Queue AC AC-C11–AC-C15 — guard, parry, and counter evidence

Mailbox reviewed through C-980. Read-only source, test, and existing-probe audit; no test, Editor, build, or PIE run by Codex.

## AC-C11 — owner report and old probe classification

Owner C-953 confirms L1 guard works in ordinary play and says prior block probes were invalid. `AA_C06_BLOCK_PROBE_CLASSIFICATION.md` identifies concrete reasons: probe 1 and 2 began with zero stamina and zero/negative health; probe 3's weapon-state claim was not corroborated by a player montage and later referenced the boss montage. The old probes therefore do not contradict the owner report and do not establish an input/gameplay defect. A valid new run still needs positive player health/stamina, player-side equip evidence, and observed guard-state tags at boss contact.

## AC-C12 — guarded-contact to counter path

1. The boss executor samples `Status.Blocking` immediately before resolving hit damage. It classifies the resolver result separately from parry (`RPGFrameworkMoveExecutor.cpp:280-295`).
2. Only an accepted hit classified `Guarded` increments guarded-hit counts and calls `URPGDodgeTiming::NotifySuccessfulGuardContact`. The source contains this call in both the direct-window and grab-damage paths (`RPGFrameworkMoveExecutor.cpp:293`, `:415`). A `Parried` outcome has its own branch and does not arm the counter.
3. `NotifySuccessfulGuardContact` records world time (`RPGDodgeTiming.cpp:523-526`). On an R2 tap, `RPGGuardCounterRules::IsCounterPress` gates a counter and consumes the timestamp before attempting the optional montage (`:489-507`).
4. An accepted counter uses the optional `GuardCounterMontage` array override if it loads and applies; otherwise the callback still replays the pack strong action and logs fallback (`:497-521`). The `GuardCounterWindowSeconds` default is 0.60 s and is explicitly documented as a proposal (`RPGDodgeTiming.h:117-121`), not an owner-approved final timing.

Static boundary: the two guard-contact calls are in `RPGFrameworkMoveExecutor`; this audit does not prove every legacy/pack damage path reaches them. Lead's receipt must identify the route and source of the accepted guarded contact.

## AC-C13 — canonical QA wording

- **Guard input:** hold L1 / `Gamepad_LeftShoulder`.
- **Guarding/blocking state:** player state while the guard ability is active; a mapping dump or held-key log alone is not proof.
- **Successful guarded contact:** an actual boss hit occurs while `Status.Blocking` is observed and the resolver accepts it as `Guarded`.
- **Parry:** distinct timing result (`Parried`), not a synonym for block; it does not arm the guard counter path above.
- **Guard counter:** one R2 tap after a successful guarded contact inside the configured window; when the optional montage is empty or unavailable, the pack strong attack is the documented fallback.

The hand sheet already asks for positive health/stamina, an incoming front-facing hit, successful block contact, then prompt R2. Prior probes are classified invalid in `AA_C06_BLOCK_PROBE_CLASSIFICATION.md`; do not describe them as proof that guard is broken.

## AC-C14 — optional counter montage fallback

Source fallback is explicit: the counter timestamp is consumed once; optional montage load/application is attempted only when the soft field is non-null; then the standard R2 strong action is replayed. The trace log distinguishes `montageApplied=1 fallback=none` from `montageApplied=0 fallback=pack strong attack` (`RPGDodgeTiming.cpp:489-521`). The existing source-contract fixture checks the field, eligibility call, and array restore references; it does not simulate a failed soft load or execute the ability. No runtime fallback behavior is claimed by Codex.

## AC-C15 — Lead counter receipt checklist

| Evidence | Required observation |
|---|---|
| Identity | Build ID, raw log path, level, route (legacy/data), player pawn/controller IDs |
| Valid setup | Positive player health and stamina; player weapon/equip evidence on the player mesh; boss held in stable attack setup |
| Guard input | L1 held; capture input action/ability activation if available and `Status.Blocking`/`State.Blocking` immediately around contact |
| Contact | One actual incoming boss hit; retain `[FrameworkProof] guard_state` and hit result showing `guard=Guarded outcome=Accepted`; distinguish `Parried` and `None` |
| Counter | R2 tap after that contact; log contact/press timestamps and whether source-configured window admitted it. The current 0.60 s is a proposal, not an approved requirement |
| Result | `guard counter accepted` line with montageApplied/fallback; observed player montage name; boss hit/hit-group and damage result |
| Controls | Include empty/unloadable optional montage fallback case only when the Lead can safely produce it; compare pack strong fallback to assigned montage in an approved test build |

No Source or asset change is proposed by this audit. Owner video approval/optional montage assignment remain separate gates.
