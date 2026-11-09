# C-1234 Ember notify parity driver hotfix

Addressed the three driver defects from Claude's C-1234 review. The log reader now prefers the current Unreal process's `-abslog` path and falls back to the newest `Saved/Logs` file only if `-abslog` is absent. It fails closed when the selected log does not exist or its modification time predates PIE start. This prevents a stale suite log from supplying the transition data.

Parry input uses the validated C-1132 montage-origin targets: A1 `0.27 s`, A3a `0.42 s`, and A3b `0.10 s`, each already equal to the observed target contact minus the `0.08 s` lead. Contact confirmation reads `URPGPlayerParry.GetParriedCount()`, the counter incremented in the shared `URPGPlayerParry::NotifyParried` route; the receipt logs before/after/delta and requires exactly one increment per trial.

An unmeasured, parry-free A1 move now runs after the encounter is awake and before all measured trials to absorb the first-play hitch. Its timings are discarded from the parity comparison. The PIE driver remains unrun by Codex.

## Verification

- `python -m py_compile Scripts/Editor/pie_ember_notify_timing_parity.py Scripts/Editor/test_ember_notify_timing_parity_contract.py`: PASS.
- Offline parity-driver contracts: PASS, 7/7, including quoted `-abslog` paths, fallback selection, stale-log rejection, C-1132 press targets, warm-up ordering, and the exact shared parry counter.
- No C++/Source changes were needed, so no build or native suite run was performed, per C-1234.
- No PIE run, asset edit, commit, or push.
