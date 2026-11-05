"""Lead-run wrapper for the P30 C3 sword-style update dry run. No apply flag."""
import runpy
import sys
from pathlib import Path


ROOT = Path("C:/UnrealProject/OneBossFight")
TOOL = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py"
CONFIG = ROOT / "Docs/BossCombatReview/Execution/Claude/C3/p30_sword_style_update_dry.json"
sys.argv = [str(TOOL), str(CONFIG)]
runpy.run_path(str(TOOL), run_name="__main__")
