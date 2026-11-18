# C-1651 SFX-06..10 Trigger Audit

**Date:** 2026-11-18
**Scope:** Lead-side source review of the first five queued SFX tasks. No source, asset, config, or project content was changed. No tests, Editor, Unreal, build, or PIE were run.

## Findings

| Queue item | Source evidence | Safe implementation seam after Owner selects a cue | Remaining check |
|---|---|---|---|
| SFX-06 Guard Counter | `RPGDodgeTiming.cpp:706-739` arms/applies the Guard Counter montage after a successful guarded contact; that source path contains no direct sound dispatch. The project-owned montage is `/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter`. Generic pack notify code can play an assigned sound (`RPGPackNotifies.cpp:30-32`), but its actual montage notify assignment was not inspected. | Use an event at the counter's authored contact/release point on the project-owned montage or a project C++ event hook. Keep it optional and null by default. | Confirm exact montage timing and existing notifies in a locked Editor readback before authoring; no live assignment claim from this source review. |
| SFX-07 Air Plunge impact | The gap audit identifies `AM_ER_Attack_Air_Heavy_Plunge` and missing landing impact (`SFX_01_GAMEPLAY_AUDIO_AUDIT.md:18`). No direct sound dispatch for the plunge was found in the reviewed C++ paths. | Project-owned montage notify at the landing frame, or a project-owned landing event if one already exists. | Verify landing frame and current notify list by locked asset readback; don't patch pack montages. |
| SFX-08 A4 sweep scrape | `RPGAttackTracker.cpp:84-101` describes A4 as a project dynamic montage. `RPGFrameworkMoveExecutor.cpp:718-741` supports timed per-card sound cues and logs whether audio played. The old gap audit says the standard swing cue exists but floor scrape is missing (`SFX_01_GAMEPLAY_AUDIO_AUDIT.md:37`). | Prefer a timed cue in the active framework move definition at the floor-crossing moment, if that definition is the selected route. | Confirm selected route and current A4 cue data before adding a second sound; avoid duplicating the standard swing. |
| SFX-09 A5 javelin | `RPGBossHealPunish.cpp:189-192` spawns and launches `ARPGBossJavelin`; the reviewed launch path has no sound dispatch. The gap audit records no launch/flight whoosh (`SFX_01_GAMEPLAY_AUDIO_AUDIT.md:38`). | Optional launch sound at the existing spawn/release seam; flight loop is a separate choice and should not be inferred. | Confirm whether the current selected encounter route uses this legacy component before integration. |
| SFX-10 Stance break | Framework posture break reaches `ARPGFrameworkBossCharacter::StartStagger()` at `RPGFrameworkBossCharacter.cpp:978,1011-1035`; the function starts the stagger animation and emits telemetry but no direct sound. Generic framework move-card audio exists, but it does not by itself prove a stance-break cue. | Add a dedicated optional project-owned sound field/dispatch at the accepted framework stance-break event, only after the candidate is selected. | Confirm route and audio-selection approval; keep current silence when unset. |

## Decision and next action

Owner directed the audio lane to resume with Antigravity. This authorizes candidate/audition preparation. The existing SFX rules still hold: no cue wiring or asset/config edits before the Owner chooses the audition candidate. Antigravity is assigned candidate preparation for SFX-06..10 on Kanban BT-109..BT-113 and was told not to wait for Codex review. After candidate selection, any Unreal asset inspection/authoring or engine verification needs the task-specific C-1155 process and current Editor handoff.

This audit is source-only. It does not claim that a sound is audible in the packaged build or that any montage/data-asset assignment was read back.
