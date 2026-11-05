# Queue Z Batch 5 — telegraphs, HUD, camera, accessibility

**Scope:** Z021–Z025 read-only source and historical-evidence review. No tests, Editor, PIE, build, package, source, or asset changes were run.

## Z021 — source-to-telegraph inventory

`FRPGAttackTiming` stores MoveId, montage identity/fallback, optional preview path, commit timestamp, active start/end, recovery timestamp and authored-windup flag (`Source/OneBossFight/Player/RPGAttackTracker.h`). All values are montage-local seconds. `URPGAttackTracker` observes current montage position and compares it with these timestamps; before active start it may adjust play rate for close telegraphs, except authored/optional montages. It is a timing/heading monitor; its header states that the pack trace notify opens the actual hit window. Its observed active interval is not proof of a live hitbox or confirmed screen cue.

| Move | Source-configured timing (montage-local s) | Source path / cue boundary | Evidence class |
|---|---|---|---|
| A1 | commit .33; active .35–.50; recovery 1.20 | authored path plus pack fallback; authored windup bypasses scaling | configured; runtime visual not inspected |
| A1b | .12; .16–.46; 1.25 | pack chained follow-up | configured; cue appearance unknown |
| A3a | .38; .40–.60; .80 | authored path plus pack fallback | configured |
| A3b | .13; .15–.40; 1.3333 | authored path plus pack fallback; branch stage | configured |
| A2 | 1.68; 1.93–2.11; 3.14 | pack charge stand-in; optional authored tracker montage is Development/test preview only | configured; preview is not production-ability proof |
| A6 | .16; .75–1.17; 1.80 | pack leap stand-in | configured |
| A4 | .40; .60–.90; 1.75 | project clip; low-sweep component separately observes it | configured; crossing cue needs live view |
| A5 | .45; .45–.50; .95 | project clip; projectile release at active start | configured; projectile flight is separate from warning |

Times are native defaults in `RPGAttackTracker.cpp:35–105`, not claims about all authored asset notifies. `AN1_AN4_ART_AND_ANIMATION_INVENTORY.md` calls A2 assembly deferred and says the phase-two aura is needed (lines 28, 80, 120). Newer Tier 2/cue records have distinct routes and asset scope; do not merge into a global statement.

The framework proof-lane cue system separately pairs card visual flipbook and sound with mode controls. BUILD-138 records retained Lead PIE mode runs on its framework proof map. It does not establish the same cues on the legacy production boss route.

## Z022 — HUD authority and stale-state paths

`URPGBossHud::TickComponent` reads current/max boss health through pack attribute reflection and normalizes health, reads posture component state and normalizes by max posture, reads phase-two state for subtitle, and shows the riposte prompt only while fighting, in the critical window, and available to the current pawn (`RPGBossHud.cpp:370–500`). The widget draws copied state; health trail drains and snaps up on refill/reset, posture changes color/flash, and prompt visibility follows the copied boolean (`:205–246`). On participant-generation change, the component clears fight/victory state and banner/retry then returns to Dormant (`:352–370`). State is tick-polled, not directly subscribed to attribute change events.

Retained `TEST_PLAN.md` HUD-01 records Lead PIE PASS 29/29 on 2026-10-20 and four screenshots reviewed. VICT-01 records retry/reload PASS 9/9. These remain dated observations; no new test or screenshot review occurred.

## Z023 — camera collision and arena framing

Source defaults: probe radius 34 cm, `ECC_Camera`, pitch −70°..32°, lag speed 10 and max lag distance 60 cm, boom attached to capsule. `Apply` enables spring-arm collision and applies settings. Each tick it reattaches a boom moved by pack death logic, restores collision testing and reapplies pitch constraints to camera manager/control rotation (`RPGCameraRig.h`, `RPGCameraRig.cpp:31–78,118–155`). These are configured safeguards, not proof of whole-arena framing/readability.

The historical CAM-01 row in `TEST_PLAN.md` reports 0/10 pitch-sweep clips, 0/197 moving clips and scenarios 6/6 after the rig, plus an image at +32° and −60°. Its limitations exclude slopes/stairs, lock-on, gamepad stick, ceilings/overhangs; the test used the Camera channel. This is retained 2026-10-20 evidence, not a current rerun or general camera-readability result.

## Z024 — accessibility and input-feedback claims

The framework proof lane has dual visual/audio cue modes and a 0.5 visual-scale mode with retained BUILD-138 evidence. D154 color palette accessibility and D185 audio telegraph remain protocol-only: actual palette/cue mapping, display/audio conditions and manual user legibility are pending. The art/animation inventory uses broad “Accessibility Cues” wording for QA-007 but separately identifies legacy parry spark as an upgrade target. Technical dual-channel support or a proposal does not prove usability for any color-vision/hearing profile, screen size or adaptive-input need. No verified project-wide UI scale, remappable chord inventory or accessibility-user study was found in this source/doc pass. Avoid universal accessibility claims.

## Z025 — receipt and unresolved evidence

Remaining Lead evidence: current authored asset/Blueprint notify-to-screen cue inspection on the intended production route; current resolution/UI scale/readability and supported controller permutations; build-bound HUD reset/riposte/victory and camera obstacle checks; manual accessibility review under recorded display/output conditions. Historical PASS rows and BUILD-138 remain restricted to their dates, maps/routes and supplied source artifacts. No look, control, color or production-default changes proposed.

**Disposition:** Batch 5 complete locally. `git diff --check` is the only validation for this documentation update.
