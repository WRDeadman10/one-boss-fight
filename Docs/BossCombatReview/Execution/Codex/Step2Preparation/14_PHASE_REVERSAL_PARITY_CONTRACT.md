# Phase adapter: reversible effects and capability boundary

Codex,2026-10-27. Read-only source audit and future witness design. No native change, new supported multiplier range, adapter release or Unreal execution. Refines09/PacketD0; all83 requirements remain active.

## Source facts and correction

1. `RPGBossPhases.cpp:62–72` samples `BaseWalkSpeed` during BeginPlay. A full-file search finds only that assignment in the implementation; removal does not use this cache. Earlier09's “reset restores” wording was too broad and is corrected there.
2. `:349–370` applies buffs once under `bBuffsApplied`, multiplies current speed, scales the then-current ability arrays and records additive `AppliedAttack = Attack*(DamageScale-1)` only when Attack is readable and positive. It sets the applied flag before dependency writes; the flag is not proof every effect succeeded.
3. `:373–394` divides the CURRENT movement speed by CURRENT `MovementScale`, rescans current ability arrays with `1/AttackRateScale`, and subtracts saved AppliedAttack only when it is positive and Attack remains readable. This is inverse arithmetic under assumptions, not restoration of all original values/objects.
4. `:397–449` traverses `CreatedAbilities` using class-prefix/exclusion filters, reflected arrays whose struct names contain AbilityMontage, and the first floating PlayRate-prefixed field. Log Scaled counts entries visited, not unique animations, actual playback rates or unchanged membership since application. It is not a grant/execution or runtime effective-rate witness.
5. `:177–180` scales a pack-written movement value when it differs from LastSetSpeed by more than0.5. External writes between ticks and reset therefore need ordering evidence. An unscaled external write immediately before removal would also be divided; no occurrence is established here.
6. `:321–345` ends transition/posture hold, checks death and avoids buffs/behavior resume if Health reads <=0. Read failure is not that death branch. `:526–550` reset removes buffs/immunity and ends posture hold; Encounter.cpp:309–325 closes trace, advances generation, aborts stagger then resets phases; later:380–382 resets posture pool. Preserve sequence and distinguish intermediate from final observations.

## Capability gaps before general data input

Current scaffold `RPGEncounterBinding.cpp:35–48` accepts positive finite phase multipliers, including an AttackMultiplier below1. Native removal's positive-only AppliedAttack condition is asymmetric for that range. Algebraic example, NOT an executed engine test: Attack100 and DamageScale0.5 produce AppliedAttack=-50 and Attack50; removal's `AppliedAttack>0` guard does not reverse that reduction. Current Boss01 default1.25 does not exercise this range. Decide an explicit supported native-adapter capability domain or separately review reversible-effect support before accepting such a definition. This audit authorizes neither a new clamp nor a gameplay fix.

Movement and rate reversal also assume the relevant factors are unchanged and nonzero, and rate reversal assumes compatible object/entry membership. Immutable participant config does not by itself make BlueprintReadWrite component properties or runtime pack arrays immutable. Live reconfiguration while effects are active must remain unsupported until an explicit design and proof exist; do not silently reread another content epoch on reset.

If an ability entry appears after application but before removal, the rescan can divide an entry that was never multiplied. If the original ability/array disappears, inverse traversal cannot prove it restored that original object. These are conditional source deductions, not observed failures or permission to change pack logic. Preserve legacy behavior in extraction; distinguish a parity finding from a separately scoped correction.

## Future witness matrix — NOT RUN

| Case | Independent observations required |
|---|---|
|Default full cycle, repeated cycle|Before apply, after apply, before reset, after reset: actual movement speed, factor, AppliedAttack/Attack, full ability object identity+array/property/entry path+stored rate. Repeat to expose accumulation; compare effective observed values, not just flags or aggregate Scaled count.|
|External movement write|Observe pack state-change write both before a normal phase tick and immediately before reset; record order and expected current-value inverse behavior. Do not assert cached startup speed restoration.|
|Rate membership change|Pin per-entry identities; add/remove/replace eligible ability only in a separately approved fixture. Compare intersection and unmatched entries explicitly. A same count or same montage name is insufficient.|
|Damage factor domains|Positive below1, exactly1 and above1; capture current native asymmetry separately from proposed adapter capability validation. Unsupported content must not silently become valid through scalar-only compilation.|
|Partial dependency/read failure|Missing ASC/array/readable Attack at apply, then present at removal and inverse. Record per-effect write success/absence; bBuffsApplied alone cannot close case.|
|Reset/transition/death/hold|Pin generation and trace/stagger/phase/posture event order, sampled health readability, hold transfer and final pool; no buff/resume on positively observed death. Preserve failed attempts and unobservable states.|

Source pins (raw SHA256): Phases.cpp `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06`; Encounter.cpp `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d`; Posture.cpp `b26e184b0410e858d1c504e0b374dbc9e8f4c6b6399b05617559bb6909e88e41`; scaffold Binding.cpp `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` (existing independently verified preflight pin). Line anchors are this snapshot, not a runtime proof.

## Stagger-to-phase handoff source addendum — 2026-10-27

This refines the existing unrun hold/transition witness, not a new gameplay hold system. `RPGBossStagger.cpp:432–485` first marks Phase Idle/sets cooldown, removes immunity, then calls Posture.RefillAfterBreak at465 **before** attempting queued phase transition at479. If transition starts, it clears its own bBehaviourHeld at481 and does not call ResumeBehaviour; otherwise it resumes. The bool handoff is behavior ownership, distinct from posture's hold enum.

`Posture.RefillAfterBreak:148–156` ends an existing hold with refill, or sets full pool/current LastDrainTime when no hold. `Phases.StartTransition:254–281` begins Pinned posture hold (when enabled) and inherits or acquires behavior hold. Thus the default queued path is not a direct Zero-to-Pinned hold preserving zero: it refills, then pins that refilled current pool. `Posture.BeginHold:168–178` ignores requests if any hold is already present; it is not a nested/reference-counted ownership API. `FinishTransition:324–329` ends hold without refill, restarting regen delay only if a hold was active. No immutable config should contain mutable HeldValue/LastDrainTime or pretend it provides an ownership token.

Reset uses a different path: Encounter325 is preceded by Stagger.AbortStagger321. AbortStagger825–840 calls EndStagger(false,true) if active (no queued phase/resume), clears its behavior flag, then EndHold(true). Phase reset later removes buffs/immunity and ends hold; Encounter eventually calls ResetPool382, whose final LastDrainTime=-1 supersedes intermediate EndHold timestamps. Observe final state AND order; an intermediate refill timestamp is not evidence the completed encounter reset preserves it. A later successful drain writes a new current timestamp before regeneration, per Posture105; do not expect immediate regen after that drain.

Existing `RPGBossRules.h:64–88` break/transition priorities and Phases.BeginPlay Stagger tick prerequisite/pending-intake deferral must remain part of the combined witness. A pair of correct scalar assignments does not establish the handoff ordering or cancellation semantics. Observe no behavior-resume gap, actual hold enum/pool/current time and cancellation in queued/death/reset cases only after a separately authorized implementation/fixture. These source paths have not been rerun here and prove no new race or hold bug.

Additional raw source pins: Stagger.cpp `c711d766b4fecb6999c638cf5d8720ca422ba758223f941ea437ebac5b474c98`; BossRules.h `e16744219deffffab4de69ddd62e5333c1b59ac43cc670c9e777aee3fd397395`; BossMath.h `89ff1aa3c367da2fe84de1583da889dd623bddd11787c416d43792f15cc2ebf0`. Existing14 hash cited by AG10 is historical after this explicit addendum; compare/version findings, do not silently refresh old evidence.
