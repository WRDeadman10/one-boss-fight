# Truth audit: what actually runs in L_SevarogArena (2026-11-13)

Lead: Claude (owner directive 2026-11-13). Method: three independent read-only audits (player, boss, features and logs) of source, scripts, config and the owner's latest editor log (`Saved/Logs/OneBossFight.log`). Nothing was changed.

## The short answer

**The game feels "entry level" because most of the work built over 20 days is not switched on in normal play.**
- Hundreds of systems were written, and 573 automated tests pass (Gate 1, today).
- But the boss you see is the Ember Warden route; Sevarog is not in the map.
- The player is the pack mannequin; Greystone is a test switch whose animations are broken.
- Many delivered features default to off, and no attack has a sound or effect cue.
- Much of the last two weeks went into tests, tools and documentation rather than visible gameplay. That was a leadership mistake, and it is what this report corrects.

## Player: is it done? **No.**

| What you saw | Cause (evidence) | Fix |
|---|---|---|
| Greystone "animation not working" | The animation layer (`ABP_UnarmedLayer_Grey` / `ABP_CombatAnimLayersBase_Grey`) fails **1,170 times** in one session: `GetMainAnimBP` returns None, so the locomotion state machine never advances (log line 2177 onward). Known issues KI-040 and KI-052, still open | Run the guarded repair `repair_grey_layer_parents.py`, then check that the layer's main-AnimBP link matches Greystone's AnimBP (editor run) |
| "Drags through the ground" | The Greystone roll animations carry their movement in the pelvis bone, not the root (roll root 0.00 cm, pelvis 511 cm; KI C-1284). The character capsule does not move while the mesh does | Run `retarget_greystone_pack_rolls_rm.py` (root-motion copies), then `repoint_greystone_rolls_rm.py` (editor runs). **Written, never run** |
| Dodge is the Mixamo clip | **By your decision of 2026-11-08** (the pack backstep was rejected, the Mixamo backstep chosen). A dodge with no direction plays the backstep. Directional rolls are the broken ones (row above) | none beyond the roll fix |

**Default player:** still the pack mannequin. Greystone becomes the default only after the fixes above and your O4 decision.

## Boss: is it done? **The Ember Warden works; Sevarog is not done.**

- **Default fight:** the pack great-sword boss, re-skinned as the **Ember Warden**. The data file is confusingly named `DA_Sevarog_G044_Encounter`, but it points at the Ember boss. Gates 0-2 are built and tested on this route; Gate 3 is code-complete; balance (M14) is open.
- **Sevarog:** a native boss with 8 move cards and phases exists, and its attacks passed live tests under test drivers (8/8). **But:**
  - it is **not placed in `L_SevarogArena`**;
  - it can only be started by a Development test switch;
  - it is **blocked by your decision O1** (X-1991): its health, posture and phase values are unset (zero), so it cannot start a real fight;
  - its normal AI selection loop has not been proven, because the tests used forced-start hooks.

## Features "not loading"

- About **9 player-visible features are off by default**, and nothing turns them on: boss hit reactions, the framework (Sevarog) selection, Greystone, Tier 1 art, boss camera blocks, the retry button, the fireball phase attack, and more. Most were built "opt-in, default off" to stay safe, then never switched on.
- **No sound or effect cues** on any authored boss attack (cue lists are empty, waiting on your SFX picks, O2).
- **Live errors** in normal play:
  - the CommonUI viewport error;
  - a stamina bar timer bug (19×);
  - an input-buffer empty-array warning (23×);
  - a DLSS initialisation-order error.

## Plan: playable build first, everything else frozen

| Step | What | Who | Needs |
|---|---|---|---|
| 1 | **Fix Greystone:** layer repair, root-motion rolls, repoint, then play-test (0 animation errors, rolls move the capsule) | Codex builds the locked runner; Claude verifies; AG reviews | engine (editor closed during runs) |
| 2 | **Sevarog values** | **You** | answer O1: health 1500, posture 100, phase-2 at 60%? posture regen 6 s at 13/s? Phase 1 speed/rate/attack all 1.0? (yes/no, or your numbers) |
| 3 | **Put Sevarog in the arena** as the real boss: author its values, place it in the map, prove the normal AI loop, make it the default route | Codex implements; Claude verifies | step 2 |
| 4 | **Switch on the dormant features** that are ready (hit reactions etc.) and fix the live errors (stamina timer, CommonUI) | Codex | your yes on the list |
| 5 | **Sounds:** pick SFX (O2); we wire them into the cue slots already planned | You, then Codex | O2 |
| 6 | **Make Greystone the default player** | You (O4) | steps 1 and 3 verified |

**When can you see it?**
- **Step 1** (a Greystone that animates and rolls correctly) is the next engine work and can be ready for your play-test soon after the runs pass. These are the first real runs of those repair scripts, so a failure means another fix round.
- **A Greystone vs Sevarog playable build** depends on your O1 answer. After it, steps 3-4 are a few rounds of engine runs.
- I will not give a date I cannot prove. You will get a play-test request at each step instead.
