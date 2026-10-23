# Brief 04 Report

## Scope

Edited only the claimed Brief 04 files:

- `Scripts/Editor/pie_build_fight.py`
- `Documentation/M14_FIGHT_NOTES.md`
- `Scripts/CheckDocs.py`

No editor, build, package, game, or PIE session was started. No Git command was run.

## M14 Bot Changes

- **a. Build openers:** `pie_build_fight.py:100-107` now retains the intended
  Strength heavy sequence (`JumpHeavy`, `Strong`, `Light`), gives Starter a
  `Strong` then `Light` recovery opener, retains Dex's three-light chain, and
  counts heavy presses for the Starter/Strength policy. The policy and its
  required runtime evidence are documented in `M14_FIGHT_NOTES.md:30`.
- **b. Close positioning and recovery:** `pie_build_fight.py:808-834` no
  longer rejects a recovery opening from a travel-time estimate; it closes and
  retries instead. The existing flank close-dodge policy and `SPACING_MAX=260`
  remain in force. `M14_FIGHT_NOTES.md:26-32` records the intent and the
  runtime checks still required.
- **c. Neutral pressure:** the existing neutral-poke path was retained and
  documented in `M14_FIGHT_NOTES.md:32`; no new project-component Python API
  was added for it.
- **d. A6 wave:** the A6 plan at `pie_build_fight.py:152` now chooses `jump`.
  `do_wave_jump` at `pie_build_fight.py:951-966` uses existing input helpers
  and logs the jump's start/end state. This follows the LEAP-01 premise that a
  jump at wave launch clears the wave; the bot timing has not been observed.
- **e. Diagnostics:** the pre-existing tracked-attack decision logging and
  dodge-end geometry logging were preserved rather than duplicated. The new
  wave log adds its end distance, displacement, falling state, and mode.
- **f. Inconclusive evidence:** `pie_build_fight.py:1268-1270` marks a
  Starter or Strength run inconclusive when it issues fewer than three heavy
  swings.

No new project-component Python call was introduced. The new helper uses
`key_hold`, `clear_stick`, and `JUMP_KEY`, which were already defined in the
driver. The driver contains no `set_editor_property` call and introduces no
heal, hold, or post-wake teleport.

## Documentation Checker

- `CheckDocs.py:28-48` has an explicit diagnostic/probe driver allowlist.
- `CheckDocs.py:145` ignores a PASS total explicitly described as automation
  tests, rather than treating it as a PIE-driver count.
- `CheckDocs.py:194-203` reports closed-KI references only when a line
  explicitly says that the KI is fixed or closed.
- `CheckDocs.py:215-217` ignores backticked `NN`, `*`, and `..` tokens before
  applying its file-reference check.

The last two changes keep the checker focused on actionable contradictions
instead of treating prose examples as status claims or paths.

## Expected Runtime Risks

These are predictions, not observations:

1. The A6 jump can be early or late because LEAP-01 proves a launch-timed
   jump, while the bot schedules from tracker timing.
2. A1/A1b/A3a/A3b may still hit: their short windups can be shorter than the
   measured input-to-i-frame delay even with a flank dodge.
3. Removing the recovery fit veto can begin an opener as the next boss windup
   starts; untracked mid-range/sprint attacks also still use a guessed dodge
   time. The editor run must inspect cuts, hits, opener usage, and the new
   inconclusive evidence before using results for balance.

## Validation Performed

I ran static Python checks only:

```text
python -I -c "import ast; ast.parse(open(r'Scripts/Editor/pie_build_fight.py', encoding='utf-8').read()); print('AST PASS: Scripts/Editor/pie_build_fight.py')"
AST PASS: Scripts/Editor/pie_build_fight.py

python -I -c "import ast; ast.parse(open(r'Scripts/CheckDocs.py', encoding='utf-8').read()); print('AST PASS: Scripts/CheckDocs.py')"
AST PASS: Scripts/CheckDocs.py

python -I Scripts\\CheckDocs.py
No documentation integrity findings.
CHECKDOCS_EXIT=0
```

No runtime behavior was verified.
