# BQ-66..70: Queue BQ batch 14, close-attack 90 cm driver analysis and the HEAVY poise victim test

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**The C++ is written but NOT compiled or run.** The analysis is static; no driver or PIE was run. No asset was written, and no commit.

## BQ-66 (C5, KI-106): why C7 hits 1-2 of 5 at 90 cm while `pie_close_reach.py` hits 100%

I compared the two drivers line by line. Both freeze the encounter (`hold_for_test(True)`), stop the active montage, refill the player, place the player in front at 90 cm facing the boss, and call `tr.start_move("Close")` in the same tick. Three differences remain:

| # | `pie_close_attacks.py` (C7) | `pie_close_reach.py` | Weight |
|---|---|---|---|
| D1 | `rpg.CloseTelegraph 0` is executed **at module import, on the EDITOR world**, before PIE starts (`:16-17`) | `rpg.CloseTelegraph 0` is executed **inside PIE**, on the PIE world, at its first tick (`:57`) | **High.** See H1 |
| D2 | The boss yaw is whatever the previous step left (`place()` reads it; it is never set) | The boss yaw is set explicitly each trial (`set_actor_rotation`, yaw 180) | Medium. KI-106's own note: the misses were at actual yaw -162.2 |
| D3 | 0.6 s gap after each 2.2 s check | 0.5 s gap after a 2.0 s trial | Low |

**H1 (leading hypothesis): the telegraph slowdown is still active during C7.** KI-106 records peak blade steps of **7-10 cm per frame in C7 against 24-32 cm** in `pie_close_reach.py`, in the same frame counts. A ratio of about 0.3 is what the telegraph produces: it lowers the play rate so the active window starts at 0.4 s instead of the clip's 0.14-0.17 s, a rate of about 0.35-0.43. If the CVar value set on the editor world before PIE does not survive into PIE (for example if config or loadout code re-applies the 0.4 default at PIE start), C7 swings at telegraph pace while `pie_close_reach.py` swings at full pace. Whether a slowed swing misses depends on the trace and hit timing under a lowered play rate. **H1 is unproven.** It explains the measured blade-step ratio, which KI-106 left unexplained.

**Cheap discriminating check (ENG, no code change):** in C7, log `rpg.CloseTelegraph` and the boss montage play rate at each `close_ability(90)` start. **Prediction under H1:** CVar 0.4, or play rate below 1.

**Proposed driver fix (for the Lead; not applied, it is a Lead-run driver):**
1. Capture the pre-run `rpg.CloseTelegraph` value, move the `rpg.CloseTelegraph 0` call into `s_wake` on the PIE world, and log the value read back. Restore the captured value on the PIE world on every exit path; do not assume the default or restore a hard-coded value.
2. Set the boss yaw explicitly before each C7 trial (D2).
3. If C7 then reaches at least 4 of 5, restore the C7 assertion to its target of 4 and close KI-106 as a driver-setup issue.

## BQ-67 (C11, KI-057): the pack poise pin blocks the HEAVY poise measurement

**Finding:** KI-057's blocker (KI-056, the boss could never stagger) is fixed. But a second blocker exists that KI-057 does not mention: `URPGBossPosture` **pins** the pack `Attribute.Poise` full **every tick**, writing back even a hit's own subtraction of 20 or 50 (`RPGBossPosture.h:12`). So no driver can see the pack's 20 (light) / 50 (heavy) cost on the boss. My notes forbid setting component properties during PIE, so toggling `bPinPackPoise` live is not an option.

**Change (opt-in, default unchanged):**
- New Development-only console switch `rpg.Posture.PinPackPoiseTest` (default **1**). It is compiled only under `!UE_BUILD_SHIPPING`, following the BQ-23 guard rule; Shipping always returns 1.
- Pure seam `URPGBossPosture::ShouldPinPackPoise(bProperty, bConfigured, Switch)`.
- `TickComponent` now calls the seam. With the switch at its default of 1 the behaviour is identical.

| Files | |
|---|---|
| `Player/RPGBossPosture.h/.cpp` | switch, seam, tick call |
| `Tests/RPGPackPoisePinSwitchTests.cpp` (new) | `OneBossFight.Boss.PackPoisePinSwitch`: 5 seam cases, the property default, and switch registration. The source declaration sets its default to 1; the test checks registration rather than current value because config/other tests may override it. |

## BQ-68: HEAVY poise victim test plan (ENG, reuses `pie_boss_hitreact.py`)

`pie_boss_hitreact.py` already lands real light (`IA_NormalAttack`) and heavy (`IA_StrongAttack`) hits on the boss and logs `Attribute.Poise` after each hit. The plan:
1. Capture the current `rpg.Posture.PinPackPoiseTest` value before PIE, send `0` for the measurement, then restore the captured value on every exit path. The registered default is `1`, but the driver must preserve an existing session override.
2. Land one light hit with poise full at 100 and expect **80**. Wait for the pack's regeneration back to 100, then land one heavy hit and expect **50**.
3. Read poise on the hit frame, before the pack regenerates. Do not chain two heavy hits: the second would reach 0 and start the pack's own hit stun.

**Accept:** light costs 20 and heavy costs 50 (`-20 - 30 * (AttackPower >= 3)`, DECISIONS "Jump attacks"). That closes KI-057's "unverified on a victim" for the sword. Claymore and unarmed stay separate items.

**Risk:** with the pin off, the pack's poise gate may start its own 0.8 s flinch if poise reaches 0. The plan avoids that. `URPGBossPosture` already ends a pack stun that starts while pinned (`PackStunSuppressed`); with the pin off, that guard does not apply.

## BQ-69: tests

`OneBossFight.Boss.PackPoisePinSwitch` (new, written, not compiled). Lead review removed a current-value assertion that could fail after a legitimate config/test override; default 1 remains source-verified. BQ-66 needs no native test: it is a driver-setup question.

## BQ-70: this report

**Gates:**
- C-1155 build and suite.
- ENG: the H1 check, the C7 driver fix, and the KI-057 PIE measurement.
- Lead: approval for the driver edits.
