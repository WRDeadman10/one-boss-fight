# Test evidence index

Updated 2026-10-25. No new engine/build/PIE/package/benchmark test executed by Codex for this initiative.

## Historical inputs — not current initiative acceptance

| Evidence ID | Existing record | What it supports | What it does not prove |
|---|---|---|---|
| HIST-C84 | [C-84](C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md:2746) | Owner-run report: 37/37 automation; flask 7/7; build select 18/18; wake 11/11; close-path diagnosis | Raw reports not independently revalidated this turn; not complete current regression |
| HIST-TRACE | [TRACE-01](C:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md:97) | Historical 30/30 trace scenarios | Every later authored clip/rate/hitch or exact visible sword alignment |
| HIST-IFR | [IFR-01](C:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md:99) | Historical 19/19 window/cleanup checks | Full current damage/defense parity or human dodge feel |
| HIST-SOAK | [SOAK-01](C:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md:120) | Historical 213/213 scripted encounter stability | Latest close/wake changes or balance |
| HIST-M14-RAW | [M14 section 14](C:/UnrealProject/OneBossFight/Documentation/M14_FIGHT_NOTES.md:154) | Nine retuned raw-pacing records: seven wins, two early deaths; wins 122.6–143.5 s | Nine wins, current authored-clip balance, human difficulty |
| HIST-M14-TELL | [M14 section 15](C:/UnrealProject/OneBossFight/Documentation/M14_FIGHT_NOTES.md:187) | Six telegraph-0.4 runs: six wins, four hits total | Same sample size as raw set or current authored-montage feel |
| HIST-PERF | [Performance log](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:21) | Valid console Shipping RTX 3060 proxy result failed target; later Development experiments | Final Shipping pass; RDP results never count as hardware acceptance |
| HIST-GRAPH | [Saved melee graph](C:/UnrealProject/OneBossFight/Saved/asset_text/GA_EnemyMeleeAttack.t3d) | Inspectable saved graph/pin connections | Current runtime instance/default equivalence |
| HIST-AUDIT | [83-row audit](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/03_REFERENCE_COMPARISON_MATRIX.md) | Prior source/asset-dependency analysis and verification backlog | Fresh gameplay or approved implementation scope |

## Source fingerprint continuity checked 2026-10-25

SHA-256 equals prior audit snapshot:

| File under Source/OneBossFight/Player | SHA-256 |
|---|---|
| RPGAttackTracker.cpp | F2D2615F1B938AA8BF1F4AD9D7574B1876446823D83B87CD69521CA9D1153F0C |
| RPGBossShockwave.cpp | 9632381F60E92D3F2D7CC7362883CBC03C3B258191ABBBB4755A4BC9591CF3A4 |
| RPGBossHealPunish.cpp | 1E63046D9C215FD0D7A5F894EE1B4539D64DDBEFD9C80812CECBBAE89C476906 |
| RPGDamageResolver.cpp | 82DA0DD3400A049D92BD96409F90DB58A319FD7DB73E44F7B46B766E938A6BCA |

No commit/build equivalence implied; shared tree is dirty.

## Required new evidence IDs

- C-P0-ROUTE: live map/controller/info/components and exhaustive ability inventory.
- C-P0-DECISION: current BT/BB/ability graph edges, defaults and gate contexts.
- C-P0-TIMING: actual montage/notifies/rates/motion/identity/recovery matrix.
- C-P0-DAMAGE: production query/resolver and defense/direct-wave outcomes.
- C-P0-REGRESSION: bounded current diagnostic runs and exact existing coverage gaps.
- A-P0-CONTACT: timestamped visible blade versus production sweep measurements.
- A-P0-CUES: tell/release/impact/recovery and debug-off wave capture.
- A-P0-MOTION: locomotion/commit/recovery/branch/phase transition capture.

All are PENDING, not artifact paths that already exist.

## Submission schema and exclusions

Each record: task/revision, source+asset+binary fingerprint, date, engine/build/config, machine/session/GPU where relevant, exact command/probe, setup/seed/coordinates, actual move/phase/rate, cvars and time dilation, raw output path plus line/frame/time, expected/observed, trials, pass/fail/not-run and limitations.

RunDrivers applies no_throttle and wake_clip_off; dedicated wake test enables then disables wake. Shipping always uses wake. Record rpg.CloseTelegraph, build and fixed-FPS state. Warming shaders is not a product fix. Do not weaken assertions to turn flakes green.

Performance acceptance: repeated comparable packaged full fights, 1080p, average >=60 FPS, p99 <=16.67 ms, accepted RTX 3060 proxy explicitly labeled, real console/NVIDIA adapter. Keep CPU/GPU and Development/Shipping results distinct. Owner hand test remains separate.

## Static setup validation

Control-doc and matrix/link checks are documentation validation only. No runtime results generated. Final check results are reported in the handoff; do not count them in combat test totals.

Setup validation completed: 10 initiative documents; 83 unique requirement rows matching the reference with no missing/extra IDs; 109 local links valid. No duplicate mailbox message headings found. Across 1,442 snapshotted existing files, only TEAM_MAILBOX.md changed; its prior text is preserved and new messages are appended. No existing files deleted. No C-n/A-n acknowledgment arrived by this check. These results validate documentation/file boundaries, not combat.

