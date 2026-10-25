#!/bin/bash
# P0 natural sample runner (bot-driven). Usage: p0_run_natural_sample.sh <label> <build> <wakeclip> <telegraph> <legend>
# Sets the cvars, starts the read-only montage observer, then the existing pie_build_fight.py driver (unchanged) and waits for its RESULT line.
cd /c/UnrealProject/OneBossFight || exit 2
export MSYS_NO_PATHCONV=1
LABEL=$1; BUILD=$2; WAKE=$3; TELE=$4; LEGEND=$5
E=Docs/BossCombatReview/Execution/Claude/Evidence
printf 'rpg.WakeClip %s\nrpg.CloseTelegraph %s\nrpg.Legend %s\n' "$WAKE" "$TELE" "$LEGEND" > Saved/p0_cvars.txt
[ -n "$EXTRA_CMD" ] && printf 'cmd %s\n' "$EXTRA_CMD" >> Saved/p0_cvars.txt
printf '%s' "$BUILD" > Saved/build_fight_build.txt
python -I Scripts/run_in_editor.py Scripts/Editor/no_throttle.py >/dev/null 2>&1
python -I Scripts/run_in_editor.py $E/probes/p0_set_cvars.py >/dev/null 2>&1
LOG=Saved/Logs/OneBossFight.log
START=$(wc -l < $LOG)
python -I Scripts/run_in_editor.py $E/probes/${OBSERVER:-p0_natural_montage_log.py} >/dev/null 2>&1
python -I Scripts/run_in_editor.py Scripts/Editor/pie_build_fight.py >/dev/null 2>&1
for i in $(seq 1 120); do
  sleep 5
  if tail -n +$START $LOG | grep -a -q 'LogPython: \[BuildFight\] RESULT [0-9]*/[0-9]* passed'; then break; fi
done
sleep 14   # the observer prints its counts ten seconds after the world is gone
tail -n +$START $LOG | grep -a -E '\[P0Cvar\]|\[P0Nat\]|\[P0Trace\]|LogRPGAttack|LogRPGStagger|LogRPGHitIntake: hit|LogAnimMontage|LogAnimation|\[BuildFight\] (METRIC|RESULT|FAIL|OUTCOME)' | sed 's/^\[[^]]*\]\[[^]]*\]LogPython: //' > $E/exports/natural_sample_$LABEL.txt
echo "wrote $E/exports/natural_sample_$LABEL.txt: $(wc -l < $E/exports/natural_sample_$LABEL.txt) lines"
