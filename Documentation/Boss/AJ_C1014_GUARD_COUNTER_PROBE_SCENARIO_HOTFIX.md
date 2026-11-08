# C-1014 — guard-counter probe scenario hotfix

## Lead finding

C-1014 reports BUILD-252 GREEN (484/484), but the two-route PIE at 220 cm did not exercise the hook: the only observed boss montage was `AnimMontage_2`, setup HP was 500 on each route, and the run ended with no `Status.Blocking` or `BlockReaction_C` sample. Claude's order is to restore the 900 cm setup that lets the boss approach, normalize boss HP at probe setup, and log HP, montage, and player state every 0.5 s.

The retained run-3 data and legacy excerpts confirm their setup distance was 900 cm, but they start at 500 HP and show only `AnimMontage_2`; neither contains a blocked-contact witness. A separate retained run-4 data-route excerpt does contain the contact described by the Lead: it starts at 900 cm / 2000 boss HP, shows `GA_PlayerGuardBlock_C active=1` and `Status.Blocking=1` from guard elapsed 0.55 s, and at 2.60 s shows `GA_Sword_BlockReaction_C active=1` with `Status.Blocking` and `Status.ActionCommitted`. The setup log says `framework_executor_present=False`, so this confirms the ability/tag state but does not establish the framework-executor notifier or counter-arm log. After elapsed 4.65 s, the player dies; subsequent logs show negative player HP and respawn, after which the blocking tag is gone. The retained 220 cm run instead starts with 500 boss HP, shows only `AnimMontage_2`, and never acquires `Status.Blocking`. These observations support keeping the 900 cm approach and normalizing HP, but do not isolate teleport/facing as the cause of the different AI behavior.

## Probe change

`Scripts/Editor/pie_er_guard_counter.py` now:

- positions the player 900 cm from the boss, facing it, and leaves the boss AI unheld so it can approach;
- reads `Attribute.Health` and its max, restores current HP to max if needed, and verifies the value by readback before continuing;
- preserves the 25 s guard window and per-tick pack `IA_Block` injection;
- logs boss current/max HP, active montage, player-to-boss distance, and the existing full player ability/tag snapshot every 0.5 s during guard.

The HP write normalizes only the health attribute; it is not asserted to reset encounter phase, AI state, perception, or other encounter state. Per-sample logs should make those differences easier for Lead to diagnose.

## Validation and handoff

Python AST parsing and scoped `git diff --check` pass. Codex did not run Unreal, PIE, native tests, or a build. Lead owns the two-route rerun. Acceptance remains a source-confirmed guarded contact followed by the configured R2 counter result, attack kind/data, and boss HP delta; KI-198 stays open until those runtime results exist.
