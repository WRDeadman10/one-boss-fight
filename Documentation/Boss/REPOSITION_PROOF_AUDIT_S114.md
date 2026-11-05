# S114 — reposition proof/profile audit

## Profile values and source path

`Docs/BossCombatReview/Execution/Claude/B_MOV/create_reposition_content.py:23–24,76–83,102–106,157` authors a new MOV map/profile with band `[110,140]` cm, boss spawn X=500 cm, walk speed 180 cm/s, acceptance 5 cm, timeout 10 s, and `reposition_max=3`; it sets turn rate to 180 deg/s. The later `set_turn_rate.py:3–9` reads the same profile, verifies turn rate 180 and max 3, and saves it. The band/speed/acceptance/timeout readback is at `B_MOV/content_run1/editor_raw.log:1374`; turn-rate/max readback is `B_MOV/turn_run1/editor_raw.log:1259`.

## Walk-to-band witness

`B_MOV/pie_run2/editor_raw.log:1787–1789` records both the triggering no-candidate state at range 326.488 cm and a subsequent `walk start` from X=500 to `(50.753,181.806)`, distance 484.641 cm, with resulting target range 128.63 cm and band `[110,140]`. The earlier startup walk at line 1575 ends at range 128.82 within the same band. These `walk start` events are movement to the authored band after a range-filter refusal; they do not prove that a card's own range filter accepts every distance in a selector band. `MOV001_BAND_PLAN.md` is the separate card-range partition proof plan.

## Turn-in-place evidence and limit

In the same `pie_run2` trace, both cards are refused by `MoveModel.Cone` at lines 1790–1791; `reposition_turn start yawToTarget=-46.2019 range=128.63 ratePerSecond=180` appears at line 1792, and a SwingSlow candidate appears on the next frame at line 1793. This is consistent with the in-band/no-candidate turn branch (`RPGFrameworkBossCharacter.cpp:465–479`) and uses the configured turn rate. However, the log contains no `reposition_turn_end` token, although source line 478 emits it when the turn branch exits. Therefore the trace shows turn initiation and subsequent candidate eligibility, but does not establish a complete, independently closed turn-in-place lifecycle. The 3-attack `CompletedWithDamage` result is not a substitute for that missing event.

The run's `command.json` invokes the shared `F4/drive_pie.py` without embedding its map path; that driver reads the mutable `F4/current_map.txt` (`drive_pie.py:6–8`). The log's PIE world name identifies the MOV map, but the archived command alone does not freeze the exact map/profile input. Treat the profile-to-run association as source/setup evidence rather than a fully self-contained command receipt.

`B_MOV/turn_run1` is asset authoring under `-nullrhi`, not a PIE turn proof. `B_MOV005/pie_leash3` is a leash scenario: its walk and turn tokens are not an isolated MOV control. Keep those proof lanes separate. No new runtime proof was run for this audit.
