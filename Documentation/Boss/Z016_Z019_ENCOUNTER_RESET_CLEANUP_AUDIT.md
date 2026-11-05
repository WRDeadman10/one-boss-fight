# Queue Z Batch 4 — encounter registration, rebind, cleanup, persistence

**Scope:** Z016–Z020, read-only source and retained-artifact audit. No tests, Unreal Editor, PIE, build, package, source, or asset changes were run. Runtime statements below describe retained Lead artifacts only.

## Z016 — selected-world registration order

`URPGPlayerMovesSubsystem::OnWorldBeginPlay` registers the actor-spawn callback before taking its pre-existing-actor census. On a requested data route it builds the transient world binding, removes owned legacy boss components, resolves the selected definition, then calls `RPGBossActivation::ActivateWorld`. A successful activation is stored before reset broadcast binding; player components and diagnostics are attached afterward. A rejected activation releases its prepared batch when present, destroys the transient binding, marks a hard error, disables/removes selected boss state, reports failure, and still attaches independent player-side components. The data route returns without falling through to legacy startup. See `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:121–244`.

The activation facade prepares the world batch before registration. Registration refusal collects registration errors, aborts the batch, checks cleanup status and owned-component count, and returns either fallback or hard error. Rebind preparation/registration refusal is always hard error. Successful registration transfers the batch into the activation result. `Release`/`ReleaseForRebind` are game-thread-only and retain the artifact on refusal. See `Source/OneBossFight/Player/RPGBossActivation.cpp:7–126` and `RPGWorldPreparation`/`RPGWorldRegistration` implementations.

Existing native test registrations include `OneBossFight.Binding.ActivationWorld.SuccessAndRelease`, `.InvalidInputAndMisuse`, `.ContentEpochRejection`, `.PreparationFailure`, and `.RegistrationFailure` in `RPGBossActivationWorldTests.cpp:522–620`, plus activation fault/lifetime tests in `RPGBossActivationTests.cpp:345–508`. These are registered source tests; not executed for this audit. The test suite does not make a live authored-level startup claim here.

## Z017 — possession/rebind epochs

Reset broadcasts are generation-gated: an equal generation is a duplicate no-op; a non-advancing generation, missing world, ambiguous local possessed player, changed selected definition/manifest/slots, failed binding census, missing candidate participant, or failed lease retag fails closed. Zero possessed players enters pending state with a 5 s timeout and 0.05 s poll. On success the existing lease is retagged, old binding destroyed, generation accepted, timers cleared, and reset delegate rebound. Shutdown clears timers, removes the reset delegate, releases the active lease, destroys the binding, and removes the spawn handler. See `RPGPlayerMovesSubsystem.cpp:248–274,354–423,430–542` and `RPGBossActivation.cpp:24–46,68–126`.

Native automation registrations include `OneBossFight.Binding.EncounterSelection.ResetBroadcastRebindsAndDeduplicates`, `.RebindGenerationRefusalFailsClosed`, `OneBossFight.Binding.EncounterLifecycle.SelectedRebindGenerationSequenceKeepsOneLease`, `.SubsystemShutdownUnbindsPendingRebind`, delayed possession, duplicate-player, dead/unpossessed player, dead boss, timeout and census-failure cases (`RPGBossStartupActivationTests.cpp:414–1059`). These are tests present in source, not run here.

Retained C915 memory-soak bundles report **20/20 reset cycles PASS** for both selected and legacy routes, with `exit_code: 0`, `timed_out: false`, selected 300 s and legacy 299 s. `result.json` raw-log SHA-256: selected `dded8f6cc0ee7c6a96c75a0f072aa73c99386db81844c8af519c558ea0044a5d`; legacy `ec41b8752ea8e58628c318f1ede962f37e2cf00027a0bfd78209f37dd55bd522`. Both `post_state.txt` snapshots hash to `d3b40a15bfe076210dd4a2a750c1117043f551cf1c7a5db56d18c2fcd502071f`. The selected raw log records generation 22/reset 21 and 1 boss/0 javelins after cycle 20; legacy records the same generation/reset count and 1 boss/0 javelins. These establish repeated-reset observations in those retained runs, beyond a single-cycle source test. They do not establish packaged behavior or an independent Codex rerun. Legacy log also contains recurring Blueprint `ClearTimer passed a bad function (UpdateLerpBar) or object (Health)` warnings; preserve as a caveat, not an attributed reset failure. Evidence paths: `Docs/BossCombatReview/Execution/Claude/C915_MEMORY_SOAK/{selected,legacy}/`.

## Z018 — EndPlay scope cleanup table

| Scope | Start / ownership | EndPlay or terminal cleanup | Source-backed gap |
|---|---|---|---|
| Hit-stop / actor custom dilation | `URPGLegendSubsystem::RequestHitStop` saves each actor's original `CustomTimeDilation` once and applies absolute hit-stop. | `Deinitialize -> CancelAll -> RestoreHitStop` restores saved actor values and clears records. | Actor weak refs that no longer resolve are skipped; retained C915 is reset-cycle evidence, not isolated cleanup-failure injection. |
| World slow motion | Request stores prior global dilation; parry pulse may also push SoundMix and set MPC scalar. | `RestoreSlowMotion` first calls `RestoreParryFeedbackPulse`, then restores global dilation only if current value still matches the applied value; otherwise leaves the external change untouched. `Deinitialize` calls `CancelAll`. | No source proof of Blueprint-authored effects outside this optional subsystem. |
| SoundMix / MPC pulse | `BeginParryFeedbackPulse` (Tier 2 preview gate) pushes configured mix and stores weak reference; sets scalar to 1 when valid. | Restore pops mix if world and mix still resolve; resets weak refs and scalar to 0 if instance survives. | Push/pop/restore code present; no direct EndPlay failure-injection automation located in this pass. |
| I-frame `Status.Invulnerable` tag | Pack notify adds; monitor tracks observed owned tag/window. | Reset/stale/death routes retry or preserve ownership on failure. EndPlay makes one `RemoveTag` call then unconditionally clears both ownership flags (`RPGIFrameMonitor.cpp:157–166`). | **Known residual teardown bug:** failed dispatch during EndPlay loses retry ownership; tag may remain on a still-live pawn. Previously recorded in `Documentation/Boss/STATUS_TAG_LIFECYCLE_AUDIT_R171_175.md`; unchanged by this audit. |
| Parry `Status.ParryActive` tag / pending stamina | Parry component owns project request/tag and retries pending payment/refund. | EndPlay retries pending cost and tag removal up to five times (`RPGPlayerParry.cpp:209–213`). | Exhausted tag-removal failures have no surviving component retry owner; same retained residual from R171–R175. |
| Dormant/wake montage scope | `URPGBossDormantWake` owns montage references and wake state; stop paths cancel encounter wake. | EndPlay calls `StopClips`, stopping both tracked montages and clearing references/state; this is montage cleanup, not an aura subsystem. (`RPGBossDormantWake.cpp:45–58,105–160`). | No aura push/pop scope found in this component. Other authored pack effects remain outside this C++ inventory. |
| Stagger posture hold | Stagger completion/end path stops owned montages and ends posture hold. | EndPlay sets phase idle (`RPGBossStagger.cpp:843–847`). | The short EndPlay override does not itself call `EndStagger`; teardown of a still-active posture hold relies on owner/component teardown semantics. No live removal experiment was run, so do not classify that as a defect. |

Related automation: `OneBossFight.Legend.DilationScope`, `.ParrySlowMotionAdmission`, `.ParrySlowMotionWorld` (`RPGAutomationTests.cpp:687–799`), dormant wake rules and adapter contracts. These registrations do not prove subsystem teardown through a live authored encounter. Broader historical lifecycle scope is summarized in `Documentation/Boss/G5_D108_D110_LIFECYCLE_RECONCILIATION.md`.

## Z019 — persistence boundary

The existing G4 audit, `Documentation/Boss/G4_SAVE_CONTENT_COMPATIBILITY_AUDIT.md`, limits its conclusion to `Source/OneBossFight`: no `USaveGame`, `SaveGame` property, `SaveConfig`, config write/flush, or config-cache write path persists selected encounter state. `SelectedDefinition` is `Transient`; benchmark path is in-memory. This does **not** establish absence of Blueprint/plugin/external content serialization or authored references, and it does not close cook/referencer gates. G4 identifies the manifest validator and Editor asset-field validator as partial current-input checks, not a full referencer/cook proof.

## Z020 — receipt, diagram, Lead-run proof still open

```text
World BeginPlay
  -> spawn delegate + existing actor census
  -> selected definition? -> build binding / remove legacy boss components
       -> prepare batch -> register owned subset
            success: retain lease + binding -> bind reset broadcast -> attach player helpers
            refusal: abort/release -> destroy binding -> hard error/disable selected boss -> attach independent player helpers
  -> reset broadcast: duplicate generation => no-op
       -> zero possessed players => poll/timeout
       -> unique player + valid next generation/selection => build rebind binding -> retag existing lease -> swap binding -> rebind delegate
       -> refusal/timeout => fail closed and release current activation
  -> subsystem shutdown => clear timers/delegate -> release activation -> destroy binding -> remove spawn delegate
```

Remaining Lead-owned proof: current build identity plus native automation run for activation and reset/rebind tests; live authored-level check of actual component/tag/montage cleanup when removing components from still-live actors; package/Blueprint/plugin persistence and referencer/cook audit; any claim beyond the exact retained C915 selected/legacy 20-cycle runs. C915 is historical evidence as of its supplied bundle, not a new run.

**Disposition:** Batch 4 complete locally. No source or content modifications. `git diff --check` is the only validation run for this documentation update.
