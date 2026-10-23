# Codex Report 01: G4-4 soak runner draft

## Files written

- \`Scripts/Editor/pie_soak.py\`
- \`Documentation/SOAK_NOTES.md\`
- \`Documentation/Codex/REPORT_01.md\`

No existing file was edited, renamed, or deleted. No editor, build, PIE,
package, or git command was run.

## Scenario table

Six batches each run, in order: a 20-second natural fight then reset; a forced
stance break then reset; a phase-two roar then reset; a real player death and
respawn; and a boss death followed by pack destruction and PIE restart. That is
30 total encounters. Boss death is last because the pack does not permit reset
to revive the destroyed boss.

## Expected check count

The driver has a fixed **213** checks: seven for each of 30 encounters (210),
plus all encounters executed, no tick error, and no watchdog hang (3). A setup
failure, watchdog, or exception fills outstanding checks as failures.

## API list

The driver uses only UFUNCTION-backed project component calls:

- Encounter API: \`Source/OneBossFight/Player/RPGBossEncounter.h:38-71\`.
- Attack counters/current move: \`Source/OneBossFight/Player/RPGAttackTracker.h:103-107\`, \`:131-160\`.
- Stagger API: \`Source/OneBossFight/Player/RPGBossStagger.h:138-148\`, \`:186-203\`, \`:227-231\`.
- Phase API: \`Source/OneBossFight/Player/RPGBossPhases.h:95-105\`.
- Posture: \`Source/OneBossFight/Player/RPGBossPosture.h:45-49\`.
- Debug hooks: \`Source/OneBossFight/Player/RPGCombatDebug.h:58-79\`, \`:66-71\`.
- Wave state: \`Source/OneBossFight/Player/RPGBossShockwave.h:66-67\`.

The pack attribute reflection call follows existing drivers and is not a
project-component Python API.

## Not verified

No runtime validation occurred. The actual respawn duration, boss-destruction
duration, stale-actor naming, total duration, and all pack reflection behavior
require Claude's PIE run. No soak pass is claimed.

## Most likely failure points

1. KI-081 cold first-PIE timing.
2. A respawn exceeding 25 seconds or retaining the same pawn name.
3. A leftover pack actor outside the expected class-name scan.

## Validation performed

Offline syntax validation ran successfully (exit code 0):

```powershell
python -I -c "import ast; ast.parse(open('Scripts/Editor/pie_soak.py', encoding='utf-8').read())"
```

No editor, build, PIE, package, or runtime validation ran.

