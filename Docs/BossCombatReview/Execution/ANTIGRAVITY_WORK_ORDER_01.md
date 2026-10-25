# Work order 01 for Antigravity (from Claude, technical lead), 2026-10-25

Same working style as Codex's work order: work through AG-1 to AG-6 in order in one continuous run, no waiting between packages. Everything is OFFLINE specification and analysis (Blender, Python, image analysis); no Unreal Editor, no asset or pack file changes, no new art or clip delivery yet (nothing past DD-1 is approved), no commit or push. G-4 and G-5 stay denied. All 83 requirements stay required.

## Standing rules

1. Never idle: after one package report (A-n, usual format) start the next. A blocker is only an owner decision or a fact only the editor can give; post it once as DECISION NEEDED or EDITOR NEEDED and continue with the next package.
2. Routine choices are yours; list them under Assumptions with how to reverse them.
3. Every number cites a file and hash or an evidence id (`Claude/Evidence/E-*`), and states its kind: declared intent, offline measurement, engine export, hypothesis. Runtime and visual claims stay UNVERIFIED without a capture.
4. Read the mailbox tail at the start of each package; new messages beat this order. Claude reviews at package boundaries.
5. Write only under `Execution/Antigravity/`.

## Packages

**AG-1: content requirements of the eight former-N/A rows** (QA-008 networking has no content: say so). For HIT-012 boss grab, ANM-003 bounded variable hold, ANM-006 motion warping, DEF-005 guard/parry/dodge, AWR-008 adaptation (tells and feedback), SEL-004 and SEL-008 (readable fallback behaviour): the exact animation clips, montage sections, notify markers (the `AN_CombatEvent` / `ANS_CombatWindow` model of Codex D02 and your contract), sockets or offsets, VFX/audio cues and UI/readability cues needed, with durations in your usual card form (windup, commit, active, recovery, blend), skeleton and retarget assumptions, and an authoring effort estimate per clip (small/medium/large with the reason). Read `Codex/D05_CONDITIONAL_ROWS_COSTING.md` first and align the content columns with it; flag any D05 content assumption you cannot support. Output `Antigravity/AG1_CONTENT_REQUIREMENTS.md`.

**AG-2: the second-boss canary content spec** (Codex D02 section "Second-boss, weapon and build canary"). A complete content brief for one boss that is clearly NOT Boss01 and needs no new combat code: look and name, skeleton choice (reuse a compatible skeleton), at least three moves that exercise a weapon sweep with two windows or an explicit follow-up, a projectile release and a radial or planar effect, one branch with success/failure/default recovery, two HP-threshold phases with a transition, dormant/wake/stagger/death/riposte clips (reuse allowed), one new weapon and a fourth player build (art needs, action table inputs, icon). For every move: the card, the notify placements, the sockets or offsets, and the data fields it fills. Mark canary numbers as test data. Output `Antigravity/AG2_CANARY_CONTENT_SPEC.md`.

**AG-3: telegraph and readability specification for P1** (design input only, no tuning). For each live move (A1, A1b, A2, A3a, A3b, A4, A5, A6, Mid01, sprint, retaliation, wake, roar, stagger): the first perceptible cue, how it is made visible (pose, VFX, audio, camera, UI), its timing against the declared and the engine timeline (use `Claude/Evidence/exports/montage_notifies_2026-10-25.txt` and the movesheets), the accessibility rule (not colour only, reduced effects), and the questions only the owner can answer (feel). Mark measurable acceptance tests that a capture or a driver could check. Output `Antigravity/AG3_TELEGRAPH_READABILITY_SPEC.md`.

**AG-4: the production shockwave cue spec (RV-01 / G01)**: what the A6 ring needs as a Shipping-visible effect (band 180 cm, speed 1000 cm/s, 200 to 1100 cm), a Niagara or material approach that is data-parameterised (width, speed, colours, audio), the jump-counterplay readability (jump clearance 50 cm), the anchoring to the production damage band so the visual cannot disagree with the query, a test plan (debug-off capture in a packaged build; the editor cannot show it: `RPGBossShockwave.cpp:164-166`), and the asset list. Output `Antigravity/AG4_SHOCKWAVE_CUE_SPEC.md`.

**AG-5: A2 authored trio integration spec** (VIS-02): how `AN_Boss01_A2_Raise`, `ApexHold` and `Slam` become one montage with a bounded, data-declared hold (sections, loop point, length bounds, the exit seam), the notify placements (commit, release, damage window, recovery), how the stable hold relates to ANM-003, what the pack's `GS_ChargedAttack` currently does differently (E-005, E-002-10), and the parity rule: DD-1 changes nothing, this is a later P-phase proposal. Output `Antigravity/AG5_A2_INTEGRATION_SPEC.md`.

**AG-6: review of Codex's design set** as it appears (`Codex/D07_*`, `D09_*`, `D10_*`): content, animation and readability consequences only; post findings as an A-n with file:line. If nothing new exists yet when you reach it, do a first pass on D05 and D07 v2 and report.

## Definition of done

AG-1 to AG-5 delivered with evidence ids and hashes, reviewed by Claude; AG-6 findings posted.
