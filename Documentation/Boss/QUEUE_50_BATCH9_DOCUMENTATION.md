# Queue_50 Batch 9 — documentation (tasks 41–45)

Date: 2026-11-10. Scope: five documentation tasks from `Docs/BossCombatReview/Execution/Codex/QUEUE_50.md`. No C++ or asset changes, build, test suite, Editor, PIE, package, commit, or push was performed for this batch.

| Task | Result |
|---|---|
| 41 — `NEW_CARD_HOWTO.md` | Corrected defensive-card rules against `RPGBossMoveCard.cpp`: forward defensive reposition requires positive distance budget; backstep requires `0 < WarpMaxDistanceCm <= 250 cm`. |
| 42 — `PROOF_WORKFLOW.md` | Added the exact command used for C-1253a and described its build, transient validator dry-run, and full-suite stages, with the evidence location and proof boundary. |
| 43 — `TEST_HOOKS.md` | Reconciled names against `python Scripts/Tools/list_cvars.py`; source scan returns 54 CVar names. Added all three missing Development camera controls and wrote each of the nine performance CVar names explicitly with its default/meaning. `rpg.DeterminismSeed` remains identified as a console command. |
| 44 — `LOG_TOKENS.md` | Replaced stale 2026-11-03 retained-sample count with the current source audit result. The validator/document inventory comparison reports exactly 138 schemas and 138 documented tokens, with no missing or extra token rows. |
| 45 — `OPEN_ISSUES_DIGEST.md` | Added navigation rows for the current aura/owner visual, package identity, first-dodge, natural A4, camera-choice, and Sevarog authoring gates. Each action is bounded by the corresponding KNOWN_ISSUES record; no resolution is inferred. |

Commands used for source-backed inventories:

```powershell
python -I Scripts/Tools/check_validator_tokens.py
python Scripts/Tools/list_cvars.py
```

Results: validator audit PASS (138 emitted / 138 schemas); CVar source inventory 54; exact log-token table comparison 138/138; source-to-hook inventory has no undocumented registrations after listing the nine performance controls individually. The repository Markdown link checker is being run against `Documentation` for this edited batch.

Next: Queue_50 Batch 10, tasks 46–50, subject to mailbox feedback.
