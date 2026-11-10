# Authoring a Boss Move Card

This is a field guide to `FRPGBossMoveCardSpec` and its nested window/cue records. The C++ declaration and `RPGBossMoveCards::Validate` are authoritative: [RPGBossMoveCard.h](../../Source/OneBossFight/Player/RPGBossMoveCard.h) and [RPGBossMoveCard.cpp](../../Source/OneBossFight/Player/RPGBossMoveCard.cpp). Values are card-time seconds unless stated otherwise. The C1 workflow for creating a boss profile is in [C1_NEW_BOSS_HOWTO.md](C1_NEW_BOSS_HOWTO.md); its `spec_json` points to this kind of card specification.

## Required identity and animation source

| Field | Unit/type | Authoring rule |
|---|---|---|
| `Schema` | integer | Use schema 1; zero-valued drafts are invalid. |
| `MoveId`, `FamilyId`, `PhaseId` | names | All must be set. `MoveId` identifies the card; family/phase participate in selection. |
| `Skeleton` | soft asset reference | Must resolve consistently with the animation and boss mesh skeleton. |
| `Sequence`, `Montage` | soft asset references | Set exactly one. Do not rely on the pure validator to load assets. |
| `SlotName` | name | Must exist on the resolved animation blueprint. |
| `SectionName` | name | `None` selects the full source; otherwise it must identify a montage section. |
| `PlayRate` | multiplier | Finite and positive. Timeline values below are card time; runtime animation time is affected by play rate. |
| `bUsesRootMotion` | boolean | Must be false; this backend supports in-place animation only. |

## Timeline, movement, selection, and damage

| Field | Unit/type | Authoring rule |
|---|---|---|
| `CommitSeconds` | seconds | At or after card start and no later than the active window. |
| `ActiveStartSeconds`, `ActiveEndSeconds` | seconds | Strictly increasing; active end must not exceed recovery end. |
| `RecoveryEndSeconds` | seconds | At/after active end and within the selected clip/section length. |
| `TrackDegreesPerSecond` | degrees/second | Finite nonnegative turn rate used while tracking. |
| `WarpStartSeconds`, `WarpEndSeconds` | seconds | Zero/zero disables warp. Otherwise commit ≤ start < end ≤ active end. |
| `WarpMaxDistanceCm`, `WarpMaxAngleDegrees` | cm, degrees | Bounded warp budget; distance ≤ 1000 cm and angle ≤ 180 degrees. |
| `WarpStandoffCm` | cm | Desired stopping distance from target for the bounded warp. |
| `WarpEaseInOut` | boolean | Optional smoothstep distribution; requires positive warp distance. |
| `bDefensive` | boolean | Defensive card: no hit windows and zero HP damage. A forward defensive reposition (`bWarpAway=false`) requires a positive `WarpMaxDistanceCm`; its move endpoint is checked from the target's standoff. |
| `bWarpAway` | boolean | Only for defensive cards; a backstep requires `0 < WarpMaxDistanceCm ≤ 250 cm`. |
| `HoldAtSeconds` | seconds | Zero/zero hold range disables hold. When enabled, commit ≤ hold point < active start. |
| `HoldMinSeconds`, `HoldMaxSeconds` | seconds | Seeded hold duration range, with 0 < min ≤ max ≤ 3 seconds. |
| `HoldSeed` | integer | Seed for deterministic hold selection. |
| `MinRangeCm`, `MaxRangeCm` | cm | Finite ordered eligibility range; maximum must exceed minimum. |
| `FrontConeDegrees` | degrees | Finite cone threshold used for forward eligibility. |
| `MaxVerticalDeltaCm` | cm | Zero disables vertical-separation refusal; positive value is the maximum vertical separation. |
| `HPDamage` | hit points | Finite, nonnegative damage. Defensive cards require exactly zero. |

## Cues

`Cues` is an array of at most eight `FRPGBossCue` entries. Each cue requires a unique non-None `CueId`, a non-None supported `Visual` (`HitSpark`, `DodgeDust`, or `BloodBurst`), a non-null `Sound` asset, and a `Socket` name (None means boss feet). `TimeSeconds` is in card time and cannot be later than recovery. Set `bAtHoldRelease` only when the card has a hold; then the cue fires when the hold releases and `TimeSeconds` is ignored. Cue IDs, visuals, and sounds must each be distinct within a card.

## Hit windows

Each `Windows` entry has `WindowId`, `HitGroup`, `StartSeconds`, `EndSeconds`, `SocketA`, `SocketB`, and `RadiusCm`. IDs/groups must be set; window times must be ordered inside the card's active interval; radius is positive. Socket endpoints must be distinct authored socket/bone names on the resolved mesh. An ordinary offensive card needs at least one direct window.

| Window option | Units/type | Rule |
|---|---|---|
| `bSecondary` | boolean | Secondary shockwave/splash may overlap direct windows but must share a `HitGroup` with a direct window; same-tick direct processing takes precedence. |
| `bRing` | boolean | Ring wave uses no sockets or baked samples. Requires positive `RingStartRadiusCm`, `RingSpeedCmPerSecond`, `RingThicknessCm`, and `RingHeightCm`; the wave front expands outward until the window ends. |
| `RingStartRadiusCm` | cm | Initial radius when the ring window opens. |
| `RingSpeedCmPerSecond` | cm/second | Outward front speed. |
| `RingThicknessCm`, `RingHeightCm` | cm | Width behind the front and vertical reach from ground. |
| `bGrab` | boolean | Grab uses blade sockets/radius, cannot be ring or secondary, and at most one grab window is allowed per card. |
| `GrabAttachSocket` | name | Required boss socket/bone where victim is attached. |
| `GrabReleaseSeconds` | seconds | After the grab window, within recovery; abort releases immediately without damage. |
| `BakedSamples` | array | Optional component-space blade samples; otherwise live sockets are sampled. Samples must be strictly time ordered and cover the full window interval. Re-bake after animation edits. |

Each `FRPGBakedBladeSample` has `TimeSeconds` (seconds), `BaseCS` (component-space cm vector), and `TipCS` (component-space cm vector). Do not combine baked samples with ring windows. Secondary windows must resolve to a direct window's hit group. A card must not have empty windows unless it is defensive.

## Validation boundary

Use the offline/native spec validation for schema, finite values, timing, geometry, and window rules. Forward defensive cards need a positive distance budget because runtime warp otherwise performs no reposition; backsteps use the stricter 250 cm cap. `CompileMetadata` is a metadata-only preview and does not grant playback capability. Real execution requires `CompileResolved` with already resolved skeleton, animation, and mesh assets on the game thread. The validator deliberately does not load assets or fill defaults.
