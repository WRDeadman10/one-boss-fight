# Queue J runtime capture snapshot contract

`URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot()` serializes current encounter diagnostics as `onebossfight.encounter-runtime-snapshot/v1`. It is a runtime-state snapshot for a future trusted driver; it is not by itself an A4 parity receipt.

## Captured fields

- Route and world path.
- Selected definition object path, encounter GUID, boss/player slots, initial boss phase, and the canonical `StableManifestHash` membership digest.
- Participant generation as an exact decimal string, reset count, and boss/player participant rows with actor path/class, role, slot, target slot, and typed definition object path.
- Activation outcome/reason, whether the data activation lease is held, and whether the transient binding remains retained.
- Per-role component paths, sorted for deterministic serialization. When activation refuses before a binding exists, the snapshot still records the live pack participant and component census for diagnostics.

The manifest digest is the authored definition membership digest. The runtime currently has no separate digest of serialized UE package bytes for the selection asset, so the capture never presents the manifest digest as a package-byte hash.

## Evidence boundary

The snapshot does not contain the driver ID/arguments, build and content identity, settings/input hashes, seed, measured gameplay observables, check totals, terminal result, or raw-log hash required by the v2 receipt. It also has no verified A4 PIE bridge that reads this world subsystem and persists the snapshot. Until both gaps are closed, no v2 receipt is emitted from this seam. Native automation assertions have been authored for selected success and compiler refusal, but remain unbuilt and unrun by Codex; Claude owns the build and runtime review.
