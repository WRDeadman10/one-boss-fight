# Framework overlay parry line

## Setup

On the framework proof map, set `rpg.BossOverlay 1` for the on-screen overlay. Set `rpg.BossOverlay 2` to show the same overlay and emit one `[FrameworkProof] overlay` line per second. The CVar defaults to 0 (off) and is registered at `RPGFrameworkBossCharacter.cpp:47`.

## PASS

- With a valid `URPGPlayerParry` component on the framework boss's target, the line includes `Parry=Closed Grade=None` before a parry and reports `Parry=Open` while the player's parry window is open; after a successful parry, `Grade=Perfect`, `Good`, or `Late` remains visible (`RPGFrameworkBossCharacter.cpp:745`, `RPGBossOverlayRules.h:31`).
- Mode 2 emits the same text in the periodic overlay log; mode 1 displays it on screen.
- With the target component absent, the optional parry suffix is omitted rather than inventing data.

## Control

Use a target without `URPGPlayerParry`; the formatted overlay should omit parry state and grade fields.

## FAIL

- Mode 1/2 does not expose the parry state, the grade remains `None` after a verified parry, or mode 0 still displays/logs the overlay.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`
