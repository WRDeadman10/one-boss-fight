"""
Lock-on camera aim. The pack's BP_TargetingComponent.UpdateTargetingControlRotation points the camera at (target actor location - (0,0,150)), clamped to pitch -25..+30.
For the 3.3 m boss (actor origin = capsule centre, 149 cm up) that is the floor under it, so the lock-on camera looks 17 to 25 degrees down and most of the screen is
floor. The pitch is measured from the player's origin and the 3.7 m boom swings the camera with it, so aiming too high is as bad (pitch +23 puts the camera 12 cm above
the floor looking up). This aims 40 cm below the target's centre (pitch about 0 at normal distances) and clamps the pitch to -8..+12 so the camera stays at head height.
Pack asset edited in place (git-ignored): run again after a pack re-import. Needs the editor open. Idempotent.
Usage: MSYS_NO_PATHCONV=1 python -I Scripts/lockon_aim_height.py
"""
import sys

sys.path.insert(0, __file__.rsplit("Scripts", 1)[0] + "Scripts")
from bp_edit import Graph, call  # noqa: E402

BP = "/Game/AdvancedARPGCombat/AdvancedCombatFramework/TargetingSystem/BP_TargetingComponent"
GRAPH = "UpdateTargetingControlRotation"
AIM_SUBTRACT, PITCH_CLAMP = "BFABA24345C113ECBE9D5B8533462C63", "4628ED4649F099475AF5D7A25AE9738D"
AIM_OFFSET = "0,0,40"  # subtracted from the target location (original 150)
MIN_PITCH = "-8.0"
MAX_PITCH = "12.0"

g = Graph(BP, GRAPH)
g.pin(AIM_SUBTRACT, "B", AIM_OFFSET)
g.pin(PITCH_CLAMP, "Min", MIN_PITCH)
g.pin(PITCH_CLAMP, "Max", MAX_PITCH)
call("asset", {"operation": "save_asset", "asset_path": BP})
print("lock-on aim: offset %s, pitch %s..%s" % (AIM_OFFSET, MIN_PITCH, MAX_PITCH))
