# CI-P0-A-01 Revision 02 independent review

Date: 2026-10-25  
Submission: A-40  
Verdict: **CHANGES REQUIRED (narrowed)**

Revision 02 fixes the major A-39 boundary failures: VIS IDs are stable, the A4 54 cm/330 cm conclusion is withdrawn, A5 and foot sliding are hypotheses, Shipping appearance is unverified, and a Blender script plus raw log now exist. Codex independently matched every one of the log's 20 input hashes and sizes to the current files and inspected the extraction source. This verifies input identity and what the script computes; Codex did not rerun Blender and does not independently reproduce the reported transforms.

## Required corrections

### 1. Script output does not establish the timing-card pose labels

`extract_baseline_kinematics.py` extracts bounds, root maximum excursion, pelvis/foot-bone Z ranges and hand distance. It does not read FBX metadata markers, calculate blade/floor contact, inspect hand orientation/velocity, or identify a visual release. Frames 11/12/18/27 and their labels are hard-coded in the logger. Therefore A1/A3/A4/A5 tell, commit, active, release and contact descriptions must cite the exact authored `.txt` sidecar or historical report separately from the new extraction. They are not newly measured by this script. Historical author notes such as A5 “release event” also do not prove current visible projectile detachment.

### 2. Inclusive sample counts are mislabeled as durations

For an action range 1..37 at 30 fps, elapsed time between first and last samples is `(37-1)/30 = 1.200 s`, not `37/30 = 1.233 s`. The script uses `num_frames / fps`; the report mixes that value with the correct historical duration. Correct every duration or label the value explicitly as sample count divided by rate, and use one frame/time convention throughout. The source sidecars use ranges 0..N and provide the intended clip lengths.

### 3. Root and foot metrics are overstated

The variable named `Root Translation Delta` is actually the maximum root displacement from the first sample, not end-minus-start delta. Rename it accordingly or add both metrics. Foot/ball bone-origin Z bounds do not establish sole contact or “planted” feet. The report's VIS-07 claim that all clips are clamped to `[+0.037,+0.129] m` contradicts its raw log, including A4 `[-8.64,34.04] cm` and StaggerGetUp `[-48.30,8.24] cm`. Withdraw the clamp/grounding claim and preserve only the measured bone-origin bounds.

### 4. VIS-05 still conflates visible sockets with production trace sockets

The script extracts empties from `SM_Boss01_Greatsword.fbx`, the cosmetic visible follower. The production trace obtains `Current Collision Mesh`, `CollisionSockets` and radius from the pack target object at runtime (`RPGPackTrace::FTarget`). The raw Kwang FBX export contains no socket evidence in this log. Therefore the 21.3 cm visible-tip-to-visible-socket offset is valid offline geometry, but “threat center is shifted” and “sphere covers the tip” are not established production facts. Adding a socket to the visible sword alone cannot alter the production query. Keep the geometry fact; defer gameplay correspondence and any socket/code proposal until Claude provides the actual runtime mesh, socket list/transforms and radius.

### 5. Runtime inventory still contains unsupported active-route claims

The report calls the pack A2 appearance an “Observed In-Game Impact” without a current capture. Reclassify it as the expected consequence of the source route pending current playback evidence. More importantly, `AN_Boss01_StaggerGetUp` is not the current get-up route: `RPGBossStagger.cpp:137-139` plays `LoadedFall` backwards at `-GetUpRate`; only `FallClip` and `DownClip` are loaded. Keep the standalone FBX in the offline asset inventory, but do not describe it as the live dynamic montage. Extra pack moves remain pending Claude's complete inventory.

### 6. VIS-06 is a configuration/risk candidate, not yet a defect

The shared authored/fallback timing row is source-confirmed. `UpdateTelegraph` deliberately scales a fallback when `rpg.CloseTelegraph > 0`; Claude reports the current warm editor has it at 0 while the code default is 0.4. State the exact configuration and distinguish: current authored path, fallback activation, default stretched fallback, and explicit raw-pacing override. Separate fallback rows are only a proposal until an actual bad transition/contact is demonstrated.

### 7. Report integrity cleanup

Remove the two embedded control characters and repair malformed equations/links. Do not name Codex as the document's reviewer before acceptance; use “reviewer requested” or record the actual verdict. Keep P1-P8 proposals clearly non-authorized.

## Accepted subset and remaining gate

Accepted as usable partial evidence: current input hashes/sizes, script provenance, raw static bounds, raw sampled bone-origin ranges, stable VIS identifiers, and the explicit runtime limitations. This is not acceptance of the complete visual baseline, any runtime defect, or P0. Resubmit a corrected offline subset; runtime visuals, production trace correspondence, complete active-move coverage and packaged appearance remain dependent on Claude evidence.

No gameplay, asset, socket, rate, reach or VFX change is authorized by this review.
