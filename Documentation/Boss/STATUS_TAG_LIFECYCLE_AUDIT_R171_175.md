# `Status.*` gameplay-tag lifecycle audit (R171–R175)

Read-only search of project C++ under `Source/OneBossFight` for tag requests, owned-tag add/remove calls, and `Status.*` reads. The content pack's Blueprint abilities/notify states are external to this source scan, so their internal add/remove behavior is noted only where project comments and monitor logic identify it.

## Project-code mutation sites

| Tag | Add path | Remove path | Failure/terminal handling | Audit |
|---|---|---|---|---|
| `Status.ParryActive` | `URPGPlayerParry::SetParryTag(true)` requests the tag and calls `AddOwnedGameplayTag` (`Source/OneBossFight/Player/RPGPlayerParry.cpp:179–190`); called after a successful `RPGParry::Press` (`:85–90`). The pack's `ParryFramesNS` also sets this same tag per the component header (`RPGPlayerParry.h:58`). | `SetParryTag(false)` calls `RemoveOwnedGameplayTag`; ordinary close is checked every component tick (`RPGPlayerParry.cpp:33–36`). | Failed removals leave `bTagOn=true`, so next ticks retry. EndPlay retries up to five times (`:172–176`); after five failures the component is gone and no project retry remains. A failed terminal removal can leave the owned tag on a still-live pawn. | Normal path is paired and retries. **Residual teardown risk:** removal failure in all five EndPlay attempts has no surviving retry owner. The Blueprint pack's duplicate tag ownership is outside the C++ audit. |
| `Status.Invulnerable` | No project C++ add site. The pack's `ANS_iFrames` notify adds it during dodge i-frames (`RPGIFrameMonitor.h:13`); `URPGIFrameMonitor` observes the actual owned tag and attributes ownership only when a dodge montage window is active (`RPGIFrameMonitor.cpp:212–235`). | `RemoveTag` invokes `RemoveOwnedGameplayTag` (`RPGIFrameMonitor.cpp:122–129`); called on stale window (`:272`), death (`:290`), encounter reset (`:146–155`), and component EndPlay (`:157–167`). The pack notify also removes it at natural window end, per the header. | Stale/death/reset callers preserve `bTag`/`bOwnedNow` when `RemoveTag` fails, allowing future tick/retry (stale/death) or reset retry. EndPlay makes one attempt and clears both flags unconditionally (`:157–164`). | **Residual teardown risk:** if EndPlay removal fails, monitor ownership state is discarded and no later project tick can retry; tag can persist on a live pawn whose component was removed. This conflicts with the EndPlay intent comment at `:161`. |

## Other `Status.*` names found

| Tag | Project source behavior | Ownership/result |
|---|---|---|
| `Status.Blocking` | Read before damage resolution in `RPGFrameworkMoveExecutor.cpp:286,408`; also documented/read by `RPGBossDamage`/`RPGBossGuardRules`. | No project C++ add/remove site. Pack guard ability owns this tag; its complete Blueprint lifecycle is outside this audit. |
| `Status.Dead` | Read by `RPGDamageResolver.cpp:147` as an additional alive guard. | No project C++ add/remove site found. |
| `Status.HitStunImmune` | Requested and read from the pack hit-stun ability's activation-blocked tags in `RPGSwingTracker.cpp:108–113`. | No project C++ add/remove site found; pack effect/ability lifecycle is external. |
| `Status.ActionCommitted` | Mentioned in `RPGBossHealPunish.h:14` as a generic pack action tag; no tag mutation in that feature. | No project C++ add/remove site found. |

`State.Blocking`, `Ability.Parry`, `Ability.Block`, `Ability.Quickslot`, and other non-`Status.*` tag-container edits were excluded from this task's requested `Status.*` inventory. They do not add/remove a `Status.*` tag in project code.

## Findings

1. **Potential BUG — I-frame monitor EndPlay:** `URPGIFrameMonitor::EndPlay` ignores `RemoveTag`'s return value, then clears `bTag` and `bOwnedNow` regardless (`RPGIFrameMonitor.cpp:159–164`). Since `RemoveTag` explicitly reports dispatch failure and other paths preserve ownership for retry (`:126–128`), a failed EndPlay removal becomes untracked. This matters if the component is removed while the owning pawn remains alive. Minimal fix would retain an explicit teardown failure/log or another retry owner; no code changed.
2. **Potential BUG — player parry EndPlay exhaustion:** `URPGPlayerParry::EndPlay` does retry the tag removal five times (`RPGPlayerParry.cpp:175`), but if all fail, `SetParryTag` leaves `bTagOn=true` and the component is destroyed. A live pawn could retain the tag with no project component left to retry. No code changed.
3. **External source boundary:** `Status.Invulnerable` and `Status.ParryActive` are also added/removed by pack notify states, and `Status.Blocking` is pack ability-owned. This source audit cannot establish the Blueprint side's every interruption/teardown path; use the monitor's retained runtime evidence or a pack asset audit for that portion.

Static source audit only; no build, tests, editor, or pack assets inspected.
