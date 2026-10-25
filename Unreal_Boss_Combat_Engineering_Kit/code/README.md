# C++ and Blueprint Integration References

These are **not a complete compilable `.uproject`**. They are UE5-oriented example C++ types and a narrowly scoped utility selector to explain the system boundary.

To integrate:

1. Replace project `YOURGAME`/module export conventions (this reference intentionally omits the `YOURGAME_API` symbol for portability).
2. Put the `.h`/`.cpp` files into `Source/YourProject/Boss/`; run **Generate Visual Studio Project Files** and compile with the UE 5.5 toolchain.
3. Add engine modules `AIModule`, `NavigationSystem`, `GameplayTags`, `GameplayTasks`, `MotionWarping`, `AnimGraphRuntime` as needed to `YourProject.Build.cs`.
4. Convert `UPrimaryDataAsset` class to instances and add montages. Most useful data lives in the editor.
5. Connect executor, movement, hit traces and posture described in docs 01/07/12; this sample alone **cannot run a boss**.
6. Use the standalone `combat_decision_reference.py` for **engine-independent attack score prototyping**. It does not replicate every behavior in Unreal and intentionally ignores animation availability.

`BossAttackDecisionComponent.cpp` intentionally returns deterministic maximum score for initial debugging. The production method in doc 03 uses seeded near-best stochastic choice + repetition penalties.
