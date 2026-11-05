# I015 — selected-route respawn rebind transaction

Approved by Claude in C-809, based on BUILD-211's measured legacy order. The selected route follows the reset broadcast, not player spawn alone.

| State | Event / guard | Action | Next state |
|---|---|---|---|
| Active(g) | pack player spawns | Record candidate identity and start 5-second deadline; keep current lease until reset signal | Pending(g, candidate) |
| Pending(g, candidate) | matching boss reset broadcast g2 | Require g2 > g and g2 != MAX_uint64 | Releasing(g2) |
| Pending(g, candidate) | 5-second deadline expires | HardError `EncounterActivation.RebindTimeout`; disable boss; no legacy fallback | Failed |
| Releasing(g2) | old lease release clean | Emit `binding_released`; destroy old binding; exact begun-world census | Compiling(g2) |
| Releasing(g2) | release refuses or reports errors | HardError; do not destroy unsafe binding or activate new lease | Failed |
| Compiling(g2) | exact census + same selection + compiler/preflight pass | Build new transient binding and activate existing plan | Active(g2) |
| Compiling(g2) | any census, identity, generation, compile or activation refusal | Release only newly owned artifacts when safe; disable boss; preserve independent player setup | Failed |
| Any state | duplicate broadcast at accepted generation | Log idempotent duplicate; no mutation | unchanged |
| Any state | lower generation or MAX_uint64 | HardError; preserve accepted generation; no activation | Failed |

The 5-second deadline starts when the spawned replacement player is first observed. Exact participant identity and generation are retained together. Generation/count values are read from the reset broadcast, never reconstructed from elapsed time or spawn order. The runtime preparation path has an explicit begun-world API; release validates exact component ownership before calling `DestroyComponent`, so normal `EndPlay` cleanup runs. A refusal retains the batch and binding and disables the boss. Claude owns selected-mode PIE validation and the G044 definition assets remain a required live-run dependency.
