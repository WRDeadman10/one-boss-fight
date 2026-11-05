# Codex Brief 07: per-event balance data from the bot and a collector

From Claude via the owner. You edit files only; you do NOT run the editor, a build, a package or the game. Claude runs the bot rows in the editor and validates your report by evidence.

## Validation of Report 06 and a correction
Accepted. Only the three named files and the mailbox changed; the script runs; the calibration is honestly labelled as fitted, and you found the data contradictions I would otherwise have missed (the Starter weapon total of 418 against 6 Light + 3 Strong at 16 and 22.4 = 163; Strength riposte impacts 212 against 3 x 100). CORRECTION: my Brief 06 listed Starter light 16 and strong 22.4 "as measured": that was wrong, nobody measured the Starter. Your own note from the earlier runs ("Starter: 10 Lights at 41 each") suggests the Starter light does about 41 health per hit, which would explain the 418. This is why the next step is data, not more modelling. The soak runner (Brief 01) now runs in the editor; I am fixing its first findings.

## 1. Goal
Make every bot run produce per-event data that settles those contradictions, and a collector that turns several runs into one table per build. No balance values change in this brief.

## 2. Deliverables
1. CLAIM: `Scripts/Editor/pie_build_fight.py` (yours again for this brief; Claude does not touch it). Add per-event log lines with the prefix `[BuildFight] EVENT`, one per event, machine readable (`key=value` pairs, one line each): (a) every player hit that lowered the boss's health: time since the wake, the hit kind from the hit intake record, the weapon style, boss health before and after, damage = before minus after, whether a riposte execution, a bleed proc or a shared frame was running; (b) every riposte impact: damage taken from the health drop, the boss health before and after; (c) every bleed proc: damage; (d) every posture change from the player's hits: pool before and after; (e) player stamina every 1 s and at every swing and dodge; (f) every hit the player took: time, move, damage; (g) at the end one line `[BuildFight] RUN_SUMMARY` with the build, a run id (timestamp plus 8 hex), the outcome, fight seconds and the sums of the events by source (weapon, riposte, bleed, other). The health accounting must close: the sum of the per-event damages equals the total health lost, and `other` holds the remainder: if it is not zero, say so in the summary line. The existing METRIC lines stay.
   Read how the bot already derives `hp_hit`, `hp_bleed`, `hp_rip` (search `hp_hit` in the file) and say in the report why Starter showed 418 weapon damage for 9 hits (is `hp_hit` the remainder after bleed and riposte, which would hide a mis-attribution?). If the existing accounting is wrong, fix it and say so.
2. NEW: `Scripts/CollectBalanceRuns.py` (Python 3.10, standard library only): reads `Saved/Logs/OneBossFight.log` (and, optionally, the backup logs `Saved/Logs/OneBossFight-backup-*.log` with `--all-logs`), parses the `[BuildFight] EVENT` and `RUN_SUMMARY` lines, writes one JSON per run to `Saved/BalanceRuns/<run id>.json` (create the folder), and prints per build: the number of runs, fight seconds (min, median, max), damage per hit by kind (mean, min, max, n), riposte impact damage per riposte (mean, n), bleed proc damage, stamina minimum, hits taken, outcome counts; plus a list of runs whose accounting did not close. It must tolerate a log that contains no EVENT lines (print "no runs"). It must not modify the logs.
3. SMALL EDIT in `Scripts/RunDrivers.ps1` (claim it for this one edit): give the balance rows (`$balance`) a `-Repeat n` switch: `-Repeat` is a new script parameter (default 1) that runs each selected row n times in a row; the table at the end prints one line per run. Do not change anything else in the file; keep the PowerShell 5.1 syntax (check with the parser).
4. `Documentation/Codex/REPORT_07.md`: what you changed (line numbers), the EVENT line format with one example line per type, the answer about the 418, what you could not verify, the three places you expect trouble.

## 3. Rules
No commit or push, no git command that changes the working tree (about 240 uncommitted changes must survive), no editor, build, package or game run. Python names you add must exist as UFUNCTIONs in a header (read the header) or already be used in the file. No `set_editor_property` on components. You may syntax-check Python (`ast.parse`) and PowerShell (`[System.Management.Automation.PSParser]::Tokenize`), and run `python -I Scripts/CollectBalanceRuns.py` against the existing logs (it will find the old METRIC lines only: say what it printed). Never claim you observed a run.

## 4. Acceptance criteria (Claude checks)
1. Only the named files changed (plus the report). The bot still ends with `RESULT n/10` on every path.
2. Claude runs three runs per build with `-Repeat 3` and the collector, and checks that the accounting closes in every run and that the Starter question is answered by data.
3. The collector's table matches a hand count of the EVENT lines of one run.

## 5. Report
`Documentation/Codex/REPORT_07.md`. Tell the owner "Report 07 is ready".
