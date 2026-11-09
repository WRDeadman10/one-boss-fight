# AY-C11 — Mid01 dodge probe range band

The `FIGHT_DODGE_TARGET=Mid01` mode now starts at 120 cm and reuses the existing parry-close 115–125 cm band controller on every targeted dodge-only tick. Above the hard 130 cm boundary it places the player at 115 cm; from 126–130 cm it retreats; below 115 cm it approaches. Generic dodge-only mode retains its separate 200 cm range cap. No gameplay code or assets changed.

Offline validation: `python -m unittest Scripts.Editor.test_pie_full_fight_offline` passed 42/42. The added contract covers the configured 120 cm setup, hold boundaries, approach/retreat behavior and use of the band helper in the targeted runtime branch. `pie_full_fight.py` is valid Python syntax.

Lead PIE command environment: `FIGHT_DODGE_ONLY=1`, `FIGHT_DODGE_TARGET=Mid01`, `FIGHT_MAX=120`, with the normal `pie_full_fight.py` launcher. Confirm `[FullFight] setup`/`[FullFight] DODGE_RANGE_CLAMP` distances and report whether `Mid01_Anim_Montage` or `GS_SprintAttackFollowUp_Montage` plays, along with `DODGE_RESULT` counts. Codex did not run Unreal/PIE.
