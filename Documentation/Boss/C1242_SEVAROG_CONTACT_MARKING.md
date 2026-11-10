# C-1242/C-1245: Sevarog contact marking (Lead visual marking)

**Status:** visual marking from captured frames, by the Lead (Antigravity did not respond to C-1243a or the C-1244 ping). These are design candidates for card timelines, **not** measured trace windows. No asset, card, or runtime value was changed.

## Source and method

- Frames: `D:/FightVideo/sevarog_frames/<clip>/<clip>_<NNN>_<t.ttt>.png`, captured by `Scripts/Editor/pie_sevarog_clip_frames.py` (Lead run C-1243, 206 bright frames, 0 dark; raw log `Docs/BossCombatReview/Execution/Claude/P_C1243_SEVAROGFRAMES/`). These frames are local only and never staged.
- Contact sheets: `D:/FightVideo/sevarog_frames/_sheets/<clip>_sheet.png`. The yellow number is the frame index NNN; time = NNN / 15 s, except the LAST frame of each clip, which the driver clamps to the clip length (the filename time is authoritative). C-1246 correction, found by Codex X-1767: Swing3_Slow ends at 1.700 s and Soul_Siphon at 1.833 s.
- Sampling: 15 Hz, so every value is accurate to about ±0.067 s. The camera is a fixed side view, and facing toward the player is not established from these frames. "Contact" means the frames where the weapon head sweeps through its striking arc (lowest/forward point). An in-game trace and the PIE parity gate must confirm every window before it is used.
- "not visible" means the frames do not show the event. No value was guessed.

## Marking

| Clip (length) | Windup / tell | Commit (last re-aim) | First contact | Last contact | Recovery start | End | What the frames show |
|---|---|---|---|---|---|---|---|
| Swing1_Medium (1.133 s) | 0-3 (0.000-0.200) | 3 (0.200) | 4 (0.267) | 6 (0.400) | 7 (0.467) | 17 (1.133) | 0-2 hammer held across the body, 3 hammer raised overhead, 4-6 fast downward/horizontal sweep low, 7 hammer comes back up, 8-17 settles to the over-shoulder rest. |
| Swing2_Medium (1.133 s) | 0-2 (0.000-0.133) | 2 (0.133) | 3 (0.200) | 6 (0.400) | 7 (0.467) | 17 (1.133) | 0-2 hammer high behind, 3 swinging down, 4-6 low sweep through, 7-8 hammer brought back across, 9-17 recovery to rest. |
| Swing1_FAST_v2 (0.533 s) | 0-3 (0.000-0.200) | 3 (0.200) | 4 (0.267) | 5 (0.333) | 6 (0.400) | 8 (0.533) | The same arc as Swing1_Medium compressed: overhead at 3, sweep 4-5, recovery 6-8. |
| Swing3_Slow (1.700 s) | 0-7 (0.000-0.467) | 7 (0.467) | 8 (0.533) | 10 (0.667) | 11 (0.733) | 26 (1.700) | 0-2 hammer raised horizontally, 3-7 lifted high (7 = peak overhead), 8 slammed into the ground, 9-10 planted, 11-26 a long recovery with the hammer on the ground (big punish window). |
| Ultimate_Swing_120fps (2.633 s) | 0-9 (0.000-0.600) | 9 (0.600) | 10 (0.667) | 13 (0.867) | 14 (0.933) | 40 (2.633) | 0-9 hammer held high overhead (long readable tell), 10-13 the hammer whips around low (fast spinning cleave; full 360 coverage is not provable from one side view), 14-23 follow-through held across the shoulder, 24-40 returns upright to rest. |
| Speedburst (1.267 s) | 0-4 (0.000-0.267) | not visible | none (no weapon strike) | none | 17 (1.133) | 19 (1.267) | A deep forward-lean dash posture, in place (0-4 lean in, 5-16 held, 17-19 recover). Movement must come from the card warp, and the strike from the follow-up Swing1_FAST_v2. |
| Subjugation (2.867 s) | 0-11 (0.000-0.733) | 11 (0.733) | not visible (spell release about 12-13, 0.800-0.867) | not visible | 30 (2.000) | 43 (2.867) | 0-11 left hand raised clawing (cast tell), 12-13 lunges forward and slams the arms down (release), 14-29 crouched hold (channel/snare), 30-43 stands back up. No hammer contact: the damage must come from a spawned ground effect at the release. |
| Soul_Siphon (1.833 s) | 0-3 (0.000-0.200) | 3 (0.200) | not visible (channel 4-19, 0.267-1.267) | not visible | 20 (1.333) | 28 (1.833) | 0-3 brings the hammer forward, 4-19 holds it low and forward (drain channel pose), 20-28 raises it back to rest. No strike: the effect is a channel, not a weapon contact. |

## Candidate card windows (for C-1243b, all to be confirmed in PIE)

- Close swings: Swing1_Medium active 0.267-0.400, Swing2_Medium 0.200-0.400, Swing1_FAST_v2 0.267-0.333.
- Delayed heavy: Swing3_Slow active 0.533-0.667, with the commit at 0.467 and a long recovery (0.733-1.700).
- Signature: Ultimate_Swing_120fps active 0.667-0.867, after a 0.6 s tell.
- Gap closer: Speedburst has no hit window. Use the warp over roughly 0.267-1.133 (the lean-held frames), then chain Swing1_FAST_v2.
- Spells: Subjugation release about 0.800-0.867 and Soul_Siphon channel 0.267-1.267 have no weapon contact. They need the effect/add-on modules listed in `C1239_SEVAROG_DEFINITION_DATA_PLAN.md`.
