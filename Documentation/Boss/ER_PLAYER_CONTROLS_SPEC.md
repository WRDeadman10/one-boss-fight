# Elden Ring style player controls: spec and task split (owner request 2026-11-06)

Owner request (chat, 2026-11-06): "full player control like Elden Ring with the same animation. A single press of the dodge button rolls in the current game; in Elden Ring it does not, it only moves away while standing. Jump attack, light attack and heavy attack have different animations." Antigravity is available for Blender animation.

Status (mailbox through A-591): optional Source plumbing is present, all four ER clips are imported and their montages are trimmed/read back to accepted lengths. Claude accepted each delivery for owner review; the owner's video review is still pending, so no optional montage field is assigned in a saved asset. Tier 2 assets were synthesized per A-591; Lead runtime verification remains pending. Scope is the single-player duel only (owner 2026-10-29). No pack asset is deleted or recreated.

## 1. What the game does today (measured, cited)

| Control | Today | Source |
|---|---|---|
| Dodge tap, moving | Quick roll, `Dodge_Small_Forward_Roll_Montage` 0.43 s about 3 m, i-frames 0.107..0.49 of the 0.667 s clip | DECISIONS "Dodge: tap quick" |
| Dodge tap, standing (no direction input) | Turns 180 degrees away from the camera and rolls (`bBackwardWithoutInput`, `BackwardTurnRate` 1800). The pack has no backstep clip | `RPGDodgeTiming.h:74-82` |
| Dodge double tap | `bDoubleTapLongRoll` defaults false; second tap selects quick again. The pack ability may buffer or drop it while a dodge is active. | `RPGDodgeTiming.h`, `RPGDodgeTiming.cpp::OnDodgePressed` |
| Dodge hold | Sprint (pack `GA_PlayerSprint`) | DECISIONS |
| Jump light attack | Empty `AirLightMontage` preserves the pack `FallingAttackMontages` route; when assigned, falling R1 temporarily overrides that array. C-975 PIE saw the optional montage play when runtime-assigned; C-978 later verified ground R1 restoration after air R1 on both routes. | `RPGDodgeTiming.cpp::OnEldenRingLight`; C-975/C-978 |
| Jump heavy attack | Empty `AirHeavyMontage` preserves the pack `StrongAttackMontages` route; when assigned, falling R2 strong temporarily overrides that array. C-975 PIE saw the optional montage play when runtime-assigned; C-978 later verified ground R2 restoration after air R2 on both routes. | `RPGDodgeTiming.cpp::OnEldenRingHeavyTap`; C-975/C-978 |
| Ground light / heavy | Pack attack montage arrays; exact selected montage depends on equipped ability data. | `RPGDodgeTiming.cpp::TickEldenRingInput`; pack ability data |
| Gamepad R1 / R2 | R1 press = light; R2 tap (<0.35 s) = strong; R2 hold (0.35 s) = charged. Lead's pie4 observed the light, strong, and charged montage paths. | C-944 input-map read-back; C-945 `pie4` (5/5) |

Canonical gamepad mapping: R1 `Gamepad_RightShoulder` -> `IA_ER_Light` -> light on press; R2 `Gamepad_RightTrigger` -> `IA_ER_HeavyTap` tap -> strong, and hold -> charged. C-944/C-945 and `ER_INPUT_DUMP/update2/editor_raw.log` establish the mapping; C-975 confirms grounded R1/R2 remain on pack routes and optional air routes played when assigned at runtime. The restore-after-air probe is `Scripts/Editor/pie_er_air_restore.py`. See `AA_C31_C34_INPUT_TIMING_AND_FEEL_AUDIT.md` for timing evidence and limits.

With optional montage fields empty in saved assets, standing tap and air attacks retain pack behavior. C-975's runtime-only PIE assignment exercised air-specific montages; it did not change saved defaults.

## 2. Target (Elden Ring behaviour, owner's wording)

1. Dodge tap WITH direction input: roll that direction (today's quick roll is acceptable).
2. Dodge tap WITHOUT direction input: a BACKSTEP: a short hop straight backward that keeps the character facing the same way (no turn, no roll). Shorter and lower i-frames than a roll.
3. Dodge hold: sprint (unchanged).
4. Jump light attack: its own clip (an airborne diagonal slash), not the ground light.
5. Jump heavy attack: its own clip (an overhead plunge that lands with the impact), not the ground heavy.
6. Light and heavy ground attacks keep their own clips (already distinct); no change.

Out of scope until the owner asks: two-handing, crouch, mounted combat, new weapons, spell casting, lock-on strafe rework.

## 3. Animation deliverables for Antigravity (Blender)

Common rules: UE mannequin skeleton used by `SK_CombatMannequin` (reuse the export/import path in `Docs/BossCombatReview/Execution/Antigravity/AG10_IMPORT_STANDARD.md`; the pack's own clips can be exported with `Scripts/Editor/export_reference.py` as the rig reference). 30 fps. In-place poses WITH root motion on the root bone for the backstep (the pack dodge uses root motion). Name clips exactly as below. Each clip ships with a short note of frame numbers for the notifies the Lead will add in the Editor.

| ID | Clip | Length | Root motion | Notify frames to report |
|---|---|---|---|---|
| ER-A1 | `Backstep_Back` | 0.40 to 0.50 s | about 180 to 220 cm straight back (opposite the rig's forward axis, as the pack's root motion defines it; facing unchanged) | i-frame window (target 0.05 to 0.28 s), input buffer open, recover end |
| ER-A2 | `Attack_Air_Light` | 0.50 to 0.65 s | none (the character is airborne) | hit window start/end, recovery |
| ER-A3 | `Attack_Air_Heavy_Plunge` | 0.75 to 0.95 s | none; the pose must read correctly when the character lands mid-clip | hit window (start of the downswing to the landing), landing impact frame |

Quality bar: no foot sliding on the backstep, no self-intersection of the sword with the body, clean first and last frames that blend with the sword idle and the fall loop. AG attaches a Blender look render (the pack's `look` workflow) of each clip as evidence; the owner approves the feel before the Lead wires it. Anything that is a guess about timing is labelled PROPOSAL.

## 4. Code and Editor work (Lead and Codex)

| ID | Owner | Work | Status |
|---|---|---|---|
| ER-C1 | Lead | `URPGDodgeTiming`: optional `BackstepMontage`; no-direction tap selects it when assigned and does not turn the pawn | Plumbing written; ER-A1 montage exists (A-588), owner video review and saved-field assignment remain pending; live proof remains Lead-owned |
| ER-C2 | Codex | Pure rule header + tests: "tap with/without direction input" decision, repeated backstep taps, roll vs backstep stamina note (stamina cost stays the pack's) | proposal, tests offline |
| ER-C3 | Lead | Optional `AirLightMontage`/`AirHeavyMontage` route on falling R1/R2 | Source plumbing, C-975 runtime-only route proof, and C-978 post-air ground R1/R2 restoration proof exist; owner review and saved-field assignment remain pending |
| ER-C4 | Lead | Hand-test sheet for the owner: tap standing, tap moving, double tap, hold, jump light, jump heavy | after ER-C1/C3 |

Rules for the code: new data fields optional with defaults equal to today (C-883 / C-871 checklist), one change per build, suite baseline 478 must stay green.

## 5. Open questions for the owner (each yes/no, default shown)

1. Should a double tap while standing also give a second backstep (Elden Ring does) instead of the full roll? Default: yes; current `bDoubleTapLongRoll` default is false. A second activated backstep is still pending approved/imported ER-A1 and PIE proof.
2. Should the moving roll stay the 0.43 s quick roll? Default: yes (the 3.2 m roll distance rule stays).
3. Should the stamina cost of the backstep be lower than the roll? Default: same cost (pack ability), revisit after the hand test.
