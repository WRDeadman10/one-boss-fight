# I011 — participant generation contract

The reset delegate is the sole selected-route rebind trigger. The `uint64` generation supplied by `URPGBossEncounter::OnResetBroadcast()` identifies the participant snapshot after a successful encounter reset; `ResetCount` is diagnostic only and is not the identity key.

- Generation zero means uninitialized and is never accepted for a participant.
- The initial selected activation uses the encounter's current nonzero generation and records the exact boss/player actor identities.
- A respawned player pawn is only a pending candidate. Spawn detection does not release or activate anything.
- A reset broadcast is accepted only when its generation is strictly greater than the last accepted generation and is not `MAX_uint64`.
- `MAX_uint64` is an exhausted state and is refused before releasing or publishing a new activation. No wrap, reset, or inferred generation is allowed.
- Repeated same-generation broadcasts are idempotent no-ops. A lower generation is stale and refused without changing the accepted generation.
- The participant generation belongs to one world encounter lifecycle. A world teardown ends that lifecycle; a new world's initial generation comes from its own initial activation, not from a process-global counter.

The current pack component exposes an `int32` encounter generation. The rebind seam must widen that source before it can claim the full `uint64` contract; until then it must fail closed before signed overflow rather than cast a wrapped value into the participant key.
