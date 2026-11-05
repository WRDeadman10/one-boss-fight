# Encounter binding and reset

This page distinguishes the pack-facing `URPGBossEncounter` from the native proof boss's `RestartEncounter`; both use generations, but they have separate authority and lifecycles.

## Pack encounter reset

`URPGBossEncounter::ResetEncounter` first stops dormant/wake behavior, then refuses reset while the pack death component is actively dying. That refusal happens before remains are destroyed so the dying boss keeps its remains (`Source/OneBossFight/Player/RPGBossEncounter.cpp:299-310`). On accepted reset it closes trace state before teleport/montage changes, increments the encounter generation to stale old callbacks, and clears i-frame state (`:311-318`). It then aborts stagger, resets phases, holds behavior, clears the controller target/combat flag, forgets perception, and asks the pack combat component to clear targets (`:321-349`). The remainder resets attached combat subsystems and restores the saved home/target state (`:350-410`).

`BeginPlay` waits for pack attributes/controller state that arrive after component startup and binds reset/death behavior (`RPGBossEncounter.cpp:67-138`). It does not replace the pack's own AI or ability lifecycle.

## Framework proof boss restart

`InitializeProof` resolves and validates a profile before marking the native boss initialized (`RPGFrameworkBossCharacter.cpp:57-80`). `CanRestart` only allows a newer generation after success or death and refuses failed actors (`RPGFrameworkBossCharacter.h:57-60`). `RestartEncounter` revalidates target health and generation, then clears terminal/move/selector/phase/posture/bleed and perception memory before walking to the profile band (`RPGFrameworkBossCharacter.cpp:854-869`). This is fixture-controlled reset authority and is not the pack encounter reset method.
