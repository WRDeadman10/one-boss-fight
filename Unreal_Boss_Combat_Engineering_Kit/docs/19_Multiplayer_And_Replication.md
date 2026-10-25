# 19 — Multiplayer Extension and Network Authority (Optional)

The kit's prototype is single-player. Adding co-op changes target selection, attack authority, collision, stagger synchronization and readable latency. Do not assume single-player Blueprint montage behavior automatically becomes network safe.

## Ownership

- **Server authoritative:** encounter state, AI attack decision, selected move/seed, phase transition, damage, posture, hit resolution, cooldowns.
- **Client cosmetic:** animation presentation, sound, VFX, camera shake, UI, predicted local defensive feedback when appropriate.
- **Replicated signals:** selected attack ID, attack instance ID, start server time, phase, target snapshot/warp target if needed, montage section, interrupt/stance events.

## Montages and root motion

Unreal supports replicating root-motion movement from montages under supported Character Movement configurations, but **Montage playback and section events still require deliberate synchronization and may require RPC/replicated state**. Test server-client montage timeline differences; don't assume a manually called `PlayAnimMontage` on server automatically displays the intended montage everywhere. Consult Epic Montage documentation in references.

## Sweeps and lag compensation

Authoritative server performs traces; client hit sparks are cosmetic until server confirmation. For PvE a short forgiveness window may be acceptable if accompanied by consistent rules; don't blindly trust clients' `HitActor` reports. Multi-player party positioning changes rear-attack and radial AoE frequency; all players must get reliable tells.

## Multiplayer-specific fairness

- Every player should see boss commitment and tracking limits similarly.
- Attack target switching is only allowed at authored retarget gates.
- Boss shouldn't instantly 180° redirect in active attack because another player healed.
- Per-victim `HitActors` tracked server-side, including rings/multi-hit windows.
- Client-side dodge iframes must be reconciled with server movement and time; test simulated 80–150ms latency.
- Ensure death/disconnect of targeted player safely closes or reselects next legal target.

## Test plan

Listen server + two clients; dedicated server; simulated 80ms/150ms round trip; packet loss; host migration only if actually supported; player join/leave mid-fight; simultaneous grabs; player death during warp; AoE damage once per wave per victim; server log event IDs match client presentation within defined tolerances.
