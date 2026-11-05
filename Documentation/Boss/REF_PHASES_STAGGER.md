# Phases and stagger

The native proof boss applies player health, posture, and bleed contributions through `ApplyHit`. A posture break calls `StartStagger`; when the stagger ends, posture is refilled and an aborted attack is recovered before neutral selection resumes (`RPGFrameworkBossCharacter.cpp:637-660,692-723`).

## Phase transition

The profile's `PhaseTwoFraction` and `PhaseTwoId` define an optional threshold. The boss checks the threshold at a neutral decision, latches Phase 2 once, and holds selection for the transition animation duration. If `bPhaseSupersedesStagger` is enabled, crossing the threshold while staggered stops the stagger clip and runs the phase transition gate in the same tick (`RPGFrameworkBossCharacter.cpp:350-367,386-407`; profile validation `RPGFrameworkProfile.cpp:91-96`). Restart resets phase ID/latch to the first card (`RPGFrameworkBossCharacter.cpp:861-865`).

## Stagger animation sequence

The three stagger sequences are optional as a coherent set: Start plays at the break, Loop fills the middle, and End begins at `StaggerSeconds - EndLength`. All use the configured `AnimSlotName`; missing clips leave the source-defined freeze behavior in place. `TickStaggerAnim` schedules the loop count and end transition from clip lengths (`RPGFrameworkBossCharacter.cpp:692-723,817-852`; profile contract `RPGBossFrameworkProfile.h:132-139`). A stance break during an attack aborts its executor timeline and closes its windows; recovery resumes after stagger (`RPGFrameworkBossCharacter.cpp:692-723`; `RPGFrameworkMoveExecutor.cpp:571-589`).

These transitions are native proof-boss behavior. The pack-facing `URPGBossPhases` and `URPGBossStagger` components are a distinct path; encounter reset calls their reset/abort APIs (`RPGEncounter.cpp:321-328`).
