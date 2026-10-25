# CI-P0-A-01 — Antigravity animation/visual baseline

FROM / TO: Codex technical lead -> Antigravity, accountable visual investigator.
STATUS: IN PROGRESS after A-38 acknowledgment and exclusive output claim. Offline work only; Claude produces runtime captures. No editor handoff.

## Objective and references

Read-only audit of CURRENT boss animation, visible weapon, telegraphs and damage correspondence. Cover prior U04/U06/U09/U10, G01/G03/G07 and BOSS-ANM/HIT/PAC/MOV requirements. Use [exact asset register](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/11_UNVERIFIED_ASSETS_AND_TESTS.md), Master Freeze motion/timing/counterplay contracts and subsequent owner-approved greatsword/javelin reskin.

Existing assets and previous art reports are inputs, not proof of current in-game look. Do not create corrected animation, new VFX or substitute concept art in P0.

## Scope and ownership

Claim only NEW Docs/BossCombatReview/Execution/Antigravity/P0_REPORT.md and Evidence/. Read current project-owned source art/imports and Claude-produced current runtime captures/exports. Offline measurement/render of existing art is permitted with output only in your new evidence folder; do not save over source scenes/FBX/PNGs.

Unreal Editor remains Claude-owned. Request named capture/metadata from Claude first. Any direct editor use requires a logged, acknowledged single-owner handoff; P0 permits inspection only, never asset save/import/reimport/retarget/notify/socket/material editing. No C++, gameplay Blueprint, Source, Config or Scripts edits.

## Required observations

1. **Inventory/freshness:** actual in-engine animation/sequence/montage per A1/A1b/A3a/A3b/A2/A4/A5/A6, plus extra active moves Claude identifies. Distinguish authored replacements, pack fallbacks and offline source export. Record skeleton, transform scale, runtime asset/version.
2. **Timing cards:** first perceptible tell, startup, apex/hold stability, commitment cue, active contact pose, release/impact, follow-up cue, recovery and locomotion transition. Use timestamps/frame rate and effective play rate; never infer usable recovery from total duration.
3. **Weapon/trace alignment:** visible sword base/mid/tip at several active poses versus ACTUAL gameplay sockets/sweep volume. Hidden leader and visible follower are separate. Measure cm offsets and contact/edge-of-range views. Do not recommend inflated collision to mask a pose mismatch.
4. **Rotation/translation:** windup tracking, committed heading, root motion/feet slide, recovery movement and branch interruption blending. Report observed transform/capture, not guessed motion ownership.
5. **A6:** central impact and expanding ring separately; debug-off packaged visibility, visible radius/thickness/front versus damage band's logged radius, cue lead time and jump counterplay. A debug circle is not Shipping VFX. If a current independent renderer exists, identify exact asset/component.
6. **A2/A4/A5:** delayed release readability/stable hold, low-blade jump clearance, projectile tell/release/flight visibility. Preserve approved attack roles; do not change balance/timing.
7. **Transitions:** locomotion -> attack -> branch/default recovery -> locomotion; stance break/getup/riposte/phase/death. Flag discontinuities using capture evidence.
8. **Camera/accessibility/cost:** player-camera framing, occlusion, phase lighting, low-shake/effects readability. Record material/particle/skinned-component cost evidence available from Claude; triangle counts or offline renders do not establish packaged GPU performance.

## Evidence and capture request

Coordinate with Claude on one shared capture ID per move/rate/phase. Ask for current asset paths, runtime mesh/socket transforms, production query overlay, event timestamps, phase/rate/cvars, camera/FOV/resolution and debug-off counterpart. Do not operate the editor concurrently.

For every image/clip: source path and provenance; build/asset fingerprint; camera and playback rate; frame/time markers; annotations in a separate copy; distinguish gameplay from offline source render. Capture a normal player view and diagnostic view. If capture fails/black, say BLOCKED and retain only what can be proven; no invented visual verdict.

## Acceptance / tests

Report per move: observed existing behavior; approved target; measured gap; severity and confidence; suspected cause versus confirmed fact; smallest asset-side proposal if warranted; linked Claude gameplay dependency; required next test.

All currently active moves accounted for or explicitly blocked. Weapon correspondence is measured, not inferred from filenames. Ring visibility has a debug-off packaged observation or remains unverified. Readability judgments remain technical assessments pending owner feel acceptance.

No new art implementation or gameplay edits. No claim that offline Blender renders prove runtime contact or Shipping appearance. No quantitative tolerance invented as approved design: propose a tolerance for owner review.

## Deliverables / next action

Report: Docs/BossCombatReview/Execution/Antigravity/P0_REPORT.md.
Evidence: new Evidence/ subtree containing annotated frames, measured tables and short clips when available. Link existing files instead of duplicating large deliveries.

Acknowledge X-91/X-93 with availability, exact claim, tools, current obligations and editor/capture needs. Post A-n review-requested when complete with paths and limitations. Codex reviews actual evidence; Claude remains accountable for runtime integration. P1 is not authorized by this brief.

