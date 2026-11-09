# AW-C06–C10 — camera config and Shipping source audit

Date: 2026-11-09  
Scope: offline source and contract audit for open KI-037/KI-066 gates. No owner camera option was selected.

## Five checks completed

1. **Defaults:** `bDefaultHideBossInside` and `bDefaultLockOnFraming` are Config properties with native `false` defaults; `DefaultGame.ini` also sets both to `False`.
2. **Override precedence:** the two Development CVars default to `-1`; `-1` follows config, `0` disables, and positive values enable. Shipping initializes the override to `-1` and reads the config property.
3. **Shipping isolation:** CVar declarations and reads are inside `#if !UE_BUILD_SHIPPING`; the B/C application paths remain compiled so Shipping can honor config. BossBlocks and debug drawing stay development-only.
4. **Disable/cleanup:** source contracts cover disabled-path restoration, invalid/missing target recovery, target replacement, controller loss and `EndPlay` cleanup for the owned hide/framing state.
5. **Handoff accuracy:** corrected stale TickComponent comments that called B/C “non-Shipping” experiments; they now describe config defaults and Development CVar overrides.

## Validation and limits

- Camera config, hide, lock-on, independence and BossBlocks contracts: **40/40 passed**.
- `py_compile` for the config contract and read-only exporter: passed.
- Scoped `git diff --check`: passed; Git reported only LF/CRLF normalization for `RPGCameraRig.cpp`.
- No UHT/C++ build, Shipping build, Unreal, PIE, editor exporter run, asset read, package or owner-choice change by Codex.
- KI-037/KI-066 remain open for owner selection and Lead runtime/package evidence. The G044 exporter output remains unproduced and its serialized readback is not runtime proof.
