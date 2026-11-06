# Elden Ring style player controls: spec and task split (owner request 2026-11-06)

Owner request (chat, 2026-11-06): "full player control like Elden Ring with the same animation. A single press of the dodge button rolls in the current game; in Elden Ring it does not, it only moves away while standing. Jump attack, light attack and heavy attack have different animations." Antigravity is available for Blender animation.

Status: SPEC + PROPOSAL. Nothing below is built yet except where marked. Scope is the single-player duel only (owner 2026-10-29). No pack asset is deleted or recreated; pack assets are edited in place only where a precedent exists (`air_light_attacks.py`).

## 1. What the game does today (measured, cited)

| Control | Today | Source |
|---|---|---|
| Dodge tap, moving | Quick roll, `Dodge_Small_Forward_Roll_Montage` 0.43 s about 3 m, i-frames 0.107..0.49 of the 0.667 s clip | DECISIONS "Dodge: tap quick" |
| Dodge tap, standing (no direction input) | Turns 180 degrees away from the camera and rolls (`bBackwardWithoutInput`, `BackwardTurnRate` 1800). The pack has no backstep clip | `RPGDodgeTiming.h:74-82` |
| Dodge double tap | Full roll, `Dodge_To_Idle_Montage` 0.92 s about 5 m | `RPGDodgeTiming.h:25` |
| Dodge hold | Sprint (pack `GA_PlayerSprint`) | DECISIONS |
| Jump light attack | The ground light clip `Attack_PrimaryA_Montage` copied into `FallingAttackMontages` of the weapon ability | DECISIONS "Jump attacks" |
| Jump heavy attack | The ground heavy clip `Ability_E_Anim_Montage` played in the air | same |
| Ground light / heavy | `Attack_PrimaryA/B/C` chain / `Ability_E_Anim_Montage` | pack |

So the owner is right on both points: standing tap is a roll (turn and roll), and the two jump attacks reuse the ground clips.

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
| ER-C1 | Lead | `URPGDodgeTiming`: new optional `BackstepMontage` (soft pointer, empty = today's behavior). A tap with no direction input and `BackstepMontage` set selects the backstep clip and does NOT turn the pawn; a tap with direction input is unchanged | plumbing WRITTEN 2026-11-06 (`BackstepMontage`, `BackstepPlayRate`, `GetBackstepCount`, stage "Backstep"; dormant while the clip is empty); BUILD-235 pending; live proof needs the ER-A1 clip |
| ER-C2 | Codex | Pure rule header + tests: "tap with/without direction input" decision, repeated backstep taps, roll vs backstep stamina note (stamina cost stays the pack's) | proposal, tests offline |
| ER-C3 | Lead | `Scripts/Editor/air_attack_clips.py` (modelled on `air_light_attacks.py`): assigns `Attack_Air_Light` to `FallingAttackMontages` and `Attack_Air_Heavy_Plunge` to the strong-attack path used by `air_heavy_selector.py`; PIE proof `pie_air_attack.py` extended to assert the new montage names | after ER-A2/A3 |
| ER-C4 | Lead | Hand-test sheet for the owner: tap standing, tap moving, double tap, hold, jump light, jump heavy | after ER-C1/C3 |

Rules for the code: new data fields optional with defaults equal to today (C-883 / C-871 checklist), one change per build, suite baseline 478 must stay green.

## 5. Open questions for the owner (each yes/no, default shown)

1. Should a double tap while standing also give a second backstep (Elden Ring does) instead of the full roll? Default: yes.
2. Should the moving roll stay the 0.43 s quick roll? Default: yes (the 3.2 m roll distance rule stays).
3. Should the stamina cost of the backstep be lower than the roll? Default: same cost (pack ability), revisit after the hand test.
