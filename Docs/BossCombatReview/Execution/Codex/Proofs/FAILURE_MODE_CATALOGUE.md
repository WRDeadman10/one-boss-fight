# Opt-in live proof failure-mode catalogue (R26–R30)

This is a diagnostic guide for Claude's live runs, not evidence that any failure occurred. A log token proves only that its code path ran; compare the control/profile, geometry, input, and values as described in each EXPECTED sheet. Source citations below identify the emitted tokens or gates.

## Retained negative setup: W3/R3c (C-712)

`Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log` is **not a successful stuck-recovery proof**. It contains three `strafe_start` windows and zero `strafe_stuck` tokens. In the second window the boss is at Y=1900 (`:1783` start and `:1955` step); its logged direction changes from -1 to +1 at elapsed 1.516 s, but this is not a stuck-triggered flip because there is no `strafe_stuck flipped=1` event. The window ends normally with `reason=CandidateEligible` at `:2045` after 2.31308 s. Claude confirmed in C-712 that the edge did not block movement and stopped further W3 live-proof work. Treat R3c as a failed setup / negative evidence only; status remains unit proven, live not proven (KI-149). A live witness still requires the expected sheet's blocked movement, `movedRatio < 0.5`, and stuck token.

| Feature | Likely live failure cause | Log line and diagnostic meaning |
|---|---|---|
| WarpEaseInOut | Wrong card/profile/map is loaded, so the eased card never executes. | `telegraph_scale card=...` identifies the card only when that separate opt-in is active (`RPGFrameworkMoveExecutor.cpp:141`); `playback_start` reports montage, slot, effective rate, and fixture label, but not card ID or map/profile (`:172`). Absent `warp_ease on=1` means the warp-ease branch was not reached (`:454`). Confirm the loaded map/profile from the run manifest or authoring readback, not these playback tokens. |
| WarpEaseInOut | Warp never starts because the move has no effective warp interval/target or its timing is invalid. | No warp steps/summary despite the expected playback; `warp_step` and final `warp_summary` are emitted from the warp path (`RPGFrameworkMoveExecutor.cpp:431,476`). |
| WarpEaseInOut | Collision blocks displacement, making the A/B total-distance comparison invalid. | `warp_blocked ... actualCm=... blocker=...` (`RPGFrameworkMoveExecutor.cpp:473`); discard that equality comparison and rerun with clear geometry. |
| Strafe stuck | Profile has neutral strafe disabled or no eligible candidate starts strafe. | No `strafe_start`; start token includes range, budget, speed, and sequence (`RPGFrameworkBossCharacter.cpp:492`). Check loaded profile and candidate eligibility. |
| Strafe stuck | Cage does not intersect the boss movement capsule, so movement is not actually blocked. | `strafe_start` without `strafe_stuck flipped=1`; the stuck token reports `movedRatio` at the flip (`RPGFrameworkBossCharacter.cpp:505`). Inspect ratio and cage placement. |
| Strafe stuck | The observation window is interrupted/reset before the stuck detector accumulates enough samples. | `strafe_budget_restarted ... reason=Interrupted` signals a reset (`RPGFrameworkBossCharacter.cpp:493`); `strafe_end` marks candidate change (`:513`). |
| Yaw/cone hysteresis | The proof CVar is off or the yaw hook is not being sampled. | No `yaw_probe sample=...`; the hook is gated by positive `rpg.BossProofYawProbe` (`RPGFrameworkBossCharacter.cpp:45,430–436`). |
| Yaw/cone hysteresis | Probe samples do not cross the active card cone edge, so the control cannot demonstrate flicker. | `yaw_probe ... yaw=...` provides samples (`RPGFrameworkBossCharacter.cpp:436`); compare values with the first card's cone and check control eligibility per `YAW_CONE_EXPECTED.md`. |
| Yaw/cone hysteresis | Hysteresis profile is not active or the selector has no cone-memory state for the candidate. | `cone_hysteresis degrees=... seq=...` appears only for positive configured slack (`RPGFrameworkBossCharacter.cpp:456`); selector applies slack only to remembered candidates (`RPGBossMoveSelector.cpp:44–46`). |
| Guard chip | Hit is not accepted as a guarded hit (miss, wrong guard state, or rejection). | No `guard_chip`; this token is inside the accepted-damage + guarded branch (`RPGFrameworkMoveExecutor.cpp:291,413`). Check the same run's hit/guard outcome. |
| Guard chip | Profile fraction is zero or wrong profile is attached. | No `guard_chip` despite accepted guarded hit; emission additionally requires `Profile->GuardChipFraction>0.f` (`RPGFrameworkMoveExecutor.cpp:291,413`). |
| Guard chip | Health cap or unrelated mitigation obscures expected applied/incoming ratio. | `guard_chip incoming=... applied=...` reports final applied damage (`RPGFrameworkMoveExecutor.cpp:291,413`); use a healthy target and compare against the checklist, not the raw ratio if clamped. |
| Parry recovery | No successful parry/recovery event occurs, or the wrong grade is tested. | No `parry_recovery grade=... extra=...`; it is emitted when a pending grade is consumed (`RPGFrameworkBossCharacter.cpp:593`). Verify the parry resolution and grade first. |
| Parry recovery | Recovery scale is zero/wrong profile, so expected extra time is zero. | `parry_recovery ... extra=...` gives computed extension (`RPGFrameworkBossCharacter.cpp:593`); confirm profile scale and grade against `PARRY_RECOVERY_EXPECTED.md`. |
| Parry recovery | Different card/play rate or recovery baseline changes comparison. | `playback_start ... rate=...` identifies the actual rate (`RPGFrameworkMoveExecutor.cpp:172`); keep card and rate fixed between grades/control. |
| Telegraph fair scale | Wrong profile or card; the fair-telegraph branch is not enabled. | No `telegraph_scale card=... rate=...`; when active the token is emitted at executor start (`RPGFrameworkMoveExecutor.cpp:141`). `playback_start` identifies what actually played (`:172`). |
| Telegraph fair scale | Source timing/rate makes the requested fair rate invalid or clamps it to an unexpected value. | Compare `telegraph_scale rate=` and `playback_start rate=` for the same card (`RPGFrameworkMoveExecutor.cpp:141,172`), then compare authored timing. |
| Telegraph fair scale | Montage effective rate is not restored after completion/abort. | Require `telegraph_restore card=... rate=...` from `RestoreCardPlayRate()` (`RPGFrameworkMoveExecutor.cpp:569–578`) and compare it to the authored card rate. `cleanup reason=Finished` alone still does not prove the restored numeric rate (`:207`). |
| Aggro switching | Synthetic dodge hook did not dispatch, or events fell outside the configured window. | `player_dodge_started n=... offset=... ok=...` exposes dispatch result (`RPGFrameworkBossCharacter.cpp:334`); `ok=0` means the injected action failed. |
| Aggro switching | Rate never reaches the enter threshold, or player/range context is invalid. | No `aggro_switch`; the transition is logged only when band changes (`RPGFrameworkBossCharacter.cpp:449`). Verify the three observations and rate/window in `AGGRO_SWITCH_EXPECTED.md`. |
| Aggro switching | Enter/exit thresholds or active profile differ from test setup. | `aggro_switch from=... to=...` reports actual transition (`RPGFrameworkBossCharacter.cpp:449`); compare against expected 0.6 enter / 0.3 exit and profile values. |
| Fatigue | Whiff was not completed as a whiff (hit, cancel, or abort path). | No incrementing `fatigue whiffs=... scale=...`; token appears in the completed-move path (`RPGFrameworkBossCharacter.cpp:587`). Check result for that card. |
| Fatigue | Grace/floor profile fields are not the intended values or wrong profile is live. | `fatigue whiffs=... scale=...` reports computed scale (`RPGFrameworkBossCharacter.cpp:587`); compare sequence with configured grace/floor. |
| Fatigue | Another speed modifier obscures the expected effective rate. | Compare fatigue scale with following `playback_start rate=...` (`RPGFrameworkMoveExecutor.cpp:172`); isolate other opt-ins before attributing the rate. |
| Parry stamina | Parry input is refused before stamina is charged (invalid target/component or closed input path). | `parry_stamina ... parried=0` with unchanged before/after identifies refusal/rollback (`RPGPlayerParry.cpp:76,81,165`); inspect nearby `parry_tag` state/reason (`:190`). |
| Parry stamina | Stamina attribute lookup/read fails or cost cannot be applied/refunded. | Compare `parry_stamina before=... after=... parried=...` (`RPGPlayerParry.cpp:165`) with actual `Attribute.Stamina` reads; identical values on a verified successful parry merit checking attribute validity and cap. |
| Parry stamina | Cost/refund runs but the measurement is taken before the parry result resolves. | `parry_stamina` includes `parried` result (`RPGPlayerParry.cpp:165`); only compare successful (`1`) resolved events and capture the final value. |
| Overlay parry line | Overlay is disabled or set to screen-only while the reviewer expects a log. | CVar 0 disables, 1 is screen, 2 is screen+log (`RPGFrameworkBossCharacter.cpp:47`); mode 2 logs `[FrameworkProof] overlay ...` at `:751`. |
| Overlay parry line | Framework boss target lacks a valid player-parry component. | Logged `overlay` line omits the optional parry fields when source data is unavailable (`RPGFrameworkBossCharacter.cpp:737–751`; format `RPGBossOverlayRules.h:31`). |
| Overlay parry line | Parry opens/resolves outside the sampled overlay interval or the grade is not successful. | Mode 2 emits on state change or at one-second intervals (`RPGFrameworkBossCharacter.cpp:751`); inspect successive `overlay` lines around the input and corroborate with `parry_stamina`/parry-grade logs. |

## Profile refusal tokens and setup corrections (S135)

Profile refusals are logged as `[FrameworkProof] ERROR token=<exact token> bossInactive=1` by `RPGFrameworkBossCharacter.cpp:886–891`; validator schema `ERROR` accepts the token field (`validate_framework_proof_logs.py:51`). For `ValidateProfile` errors, `Framework.Profile.Domain` is intentionally shared by many conditions: check the named source predicates and correct the offending value/feature-lane combination; the token alone does not identify which domain failed.

| Exact refusal token | Setup correction |
|---|---|
| `Framework.Fixture.Profile` | Assign a valid loaded profile asset to the proof fixture (`RPGFrameworkProofFixture.cpp:40`). |
| `Framework.Profile.Identity` | Use fixture label F3/F4/F5 consistent with damage flag; set mesh, anim class, target class; F5 uses a nonempty Cards array and empty single Card, F3/F4 use only Card. |
| `Framework.Profile.Domain` | Check finite/domain values, F5-only opt-ins, pair/coherence constraints, profile/card weights and cooldowns, boss/player damage bounds, attack count, and shared limits in `RPGBossFrameworkProfile.cpp:53–148`; correct the first failing predicate. This token is broad, so capture a validation diagnostic or inspect the profile field-by-field. |
| `Framework.Profile.Geometry` | Require `BandMinCm < BandMaxCm`, acceptance below half-band width, and capsule radius <= half-height (`:178–179`). |
| `Framework.Profile.Alignment` | Author a finite valid mesh-relative transform with positive bounded scale and set the explicit alignment-authored flag (`:180–182`). |
| `Framework.Profile.Phase` | Use F5 with a hittable boss, `0 < PhaseTwoFraction < 1`, and a nonempty PhaseTwoId; leave both phase fields off together to disable (`:58–60`). |
| `Framework.Profile.Posture` | Use F5 and positive boss health; set all five posture values coherently, with positive max/hit amount, hit <= max, stagger 0.5–60 s, finite nonnegative regen fields; all zero disables (`:61–70`). |
| `Framework.Profile.Bleed` | Use F5 and a hittable boss; configure all bleed fields coherently with positive buildup/initial threshold, max >= initial, and HP fraction in (0,1], or set all five to zero (`:117–128`). |
| `Framework.Profile.ConeHysteresis` | Use F5 and finite `ConeHysteresisDegrees` in [0,40] (`:132–133`). |
| `Framework.Profile.NeutralStrafe` | Use F5, finite strafe budget in [0,20] seconds, and positive walk speed when enabled (`:134–135`). |
| `Framework.Profile.GuardChip` | Use F5 and finite `GuardChipFraction` in [0,1] (`:136–137`). |
| `Framework.Profile.ParryRecovery` | Use F5 and finite recovery scale in [0,3] (`:138–139`). |
| `Framework.Profile.ParryFairTelegraph` | Use F5 when enabled and finite fair minimum scale in (0,1] (`:140–141`). |
| `Framework.Profile.Aggro` | Use valid separated enter/exit range and dodge-rate thresholds; if enabled, use F5 and a finite positive bounded dodge speed (`:142–146`). |
| `Framework.Profile.Fatigue` | Use F5; grace whiffs 0–100 and floor 0–1; if either option is enabled, floor must be positive (`:147–149`). |
| `Framework.Profile.ParryPosture` | Use F5, finite nonnegative posture amount, and when positive require posture enabled and amount <= posture max (`:150–151`). |
| `Framework.Profile.ParryGradeScale` | Enable only on F5 (`:152–153`). |
| `Framework.Profile.StaggerAnim.SlotNameEmpty` | Assign the authored animation slot name when any optional animation clip is set (`:77`). |
| `Framework.Profile.StaggerAnim.CoherentSet` | Set all three stagger start/loop/end clips or clear all three (`:78`; stagger rules header `:28`). |
| `Framework.Profile.StaggerAnim.NoPosture` | Enable valid F5 posture with positive max before authoring stagger-start clip (`:79`). |
| `Framework.Profile.StaggerAnim.StartLoad` / `LoopLoad` / `EndLoad` | Repair the corresponding soft asset reference and ensure it loads as an AnimSequence with a valid skeleton (`RPGBossFrameworkProfile.cpp:281–283`). |
| `Framework.Profile.StaggerAnim.StartSkeleton` / `LoopSkeleton` / `EndSkeleton` | Use clips whose skeleton exactly matches the boss AnimBP skeleton (`RPGBossStaggerAnimRules.h:29–31`). |
| `Framework.Profile.StaggerAnim.TooShort` | Increase the relevant clip durations to satisfy the authored total stagger duration (`RPGBossStaggerAnimRules.h:34`). |
| `Framework.Profile.StaggerAnim.SlotNode` | Add the named slot node to the boss AnimBP graph (`RPGBossStaggerAnimRules.h:35`; runtime check `RPGFrameworkBossCharacter.cpp:94`). |
| `Framework.Profile.PhaseTransitionAnim.Phaseless` | Set F5, positive boss health, valid phase fraction and phase ID before assigning transition clip (`RPGBossFrameworkProfile.cpp:80`; stagger rules `:70`). |
| `Framework.Profile.PhaseTransitionAnim.Load` | Repair/load the transition clip as a valid sequence (`RPGBossFrameworkProfile.cpp:287`). |
| `Framework.Profile.PhaseTransitionAnim.Skeleton` | Match transition clip skeleton to the boss skeleton (`RPGBossStaggerAnimRules.h:71`). |
| `Framework.Profile.Combo.Empty` / `Framework.Profile.Combo.MaxDepth` / `Framework.Profile.Combo.Root` / `Framework.Profile.Combo.DuplicateNode` / `Framework.Profile.Combo.UnknownNode` / `Framework.Profile.Combo.EdgeDomain` / `Framework.Profile.Combo.Cycle` / `Framework.Profile.Combo.Depth` | Author a nonempty combo DAG, depth 1–3, existing root/node/edge targets, unique node IDs, finite valid edge bounds, and no cycle or path exceeding max depth (`RPGBossComboRules.h:52–69`). |
| `Framework.Profile.Combo.UnknownMove` | Make every combo node MoveId match a resolved candidate card (`RPGBossFrameworkProfile.cpp:223–225`). |
| `Framework.Profile.PhaseCards` | Ensure every candidate belongs to exactly phase one or PhaseTwoId, with at least one card in each (`:211–215`). |
| `Framework.Profile.PhaseCooldownStarvation` | Adjust per-phase cooldown pools so each phase can offer a candidate for the maximum configured attack count (`:216–218`). |
| `Framework.Profile.DamageBudget` | Reduce worst-card damage or attack count, or increase target health so worst hit × attack count stays below target health (`:228`). |
| `Framework.Profile.DefenseCooldown` | Give defensive/backstep cards at least the rule's minimum cooldown (`:231–234`). |
| `Framework.Profile.PunishData` | Supply valid player reach, both player attack montages, and a target class with a valid movement/run-speed default when punish margins are enabled (`:240–244`). |
| `Framework.Profile.PunishMargin` | Increase recovery margin or reduce required margin; ensure light/heavy punish checks pass for every attack card (`:245–253`). |
| `Framework.Profile.DefenseCounterplay` | Reduce backstep distance or recovery so the player can walk in and punish after the move (`:254–261`). |
| `Framework.Profile.ObjectOrThread` | Resolve only a valid profile UObject on the game thread (`RPGBossFrameworkProfile.cpp:185–186`). |
| `Framework.Profile.Dependency` | Repair soft mesh/AnimBP/target/card references; require valid concrete compatible classes and assets (`:188–195`). |
| `Framework.Profile.SequenceTelemetryOnly` | For F3/F4/F5, use sequence-only cards with allowed slot/no section, valid active timing, and zero damage unless damage-enabled; use an F4/F5 damage card only with positive sub-target-health damage (`:196–202`). |
| `Framework.Profile.DamageCard` | For damage-enabled profiles, author each nondefensive card with positive damage below target health (`:199–201`). |
| `Framework.Profile.AnimSkeleton` | Ensure the loaded sequence skeleton matches the AnimBP target skeleton (`:204–205,270–272`). |
| `Framework.Profile.ResolvedCard` | Repair the card's sequence, authored trajectory/metadata, and compile errors; ensure resolved assets are present (`:206–209`). |
| `Framework.Profile.CardBandOrBlendTail` | Align profile band with each card range unless partition mode is enabled, and keep recovery plus blend-out within clip length (`:210–212`). |
| `Framework.Profile.ParryFairTelegraph.Unachievable` | Raise the card's maximum play rate or relax the requested fairness window so the computed rate is achievable (`RPGFrameworkMoveExecutor.cpp:140`). |

The exact token is available only when the failure path calls `Fail` or fixture startup reports validation failure; a missing runtime ERROR is not proof that validation passed. `ValidateProfile` can return a token directly to its caller before the boss actor is initialized (`RPGFrameworkBossCharacter.cpp:64`), so consult the fixture/driver diagnostic too.

## Map-copy crash prevention noted by lead (C-706)

Claude reported that duplicating a `.umap` and loading the duplicate crashes the editor due to a world GC leak. The profile scripts now load `LEVEL_SRC`, set the proof fixture's profile in memory, and save the loaded world to `LEVEL_DST` with `EditorLoadingAndSavingUtils.save_map`; `make_warp_ease_profile.py` already follows this pattern. The scripts remain unexecuted by Codex.
