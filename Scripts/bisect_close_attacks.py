"""Bisect helper for KI-106 (writes Scripts/Editor/_bisect_tmp.py, delete it afterwards): builds a copy of pie_close_attacks.py whose STEPS are wake, arm, the steps given as the first argument (python source of STEPS entries), then the five 90 cm real-ability trials and c7_summary. Run the copy with Scripts/run_in_editor.py. Results 2026-10-24: no earlier steps 5 of 5; only C1-C3 (bare A1/A3a/A3b) 2 of 5; only C4-C5 (denied branch stops) 0 of 5; only C6 (lock_move) 1 of 5."""
import re, sys
src = open("C:/UnrealProject/OneBossFight/Scripts/Editor/pie_close_attacks.py").read()
# keep s_wake, s_arm, then the listed middle steps, then the five 90 cm trials and the summary
start = src.index("STEPS = [")
end = src.index("]\n", start) + 2
mid = sys.argv[1] if len(sys.argv) > 1 else ""
steps = "STEPS = [\n    (9.0, s_wake), (3.0, s_arm),\n" + mid + "\n    (2.5, close_ability(90)), (2.2, close_ability_check), (0.6, close_ability(90)), (2.2, close_ability_check), (0.6, close_ability(90)), (2.2, close_ability_check),\n    (0.6, close_ability(90)), (2.2, close_ability_check), (0.6, close_ability(90)), (2.2, close_ability_check), (0.1, c7_summary),\n]\n"
open("C:/UnrealProject/OneBossFight/Scripts/Editor/_bisect_tmp.py", "w").write(src[:start] + steps + src[end:])
