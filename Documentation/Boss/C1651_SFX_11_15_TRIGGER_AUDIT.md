# C-1651 SFX-11..15 Trigger Seam Audit

**Date:** 2026-11-18
**Scope:** Read-only code/document audit for SFX-11 through SFX-15. No source, asset, or config changes; no tests, Editor, Unreal, build, or PIE.

| Queue cue | Evidence in current source/docs | Lead finding / safe follow-up after Owner selection |
|---|---|---|
| SFX-11 A1 horizontal | `RPGAttackTracker.cpp:73-76` maps A1 to authored `AM_Boss01_A1` but keeps `GS_Attack03_Montage` fallback. `RPGBossCloseClipSwap.cpp:78-83` replaces pack Attack03 with the authored A1. | The authored A1 montage is a plausible notify seam only when the close-clip swap is active; fallback remains possible. Verify selected route and existing notify assignments before wiring, to avoid duplicate pack swing audio. |
| SFX-12 A2 overhead | `RPGAttackTracker.cpp:39-51` says production/stand-in is `GS_ChargedAttack_Montage`; `AM_Boss01_A2` is `OptionalTrackerMontagePath` for the Development preview, not a production replacement claim. | Do not assume an `AM_Boss01_A2` notify will fire in the encounter. First confirm selected route/montage and notify contents; otherwise put an optional cue on the active framework card at the approved strike point. |
| SFX-13 A3 stomp | `RPGAttackTracker.cpp:53-76` maps close combo stages to A3a/A3b and pack Attack01/02 fallbacks. Queue/spec instead names `AM_Boss01_A3`; no such A3 path is mapped in this tracker block. | Trigger identity is ambiguous: distinguish an A3 ground stomp from A3a/A3b close combo before wiring. Existing optional framework timed cue is a possible seam only if this framework route/card is selected. |
| SFX-14 Mid01 thrust | `TRACKER_COVERAGE_GAP_PROPOSAL.md:19-34` documents Mid01 as a pack `Mid01_Anim_Montage` candidate but explicitly as a proposed, unregistered timing entry; C-1132 docs call it untracked. | No confirmed native tracker seam. Verify which montage/route is active; if framework move-card route is used, cue can be time-based and remain null by default. |
| SFX-15 Sprint gap-closer | Existing audit docs identify `GS_SprintAttackFollowUp_Montage` as a pack follow-up, while Queue SFX/spec uses `AM_Boss01_Sprint`; no native route binding or montage replacement was found in reviewed code. | Do not attach the Queue-named montage cue based on name alone. Confirm selected attack/card and exact montage before wiring; framework timed cue is conditional on that being the active route. |

## Shared audio behavior and limits

`RPGFrameworkMoveExecutor.cpp:708-716` fires per-card cues once when the card time threshold is crossed. `:718-742` dispatches `Cue.Sound` through `UGameplayStatics::PlaySoundAtLocation` only when the selected cue channel enables audio and a non-null sound is assigned. This supplies a code-level opt-in/null-safe seam, but it does not prove any current SFX-11..15 card contains a cue or that these cards/montages are used in the packaged encounter. Candidate reels and the existing SFX_05 spec/manifest establish candidate names only; they do not establish a live notify assignment.

## Lead recommendation

Antigravity can continue candidate/audition preparation independently. Before implementation, Owner picks must be recorded, then verify the active route and actual montage/card/notify assignment under the required C-1155 readback. Preserve silence when unset and check for any existing pack swing cue to avoid doubling. No wiring or project asset/config edit is authorized by this audit.
