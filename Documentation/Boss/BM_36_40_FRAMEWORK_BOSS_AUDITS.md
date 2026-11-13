# BM-36..40: framework boss source audits (lane BM, batch 8 of 10; KI-174 / KI-154 / KI-155 / KI-136)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_framework_boss_static_pins.py`. **No source change. Nothing compiled or run.** Each of these KIs needs live PIE evidence or a lead or owner intent decision to resolve. This batch re-verifies each against the current code and pins the facts.

## BM-36: KI-174, leash versus combo pause (re-verified; cites moved)

| Fact | Current line (KI cites `:600, 788`) |
|---|---|
| The leash early-return is `if (Fault == OffArena && bArenaLeash) { HandleLeash(); return; }` | `RPGFrameworkBossCharacter.cpp:542` (in `Tick`, `:529`) |
| The combo pause check is `if (bComboPausing) { if (Now < ComboPauseUntil) return; StartComboCard(); }` | `:897`, **after** the leash return |
| The pause deadline is **absolute world time**: `ComboPauseUntil = Now + PauseSeconds` | `:1100` |
| `HandleLeash` touches neither `bComboPausing` nor `ComboPauseUntil`; the resume path (`:543-549`) doesn't either | checked |

**So:** off-arena time **counts toward** the combo pause. If the target returns after the deadline, the pending card starts at the first non-leashed tick that reaches `:897`. **Status: Open, unchanged.** The intent (should off-arena time count?) is the lead's decision. **Proposed KNOWN_ISSUES cite update:** `:542, 897, 1100`.

## BM-37: KI-154, Javelin parry routing (re-verified)

- `RPGBossJavelin.cpp:155-157`: `case ERPGDamageOutcome::Parried` → `Finish(ERPGJavelinResult::Parried, …)`. `Finish` (`:83`) then reaches the owning `URPGBossHealPunish` (`:91`).
- This matches the AX-C01 audit. **No source defect.** The LowSweep, Shockwave and HealPunish counters are not re-audited here, because AY-C04 already found no defect.
- **Status: Open (live contact evidence needed, engine-gated).**

## BM-38: KI-155, PARRY proof-profile starvation

- This is a **profile-level limitation, not code**. A posture-breaking parry aborts the card, every candidate is on cooldown during the 1 s stagger, and the selector emits `Framework.Selector.NoCandidate`.
- **Status: Open.** The recommended proof settings (`parry_posture_amount=0`, `attack_count=4`) are in the KI row.
- Validating that enough candidates remain selectable would be new tooling for a proof profile; it is not part of this lane (owner-independent but feature-sized).

## BM-39: KI-136, Death citation ambiguity (proposal)

- `RPGBossDeath.cpp:126` and `RPGBossDeath.h:31,99` still cite **KI-083**, an entry that mixes the PIE `set_editor_property` hazard with pack death destruction. `RPGBossDeath.h:137` correctly cites KI-083 for the `set_editor_property` hazard.
- **Proposed comment-only edit (not applied, because it touches production files):** change the three death-lifecycle citations to **KI-136**, the dedicated Death lifecycle entry. Keep `:137` on KI-083.
- The static pin will flag when this lands.

## BM-40: tests and limits

`python -m unittest discover -s Scripts/Tools -p test_framework_boss_static_pins.py -v` → **`Ran 5 tests ... OK`**.

| Test | Pins |
|---|---|
| KI-174 | the leash return precedes the pause check within `Tick`; the absolute deadline; `HandleLeash` has no combo-pause writes |
| KI-154 | `Parried` → `Finish(Parried)` |
| KI-136 | the KI-083 citations are present |

**Limits:** these are static text pins. The runtime timing (KI-174), the counters (KI-154) and profile starvation (KI-155) stay engine-gated.
