# AJ-C31–C35 — guard-counter probe evidence and cleanup audit

Date: 2026-11-07  
Status: Static source and code review; Lead runtime remains pending.

## Review

- The two log triggers in `pie_er_guard_counter.py` match the current `UE_LOG(LogRPGDodge, Log, ...)` strings in `RPGDodgeTiming.cpp`: `successful guarded contact armed guard counter window` and `guard counter accepted after successful block`.
- `RPGHitIntake::GetRecordLines()` and `GetBossHitCount()` are `UFUNCTION` Blueprint-callable/pure APIs; the script calls them read-only and logs the last eight rows. Record serialization includes the attack `kind` and `AttackData` name.
- Input events are tracked in `S["held"]`; `finish()` unregisters the Slate tick callback, releases held keys, unholds the encounter when present, writes a summary, and requests PIE end. Exception and timeout routes both reach `finish()`.
- Review found a log rotation/new-file gap: a log path absent from the initial baseline defaulted its cursor to current EOF, which could skip an early guard event. The cursor now defaults to byte zero for previously unseen log paths. Existing logs still start at their pre-PIE baseline.

## Acceptance boundary

This closes probe implementation review only. It does not establish that a log file can be read while Unreal writes it in the Lead's session, that the current arena boss invokes the framework notifier, or that either route produces a guarded hit/counter. Those require paired Lead PIE logs. Current route-host uncertainty is documented in `AJ_C26_C30_GUARD_HOOK_REACHABILITY_AUDIT.md`.

## Validation

Source/API review and scoped `git diff --check` only. No Python execution, tests, Unreal/Editor/PIE, build, asset edit, commit, or push by Codex.
