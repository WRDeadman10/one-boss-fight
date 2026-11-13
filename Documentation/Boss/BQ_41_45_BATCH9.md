# BQ-41..45: Queue BQ batch 9, Sevarog S6/S7/S8 acceptance and saved-asset readback

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Static only.** The readback script is written but **not run**; it needs the Editor under C-1155, which is ENG. Its static contract ran in-process: 6/6. No asset, card, source, engine, editor, PIE or commit.

| Task | Result | Files |
|---|---|---|
| **BQ-41** S6 acceptance checklist | **reconciled.** The live criteria are `X26-S6` in `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`: exactly 1 accepted `HitGroup_ScytheBlade` hit of 65 at 90-150 cm in Phase 2, commit 0.600, active 0.667-0.900, recovery 2.603. It passed live in R3 arm B and R4 arm E (BQ-33). **Added:** step 0, the saved-asset readback below, so a live pass is tied to the saved values | none |
| **BQ-42** S7 acceptance checklist | **reconciled** to `X26-S7a`/`S7b`: release 0.8, delay 0.75, radius 225, damage 35, snare 0.55 for 2.5 s, Phase 1 plus Phase 2. Passed live in R3 arms A and C. Open item still carried: `area_effect_snare state=Ended` has no instance id. **Added:** step 0 readback | none |
| **BQ-43** S8 acceptance checklist | **reconciled** to `X26-S8a`/`S8b`: channel 0.267-1.267, five ticks at 0.2 s intervals, tick damage 8, heal fraction 0.50, cone 650 cm / 45 degrees, facing fixed at start, Phase 2. S8a and S8b passed in R3 arm B. **Still open:** a cone-escape arm of its own (BQ-34 gives the arm spec). **Added:** step 0 readback | none |
| **BQ-44** saved-asset readback script | **new; lead hotfix X-2353 accepted by Codex and AG (A-968).** `verify_sevarog_s6_s8_card_readback.py` is a read-only Editor script. It loads the three saved C1277 cards from `/Game/OneBossFight/Data/Sevarog`, reads reflected fields with `get_editor_property` only, and compares timing, range, cone, damage, phase, extra phases, window counts, S6's exact blade-window identity/timing/sockets/radius/flags/empty baked samples, and the `area_effect` / `channel_drain` structs, including `enabled`. Floats are compared within 1e-4 (float32). It is fail-closed: a missing asset, unreadable field or mismatch is a FAIL. It prints `FIELD ... match=`, `CARD PASS/FAIL` and a terminal `RESULT=PASS cards=3 saves=0`. Post-hotfix static contract: 6/6 in-process (Claude and AG); direct empty/non-empty list cases are pinned. **Lead review gap fixed:** the initial readback compared only the S6 window count, which would miss drift in its accepted hit group or blade geometry. X-2353 adds exact per-field readback plus an author-script drift check for that window | `Scripts/Editor/verify_sevarog_s6_s8_card_readback.py` (new), `Scripts/Editor/test_verify_sevarog_s6_s8_card_readback_contract.py` (new) |
| **BQ-45** | this report | |

## Lead run (ENG, C-1155)

1. Check both locks and that no Unreal process is running. Launch the Editor with `-nosound` and run `py Scripts/Editor/verify_sevarog_s6_s8_card_readback.py`.
2. Expect `RESULT=PASS cards=3 saves=0`. Any `CARD FAIL` means the saved asset differs from the approved draft. Fix it by authoring, not by editing the expected values.
3. Only after a readback pass, tie the existing X26 live receipts (R3, R4) to the saved values, and add the S8 cone-escape arm.

## Limits

- **Not covered:** the S1/S2/S4/S5 C1247 cards (C-1274 saved-row readback, the 110 cm S4 trial from BQ-39). The same pattern could be extended to them once the Lead approves.
- **Unverified until the Editor run:** the reflected Python field names (`spec`, `area_effect`, `channel_drain`, `enabled`, `track_facing_each_tick`). They follow the names the author script already writes through the same reflection.
- The expected values are provisional ("tune after PIE"). A later approved retune must update the author script and this readback together, and the drift guard enforces that.

## Lead re-review (X-2353)

The first readback implementation checked `windows` only by count. That would not detect a saved S6 window whose `HitGroup`, time bounds, sockets, radius, behavior flags or baked-sample list diverged while the array still contained one element. The Lead added fail-closed comparisons for the S6 window and extended the drift contract against the author script. AG accepted the hotfix (A-968), and the post-hotfix in-process contract passed 6/6. The Editor readback remains ENG-gated and was not run.
