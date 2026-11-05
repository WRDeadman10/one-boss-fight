# MoveCard lifecycle: bake through abort

This guide follows one `URPGBossMoveCard` from authoring data into runtime playback. It distinguishes offline structure checks, loaded-asset resolution, and runtime execution; passing an earlier stage does not imply later stages passed.

## 1. Bake (optional, for blade-sweep samples)

The C1 authoring pipeline is `Docs/BossCombatReview/Execution/Claude/C1/new_boss.py`. For a new card with `bake: true`, it calls `Antigravity/MoveCards/bake_blade_path.py` (`new_boss.py:131-133`) before `author_move_cards.py`, then calls `verify_baked_cards.py` (`:145-157`). The baker samples the selected sequence across each requested window at 120 Hz plus window boundaries and emits `TimeSeconds`, `BaseCS`, and `TipCS`; it refuses a sequence mismatch or window extending beyond the clip (`bake_blade_path.py`). The verifier compares stored samples with evaluated pose/socket positions and uses a 2 cm default drift tolerance; it also requires samples for windows designated as baked (`verify_baked_cards.py`).

The baker is optional when windows use live sockets. Baked values are copied animation data. Re-bake after changing the animation: the MoveCard schema has no animation content hash, so the C++ structural validator cannot determine whether a previously baked path is stale. The C1 pipeline's verifier can detect sampled pose drift for the checked points, but does not attach a permanent freshness identity to the asset.

## 2. Author and validate

`author_move_cards.py` writes the `URPGBossMoveCard` assets and `new_boss.py` checks the returned status, verifies baked cards, then reloads the saved card assets before constructing its profile (`new_boss.py:131-159,162`). Do not overwrite an existing destination through this path: the C1 preflight refuses existing profile/level destinations and the authoring workflow also refuses an existing card.

`RPGBossMoveCards::Validate` is pure and never loads assets (`Source/OneBossFight/Player/RPGBossMoveCard.cpp:31-164`). It checks schema 1, identity, exactly one animation source, source/metadata identity, skeleton identity, slot/section, root motion, finite domains, timeline ordering, windows, cues, hold/warp, defense, grab/ring/secondary relationships, and baked sample structure. Failures are named `MoveCard.*` issues; this stage can consume caller-supplied metadata and is not proof that an asset was actually loaded.

For offline config data, run the C1 `new_boss.py --dry-run` path through `run_editor_script.ps1` as documented in `C1_NEW_BOSS_HOWTO.md` §3.1. `Scripts/Tools/validate_baked_cards.py` is an additional JSON-level finite/ordered sample check, not a replacement for C++ validation. The helper unit tests under `Antigravity/MoveCards/test_*.py` cover offline tool behavior. Neither metadata preview nor JSON validation proves Unreal asset identity or gameplay contacts.

## 3. Resolve real assets

`RPGFramework::ResolveProfile` first calls `ValidateProfile`, then loads the profile's mesh, animation class, target class and card dependencies at the explicit load boundary (`RPGBossFrameworkProfile.cpp:168-198`). For each card it invokes `CompileResolved` (`:192`), which is game-thread-only and checks actual animation type, animation/skeleton/mesh identities and available slots/sockets/bones before publishing an immutable compiled card with strong leases (`RPGBossMoveCard.cpp:173-207`). The profile resolver additionally enforces card range-band/blend-tail, phase-pool, combo membership, damage budget, defense cooldown/counterplay, and optional punish constraints (`RPGBossFrameworkProfile.cpp:197-264`). A metadata-only compiled preview has no resolved leases and cannot play.

## 4. Initialize and start

`URPGFrameworkMoveExecutor::Initialize` accepts only a resolved sequence-based card, a valid boss/target pair, the expected animation instance and a real slot node; it initializes the move model and playback references (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:69-89`).

`StartCard` then requires initialized, idle, non-aborted state; it revalidates the resolved card and selector snapshot, computes fatigue/fairness rate and watchdog bounds, verifies the already-loaded sequence, reserves the model instance, and starts the dynamic montage (`:120-181`). If montage play or initial observation fails after reservation, it aborts that owned instance. Successful start emits `[CARD_START]` and `FrameworkProof playback_start`; these show runtime start, not a hit/result.

## 5. Finish or abort

Natural completion is recognized after the model is idle and the owned montage stops; the executor releases any grab, unlocks owned motion, restores playback rate, marks finished and disables ticking (`RPGFrameworkMoveExecutor.cpp:199-208`). `Abort` is idempotent: it releases a held victim, aborts the model token, stops only the owned montage, disables ticking, unlocks motion and logs `[CARD_ABORT]`/cleanup (`:579-596`). `EndPlay` routes through `Abort` (`:603-604`); watchdog, lifecycle/observation failure, stance break, death, arena leash and other callers can also terminate an active card. A successful bake, validation or resolve does not guarantee execution will start or finish.

Source references: [field/default reference](REF_MOVECARD.md), new-card authoring guide (`NEW_CARD_HOWTO.md`, archived), [C1 pipeline](C1_NEW_BOSS_HOWTO.md), and [executor reference](REF_EXECUTOR.md).
