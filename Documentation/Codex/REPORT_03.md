# Codex Report 03: Documentation Integrity Audit

## Files Written

- `Scripts/CheckDocs.py`
- `Documentation/Codex/REPORT_03.md`

The optional soak-watchdog follow-up was not made. No existing file was edited.

## Checker Run

Command actually run:

```powershell
python -I Scripts\CheckDocs.py
```

Observed output (exit code `1`):

```text
UNDOCUMENTED_PIE Scripts/Editor/pie_a2_diag.py:1 pie_a2_diag.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_attr_probe.py:1 pie_attr_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_body_look.py:1 pie_body_look.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_body_look_short.py:1 pie_body_look_short.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_boss01_look.py:1 pie_boss01_look.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_boss_abilities.py:1 pie_boss_abilities.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_boss_arm_diag.py:1 pie_boss_arm_diag.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_boss_fireball.py:1 pie_boss_fireball.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_boss_look_shots.py:1 pie_boss_look_shots.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_cam_probe.py:1 pie_cam_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_clip_look.py:1 pie_clip_look.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_clip_look12.py:1 pie_clip_look12.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_close_combo_watch.py:1 pie_close_combo_watch.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_death_probe.py:1 pie_death_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_debug_overlay.py:1 pie_debug_overlay.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_dump_abilities.py:1 pie_dump_abilities.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_dump_player_functions.py:1 pie_dump_player_functions.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_g3_probe.py:1 pie_g3_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_gate_look.py:1 pie_gate_look.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_hit_diag.py:1 pie_hit_diag.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_hud_probe.py:1 pie_hud_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_input_smoke.py:1 pie_input_smoke.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_jump_probe.py:1 pie_jump_probe.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_montage_shots.py:1 pie_montage_shots.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_montage_travel.py:1 pie_montage_travel.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_player_tags.py:1 pie_player_tags.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_poise_enemy_test.py:1 pie_poise_enemy_test.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_soak.py:1 pie_soak.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_stamina_trace.py:1 pie_stamina_trace.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_state.py:1 pie_state.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_stop.py:1 pie_stop.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
UNDOCUMENTED_PIE Scripts/Editor/pie_vfx_gallery.py:1 pie_vfx_gallery.py is not in RunDrivers.ps1 and is not named in Documentation/TEST_PLAN.md
PASS_TOTAL_MISMATCH Documentation/TEST_PLAN.md:109 pie_hit_intake: TEST_PLAN PASS 16/16, RunDrivers Min 36; lower total is TEST_PLAN
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:36 says Open for KI-032; Documentation/TASKS.md:71 says fixed/closed: | G3-1 | Per-weapon-attack data: posture damage, stamina cost, hyperarmor window (`ANS_HyperArmor`, not invulnerable), bleed buildup. Replaces the pack's poise numbers for the boss | C | G2-5 | Values in data, KI-032 clo
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:85 says Open for KI-081; Documentation/DEATH_CLIP_NOTES.md:72 says fixed/closed: - Found by the first runs: a health of 0 in the first frames of a PIE (KI-081) counted as a death and started the clip on a living boss; fixed: a death counts only after the boss was seen alive.
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:89 says Open for KI-085; Documentation/DECISIONS.md:535 says fixed/closed: | `DisableInput` and its price (KI-085) | The player is locked with `DisableInput` / `EnableInput` on the controller: one call, nothing of the pack's input handling is edited, and a press or a dodge during the clips star
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:89 says Open for KI-085; Documentation/MILESTONE_GATE2_CODE.md:22 says fixed/closed: | M7 | Boss clips, synchronized riposte execution, third review, boss look (G2-7, G2-8 roar, G2-15) | - | `pie_boss_clips.py`, `pie_riposte_exec.py`, `pie_riposte_lethal.py`, `pie_boss_look.py` | the Report 12 clips play
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:89 says Open for KI-085; Documentation/TASKS.md:153 says fixed/closed: - 2026-10-21/22 Report 12 clips wired, synchronized riposte, third review, boss look (G2-7, G2-8 roar, G2-15, G2-9 part). Clips: the six Report 12 clips are imported to `/Game/OneBossFight/Boss01/Animations` (`Scripts/Ed
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:90 says Open for KI-086; Documentation/TASKS.md:64 says fixed/closed: | G2-15 | Boss look swap: `SK_Boss01` and sword on `BP_ExampleGreatSwordBoss` (or a child), material parameters `PhaseGlow`, `Dissolve` wired | C + AG | M-01, M-02 | Same fight plays | Built 2026-10-21/22 (code done, NOT
KI_STATUS_HEURISTIC Documentation/KNOWN_ISSUES.md:98 says Open for KI-092; Documentation/TASKS.md:151 says fixed/closed: - 2026-10-22 Review D fixes, M13 builds loadout (G2-15, G2-9, G3-2, G3-3, part G3-5): review D (two read-only reviewers on the death and look components) found the pack's own sword still drawn (`URPGBossLook` now hides t
MISSING_BACKTICK_PATH Documentation/TASKS.md:115 `Documentation/AG/BRIEF_NN.md` does not exist
MISSING_BACKTICK_PATH Documentation/TEST_PLAN.md:24 `Documentation/UI/*.png` does not exist
MISSING_BACKTICK_PATH Documentation/DECISIONS.md:192 `Scripts/Editor/sevarog_pack_01..04*.py` does not exist
43 finding(s)
CHECK_EXIT=1
```

`KI_STATUS_HEURISTIC` is intentionally conservative: text such as “not fixed” can mention the word `fixed`, so each of those findings needs a human disposition rather than an automatic status change.

## Ten Hand-Checked Contradictions or Stale Statements

1. **Current project path is internally stale.** `Documentation/PROJECT_STATE.md:38` says `"-Project=C:\Users\winss\Documents\Unreal Projects\OneBossFight\OneBossFight.uproject"`; `Documentation/PROJECT_STATE.md:46` says `"Project C:\UnrealProject\OneBossFight"`. The latter is right for this checkout; the old build command should be replaced by the project-relative rebuild procedure. Evidence to settle: run the documented command only after owner approval.
2. **The phase threshold is stale in the project-state implementation summary.** `Documentation/PROJECT_STATE.md:62` says `"phase two at 50 % health"`; `Documentation/TASKS.md:57` says `"Phase two: once at 0.60"`. The task row is right because it records the current driver evidence. Evidence to settle: current `RPGBossPhases` source or `pie_phase_reset.py` run.
3. **Boss-look re-run status conflicts.** `Documentation/TASKS.md:64` says `"re-run pending"`; `Documentation/TEST_PLAN.md:123` says `"PASS 14/14 2026-10-22"` and `"Seen on screen"`. The test-plan row is later and should be retained; the Gate 2 task row is stale. Evidence to settle: existing driver log/screenshots.
4. **Boss-look status is also stale in the decision record.** `Documentation/DECISIONS.md:540` says `"pie_boss_look.py: built, first run found the scale fault, re-run pending"`; `Documentation/TASKS.md:151` says `"pie_boss_look.py 14/14, seen on screen"`. The latter is later verification; update the former’s Not verified list while retaining its visual/tracing caveats. Evidence to settle: `pie_boss_look.py` log and screenshots.
5. **Death-clip wiring status is stale in the decision record.** `Documentation/DECISIONS.md:540` says `"The death clip is imported but not wired"`; `Documentation/TASKS.md:152` says `"G2-9 death clip wired ... pie_boss_death.py 10/10"`. The task record is later and specific; the decision note is stale. Evidence to settle: current component source and the recorded driver run.
6. **G3-1 still describes M13 as a plan/probes not run.** `Documentation/TASKS.md:71` says `"M13 (builds) and M14 (balance) open"` and `"probes not run"`; `Documentation/TASKS.md:150` says `"pie_builds.py 103/103"` and names the M14 bot. The status cell is stale in at least its M13 portion; it should separate completed M13 from incomplete balance tuning. Evidence to settle: existing build-driver log.
7. **KI-032's status conflicts with the Gate 3 completion condition.** `Documentation/KNOWN_ISSUES.md:36` ends `"Open"`; `Documentation/TASKS.md:71` declares G3-1 done when `"KI-032 closed"`. The task row’s condition is unmet as written; do not silently close KI-032 without deciding whether the new project-owned posture table supersedes the old pack-poise issue. Evidence to settle: owner/Claude disposition of KI-032’s obsolete pack-specific wording.
8. **The performance log gives two incompatible meanings to 120 FPS.** `Documentation/PERFORMANCE_LOG.md:3` says `"120 FPS and 8.33 ms are stretch telemetry only"`; `Documentation/PERFORMANCE_LOG.md:16` says `"Treat 120 FPS here as a necessary, not sufficient, check"`. The first line agrees with `CLAUDE.md` and `AGENTS.md`; line 16 is stale and should say proxy telemetry only. Evidence to settle: owner’s final 60-FPS decision already quoted in the same document.
9. **The current test-plan count is stale against the gate table.** `Documentation/TEST_PLAN.md:109` says `"PASS 16/16"` for `pie_hit_intake.py`; `Scripts/RunDrivers.ps1:18` sets `"Min = 36"` for `pie_hit_intake`. The 16/16 result is obsolete or describes a reduced historical driver; it cannot document the current gate minimum. Evidence to settle: a fresh `pie_hit_intake` log (not run in this brief).
10. **The project-state “whole fight” driver is not the current gate.** `Documentation/PROJECT_STATE.md:41` calls `"Scripts/Editor/pie_pack_fight.py"` the `"PIE check of the whole fight"`; `Documentation/PROJECT_STATE.md:118` says the full gate is the `RunDrivers.ps1` table with 31 rows. The latter is the actual regression-gate authority, while the old smoke-driver wording is stale. Evidence to settle: the current `RunDrivers.ps1` table and a decision whether `pie_pack_fight.py` remains a supported smoke test.

## Not Verified

- No editor, build, package, staged game, PIE driver, or benchmark was run.
- The checker was run only against the current working tree. A deliberately planted scratch-copy mismatch was not created because this brief permits no edits beyond the two deliverables.
- Automated status findings are heuristic and do not prove an issue is fixed or closed; no status was changed.
- The audit did not inspect third-party/git-ignored content or validate driver behavior.
