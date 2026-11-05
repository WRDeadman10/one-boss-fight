# Authoring a framework boss move card

This is a source-backed field reference for `FRPGBossMoveCardSpec` and its nested window/cue/sample structures in `Source/OneBossFight/Player/RPGBossMoveCard.h`. The authoritative rules are `RPGBossMoveCards::Validate` in the adjacent `.cpp`; validation fails closed and never loads assets or supplies tuning defaults. A metadata preview is not playback proof: only `CompileResolved` retains the real skeleton, animation, and mesh.

## Card identity and animation

| Field | Unit / default | Rule |
|---|---|---|
| `Schema` | integer / 0 | Must be 1. Zero draft is invalid. |
| `MoveId`, `FamilyId`, `PhaseId` | names / None | All required. Window IDs are unique within a card; family and phase feed selector grouping. |
| `Skeleton` | soft asset / null | Must resolve to the same skeleton as the selected animation and mesh. |
| `Sequence`, `Montage` | soft asset / null | Exactly one is set. Selected source path must match metadata. Montage sections are checked when named. |
| `SlotName`, `SectionName` | names / None | Slot must exist on the source; a named section must exist in a montage. None section means full source. |
| `PlayRate` | multiplier / 0 | Finite and positive, within validator domain. Used when converting card time to playback time. |
| `CommitSeconds` | seconds / 0 | Timeline starts at commit; no targeting/turn before it. |
| `ActiveStartSeconds`, `ActiveEndSeconds`, `RecoveryEndSeconds` | seconds / 0 | `commit <= activeStart < activeEnd <= recoveryEnd <= clipLength`. |
| `TrackDegreesPerSecond` | degrees/s / 0 | Finite, nonnegative; maximum facing turn rate during tracking. |
| `MinRangeCm`, `MaxRangeCm` | cm / 0 | Finite, nonnegative; max must be at least min. |
| `FrontConeDegrees` | degrees / 0 | Finite, nonnegative, at most 360. |
| `MaxVerticalDeltaCm` | cm / 0 | Finite, nonnegative; zero means no vertical-difference limit. |
| `HPDamage` | health points / 0 | Finite, nonnegative; defensive cards require zero. |
| `bUsesRootMotion` | bool / false | Root motion is unsupported; true is rejected. Animation metadata must also report no root motion. |
| `WarpStartSeconds`, `WarpEndSeconds` | seconds / 0 | Warp is off when both budgets are zero. If enabled: `commit <= start < end <= activeEnd`. |
| `WarpMaxDistanceCm`, `WarpMaxAngleDegrees` | cm, degrees / 0 | Finite budgets, capped at 1000 cm and 180 degrees. `WarpEaseInOut` requires positive distance budget. |
| `WarpStandoffCm` | cm / 0 | Finite, nonnegative target spacing used by the bounded warp. |
| `WarpEaseInOut` | bool / false | Optional smoothstep distribution of the distance budget. |
| `bDefensive`, `bWarpAway` | bool / false | Defensive card has no windows or damage and must have a readable telegraph; warp-away belongs only to a defensive card and requires 0–250 cm backstep budget. |
| `HoldAtSeconds`, `HoldMinSeconds`, `HoldMaxSeconds` | seconds / 0 | Off at 0/0; when active, `commit <= at < activeStart` and `0 < min <= max <= 3`. |
| `HoldSeed` | integer / 0 | Seed for deterministic hold duration selection. |
| `Cues` | array / empty | At most 8; each cue needs unique ID, non-None in-range visual and sound. Cue IDs, visuals, and sounds cannot collide. |
| `Windows` | array / empty | Required except defensive cards. Direct windows lie inside active interval and do not overlap; secondary windows may overlap but share a hit group with a direct window. |

## Nested records

`FRPGBossCue`: `CueId` (required name), `TimeSeconds` (seconds within recovery), `bAtHoldRelease` (bool; requires an enabled hold and ignores cue time), `Visual` (`HitSpark`, `DodgeDust`, or `BloodBurst`; `None` invalid), `Sound` (required soft sound asset), and `Socket` (name; None means boss feet).

`FRPGBossMoveWindow`: `WindowId` and `HitGroup` (required names; repeated hit groups intentionally deduplicate contacts); `StartSeconds` / `EndSeconds` (seconds within active interval); `SocketA` / `SocketB` (distinct mesh socket or bone names for a blade sweep); `RadiusCm` (positive sweep radius); `bSecondary` (bool, shared direct hit group required); `bRing` (bool, ring mode excludes sockets and baked samples; `RingStartRadiusCm` cm, `RingSpeedCmPerSecond` cm/s, `RingThicknessCm` cm, `RingHeightCm` cm); `bGrab` (bool, blade window only, at most one per card); `GrabAttachSocket` (existing boss socket/bone); `GrabReleaseSeconds` (seconds, after window end and no later than recovery); `BakedSamples` (optional samples that cover the entire window). Ring and grab cannot be combined; grab cannot be secondary.

`FRPGBakedBladeSample`: `TimeSeconds` (seconds, strictly increasing, at/around window coverage and within clip), `BaseCS` and `TipCS` (finite component-space vectors). A bake is copied animation data: rebake whenever its animation changes. Structural validation does not prove the samples still match the animation.

## Authoring workflow

The C1 guide at [C1_NEW_BOSS_HOWTO.md](C1_NEW_BOSS_HOWTO.md) documents the project-level profile/level flow. For cards, author the card asset first, bake blade paths when used, then run the config validator and a real framework proof PIE. The exact bake → validate → resolve → start/abort transition map is in [MOVECARD_LIFECYCLE_S144.md](MOVECARD_LIFECYCLE_S144.md). Do not treat metadata-only validation or a passing synthetic test as proof of resolved animation assets or hit behavior.
