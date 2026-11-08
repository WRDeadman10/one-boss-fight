# Queue AH-C01–C04 — ER air zero-damage source audit

Date: 2026-11-07. Static source and Lead-log review only. Codex did not modify code/assets or operate Unreal, build, cook, package, PIE, or benchmarks.

## AH-C01 — notify-to-hit intake boundary

The authoring scripts set the CollisionTrace notify state and timing (`Scripts/Editor/reauthor_c992_montages.py:72–97,156–160`), but the pack's `ANS_CollisionTrace` Blueprint executes the weapon trace. Codex source has no C++ implementation of that notify. `URPGHitIntake::TryBind` binds the player's pack `BP_CollisionComponent_C.OnHit(FHitResult)` (`Source/OneBossFight/Player/RPGHitIntake.cpp:307–339`); `HandlePackHit`/`FinalizePending` record/process only hits that arrive (`:470–499,528–551`). Thus a no-hit run cannot distinguish a notify that never opened from a trace that opened but missed/was filtered. A log of active trace target/tag/socket endpoints is needed.

Lead's current driver logs the montage and the player's `hand_r` distance to the boss actor, but not collision enabled state, collision sockets, trace endpoints, or hit candidates (`pie_er_air_hits.py:230–237`). During AirLight's authored notify window, hand-to-boss distance is roughly 242–261 cm in the latest legacy sample (`probe_legacy.log:1651–1663`); AirHeavy's window shows roughly 242–246 cm (`:1727–1735`). This is a plausible range/position confound, not proof of the cause, because the actual weapon trace endpoints and boss hit volume are not logged.

The setup line is internally inconsistent: the driver places the pawn at boss X + 160 cm (`pie_er_air_hits.py:150`) but logs `player_distance_cm=900` (`:157`). The recorded 900 cm is false for that setter; logs should use the actual measured transform distance. Ground controls still deal damage, but that does not establish the air montage's trace overlapped the target.

## AH-C02 — attack-data path

The successful-hit path reads the active trace target's `HitData.AttackData` one frame after `OnHit`, then falls back to target `Attack Data` (`RPGHitIntake.cpp:528–551`). It does not inject an attack or prove what an ability assigns before a collision. This is consistent with C-994's statement that ability supplies attack data when the notify override is unset, but the ability-side assignment is in pack Blueprint and is not verified by this C++ path. With 0-damage attacks and no `OnHit`, no `RPGHitIntake` record exists to establish attack-data attribution.

The re-author script sets `AttackData` to `None` inside a broad try/except that suppresses errors (`reauthor_c992_montages.py:156–160`); saved-text exports/readback are therefore necessary. Current GuardCounter/AirLight exports provide that check, but no full AirHeavy export exists.

## AH-C03 — StoredInputTags warning

The exact `StoredInputTags` identifier has no match in source or scripts; the log identifies the Blueprint caller as `BP_InputBufferComponent_C`, so Codex cannot trace its Blueprint graph here. The warning occurs in the same hit test around successful ground controls as well as ER air attempts (`probe_data.log` and `probe_legacy.log`), so it is not unique to the zero-damage cases and does not establish causation. Preserve as an observation; don't treat it as the diagnosed defect.

## AH-C04 — Lead discriminator matrix

1. Fix the setup-distance log and record the actual pawn, boss, and weapon socket coordinates at attack time.
2. Run identical air attacks at a close, known-overlap distance and at the existing x+160 cm setup, with matched R1/R2 controls on each route.
3. For each notify window, record montage position, trace target active state, collision tag, configured socket names, start/end socket positions, and candidate actor/hit-set changes.
4. If `OnHit` fires, capture the FHitResult and the active target's `HitData.AttackData`/fallback value on finalize. If no event fires, classify the first missing stage (notify, active target, socket sweep/overlap, or target filter) rather than inferring an AttackData fault.

This matrix is a review suggestion only. It does not change the Lead-owned driver or authorize another Editor run by Codex.
