# BB-A21..A23: Ember A2 Full Composite Montage Plan (`Raise + ApexHold + Slam`)

**Queue Lane:** `QUEUE_BB` Tasks `BB-A21`, `BB-A22`, `BB-A23` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BB.md`, `[C-1267]`, `[C-1269]`  
**Status:** **PLAN ONLY** (Zero asset edits, zero wiring, zero look changes; any visual swap away from `GS_ChargedAttack_Montage` requires explicit Owner YES + Lead runtime verification)  

---

## 1. Current Asset & Engine Constraints

1. **Disk-Verified Input Sequences & Asset:**
   - `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_Raise` (`0.600 s`)
   - `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_ApexHold` (`1.167 s`)
   - `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A2_Slam` (`1.367 s`)
   - Existing disk asset `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2` (`V_A013_A2_MONTAGE_NOTIFY_REVIEW.md`).
2. **Known Segment Composition Finding (`W_A008` / `W_C046` & `[C-1269]`):**
   - Creating a montage in UE 5.5 Python via `AnimMontageFactory.SourceAnimation` populates only the first segment (`Raise`) because `AnimTrack` / `SlotAnimationTrack` / `composite_sections` cannot be authored cleanly from Python (`[C-1269]`, `[X-1811]`).
   - Therefore, full three-segment composite authoring must execute through an Editor-only C++ helper (extending the `URPGMontageWrapperLibrary` pattern ordered in `[C-1269]`) or verified Editor composite assembly, followed by save + reload + notify readback.
3. **Production Default Boundary (`W_A008`):**
   - Production default stays `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage` (`RPGAttackTracker.cpp`).
   - Authored composite testing remains behind Development-only `rpg.AttackTracker.A2PreviewClip` (`default 0`) and `OptionalTrackerMontagePath` (`nullptr`/empty default) until Owner approves the look change.

---

## 2. Composite Segment & Section Plan (`Total 3.134 s` @ `1.0x`)

| Segment # | Source `AnimSequence` | Clip Length (s) | Montage Timeline Span (s) | Proposed Section Name | Section Next | Blend Policy |
|---|---|---|---|---|---|---|
| `0` | `AN_Boss01_A2_Raise` | `0.600` | `0.000 – 0.600` | `A2_Raise` | `A2_ApexHold` | Slot `DefaultSlot` (or pack boss slot), blend-in `0.15 s` |
| `1` | `AN_Boss01_A2_ApexHold` | `1.167` | `0.600 – 1.767` | `A2_ApexHold` | `A2_Slam` | Continuous segment stitch (`0.00 s` cut or `0.05 s` curve blend inside Editor C++ composer) |
| `2` | `AN_Boss01_A2_Slam` | `1.367` | `1.767 – 3.134` | `A2_Slam` | `None` | Blend-out `0.250 s` starting `2.884 s`, reaching idle at `3.134 s` |

*Comparison vs `RPGAttackTracker.cpp` A2 target bounds (`1.680 s` commit, `1.930–2.110 s` active, `3.140 s` recovery):*
- Total span `3.134 s` vs `3.140 s` (`-6 ms`, `< 0.5 frame` at 60 Hz).

---

## 3. Complete Notify & State Timing Plan

Targets all timings from `V_A013_A2_MONTAGE_NOTIFY_REVIEW.md` and preserves the pack collision trace contract noted in `Documentation/Boss/SWITCH_PLAN.md:49` (preserving `ANS_CollisionTrace` + second slam hit interval and `OptionalTrackerMontagePath` exact matching):

| Notify / State Class | Track | Montage Start (s) | Montage End (s) | Relative Segment Time (s) | Purpose & Contract Alignment |
|---|---|---:|---:|---:|---|
| `URPGANS_BossMoveTiming` *(optional migration row, `bUseMontageNotifyTimings=false` default)* | `1` (Timing) | `0.000` | `3.134` | Full composite span | Encodes `MoveId=A2`, `CommitTime=1.687`, `WindowStart=1.937`, `WindowEnd=2.107`, `RecoveryEnd=3.134`, `TrackTurnRate=120` |
| `Notify_AttackCommit` (Tracker / Telegraph Lock marker) | `2` (Events) | `1.687` | — (instant) | `ApexHold + 1.087 s` (`80 ms` before `A2_Slam` begins) | Locks heading `0.250 s` before sword floor impact (`RPGAttackTracker.cpp` `CommitTime 1.680 s`, `+7 ms` delta) |
| `ANS_CollisionTrace` *(Secondary / Slam Active Window)* | `3` (Hit) | `1.937` | `2.107` | `Slam + 0.170 s` to `Slam + 0.340 s` | Sweeps blade sockets (`1.930–2.110 s` tracker band, `+7 ms / -3 ms` delta); triggers `URPGBossShockwave` / Legend slam camera shake |
| `Notify_RecoveryBlend` *(or `BlendOut` trigger)* | `2` (Events) | `2.884` | — (instant) | `Slam + 1.117 s` | Starts `0.250 s` blend out back to idle at `3.134 s` |

**Note on Pack Trace Interval 1 (`1.57–1.76 s`):** Per `SWITCH_PLAN.md:49`, `GS_ChargedAttack_Montage` carries an early pack trace (`1.57–1.76 s`) that did not land damage in the cited close scenario alongside the real slam trace (`1.93–2.11 s`). Before replacing `GS_ChargedAttack_Montage` for Shipping, Lead must decide whether to author a non-damaging early raise trace window or keep strictly the slam active window (`1.937–2.107 s`) during live parry/hit parity runs (`C-1132` / `C-1152`).

---

## 4. Verification Gates (Before Any Owner Look Approval Request)

1. **C++ Composite Authoring Helper:** Author multi-segment montage assembly + notify placement via `OneBossFightEditor` C++ (no partial Python `SourceAnimation` stub), save + reload + read back all 3 segments, section links, and exact notify times.
2. **Paired PIE Comparison (`C-1132` / `C-1152`):** Lead runs `rpg.AttackTracker.A2PreviewClip=1` vs `0` and verifies telegraph lock timing (`~1.68 s`), active damage (`1.93–2.11 s`), parry contact reward, and recovery end (`~3.14 s`).
3. **Owner Video Review (`GATE-07`):** Capture paired MP4 (`GS_ChargedAttack_Montage` vs `AM_Boss01_A2` Raise+Hold+Slam) for explicit Owner approval before flipping any default reference.
