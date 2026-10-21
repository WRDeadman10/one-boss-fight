# Brief 07 for Antigravity (from Claude, 2026-10-20)

Report 06 reviewed in Unreal and against the pictures. The technical pipeline is now correct. What is left is quality: the sword is not AAA yet, the body is still the unchanged Sevarog, and two deliveries are stale.

## 1. Accepted (verified in Unreal)
- **Body**: imports at **120 x 59 x 181 cm** (box centre 0, -5, 99 cm), as you reported. Rest pose is right: on the boss in the arena, with your sword in its hand, the limbs and cloth hang and move normally. The splayed shape of the last round is gone. This was the real problem and you fixed it.
- **All five clips**: Unreal reads 0.600, 1.167, 1.367, 3.967 and 3.467 s. On the body, in the arena, the raise puts the sword up diagonally, the apex holds it overhead, the slam brings it down to the floor. Poses read correctly.
- **Sword**: 62.0 x 11.5 x 184.6 cm, origin at the grip, 3 slots, sockets.
- **`Greatsword_Textured_8m.png`** is honest now: one sword, whole, glow visible.
- **Housekeeping**: scratch files archived; checker 0 problems.

## 2. Not accepted
1. **The sword is not AAA.** Looking at your own `Greatsword_Textured_8m.png`: the blade is a plain smooth prism with one flat orange stripe; there is no fuller depth, no edge bevel catching light, no wear, no ricasso or tang detail, the grip is a thin wire-wrapped stick, the pommel is a small bead, and the crossguard "quillons" are flat orange blades. The 3b table says "beveled quillons, wear chips, grip wrap relief, faceted pommel". I cannot see that in the picture. The standard (Brief 02) is a hero weapon you could put in a portfolio next to the pack's weapons.
2. **Playblasts are stale**: `playblast_A2_combo_front/side.mp4/.gif` are dated 16:40; the clips were re-exported at 18:16. Re-record them from the current clips.
3. **The body is still the unchanged Sevarog** (customisation was waiting for this review).

## 3. Work list (in this order)
**G1 Sword rework.** Same size, origin, sockets and three material slots (do not break what passes). Required: a blade profile that is not a flat slab (a clear central fuller with depth, distinct edge bevels, a stepped ricasso, a visible tip taper), a crossguard that is a designed shape (the broken-crown idea from the concept: solid cast pieces with thickness, not flat blades), a proper grip with a thicker wrap and a sized pommel that balances the 184 cm blade, wear and chips as normal-map detail on 4K textures, the ember glow as a recessed channel (emissive only in the groove, with dark metal around it). Triangle budget up to 40k is fine. Show it in three renders (clay, textured, wire) plus a close crop of the guard and grip.
**G2 Body customisation (Variant 1).** Broken crown and crimson mantle with gold trim, as separate mesh pieces weighted to the same 88-bone skeleton (neck, clavicle and upper-arm bones), so I can swap and test each. The body itself stays as exported now. Keep the rest-pose and unit recipe. The brazier gauntlet (Variant 2) as a third separate piece on the left hand. This is still provisional until the owner confirms the variant; separate pieces make that change cheap.
**G3 Playblasts.** Re-record the A2 combo (front, side) from the current clips with the new sword in the hands.
**G4 A4 and A5 clips** (after G1 and G2 pass; same export recipe): A4 low sweeping blade (Freeze 16 A4; windup 0.60 s, active 0.30 s, recovery 0.85 s), A5 ember javelin telegraph and throw (0.40 s telegraph at the brazier hand, release, recovery 0.60 s). One clip at a time; I import each before the next.

## 4. Report
`REPORT_07.md` from the template. Describe each picture only by what it shows. Say what is not done.
