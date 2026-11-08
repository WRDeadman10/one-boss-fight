# Owner decision: dynamic melee camera inside boss mesh

Lead C-1051 reports that the 12-minute fight capture spends many close-range frames inside the boss mantle/legs or against ruins. The boss capsule ignores `ECC_Camera`, so the spring arm can extend into the body when the boss circles beside or behind the player. Antigravity A-636 independently confirms the same issue in fight video 2. This is a dynamic problem; C-1044's open-ground samples did not cover it.

Choose one approach before any camera Source change:

| Option | Behavior | Advantages | Costs / risks |
|---|---|---|---|
| **A. Boss capsule blocks `ECC_Camera`** | Spring-arm sweep hits the live boss capsule and shortens the arm before the camera enters the body. | Uses existing spring-arm collision behavior; preserves the boss render and player-centered camera; smallest design change. | Camera distance can pulse as the boss circles; capsule bounds do not match mantle/weapon silhouette; may push the camera too close to the player; requires checking wall/floor collision interactions. |
| **B. Hide or dither boss mesh when camera is inside its bounds** | Detect camera-inside-boss-mesh and fade/hide the boss presentation until the camera exits. | Preserves camera distance and player framing; directly removes the opaque mesh obstruction. | Boss may pop/fade during melee; must handle body, mantle, crown, gauntlet and sword followers consistently; avoid hiding hit feedback, telegraphs or phase-two aura; needs stable enter/exit hysteresis. |
| **C. Lock-on/orbit framing keeps boss in front** | Adjust orbit or camera aim so the boss stays ahead of the camera during close circling. | Preserves the full boss and avoids camera-inside-mesh states; can retain readable distance and silhouette. | Largest gameplay feel change; can move player/boss off-center or fight player camera input; must handle target loss, walls, phase-two effects and both orbit directions. |

## Comparison probe and acceptance

Before selecting, Lead runs the same no-change baseline on the live arena: hold the player near the boss while it circles on both sides at 150–250 cm. Log each tick's camera world position, actual spring-arm length, sweep hit component, boss capsule response, and a camera-inside-boss-bounds boolean. Keep the combat state fixed across options and record a short video with player and boss silhouettes visible. Include standing, attack recovery, dodge, phase-two aura, and wall/floor passes. The dynamic baseline confirms when and how often intrusion occurs; it does not itself choose a fix.

Lead-only telemetry is prepared in `Scripts/Editor/probe_camera_inside_boss.py`. It starts PIE, enters combat after the actors are ready, and samples the live player/boss/camera state for a bounded 30 seconds while the Lead manually circles in both directions at 150–250 cm and captures the named standing/recovery/dodge/aura/wall/floor segments. The marker includes the actual camera position and pivot-to-camera distance, target arm length, estimated spring-arm sweep hit component (offsets are unavailable in the current Python API), boss capsule `ECC_Camera` response, and whether the camera point lies in a visible boss-mesh component's world AABB. AABB occupancy is an approximation, and unreadable component bounds remain `None`; it is not a rendered-pixel visibility verdict. The script does not alter camera or collision settings. Offline geometry/marker checks are in `Scripts/Editor/test_probe_camera_inside_boss.py`; Lead owns both-route PIE and video evidence.

After the owner chooses A/B/C, implement only that option under a separate reviewed order. Acceptance: no camera-inside-boss-bounds frames during the circling case; attacks, dodge direction and phase-two aura remain readable; no new wall/floor penetration or unstable camera jumps; repeat at 105 cm and 150–250 cm and compare the same video views. Preserve the current floor/wall spring-arm safety path. No camera Source setting has been changed by this proposal.

## Prior static probe boundary

C-1044's clean legacy/data PIE trace at 105/200/300 cm found a full ~375 cm pivot-to-eye distance against a 370 cm arm, `sphere_trace=None`, and the boss capsule's `ECC_Camera` response `IGNORE` on the open-ground lane. It ruled out a boss-caused spring-arm hit for those samples only. It did not test a circling boss or the camera-inside-rendered-mesh condition in C-1051.
