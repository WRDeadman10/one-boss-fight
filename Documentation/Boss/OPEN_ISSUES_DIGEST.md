# Open issue digest

This is a compact navigation aid for open items in `Documentation/KNOWN_ISSUES.md`, not a new status ledger. The source file remains authoritative; resolved entries and caveats are deliberately excluded here. Each row names the evidence or decision explicitly called for by the source entry.

| Area | Open item | Evidence still needed (per KNOWN_ISSUES) |
|---|---|---|
| Authoring / combat range | KI-145 legacy cards retain earlier ranges; calibrated R2 cards exist. | Decide whether to apply calibrated values to legacy cards, then validate/read back and prove any changed cards. |
| Player dodge / iframe | KI-146 timing-dependent proof has a resolved route, but observed input-to-iframe latency and contact timing vary. | If deterministic proof is needed, trigger the dodge from the boss executor's active-window event and capture resolver outcomes. |
| Hit windows | KI-147 unbaked live-socket windows retain long-frame interpolation risk; baked windows need rebaking after animation edits. | Bake remaining damaging windows; rebake on animation change and run hit proof. |
| Player hit intake | KI-151 real-swing evidence covers Sword Light; other weapon/attack rows remain outside that witness. | Prove real Claymore and Dual Swords, plus strong/charged/jump attacks through loadout switch and real swings. |
| Boss presentation | KI-152 stagger triplet and phase hold are resolved with limits. | Author/prove boss death animation and a dedicated phase-roar animation if those limits are to close. |
| Parry | KI-153 confirms player grant/tag and resolver contacts; pack boss reaction remains unwitnessed. | Real-arena PIE parry contact and evidence of pack boss's own reaction. |
| Legacy player moves | KI-154 source audit AX-C01–C05 confirms three contact branches and the HealPunish javelin callback; generic resolver tests and C-683 compile confirmation are not old-path contact witnesses. | Lead PIE contact against Javelin, LowSweep, Shockwave and HealPunish's javelin response; confirm counters. See `AX_C01_C05_KI154_OLD_MOVE_PARRY_AUDIT.md`. |
| Boss strafe stuck recovery | KI-149's opt-in stuck-recovery branch is unit proven, live not proven; the R3c arena-edge run strafed normally and emitted no `strafe_stuck` line (C-712). | Obtain a safe live setup that blocks the strafe and emits `strafe_stuck flipped=1`; do not treat the R3c run as proof. |
| Framework proof profile starvation | KI-155: the PARRY profile with `attack_count=2` and nonzero parry posture ends after a posture-breaking parry; its remaining two-card pool is on cooldown and reports `NoCandidate`. | Keep recovery proof setup at `parry_posture_amount=0`, `attack_count=4`, and zero candidate cooldowns; do not infer a runtime defect from this proof-profile limitation. |
| Test-plan ID consistency | `TEST_PLAN.md` repeats BUILD-03 through BUILD-06 (rows 121/134, 122/138, 128/140, 125/142) and the later section is not numerically sorted. | Reconcile or rename the historical rows only with lead/owner direction; Codex recorded the finding and left the rows unchanged. `check_test_plan_ids.py` reports it. |

Use the KI entry itself for dates, linked evidence paths, scope, and any superseding status. This digest does not infer that code completion, compilation, or a different proof lane satisfies those outstanding witnesses.

## Live proof update (C-715, 2026-11-03)

Claude reports the parry-stamina and overlay checks passed, and fatigue reached three consecutive live whiffs followed by a contact reset. The cost-20 parry run showed an opened window without contact retains its 20-point cost; a Perfect parry refunded half of the next 20-point cost. Insufficient-stamina refusal was not exercised. Fatigue's 0.5 floor is unit-tested only; the live run reached whiffs 1–3 (scales 1, 0.95, 0.9), reset on contact, and later ended `NoCandidate` after scheduled target shifts left the target out of range. See `Docs/BossCombatReview/Execution/Codex/Proofs/PARRY_STAMINA_EXPECTED.md`, `Docs/BossCombatReview/Execution/Codex/Proofs/FATIGUE_EXPECTED.md`, and live evidence under `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA` and `B_FATIGUE`. W3 strafe-stuck remains unproven live (KI-149). C-715 reports all ten opt-in feature checks live-proven except W3; use the feature-specific evidence before relying on that aggregate claim.

## Queue C S51–S60 review follow-up (C-719, 2026-11-03)
pg.BossProofCenterBias now ignores non-finite overrides (Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:23), and the yaw-probe hook now ignores non-finite amplitudes (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:431). Both are one-line guards requested by Lead. Other S51–S60 candidates remain listed for review; no runtime claim or test result is implied.

## Queue C S75 arithmetic extreme
RPGBleedRules::Apply (Source/OneBossFight/Player/RPGBleedRules.h:68) increments State.Procs without an INT32_MAX guard; no test covers a near-limit state. This is a theoretical extreme-state overflow risk, not a normal combat reachability claim. S73's enrage monotonicity test assertion was corrected; S74 noted exact enrage speed saturation lacks a dedicated assertion.
