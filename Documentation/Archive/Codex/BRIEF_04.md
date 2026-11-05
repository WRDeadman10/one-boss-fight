# Codex Brief 04: improve the M14 balance bot (G3-6) and quiet the docs checker

From Claude via the owner. You edit files only; you do NOT run the editor, a build or PIE. Claude runs your version in the editor, validates your report by evidence and writes Brief 05.

## Validation of Report 03
Accepted. I opened the cited quotes: the ten hand findings are real (nine fixed in the docs now, KI-032 closed as superseded by the weapon attack table); one checker finding was a false positive (TEST_PLAN line 109 "16/16" counts automation tests, not `pie_hit_intake`). Noise to remove in section 2.2.

## 1. Context
Read `AGENTS.md`, `Documentation/PROJECT_STATE.md` ("Team protocol"; the claims table), `Documentation/M14_FIGHT_NOTES.md` fully (what the bot does, sections 7 weak points, 10 reviews and OPEN list, 11 first runs), `Scripts/Editor/pie_build_fight.py`, `Source/OneBossFight/Player/RPGAttackTracker.cpp` (real move timings), `RPGDodgeTiming.*`, `RPGIFrameMonitor.*`, `RPGBossStagger.cpp` (riposte rules), `RPGBossShockwave.h`, `Documentation/TEST_PLAN.md` (dodge, iframes, riposte, leap wave rows).
Facts from the first four runs (all Strength, no win): the bot lands about 16 health per Light hit (Strong 22.4, Charged 25.6), threw 1 to 2 heavy swings in 420 s, three runs took no damage and never broke posture or riposted, phase two came late (190 to 268 s), one run with a stance break and a riposte (100 health) came closest (boss 51 of 500 left at 240 s). The boss has 500 health, posture 100 (breaks in three Strength jump heavies), the player 120 health.

## 2. Deliverables
1. CLAIM: `Scripts/Editor/pie_build_fight.py` and `Documentation/M14_FIGHT_NOTES.md` are yours for this brief (Claude does not touch them until you report). Improve the bot, keeping the structure, the 10 sanity checks and the RESULT line, per the OPEN list of section 10 of the notes:
   a. Heavy openers: for Strength prefer the jump heavy / strong on stagger and on long recoveries so posture breaks (3 jump heavies = 114 posture), and use the Light only to fill; for Dex the three tap Light chain; Starter the strong then light. The hyperarmor window of the Strength heavy swings is authored (0.352 to 0.618 s of the montage): the bot may use it to trade a hit for a heavy.
   b. Dodge geometry: dodge close attacks (A1, A1b, A3a, A3b) towards the flank or forward instead of sideways at 350 cm, so the bot stays within about 260 cm; lower `SPACING_MAX` accordingly; on every Recovery close in and throw one opener whether or not the estimate fits (the old fit test skipped most openings), then dodge.
   c. Poke while the boss is neutral and the bot is in range with stamina above the reserve.
   d. A6 leap and wave: jump over the wave instead of the backward roll that ends after the i-frames (read `RPGBossShockwave.h`, `pie_leap_wave.py` and `LEAP-01` in the TEST_PLAN for the proven jump timing).
   e. More logging: one `decide` line about every 0.5 s while a tracked attack runs (boss move, phase, position, distance, decision), and at the end of a dodge: bot distance, off-front angle, position change, mode, boss yaw.
   f. Keep the INCONCLUSIVE evidence flags; add one when the bot throws fewer than 3 heavy swings with a heavy-opener build.
   Every Python name must be a UFUNCTION in a header (snake_case) or already used elsewhere in the file; read the header before adding a call. No `set_editor_property` on components. No cheating: no heal, no hold, no teleport after the wake.
2. `Scripts/CheckDocs.py` (yours from Brief 03): remove the noise I found: skip the probe, look and diagnostic scripts in the "not in the gate and not documented" check by an explicit allow-list at the top of the file (list the names you allow and why), skip backtick paths that contain `NN`, `*` or `..`, and do not compare the totals of rows whose text says "automation tests". Run it and paste the new output in the report.
3. `Documentation/Codex/REPORT_04.md`: what you changed in the bot (by section a to f, with line numbers), which behaviours you could not verify, the three places you expect the new version to misbehave first, the checker output.

## 3. Rules
No commit or push, no git command that changes the working tree (about 240 uncommitted changes must survive), no editor, build, package or game run. Syntax-check with `python -I -c "import ast;ast.parse(open(path,encoding='utf-8').read())"`. Never claim a behaviour was observed: you cannot run it. Keep your edits small and localised so the diff reads cleanly.

## 4. Acceptance criteria (Claude checks)
1. Only the named files changed. The bot parses and still ends with `RESULT n/10` on every path (Claude greps the exits).
2. Every new name exists (Claude runs `Saved/check_names.py` style grep against the headers).
3. Claude runs the three build rows in the editor and reads the metrics: the acceptance for the bot is not "wins" but "plays as designed": heavy swings thrown, posture breaks seen, fewer skipped recoveries, no stuck loops; failures go into Brief 05.
4. The checker output shrinks to real findings.

## 5. Report
`Documentation/Codex/REPORT_04.md`. Tell the owner "Report 04 is ready".
