# Elden Ring reference video study (owner videos, 2026-11-06)

Source: two owner-supplied clips in `C:\UnrealProject\Ref\` (`1.mp4` 121 s, `2.mp4` 62 s, 1918x1078, 30 fps): a third-party PS5 recording of the Elden Ring opening cave (tutorial area), screen-captured from a browser. Reference only: the files stay OUTSIDE the repository and are never committed or redistributed. Usable gameplay: `1.mp4` 0:00-1:57 (1:58 onward is an unrelated advert), `2.mp4` 0:00-0:58 (0:59 onward is the browser page).

**Timing caveat:** the recording shows the browser's playback-speed menu switched from 1.00x to 1.25x at `1.mp4` 0:13-0:15. Durations measured from these clips after that point are probably 1.25x fast: multiply by 1.25 for real game time. Every number below is labelled REFERENCE (approximate, 30 fps capture), never a target by itself.

## 1. Controls the videos teach (read from the on-screen tutorial panels and prompts)

| PS5 input | Action (game's own wording) | Where in the video |
|---|---|---|
| Left stick | Move (walk/run) | throughout |
| Left stick + Circle (tap) | **Dodge roll** | `1.mp4` 0:36 "Dodging" panel; roll at 0:40.7 |
| Circle (tap, no direction) | **Backstep** ("You can avoid enemy attacks with a dodge roll or backstep. Both of these actions consume stamina.") | 0:36 panel |
| Hold left stick + Circle | **Dash** (sprint) | 0:51-1:00 prompt |
| Cross | Jump | 0:47-0:50 prompt |
| R1 | Attack (right hand / two-handed armament) | 0:22 prompt |
| R2 | Strong attack | 0:26 prompt |
| Hold R2 | **Charge attack** | `2.mp4` 0:12 "Stance-Breaking" panel |
| R2 while jumping | **Jump attack** ("Charge attacks and jump attacks make it particularly easy to break an enemy's stance") | `2.mp4` 0:12 panel; jump attack at 0:17 |
| L1 | Guard (shield; "Guarding consumes stamina. If your stamina runs out, your stance will be broken") | `1.mp4` 0:29 "Guarding" panel |
| R2 immediately after blocking | **Guard counter** ("make it easy to break an enemy's stance") | `2.mp4` 0:37 "Guard Counters" panel; used at 0:44 |
| L2 | Skill (with the shield equipped the skill is "Parry"; two-handing the sword shows "Square Off") | `1.mp4` 1:34 "Skills" panel; HUD label |
| R3 | Reset camera, lock on / remove target | 0:20 prompt |
| Right stick while locked on | Change target | 1:19 prompt |
| R1 near a back-turned enemy | Critical hit (backstab) | `2.mp4` 0:03 prompt; backstab at 0:05.4 |
| R1 on a stance-broken enemy | Critical hit (riposte) | `2.mp4` 0:18.8 and 0:46 |
| L3 | Crouch / stand up (stealth; extra damage on an unaware enemy) | `1.mp4` 1:52 "Crouching" panel |
| Triangle + L1/R1 | Wield with two hands (+50 % effective strength) | 1:03 "Wielding Armaments" panel |
| D-pad right / left | Switch right / left-hand armament | 1:03 panel |
| Square | Use item (flask of crimson tears, HUD bottom left) | HUD |

## 2. What the animations show (REFERENCE timings, see the caveat)

| Move | What is seen | Approx. duration on video |
|---|---|---|
| Dodge roll (`1.mp4` 0:40.7) | low forward-diagonal roll with dust, shield stays on the arm, character faces the roll direction, recovers into a run | about 0.6 s on video (about 0.75 s real) |
| Backstep | named in the tutorial but NOT clearly performed in either clip; the clip cannot be used to time it | none |
| R1 chain (`1.mp4` 0:22.5-0:25) | two one-handed slashes, each with a step forward; the second follows within about 0.75 s | about 0.5 s per swing |
| R2 strong attack (0:27.0-0:28.3) | sword raised high over the shoulder, heavy downward diagonal with a big step; clearly different from R1 | about 1.2 s with recovery |
| Jump attack (`2.mp4` 0:16.9-0:17.5) | running jump, sword lifted overhead in the air, downward slam on landing; the hit staggers the enemy | air time about 0.5 s; landing slam to recovery about 0.6 s |
| Stance break + critical (`2.mp4` 0:17.3-0:19.4) | enemy drops to one knee after the jump attack; the player steps in and stabs (big blood burst, camera shake), long recovery | critical about 1.0 s, recovery about 1.0 s |
| Guard then guard counter (`2.mp4` 0:43.75-0:46.25) | shield block (sparks), then a wide forceful counter swing; a yellow stance bar appears under the enemy health bar and fills; the enemy breaks and gets a critical | block to counter about 0.75 s |
| Backstab (`2.mp4` 0:03.2-0:06.7) | crouch-walk through grass, stand up behind the enemy, grab and stab through the back | critical about 0.7 s, recovery about 0.7 s |
| Dash (`1.mp4` 0:51-0:53) | sprint with the cape trailing, arms back | n/a |
| Crouch (`2.mp4` 0:03.2-0:05) | low crouched walk | n/a |

HUD notes: boss/enemy health bar at the bottom centre; the enemy STANCE bar (yellow, under the health bar) appears once stance damage starts; the skill name (Parry / Square Off) sits above the equipment slots at the bottom left.

## 3. Our game today against the reference (source-checked)

| Control | One Boss Fight today | Gap |
|---|---|---|
| Dodge roll with direction | yes: quick roll on tap, long roll on double tap (`RPGDodgeTiming`) | ER has no double-tap long roll (keep or drop: owner question) |
| Backstep (tap, no direction) | turn 180 degrees and roll; backstep plumbing is in (BUILD-235/237) and waits for the ER-A1 clip | **clip needed (ER-A1, in progress)** |
| Dash (hold dodge) | yes (pack sprint) | none |
| Jump | yes (pack) | none |
| R1 light chain | yes (pack `Attack_PrimaryA/B/C`) | none |
| R2 strong attack | yes (pack `Ability_E`) | none |
| Hold R2 charge attack | the pack has `GA_Player_ChargedAttack` and its own input `IA_ChargedAttack`; whether a hold of the heavy key reaches it is UNVERIFIED (no project doc records it) | **Editor check of the binding**, then map hold-heavy to the charged attack if missing |
| Jump attack | light/heavy in the air reuse the ground clips | **ER-A2 / ER-A3 clips (Antigravity)**; ER's main jump attack is the R2 overhead slam, so ER-A3 matters most |
| Guard (L1) | yes (pack `GA_PlayerGuardBlock`) | none |
| Guard counter (R2 right after a block) | does not exist | **new: ability + clip + stance damage** (owner question) |
| Parry (L2 with shield) | yes (`RPGPlayerParry`, opt-in features, stamina cost) | none |
| Critical on a stance-broken boss (riposte) | yes (boss posture + `RPGRiposteInput`) | compare the HUD stance bar with the reference (yellow bar under the health bar) |
| Backstab | pack has `GA_Player_BackstabAttack`; whether it can trigger on the Ember Warden is UNVERIFIED | owner question; Elden Ring bosses mostly cannot be backstabbed, so the default is to leave it off |
| Lock-on (R3), change target | lock-on yes (`RPGCameraRig`); only one enemy | none |
| Crouch | pack has `IA_Crouch`; no stealth in a boss duel | skip unless the owner wants it |
| Two-handing, weapon switch, skills | not present | out of scope unless the owner asks (needs a full two-hand animation set) |
| Flask | yes (`RPGFlaskHud`) | none |

## 4. Proposed additions to the ER task list (owner decides 1-3)

1. **Guard counter** (R2 within a short window after a successful block): one new clip from Antigravity (wide forceful swing, about 0.75-0.9 s), a C++ window rule plus test (Codex), stance damage on the boss's posture, PIE proof (Lead). Recommended: YES (it is a core Elden Ring defensive tool).
2. **Hold R2 = charge attack**: wire the pack's charged attack to a hold of the heavy key (Lead, Editor plus a small input rule). Recommended: YES.
3. **Drop the double-tap long roll** so the dodge matches Elden Ring exactly (tap = roll or backstep, hold = dash). Recommended: YES, after the backstep is in.
4. Not proposed: crouch, two-handing, weapon switching, skills (no gameplay value in a one-boss duel without new animation sets).

For Antigravity: use these clips for pose and silhouette only (ER-A1 backstep cannot be timed from them; ER-A3 plunge should follow the `2.mp4` 0:16.9-0:17.5 overhead slam). Keep the 1.25x caveat on any number taken from them.
