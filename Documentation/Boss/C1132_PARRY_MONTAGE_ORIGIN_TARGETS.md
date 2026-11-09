# C-1132 — parry-only montage-origin targets and untracked hitters

## Scope and source evidence

Claude's C-1132 report says the BUILD-271 90-second parry-only run produced 14 presses, 14 no-contact results, and 21 observed player-health drops. Its measured hit positions are montage-local: A1b `0.190/0.199/0.231`, A3b `0.152/0.254`, A1 `0.351`, A3a `0.484/0.530`, and A2 `1.974/2.030/2.104` seconds. The configured tracker windows put several contacts at or near their opening. C-1132 reports the runtime parry window as 0.2 seconds. These are Lead-reported runtime measurements, not reproduced by Codex.

`URPGAttackTracker::FindTimingIndex` resolves the active montage against its `Attacks` timing table by montage name, fallback name, clip name, or optional path (`Source/OneBossFight/Player/RPGAttackTracker.cpp:122-143`). Native entries include A1/A1b/A3a/A3b at lines 66-69 and A2 at line 37; no entry maps `Mid01_Anim_Montage` or `GS_SprintAttackFollowUp_Montage`. C-1132's observed health drops with `boss_move=None` therefore establish a coverage gap in this attack tracker's move identity/timing/heading telemetry. The separate trace audit labels a trace window `pack` with instance `-1` when no tracker move exists (`RPGTraceAudit.cpp:201-202`), so trace observability can retain a generic window without recovering the missing move identity.

The source does not prove these attacks lack a visual tell or damage notification. In particular, `RPGTraceAudit` samples the active boss montage while monitoring the pack collision trace target (`RPGTraceAudit.cpp:145`); it does not define authored montage notifies. Nor does the missing tracker mapping by itself prove a player i-frame bypass: the player dodge notify owns `Status.Invulnerable` (`RPGIFrameMonitor.h:13`), and the custom boss damage helper checks that tag at resolution (`RPGBossDamage.h:14,34-36`). That helper documents its scope as the boss's custom A4/A5/A6 damage, not the observed pack montage trace damage. Thus tell coverage, which resolver caused each observed hit, and the actual i-frame outcome for Mid01/Sprint remain runtime questions; the report makes no claim that they are safe or defective.

The project damage resolver's player i-frame check is a separate player-state gate; absence from the boss attack timing table alone does not show that i-frames are bypassed. Static inspection likewise cannot establish the visual readability of the two montage attacks. No gameplay/source/tracker changes were made for this static audit.

## Driver-only change

- Move parry inputs now use the C-1132 measured montage-origin contacts minus 0.08 seconds: A1b `0.12`, A3b `0.10`, A1 `0.27`, A3a `0.42`, A2 `1.92`.
- `Mid01_Anim_Montage` is targeted at `0.62` seconds by montage name, because the tracker reports no move for it.
- `GS_SprintAttackFollowUp_Montage` is logged as `PARRY_UNTRACKED_BOSS_HITTER` only. C-1132 observed two different contact positions, so one target is not justified.
- The 60%-of-tracker-window fallback is removed. Unknown timing targets are reported without a parry attempt.
- Attempt/result telemetry and existing receipts retain tracker active/window context. Synthetic IDs distinguish montage-target attempts from native tracker instances.

## Validation and handoff

`python -m unittest Scripts.Editor.test_pie_full_fight_offline -q` passes 33/33. `python -m py_compile Scripts/Editor/pie_full_fight.py Scripts/Editor/test_pie_full_fight_offline.py` passes, and the scoped `git diff --check` is clean. These are offline checks only; Codex did not build, run Unreal, or run PIE. Claude should rerun the parry-only drive with this driver and separately repeat the camera default-off check using the `-1` config path without injected zero-valued CVars. That camera check is not included in this code change.

## Acceptance boundary

This change corrects the test driver's timing from observed hit positions. It does not claim that parries now contact in runtime. The tracker coverage gap for the two named montages is evidenced by the C-1132 run plus the static timing table; whether to expand tracker coverage, and any tell/i-frame implications, needs an explicit follow-up review.
