# AX-C01–C05 — KI-154 old-move parry source audit

Date: 2026-11-09. Source-only; no code changes, tests, build or runtime evidence.

| Path | Source finding | Counter/readback | Runtime status |
|---|---|---|---|
| Javelin | `RPGBossJavelin.cpp:137-158` routes resolver `Parried` through `Finish`; `Finish` reports once to its owner at `:83-95`. | `URPGBossHealPunish::ReportJavelin` increments `JavelinParried` at `RPGBossHealPunish.cpp:197-205`; getter `RPGBossHealPunish.h:126-136`. | Not proven by this audit. |
| LowSweep | `RPGBossLowSweep.cpp:77-83,136-154` blocks repeat samples after a parry, then sets the per-sweep flag and increments `ParriedCount`. | `RPGBossLowSweep.h:75-80`. | Not proven by this audit. |
| Shockwave | `RPGBossShockwave.cpp:112-139` resolves once per player and increments the parry counter in a separate outcome branch; it does not increment `HitCount`. | `RPGBossShockwave.h:80-89`. | Not proven by this audit. |
| HealPunish | Owns javelin lifecycle and terminal counters; its callback receives the projectile result. The projectile owns collision and resolver contact. | `ReportJavelin` declaration `RPGBossHealPunish.h:146-147`; callback counter branch above. | Not proven by this audit. |

## Coverage boundary

`RPGAutomationTests.cpp:174-192` tests the pure resolver decision and confirms Parried outranks guard. Native tests found for the adapters exercise configuration/lifecycle, not these specific contact result branches and counters. Claude's C-683 compile confirmation covers compilation only. KI-154 therefore remains open for a Lead PIE contact against each old move with source counter readback.
