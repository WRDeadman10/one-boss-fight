# H4/H5 parity driver hotfix

Date: 2026-11-05. Mailbox orders C-845/C-846.

## H4 — A4 S9 diagnostics

`pie_a4_low_sweep.py` now reads the Character mesh through `get_editor_property("mesh")`, matching `g0_pack_boss.py:58`. Every S9 diagnostic is best-effort and catches its own exceptions; the first failure logs `S9DIAG unavailable: <exc>` once, then trials continue. Diagnostic sampling covers S6 backward roll at 0.50 s and the two reproduced S9 boundaries (jump 0.05 s, roll 0.40 s). The unsupported reflective tick-group probes were removed; the diagnostic still reports component class and enumeration order.

API audit references in working Editor drivers:

- Mesh property: `g0_pack_boss.py:58`.
- Actor component enumeration and class-name lookup: `pie_a2_diag.py:10`.
- Animation instance, active montage, montage name, and position: `pie_a2_diag.py:37-40`.
- I-frame boolean: `pie_iframes.py:145` and `pie_build_fight.py:443`.
- Tracker position: `pie_build_fight.py:417`.
- Sweep active state: `pie_transition_rules.py:336`.

## H5 — telegraph timing observables

`pie_telegraph.py` emits four raw-second readings with `timing_seconds` declarations at finish: authored A3a (0.40 ± 0.06 s), pack A1b cap (0.35 ± 0.06 s), A1 cap (0.35 ± 0.06 s), and A2 authored windup (1.93 ± 0.12 s). The existing `[Telegraph] PASS/FAIL` message text is unchanged. `write_a4_parity_receipt.py` maps each typed value onto its matching check observable so the comparator uses the existing 1/60 s timing rule. A missing/ambiguous check name is rejected.

## Verification / limits

- H4 offline Scripts/Tools discovery: 127 passed, 1 skipped; A4 Python AST parsed.
- H5 offline Scripts/Tools discovery: 127 passed, 1 skipped; A4, telegraph and receipt-writer AST parsed.
- A synthetic closed-log check confirmed typed mapping to check-0010, check-0014, check-0017 and check-0020.
- `git diff --check` still reports a pre-existing trailing-space line in `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json:22`; no edits were made to that file.
- No Editor/PIE or build run by Codex. Lead must rerun both A4 arms and telegraph pairs to obtain runtime evidence.
