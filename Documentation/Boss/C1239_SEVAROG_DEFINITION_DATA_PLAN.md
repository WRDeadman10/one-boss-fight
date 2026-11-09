# C-1239: Sevarog `URPGBossDefinition` data plan

**Status:** design plan only. No definition asset, animation asset, annotation, runtime configuration, source code, or Content was changed. This is a proposed mapping of the A-720 move list to the existing typed data shape; it is not approval to create the asset or proof that the moves can run data-only.

## Scope and source rules

The plan uses `Documentation/Boss/C1239_SEVAROG_ANIMATION_INVENTORY.md` and its Section 7 move list, with engine-read facts traced there to `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log`. The exact runtime authoring shape is `URPGBossDefinition` in `Source/OneBossFight/Player/RPGEncounterBinding.h` and `FRPGAttackTiming` / `FRPGAttackTrackerConfig` in `Source/OneBossFight/Player/RPGAttackTracker.h`.

The move list's “Estimated Timing” ranges and its narrated combat roles are design hypotheses, not probe measurements. They are deliberately excluded as values for `CommitTime`, `ActiveStartTime`, `ActiveEndTime`, `RecoveryEndTime`, damage, reach, cooldown, phase threshold, or any other runtime field. Sequence duration and `root_motion=False` are the only per-sequence animation facts used below; montage root motion is `n/a` in the probe. `root_motion=False` does not establish whether the animation's root bone translates; root-bone displacement has not yet been measured. No timing window can be inferred from clip length.

Owner constraint from C-1239: use Sevarog's own animations and do not retarget. C-1240 reports that probe v2 resolved both `Swing1_Medium_Montage` and `Swing2_Medium_Montage` notifies as `NamedNotify SaveAttack` and `ResetCombo` (the Paragon combo-chain markers). This resolves their identities, not their timestamps, combat windows, or suitability as the final authored contract. Do not repurpose or mutate the pack montages.

## Definition outline (all unfilled values remain TBD)

| `URPGBossDefinition` field | Plan | Evidence / gate |
|---|---|---|
| `Schema` | Use the class schema value `1`. | Native declaration, `RPGEncounterBinding.h`. |
| `DefinitionId`, `PresentationId` | Unique Sevarog values; names and uniqueness check TBD. | Choose and validate when an asset is authorized. |
| Definition asset path | TBD under the project data root; do not create one in this plan. | Must be unique and pass checklist preflight. |
| `Skeleton`, `Animations` | Use only the actual Sevarog skeleton and project-owned Sevarog animation dependencies confirmed by asset readback. Include each referenced animation in the dependency list. | Probe inventory confirms animation facts, but the final skeleton/path/reference set must be captured and validated before authoring. No retargeted clips. |
| `Stats`, `EncounterPolicy`, `ParrySlowMotion`, `StaggerPolicy`, `PhaseFlow`, `Phases` | No values proposed. Select only after source/owner design inputs are available and record each selected non-default value in `Fields`. | Existing C++ defaults describe authoring defaults and are not evidence of desired Sevarog behavior or serialized values. |
| `Fireball` | Leave disabled unless a Sevarog move is deliberately assigned to a verified existing projectile ability. | The A-720 move list supplies no fireball mapping. Do not repurpose it as an assumed ranged solution. |
| `PhaseDependencies` | Transition montage, roar clip, and immunity effect remain TBD; do not borrow Boss01 or pack references by default. | Asset references are typed fields, but existence, skeleton compatibility, cooking, and transition behavior require verification. |
| `StaggerProfile` | Candidate Sevarog reaction references are `Stun_Start`, `Stun_Loop`, and `Stun_End`, but the current record has fall/down and riposte clip slots, not a start/loop/end sequence contract. Do not force-fit the three states into unrelated slots. | Requires a code/behavior seam below or a separately verified existing state driver. |
| `DormantWake` | `WakeClip` can be evaluated against the probed `Wake` sequence; dormant clip and playback entry point remain TBD. `LevelStart_Montage` is not a field in this record. | The montage was read as 5.000 s / one `Default` section; that does not prove it is the dormant-wake component's accepted input. |
| `Bleed`, `LowSweep`, `Shockwave`, `HealPunish`, `CloseClipSwap` | Leave unused/unconfigured unless a move is explicitly approved and its mechanic matches the corresponding adapter. | These typed records are specialized existing mechanics; similar names or visual concepts are not proof of a semantic match. In particular, do not use Bleed for Soul Siphon. |
| `Look` | Sevarog body, pieces, weapon, socket, and attach transform all TBD pending actual asset/socket readback. | The struct can carry mesh and sword references, but does not establish compatibility or a correct weapon attach. |
| `Death` | Candidate `Death_front` sequence (0.966667 s) may be evaluated for `DeathClip`; montage path/mode and playback integration remain TBD. | Probe fact is sequence duration/root motion; using it requires the death adapter's selection and live behavior gate. |
| `AttackTracker` | Proposed rows below; `bEnabled` and policy values need explicit source/design approval. Each numeric timing field remains unset until per-montage timing evidence exists. | Tracker configuration observes active montage timing; it does not itself implement move selection, damage, target effects, or capsule movement. |
| `bUseMontageNotifyTimings` | Keep `false` in the draft. Change to `true` only after Sevarog annotations pass strict audit and the matching typed source field is present. | C-1237a default-off and provenance behavior; NEW_BOSS_CHECKLIST steps 2–3. |
| `Fields` | Build a complete typed provenance row for each authored non-default/runtime-significant field, including `FieldPath`, type/value/units, source path + SHA-256, source site, origin, precedence, destination, first read, and witness. | `FRPGParityField` and binding preflight. Missing/unsupported provenance is a stop, not a default to guess. |

## Proposed tracker rows from the move list

The IDs shown are the inventory's proposed `A1`–`A7` labels, not newly approved native move identities. Asset names and durations below are readback facts; role, timing, and mechanic semantics remain proposed. `MontagePath` must point to the exact Sevarog-owned montage after path/skeleton verification. The timing windows remain TBD for all rows.

| Proposed move | Candidate animation(s) and probe fact | Data-only fit / unresolved part |
|---|---|---|
| A1: close combo first strike | `Swing1_Medium_Montage`, 1.133317 s, one `Default` section, `SaveAttack` and `ResetCombo` notifies (C-1240 probe v2; base inventory rows `probe_sevarog.log:1154–1155`). | Candidate `FRPGAttackTiming` row once the project-owned montage/annotation contract and timings are audited. A tracker row does not decide when the AI selects the follow-up. |
| A2: close combo follow-up | `Swing2_Medium_Montage`, 1.133317 s, one `Default` section, `SaveAttack` and `ResetCombo` notifies (C-1240 probe v2; base inventory rows `:1156–1157`). | Candidate row, timing TBD. Combo sequencing/branch choice must be supplied by a verified existing ability or a code add-on. Do not mutate the pack montage. |
| A3: delayed heavy | `Swing3_Slow`, 1.700 s, `root_motion=False`, zero notifies (`:1179`). | Sequence needs a project-owned Sevarog montage before it can be referenced as the attack tracker's active montage. The proposed delayed windup is not measured by duration. The listed slam step-in requires displacement behavior too. |
| A4: gap closer then strike | `Speedburst`, 1.267 s, and `Swing1_FAST_v2`, 0.533 s; both sequences are `root_motion=False`, zero notifies (`:1198`, `:1163`). | Two animation dependencies are possible; montage/ability dispatch and actual capsule translation are not represented by these sequence facts or by timing rows. |
| A5: area-denial hex | `Subjugation`, 2.867 s, `root_motion=False`, zero notifies (`:1194`). | Candidate animation only. Targeted ground warning, area/spawn, damage, snare, and interruption semantics are not shown by the clip or a matching field in the current definition. |
| A6: signature cleave | `Ultimate_Swing_120fps`, 2.633 s, `root_motion=False`, zero notifies (`:1190`). | Candidate animation only. Phase gate and 360-degree damage/coverage/knockback semantics need an existing verified ability or code. |
| A7: life-drain hex | `Soul_Siphon`, 1.833 s, `root_motion=False`, zero notifies (`:1195`). | Candidate animation only. Frontal target selection, damage/channel behavior, interruption, and healing transfer need an existing verified ability or code. Do not map it to the unrelated Bleed profile. |

For each eventual `FRPGAttackTiming`, `MoveId`, exact montage reference/path, `bAuthoredWindup`, `CommitTime`, `ActiveStartTime`, `ActiveEndTime`, `RecoveryEndTime`, turn rate, branch-stage flag, and any branch policy must be decided from reviewed behavior/timing evidence. The A-720 estimates are not acceptable evidence. `bUseMontageNotifyTimings` stays off until each annotation and its provenance is valid; then the checklist's fresh-log off/on parity run must pass.

## Work still requiring code or a verified existing runtime route

These are capability gaps in the evidence/schema, not a claim that no reusable project ability exists. Before adding code, inspect and prove any proposed existing route. If none covers the contract, the listed behavior needs a code add-on and native tests. Never edit the pack assets in `/Game/ParagonSevarog/`.

1. **Move selection and combo orchestration:** select A1–A7 from combat state/range/phase, play the selected Sevarog montage, chain A1 to A2, and interrupt/branch consistently. `URPGAttackTracker` records timing for an active montage; it is not an AI ability dispatcher.
2. **Move displacement (A4 gap closer, any lunge, and A3 slam step-in):** all Sevarog sequences report `root_motion=False`, but root-bone translation has not been sampled. Two options remain: **(a)** on duplicated project-owned copies only, enable root motion only if a guarded root-bone sample proves translation exists and review the result; or **(b)** implement a reusable data-driven move-displacement add-on (for example, per-move distance/curve) with collision-safe capsule movement. Do not assume root translation from the animation, and never change `/Game/ParagonSevarog/` pack assets. The A4 dash still needs sequencing into the follow-up swing.
3. **A5 Subjugation effect:** telegraph a target/ground area, spawn or evaluate the rupture, apply area damage/snare, and define interrupt/cancel behavior.
4. **A6 ultimate effect:** enforce phase eligibility and implement verified 360-degree hit coverage plus any radial knockback. A swing animation does not establish its collision arc or damage.
5. **A7 Soul Siphon effect:** choose/validate the frontal target or cone, apply channel damage, transfer the specified health to Sevarog, and stop on interruption/death/range loss. No transfer semantics are in the current move row or the unrelated Bleed config.
6. **Stun start/loop/end state driver:** play `Stun_Start` → looping/vulnerable `Stun_Loop` → `Stun_End` and connect the vulnerable interval to posture/riposte state. `FRPGStaggerProfileConfig` has no three-state sequence field contract; implement or identify a verified compatible driver.
7. **Intro playback entry point:** trigger `LevelStart_Montage` at the intended encounter start and handle completion/skip/reset. Existing `DormantWake` holds sequence references and does not by itself prove a montage start route.
8. **Damage/contact source:** bind each row's active interval to the correct Sevarog weapon trace/contact source and prove hit/parry behavior. The montage inventory does not show combat traces, notify timestamps, damage, or parry semantics. Reuse is acceptable only after exact Sevarog binding and runtime proof; otherwise add an adapter/ability and tests.
9. **Presentation/asset binding:** if verified Sevarog mesh, skeleton, weapon socket, death, wake, or transition references cannot be expressed by the existing typed fields, add the smallest typed config/adapter and native validation. No reflection-only or unproven path substitution.

## Remaining checklist sequence and acceptance

1. Lead reruns the guarded name-read probe; resolve the two `Unknown` swing montage notify identities. Obtain the exact Sevarog skeleton, mesh, montage, and socket paths from readback.
2. Review each move's gameplay contract and choose which rows can use an existing verified ability vs. which require the code add-ons above. Approve source-backed stats, policies, phases, and presentation inputs.
3. Author Sevarog-owned attack montages/annotations with an idempotent authoring script that refuses conflicting assets/notifies, preserves unrelated notifies, reloads, reads back, and passes the strict audit. No retargeting.
4. Produce the final definition asset and complete `Fields` provenance; run definition preflight/native binding validation and validate all animation skeleton dependencies.
5. Only after strict audit, set source-backed `bUseMontageNotifyTimings=true`; Lead runs fresh-log off/on PIE timing parity on the data route using the hitch-aware driver. Keep the run ID, build ID, map/route, and raw log.
6. Lead reviews and accepts that evidence. Until then the Sevarog definition pipeline and move behaviors remain planned, not proven.

## Source index

- `Documentation/Boss/C1239_SEVAROG_ANIMATION_INVENTORY.md` (engine facts and A-720 proposed move list).
- `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log:1152–1217` (probe rows cited by the inventory); C-1240 reports the v2 notify names and root-motion readback.
- `Source/OneBossFight/Player/RPGEncounterBinding.h` (`URPGBossDefinition`, typed policy/config fields, and provenance record).
- `Source/OneBossFight/Player/RPGAttackTracker.h` (`FRPGAttackTiming`, `FRPGAttackTrackerConfig`, and tracker behavior).
- `Documentation/Boss/NEW_BOSS_CHECKLIST.md` (definition, annotation, strict audit, parity, and completion gates).
- `Documentation/TEAM_MAILBOX.md` C-1239 and A-720 (assignment and owner animation constraint).
