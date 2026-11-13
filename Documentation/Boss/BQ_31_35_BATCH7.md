# BQ-31..35: Queue BQ batch 7, framework acceptance planning

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Offline analysis only.** Nothing was compiled, run, edited in source or launched: no engine, editor, PIE, script run or commit. Every file reference was read statically, and the key ones were re-checked by grep (test name strings, script paths, runner lines). No source or script was changed in this batch.

## BQ-31: native test list for selector early refusal and the tag-generation fence (BK-26..30)

| Automation name | File:line | What it pins |
|---|---|---|
| `OneBossFight.Binding.EncounterSelection.ThreadAndWorldStateRefuseBeforeResolution` | `Tests/RPGBossStartupActivationTests.cpp:1200` | A stale `EncounterSelection.Absent` diagnostic is replaced. Off the game thread: `EncounterSelection.NotGameThread`, no binding. A foreign world: `EncounterSelection.WorldState`, no binding, empty selections |
| `OneBossFight.Player.OwnedTagCleanup.PriorGenerationCannotRemoveCurrentTag` | `Tests/RPGGenerationResetRegressionTests.cpp:138` | `RPGOwnedTagCleanup::MayRemoveForGeneration`: same actor and generation allowed; an older generation or another actor refused |
| (related, not BK-26..30 scope) `OneBossFight.Binding.EncounterSelection.AlreadyBegunActorsRefusedBeforeBinding` | `Tests/RPGBossStartupActivationTests.cpp:1235` | Actors that already began play are refused before binding |

**Doc defect:** `BK_26_30_SELECTOR_DIAGNOSTICS_TAG_GENERATION_FENCE.md` previously named the first test incorrectly. Lead corrected it to the source-verified automation name in the table above during batch review.

**Gaps (BK report behaviours with no native test):**
1. A successful binding clears the diagnostic.
2. The refusal tokens other than Absent, NotGameThread and WorldState: generation, definition, census, actor state, spawn and profile.
3. Concurrent access to the locked diagnostic getter and writer.
4. The I-frame and parry components capture the generation when they acquire a tag. Only a Python source-contract guard covers this.
5. The retry callback carries the generation token, and a stale callback logs `cancelled_stale`. Only the pure predicate is pinned.
6. Legacy unbound actors use generation 0.
7. Ambiguous duplicate binding fails closed.
8. The participant-generation lookup itself.

Gaps 1, 2 and 5 are the cheapest to add as native tests.

**Lead checklist (C-1155):**
1. Close the editor and take both locks, then build Development Editor Win64 with 0 errors.
2. Run the suite filters `OneBossFight.Binding.EncounterSelection` and `OneBossFight.Player.OwnedTagCleanup` (`-nosound`).
3. As regression checks, run the remaining `OneBossFight.Player` tests and the selector tests.
4. Record counts and the log path in `TEST_PLAN.md`, then release the locks.

## BQ-32: BF-X05 one-run acceptance driver plan (static; the run is ENG)

**Existing pieces (paths confirmed):**
- `Scripts/Tools/verify_bf_x05_selected_route.py`: a fail-closed verifier for a v1 JSON receipt. It always writes `live_run_verified: false`.
- `Scripts/Tools/test_bk3_bf_x05_verifier.py`: its synthetic tests.
- `Scripts/Editor/pie_sevarog_framework_live.py`: the live driver. It emits `PACK_STYLE_READY`, `RESULT route=...` and `route_verified`.
- `Scripts/Editor/run_bk56_60_deferred_selection.ps1`: the C-1155 runner pattern (build, pinned suite, bounded no-save PIE).

**Rows one run must cover** (`BF_X05_SELECTED_ROUTE_ACCEPTANCE_TABLE.md`): ID-01, PACK-01, FW-01, PART-01, HUD-01, TERM-01, RETRY-01, RESET-01, REPLACE-01. Each needs a raw-log excerpt.

**Step order:**
1. Take the locks, then build and run the pinned suite.
2. Default-off launch: log the build ID, map and pack boss identity. Covers ID-01 and PACK-01.
3. Opt-in launch: `rpg.FrameworkEncounterSelection=1`, definition path plus SHA-256, deferred activation of exactly one framework boss, gated on `PACK_STYLE_READY`. Covers FW-01.
4. Participant slots and generation. Covers PART-01.
5. HUD health and fraction against the native value. Covers HUD-01.
6. Kill the boss: terminal callback actor, generation and counts. Covers TERM-01.
7. Retry visibility and delay. Covers RETRY-01.
8. Reset and rebind: the generation advances and a stale callback is refused. Covers RESET-01.
9. A callback from a replacement actor is refused. Covers REPLACE-01.
10. Terminal `RESULT` and readiness markers, per the BK-41..45 helper pattern.
11. Transcribe the log into the v1 receipt and run the verifier.

**To be written:**
- PIE steps 5 to 9: the live driver has no HUD, retry, rebind or replacement hooks found.
- A two-arm runner that does the default-off and opt-in launches in one go.
- Optionally, a log-to-receipt transcriber; transcription is manual today.

**Blocked today:**
- BK-3 deferred selection refuses on the invalid Sevarog Stats and Phase_1 data.
- The owner's X-1991 values are pending.
- The PythonScriptPlugin crashes at exit after a refusal (BK-61..65).

## BQ-33: X26 matrix gap list per arm (newest evidence wins)

| Arm | Passed (evidence) | Failed or absent |
|---|---|---|
| A | S7a, S7b (R3, AG A-835) | S4 to S5 refused with `MoveModel.Range` at the 120 cm boundary (outside the C1278 matrix) |
| B | S6, S8a, S8b (R3) | none in scope |
| C | S7a, S7 dodge-out (R3; also Run 1) | none in scope |
| D | P1 (R3) | none in scope |
| E | P1 and P2 (R4 `P_C1297_X26R4_E`, 2026-11-11, AG A-840: one Phase_1 to Phase_2 transition at 125/250, S6 at 115 cm, S8 at 400 cm, 511/511) | R3's P2 failure (first card before the phase latch) is superseded by R4 |

- **Aggregate:** all seven C1278 checks plus the dodge-out variant pass, 8/8 (`BK_06_10_X26_DRIVER_SUPPORT.md`, TASKS X26 line).
- **Stale entries:** the BK-46..50 TASKS line ("arm B incomplete") and `C1280_X26_PHASE_ELIGIBILITY.md` ("live checks pending") predate R3 and R4.
- **Still needed (outside the matrix):**
  - S8 cone escape as its own arm.
  - An instance id on `area_effect_snare state=Ended`, so it can be tied to its S7 instance.
  - The S4 to S5 120 cm float boundary follow-up.
  - The BK-3 deferred-selection live arm.

## BQ-34: S8-first arm runner configuration (static; the run is ENG)

**Today's mechanism:**
- In `Scripts/Editor/run_bk2_x26_locked_validation.ps1`, each arm is one hard-coded `Invoke-BoundedCardSelfTest <stage> <card> <healthFraction>` call. The existing arms are S1 and S6 (lines 92-93).
- Each call sets `SEVAROG_LIVE_SELF_TEST=1`, `SEVAROG_LIVE_SELF_TEST_CARDS=1`, `SEVAROG_LIVE_CARDS=<card>` and `SEVAROG_LIVE_BOSS_HEALTH_FRACTION`, then runs its own `-nosound` PIE.
- The driver forces the listed card with `boss.start_card_for_test`. It places the player from a per-card table: Soul Siphon (S8) at 400 cm, line 525 of `pie_sevarog_framework_live.py`. It fails if the player is out of band.

**Proposed S8-first arm (the existing mechanism only):** `Invoke-BoundedCardSelfTest 'S8' 'Move_Sevarog_Soul_Siphon_C1277' '0.5'`, placed before the S1 and S6 calls.
- **Range:** 400 cm, inside the documented 220-620 cm band.
- **Phase:** S8 is Phase 2 only; the 0.5 health fraction matches the S6 arm.
- **Expected keys:** `S8_PACK_STYLE_READY`, `S8_SPAWN_PASS`, `S8_CARD_ACCEPTED`, `S8_CARD_WINDOW_ELAPSED`, `S8_FINISHED`, `S8_HEALTH_HOOK`, `S8_ORDER_VALID` and `S8_PASS`.
- **Pass:** `S8_PASS=True` with the order style < spawn < accepted. The behaviour must also be judged against the C1278 table: five 8-damage ticks (0.467 / 0.667 / 0.867 / 1.067 / 1.267 s), heal fraction 0.50, and `recoveryGate=ExemptConeEscape`.

**What does not exist yet:**
- The S8 call itself. I did not add it: the runner is a Lead-run C-1155 script, so the Lead decides.
- An automatic check of tick cadence, heal or cone escape.
- Any way to make the **selector** pick S8 first. The autonomous `PHASE2_PROBES` route only observes the 400 cm band after Phase 2. This arm therefore forces the card; it does not prove selection.
- Unverified statically: whether `start_card_for_test` enforces the phase gate. Keep 0.5 health to be safe.

**Stays ENG:** the run under the locks; BD-A11 and BD-A13 stay blocked until it exists.

## BQ-35: this report

**Gates:** all live runs (BQ-32, BQ-34) and the Lead build and suite (BQ-31) are ENG. BF-X05 is additionally blocked by BK-3 data and O1 (X-1991).
