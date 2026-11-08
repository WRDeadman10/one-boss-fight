# Elden Ring style player controls: spec and task split (owner request 2026-11-06)

Owner request (chat, 2026-11-06): "full player control like Elden Ring with the same animation. A single press of the dodge button rolls in the current game; in Elden Ring it does not, it only moves away while standing. Jump attack, light attack and heavy attack have different animations." Antigravity is available for Blender animation.

Status (C-1060/C-1063): owner approved `AM_ER_Backstep_Mixamo_V2` as the default backstep. The earlier hand-built `AN/AM_ER_Backstep_Back` is rejected and remains unreferenced in Content. A-640/C-1059 report a 0.567 s two-foot hop, root-bone travel, and the owner-approved showcase clip. Lead BUILD-260 passed 485/485 and no-assignment PIE confirms V2; reps 2/3 moved 84/88 cm without a snap. C-1063 BUILD-261 passed 485/485 but preload/map priming did not fix the first post-draw press (0 cm; later reps 96.6/97.8 cm). Default-wired standing and moving acceptance remains open pending activation diagnostics and fresh Lead probes (KI-199/KI-196). Earlier C-1004 runtime-assigned AirLight/AirHeavy and C-1042 default-wired attack proof retain their own scopes; KI-193 package gate remains open. Scope is the single-player duel only. No pack asset was deleted or recreated.

## 1. Last measured behavior and current Source defaults

| Control | Today | Source |
|---|---|---|
| Dodge tap, moving | Quick roll, `Dodge_Small_Forward_Roll_Montage` 0.43 s about 3 m, i-frames 0.107..0.49 of the 0.667 s clip. C-980's retained backstep probe logged 486.8 cm/s legacy and 474.2 cm/s data with last input `(-1,0,0)` before press, then the quick roll. Earlier zero-speed injected samples are invalid. | DECISIONS "Dodge: tap quick"; `P_C980_BACKSTEP/probe_legacy_lines.txt` and `probe_data_lines.txt`; KI-196 |
| Dodge tap, standing (no direction input) | Source default is `AM_ER_Backstep_Mixamo_V2`. Lead no-assignment PIE shows reps 2/3 moving backward 84/88 cm with no snap; first press after R2 draw failed 2/2 and is under test-first hotfix verification. | C-1060/C-1061; `RPGDodgeTiming.cpp`; KI-199; `Documentation/Boss/AN_C01_C05_FIRST_DODGE.md` |
| Dodge double tap | `bDoubleTapLongRoll` defaults false; second tap selects quick again. The pack ability may buffer or drop it while a dodge is active. | `RPGDodgeTiming.h`, `RPGDodgeTiming.cpp::OnDodgePressed` |
| Dodge hold | Sprint (pack `GA_PlayerSprint`) | DECISIONS |
| Jump light attack | BUILD-255 defaults `AirLightMontage` to `AM_ER_Attack_Air_Light`; falling R1 temporarily overrides the pack array. C-1004's runtime-assigned two-route hit proof precedes this default wiring; fresh PIE remains due. | C-1021 / `RPGDodgeTiming.cpp:43`; C-1004 |
| Jump heavy attack | BUILD-255 defaults `AirHeavyMontage` to `AM_ER_Attack_Air_Heavy_Plunge`; falling R2 temporarily overrides the pack array. C-1004's runtime-assigned two-route hit proof precedes this default wiring; fresh PIE remains due. | C-1021 / `RPGDodgeTiming.cpp:44`; C-1004 |
| Ground light / heavy | Pack attack montage arrays; exact selected montage depends on equipped ability data. | `RPGDodgeTiming.cpp::TickEldenRingInput`; pack ability data |
| Gamepad R1 / R2 | Intended map: R1 press = light; R2 tap = strong; R2 hold = charged at the 0.35 s mapping. C-971's latest PIE saw Ability_E at 0.34/0.35 s on both routes and at 0.36 s on data, while legacy chose ChargedAttack; at 0.70 s both chose ChargedAttack. The near-boundary route split remains unresolved and values are tick-bounded, not device latency. | Intended mapping C-944/C-945; latest route observations and limits C-971 / `P_C971_ERLATENCY/SUMMARY.md`; KI-192 |

Canonical intended gamepad mapping: R1 `Gamepad_RightShoulder` -> `IA_ER_Light` -> light on press; R2 `Gamepad_RightTrigger` -> `IA_ER_HeavyTap` tap -> strong, and hold -> charged. C-944/C-945 and `ER_INPUT_DUMP/update2/editor_raw.log` establish mapping intent; C-971 qualifies the observed 0.36 s boundary behavior. C-975 confirms grounded R1/R2 remain on pack routes and optional air routes played when assigned at runtime. C-978 confirms ground R1/R2 array restoration after each air case. The restore-after-air probe is `Scripts/Editor/pie_er_air_restore.py`. See `AA_C31_C34_INPUT_TIMING_AND_FEEL_AUDIT.md` for timing evidence and limits.

All four ER action fields have nonempty Source defaults; the backstep field was replaced with the owner-approved V2 in BUILD-260. Clearing an optional field still restores the pack fallback. Attack runtime-assignment results before BUILD-255 do not prove newly default-wired gameplay; the first-dodge-after-draw failure also remains open until Lead's post-hotfix PIE.

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
| ER-A1 | `Backstep_Mixamo_V2` (owner-approved; C-1060) | 0.567 s | Root-track travel -156.75 cm backward Y; Lead PIE reps 2/3 move 84/88 cm without pop; facing unchanged | A-640 readback: i-frames 0.091+0.323 s, InputBuffer 0.198+0.369 s; 0 SetDesiredRotation |
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
