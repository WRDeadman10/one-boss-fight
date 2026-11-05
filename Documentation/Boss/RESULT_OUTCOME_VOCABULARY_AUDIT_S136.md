# RESULT outcome vocabulary audit (S136)

## Current emitted outcomes

| Outcome | Runtime path | Meaning |
|---|---|---|
| `CompletedWithDamage` | `RPGFrameworkBossCharacter.cpp:618` | Damage-enabled encounter finished cleanly with accepted damage (or no parries). |
| `CompletedAllParried` | `:618` | Damage-enabled encounter finished cleanly with zero accepted hits and at least one parry. |
| `CompletedTelemetryOnly` | `:623` | Non-damage proof encounter finished cleanly. |
| `BossDefeated` | `:884` | Hittable framework boss died; executor aborts active card and RESULT follows `boss_dead`. |

An inventory of retained Claude execution logs found exactly these four outcome strings. `validate_framework_proof_logs.py:50` validates RESULT shape but accepts any non-whitespace outcome. `Scripts/Tools/framework_results.py:35–37` requires a nonempty outcome and does not enumerate or grade its meaning. Its current test fixture uses `Won` (`test_queue_c_tools.py:143`) to test row parsing; that value is not emitted by the framework.

## Unknown outcome handling

Today an unknown nonempty outcome is syntactically accepted and preserved as data; the parser does not classify it as a passing gameplay result. This is forward-compatible parsing, not vocabulary validation. A future consumer that needs a semantic verdict should maintain a known-outcome set and report unknown names as `UNKNOWN/UNCLASSIFIED` with the original row retained; changing the base schema to reject new values would break future logs and is not recommended without a versioned contract. No code change or tests in this audit.
