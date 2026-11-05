# MoveCard inventory spot audit — D112

**Scope:** 15 representative spec fields across declaration/default, pure validation, resolved compilation, and runtime use. Static source review only; no assets or tests loaded.

| Field | Declaration/default | Schema validation / resolution | Runtime interpretation | Result |
|---|---|---|---|---|
| `Schema` | `0` (`RPGBossMoveCard.h:85`) | Requires exactly `1` (`RPGBossMoveCard.cpp:34-35`). | Version gate; not a tuning fallback. | Agreement; default intentionally invalid. |
| `MoveId` | `NAME_None` (`:86`) | Must be nonempty (`MoveCard.cpp:34-35`). | Used for candidate identity/logging and combo node lookup. | Agreement. |
| `PhaseId` | `NAME_None` (`:88`) | Must be nonempty (`MoveCard.cpp:34-35`). | Selector/model requires observed phase to equal card phase (`RPGBossMoveModel.cpp:38`). | Agreement. |
| `Skeleton` | null soft ref (`:89`) | Resolved path must match metadata skeleton, animation skeleton, and mesh skeleton (`MoveCard.cpp:41-43`); real compiler loads/checks objects. | Skeleton identity binds the authored animation to the runtime mesh. | Agreement; null is not auto-filled. |
| `Sequence` | null (`:91`) | Exactly one of Sequence/Montage; selected path must match resolved animation descriptor (`MoveCard.cpp:36-40`). | Framework profile runtime currently requires sequence-only (`RPGBossFrameworkProfile.cpp:185-187`); generic compiler supports either. | Schema capability is broader than this profile lane; not conflated. |
| `Montage` | null (`MoveCard.h:92`) | Same exactly-one-source rule; section use is montage-only (`MoveCard.cpp:36-46`). | The resolved compiler can inspect a montage; the framework profile resolver refuses montage cards. This audit makes no broader playback-caller claim. | Agreement with separate caller restriction. |
| `SlotName` | `NAME_None` (`MoveCard.h:93`) | Must be nonempty and present in resolved slot metadata (`MoveCard.cpp:44`). | Used by executor's dynamic montage playback slot (`RPGFrameworkMoveExecutor.cpp:158`). | Agreement; no guessed slot fallback. |
| `PlayRate` | `0` (`MoveCard.h:96`) | Finite and strictly positive (`MoveCard.cpp:48`, `17-22`). | Executor derives and applies a playback rate (`RPGFrameworkMoveExecutor.cpp:137-158`). | Agreement; zero default is invalid. |
| `CommitSeconds` | `0` (`MoveCard.h:97`) | Finite/nonnegative; timeline requires commit <= active start (`MoveCard.cpp:50`, `90-92`). | Model starts committed and crosses into active state at card-local active start. | Agreement; zero can be valid. |
| `MinRangeCm` / `MaxRangeCm` | both `0` (`MoveCard.h:112-113`) | Finite/nonnegative, max >= min (`MoveCard.cpp:55-56`, `88-89`). | Inclusive 2D range gate in `FRPGBossMoveModel::IsEligible` (`MoveModel.cpp:33-34`). | Agreement; zero-width range is schema-valid but usually only one exact range. |
| `FrontConeDegrees` | `0` (`MoveCard.h:114`) | Finite/nonnegative and <=360 (`MoveCard.cpp:57`, `88-89`). | Interpreted as full cone width, halved for the yaw test (`MoveModel.cpp:35-37`). | Agreement; zero width permits exact facing only subject to aim-rule boundary. |
| `MaxVerticalDeltaCm` | `0` (`MoveCard.h:116`) | Finite/nonnegative (`MoveCard.cpp:58`, `17-22`). | Zero disables the vertical gate; positive limit allows equality, refuses only greater separation (`MoveModel.cpp:41-42`). | Agreement with field comment. |
| `HPDamage` / `bUsesRootMotion` | damage `0`, root motion false (`MoveCard.h:117-119`) | Damage finite/nonnegative; root motion capability is explicitly refused if requested or present in resolved animation (`MoveCard.cpp:47`, `59`). Defensive cards require zero damage (`:94-102`). | Damage is payload; first backend is in-place only. | Agreement; no silent root-motion fallback. |

**Acceptance result:** all 15 field groups agree when schema rules, resolved-asset checks, and caller-specific playback restrictions are kept distinct. Zero/empty defaults are draft state, not runnable defaults. This sample does not certify any authored MoveCard asset or every field in the schema.
