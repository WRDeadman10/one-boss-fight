# C-1247a: Sevarog first-five MoveCard plan

**Status (C-1251a):** source fixes and authoring script are ready; all values remain provisional, tune after PIE. Combo USTRUCTs are now BlueprintType with writable fields for the Editor Python path. Defensive counterplay measures travel from the actual end distance: max range plus backstep when moving away, warp standoff when closing forward. Script S4 Whiff now routes to Swing1_Medium (light margin estimate +0.3327 s); the fast Swing1_FAST_v2 candidate remains a standalone card and is excluded from the active profile. S4 forward-counterplay estimate is +0.1167 s. Offline contract 9/9; Development build PASS; full suite 498/498 with DD27j hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`; both C-1155 locks released. Claude owns acceptance build and script run. No script execution or assets authored.

C-1248 corrected the Ember premise: Ember uses pack abilities plus the `RPGAttackTracker` table, not framework MoveCards. Claude approved Sevarog F5 proof-card analogs as provisional sources. C-1249 added the Editor-only `URPGBossCardValidationLibrary` bridge and native parity test. The missing Ember-card source is no longer a gate.

All timings are design candidates from `C1242_SEVAROG_CONTACT_MARKING.md`, sampled at 15 Hz (about ±0.067 s), not measured traces. The F5 JSON proof set is a Sevarog framework dataset and marks damage/cooldowns as proposed. C-1248 confirms the Sevarog mesh and selected sequences share `Sevarog_Skeleton`; trace endpoints `weapon_r` and `root_weapon_end_r` are bones accepted by `DoesSocketExist`, not sockets. FullBody could not be read from Python and remains a C++ validator gate. C-1250 supplied the provisional S3/S4 values; C-1251 corrected the forward-warp counterplay math. Native profile validation and Lead PIE remain acceptance gates.

## Candidate cards

Paths below are soft references only. Never edit, duplicate, or save anything under `/Game/ParagonSevarog/`. Slot `FullBody`, the socket/bone pair, and shared damage/range values follow the closest corresponding Sevarog F5 proof card, cited in the source column. The proof set has no defensive reposition row; S4's zero-damage/no-window shape and movement limits are a new provisional proposal, not copied Ember data.

| Field | S1 `Move_Sevarog_Swing1_Medium_C1247` | S2 `Move_Sevarog_Swing2_Medium_C1247` | S3 `Move_Sevarog_Swing3_Slow_C1247` | S4 `Move_Sevarog_Speedburst_C1247` | Standalone fast candidate `Move_Sevarog_Swing1_FAST_v2_C1247` (not in active profile) |
|---|---|---|---|---|---|
| `Schema`, `FamilyId`, `PhaseId` | `1`, `Family_08_ComboSweep`, `Phase_1` | `1`, `Family_08_ComboSweep`, `Phase_1` | `1`, `Family_06_HeavySlam`, `Phase_1` | `1`, `Family_05_GapCloser`, `Phase_1` | `1`, `Family_02_AntiGreed`, `Phase_1` |
| Animation source | `Sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium.Swing1_Medium`; Montage=None | `Sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium.Swing2_Medium`; Montage=None | `Sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing3_Slow.Swing3_Slow`; Montage=None | `Sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.Speedburst`; Montage=None | `Sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2.Swing1_FAST_v2`; Montage=None |
| Skeleton, slot, section | Sevarog skeleton candidate `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton`; `FullBody`; `None` | Same | Same | Same | Same |
| `PlayRate`, root motion | `1.0`, false | `1.0`, false | `1.0`, false | `1.0`, false | `1.0`, false |
| `CommitSeconds`; active interval; recovery end (s) | `0.200`; `0.267–0.400`; `1.133` | `0.133`; `0.200–0.400`; `1.133` | `0.467`; `0.533–0.667`; `1.700` | `0.200` provisional; movement interval `0.267–1.133`; `1.267` | `0.200`; `0.267–0.333`; `0.533` |
| `TrackDegreesPerSecond` | `120` | `120` | `45` | `0` (provisional legacy F5 candidate; `FIRST_FIVE_CARDS_SPEC_TABLE.md:69`) | `180` |
| Warp start/end; distance/angle/standoff; ease | `0/0`; budgets `0/0`, standoff `0`; ease false (off) | `0/0`; budgets `0/0`, standoff `0`; ease false (off) | `0.467/0.533`; `50 cm / 45° / 100 cm`; ease false | `0.267/0.800`; `450 cm / 45° / 120 cm`; ease true; toward target (`bWarpAway=false`) | `0/0`; budgets `0/0`, standoff `0`; ease false (off) |
| Defensive flags; holds/cues | `bDefensive=false`, `bWarpAway=false`; hold off; cues empty | Same | Same | `bDefensive=true`, `bWarpAway=false`; hold off; cues empty | `bDefensive=false`, `bWarpAway=false`; hold off; cues empty |
| Range; front cone; vertical limit (cm/degrees) | `90–180 cm`; `90°`; `0` (unlimited) | `90–180 cm`; `90°`; `0` | `90–180 cm`; `60°`; `0` | Selector `300–650 cm`; `120°`; `0` | `90–185 cm`; `100°`; `0` |
| `HPDamage`; `Windows` | `25`; one direct blade window `0.267–0.400`, group `HitGroup_ScytheBlade`, `weapon_r` to `root_weapon_end_r`, radius `15 cm` | `25`; one direct blade window `0.200–0.400`, same group/socket pair/radius | `55`; one direct blade window `0.533–0.667`, same group/socket pair, radius `25 cm` | `0`; empty | `20`; one direct blade window `0.267–0.333`, group `HitGroup_ScytheBlade`, same socket pair, radius `15 cm` |
| Profile candidate cooldown (s) | `1.0` | `1.0` | `3.5` | `4.0` | `2.5` (standalone; excluded from profile) |
| Proof-data analogue | F5 `Move_Sevarog_SwingMedium_F5` | F5 `Move_Sevarog_SwingMedium_F5` | F5 `Move_Sevarog_HeavySlam_F5` | None for defensive | F5 `Move_Sevarog_AntiGreed_F5` |

The F5 values above are found at `Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json`: SwingMedium begins line 48 (timing/range/damage lines 57–80); AntiGreed line 86 (lines 95–118); HeavySlam line 124 (lines 133–156). Their sequence/skeleton/slot, windows, damage, and proposed cooldown are documented there. These are Sevarog proof analogs only. Poise is not a field of `FRPGBossMoveCardSpec`; profile fields `PostureMax`, `PlayerPostureHitAmount`, and stagger settings govern boss poise/stagger globally, so no per-move poise number is invented (`RPGBossFrameworkProfile.h:128–141`). Profile cooldown is on each candidate, not the card spec (`RPGBossFrameworkProfile.h:35–41`; selector candidate construction in `RPGFrameworkBossCharacter.cpp:73–78`).

**Limits:** C-1248 closed the value-source and mesh/socket readback gates. FullBody slot still needs the C++ validator. C-1250 approved provisional S3/S4 ranges, warp budgets and cooldown. C-1251 changed S4's profile counterplay calculation to use the forward warp standoff and revised its follow-up to Swing1_Medium; the script runs the native bridge, but Claude has not yet rerun it after this change. These remain proposed values, not runtime data.

## Validator paper walk

`RPGBossMoveCards::Validate` at `Source/OneBossFight/Player/RPGBossMoveCard.cpp:31–163` is a pure validation of the spec plus resolved metadata. It cannot prove soft references resolve or supply actual metadata by itself.

| Rule | Candidate result / condition |
|---|---|
| Schema and identity (`:34–35`) | Schema 1; every proposed MoveId, FamilyId and PhaseId is nonempty and unique per card. |
| Exactly one animation and matching path (`:36–40`) | Each row selects one Sequence, no Montage; proposed resolved `AnimationPath` must equal that sequence path. |
| Skeleton identity (`:41–43`) | All rows declare the candidate Sevarog skeleton. Pass requires resolved animation, mesh and declared skeleton paths to be exactly equal; not certified until asset readback. |
| Slot/section (`:44–46`) | `FullBody` must appear in resolved AnimBP slot metadata. `SectionName=None`; there is no montage section requirement. Slot readback remains open. |
| Root motion and numeric domain (`:47–68`) | All candidates set root motion false; F5 probe reports in-place Sevarog clips. Positive play rate, finite/nonnegative times, angles, ranges, damage and budgets; no value exceeds the 1e6 generic ceiling, 1000 cm warp cap, or 180° warp cap. Warp-off rows have both budgets zero. S3 cannot be claimed to step in until a measured/approved positive budget replaces TBD. |
| Holds/cues (`:69–86`) | Holds are off (`0/0`); cues empty, within max 8. |
| Eligibility/timeline (`:88–92`) | Cone ≤360° and min≤max. Timelines are monotonic: S1 `.200≤.267<.400≤1.133≤1.133`; S2 `.133≤.200<.400≤1.133≤1.133`; S3 `.467≤.533<.667≤1.700≤1.700`; S4 `.200≤.267<1.133≤1.267≤1.267`; S5 `.200≤.267<.333≤.533≤.533`. The final comparison is against resolved clip length, which must equal the marked/probed length. |
| Defensive shape/fairness (`:93–102`; `RPGBossDefenseRules.h:16–22`) | S1/S2/S3/S5 are nondefensive and have direct windows. S4 is defensive with no windows and zero damage; move starts at `.267/1.0=.267s≥.25s`; `bWarpAway=false`, so backstep distance rule does not apply. Profile candidate cooldown must remain `≥3s`; the profile's separate counterplay check still needs approved player reach/startup and range values. |
| Window ids, intervals, sockets, radii (`:103–139,156–161`) | Each attack has one unique nonempty WindowId and nonempty HitGroup; positive radius; ordered interval inside active bounds; direct window means no all-secondary failure. `weapon_r` and `root_weapon_end_r` are distinct and are present in F5 proof metadata, but their membership on the actual Sevarog mesh/skeleton is an unresolved asset readback gate. No baked samples, ring, grab, or secondary window is proposed. |

The source enforces profile defensive cooldown and punish/counterplay separately at `RPGBossFrameworkProfile.cpp:237–268`. C-1251's source-based S4 counterplay estimate is `0.467 - 0.3503 - max(0, 120-150)/600 = +0.1167 s`; the profile bridge remains authoritative. Combo transition data is profile-level: S1→S2 uses the Hit edge; S4→S5 uses the Whiff edge because S4 produces no hit (`RPGFrameworkBossCharacter.cpp:769–805`). The S5 node now points to the Swing1_Medium card already in the profile; the fast standalone card is excluded from the profile until its punish margin is acceptable. The target snapshot/range/yaw gates, attack budget and combo graph are set in the script; this card table does not prove an encounter route.

## Actor, profile and asset readback

- The executor is created by `ARPGFrameworkBossCharacter` (`RPGFrameworkBossCharacter.cpp:58`) and initialized after `RPGFramework::ResolveProfile` (`:60–68,94`). Its profile supplies mesh and AnimClass to the actor mesh (`:87–89`). This is the existing framework proof route; it is not proof that a production Sevarog encounter currently spawns this actor.
- The route can accept another mesh only if profile resolution returns it and each selected card's resolved mesh, animation and declared skeleton match (`RPGBossMoveCard.cpp:41–43`). `ARPGFrameworkBossCharacter` also requires two distinct weapon trace endpoints named `weapon_r` and `root_weapon_end_r` (`RPGFrameworkBossCharacter.cpp:90–93`). The checker uses `DoesSocketExist`, which can find a socket or bone; the proof JSON names these endpoints, but no evidence here confirms their existence on the exact Sevarog mesh.
- C-1248 readback (`Docs/BossCombatReview/Execution/Claude/P_C1248_SEVAROGREADBACK/readback.log`, exit 0, 0 Content changes): mesh `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog` resolves to `.../Meshes/Sevarog_Skeleton`; all five sequence skeletons match and root motion is false. `weapon_r` and `root_weapon_end_r` are distinct trace bones (`does_bone_name_exist=True`, `find_socket=None`). Useful sockets include `HammerSocket` on `hand_r` and `Weapon_01`, `Weapon_02`, `HammerCenter` on `weapon_r`; 29 sockets were logged. Python could not inspect the AnimBP `FullBody` slot, so the C++ validator remains the required gate.

## Editor script implementation gate

1. **Preflight only:** retain Claude's approval of Sevarog F5 analogs and C-1248 mesh/socket readback. C-1250 supplied the S3/S4 values and profile inputs; script checks all sourced values before proceeding. Resolve the existing project content root and refuse to run if the editor is not in the expected project.
2. **Write allowlist:** the only creation/save targets are `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft` and its five `DA_Move_Sevarog_*_C1247` children, plus `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft`. Refuse any output, rename, overwrite, delete, or save target outside this directory. Specifically reject all writes under `/Game/ParagonSevarog/` and all pack asset mutation.
3. **Read-only dependencies:** permit only the exact approved Sevarog Sequence and Skeleton soft references in this plan, loaded read-only. Never duplicate/modify/save pack dependencies. Fail closed if source path resolution returns another package.
4. **Construct typed values:** create `URPGBossMoveCard` assets with `FRPGBossMoveCardSpec` fields exactly as approved, plus a separate `URPGBossFrameworkProfile` whose `Cards` array references the active profile candidates; framework proof executor consumes this profile. `URPGBossDefinition` is a distinct definition/tracker asset and has no field binding it to the framework profile in its current declaration, so do not imply a production encounter binding. The script creates `DA_Boss_Sevarog_Draft` with `bUseMontageNotifyTimings=false`, and `DA_Boss_Sevarog_FrameworkProfile_Draft` separately. It keeps the definition unselected (there is no `bSelected` UPROPERTY on `URPGBossDefinition`). Profile combo data includes S4 Whiff→S5 Swing1_Medium at depth 2; `Swing1_FAST_v2` is not in the active profile.
5. **Validate before save:** `URPGBossCardValidationLibrary` in `OneBossFightEditor` is Editor-only and UFUNCTION-exposed. `ValidateMoveCard` calls `CompileResolved` (which runs `Validate`) with the resolved mesh, sequence and skeleton; `ValidateFrameworkProfile` calls `ResolveProfile` (which runs `ValidateProfile`). The script creates only allowlisted unsaved project assets, invokes the bridge on every card and the profile, prints every diagnostic, and fails before any save on an error or unresolved path/slot/socket. It refuses if either bridge method is unavailable. Do not claim a Python mirror is the C++ validator. No auto-fix, retarget, montage mutation, source change, or implicit default.
6. **Save/report:** only after approval and all validations pass, save the allowlisted project-owned draft assets; emit a receipt with package/object paths, serialized field dump, hashes and validation output. C-1251a updated source/script; Lead owns the acceptance build and Editor run. No content has yet been authored.

## Follow-up gates

### C-1250 approved provisional values (tune after PIE)

These are design proposals to test, not measured values. Claude approved these values in C-1250 and they are reflected in the guarded script. Runtime validation and PIE remain open.

| Open value | Proposed first-PIE candidate | Reason / validation gate |
|---|---|---|
| S3 step-in warp | `WarpStart=0.467 s`, `WarpEnd=0.533 s`, max distance `50 cm`, max angle `45°`, standoff `100 cm`, ease off | Legal interval: `0.467 <= 0.467 < 0.533 <= 0.667`; still requires resolved C++ card/profile validation and PIE displacement check. |
| S4 selector envelope | `MinRange=300 cm`, `MaxRange=650 cm`, front cone `120°`, vertical limit `0` | Lead-defined gap-closer selector envelope (C-1250); enable range-band partition so this per-card band is not forced to contain the profile walk band. |
| S4 forward warp / cooldown | `WarpStart=0.267 s`, `WarpEnd=0.800 s`, max distance `450 cm`, max angle `45°`, standoff `120 cm`, smooth ease on, toward target; cooldown `4.0 s` | Lead decision C-1250. C-1251 estimates counterplay from end standoff `120 cm`: 0 travel at 150 cm reach, leaving `0.467 - 0.3503 = +0.1167 s`; native profile validation remains the acceptance check. |

These approved proposals are not runtime evidence; the native validator/profile gate and Lead's first PIE remain authoritative.

1. **Closed by C-1248:** Claude approved Sevarog F5 analog values and corrected the Ember premise; the Lead supplied mesh/skeleton/trace-bone readback.
2. **Closed by C-1250/C-1251 at the source/proposal level:** S3/S4 proposals and forward-warp counterplay formula are decided; Lead Editor validation and PIE remain pending.
3. **Closed by C-1249:** the Editor-only bridge exposes the native card/profile validators; the native synthetic parity test and full suite passed.
4. Lead runs the guarded authoring script after BUILD-289 acceptance, keeping all pack dependencies read-only.


