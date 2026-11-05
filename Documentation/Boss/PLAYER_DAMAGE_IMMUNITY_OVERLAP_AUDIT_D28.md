# Player damage-immunity overlap audit (Queue D28)

Scope: source-derived precedence and timing map for player dodge invulnerability versus the native parry window across the shared C++ damage resolver. Pack-owned melee routing is called out separately. No tests/build/Editor/PIE run.

## Timing sources

- The native parry window is a press-time interval `[OpenedAt, OpenedAt + WindowSeconds)`; defaults are a proposed 0.25 s window and 0.7 s cooldown (`Source/OneBossFight/Player/RPGParryRules.h:13-25`). `URPGPlayerParry::Press` does not reject a press because the player is currently invulnerable or dodging (`RPGPlayerParry.cpp:69-108`); it opens the independent parry clock and sets `Status.ParryActive` on success (`:95-100,189-200`).
- Dodge invulnerability is read as the pack's `Status.Invulnerable` tag at the instant of contact (`Source/OneBossFight/Player/RPGBossDamage.h:12-36`). `URPGIFrameMonitor` observes the tag against the current dodge montage's `AnimNotifyState` interval and can clear stale/ended state, but it does not add the tag (`RPGIFrameMonitor.cpp:18-46,169-280`). The actual tag source/timing is pack-owned; exact frame overlap with a particular parry press requires runtime evidence.
- `URPGPlayerParry::IsParrying` independently reads the component's time-based window, not the gameplay tag (`RPGPlayerParry.cpp:111-136`). Thus a contact can see both invulnerability and parry as true.

## Shared resolver truth table

For a target that is alive, an alive/current-generation attacker, and a fresh swing key:

| `Status.Invulnerable` at contact | Parry component window open | Resolver result | Mutation/notification |
|---|---|---|---|
| false | false | `Accepted` | Health write; swing key spent only if the health write succeeds. |
| false | true | `Parried` | No health damage; key spent; `NotifyParried` updates player grade and pending parry refund. |
| true | false | `RejectedInvulnerable` | No health write, no spent key, no `NotifyParried`. |
| true | true | `RejectedInvulnerable` | Invulnerability wins; no parry callback/refund and the key remains available for a later eligible contact. |

Dead target, dead/stale attacker, or duplicate key rejects before either immunity flag determines the outcome (`Source/OneBossFight/Player/RPGDamageResolver.cpp:141-154`; pure order in `RPGDamageResolver.h:94-103`). In particular, a duplicate stays `RejectedDuplicate` even if the parry window is open; a stale/dead result cannot be converted into a parry.

At a timeline level, contacts before either interval follow ordinary acceptance (subject to the other gates); dodge-only contacts are invulnerable; parry-only contacts are parried; contacts in the overlap are invulnerable. Once dodge invulnerability ends while the parry window remains open, a *new resolver contact* can be parried. A rejected invulnerable contact does not mark the swing spent, so it does not block that later reevaluation. The resolver does not schedule a second contact itself.

## Caller coverage and boundary

Framework executor, javelin, low sweep, shockwave, and delayed framework reaction call the shared resolver (`RPGFrameworkMoveExecutor.cpp:290,412`; `RPGBossJavelin.cpp:147`; `RPGBossLowSweep.cpp:127`; `RPGBossShockwave.cpp:113`; `RPGFrameworkBossCharacter.cpp:303`). Each consumes the resulting outcome in its caller-specific counters/logs. The resolver adds the spent key and sends parry notification only in the `Parried` branch; the `RejectedInvulnerable` branch only assigns its reason (`RPGDamageResolver.cpp:175-189`).

Pack A1/A3 melee uses the pack's impact decision and `Status.ParryActive`, not this resolver. The native source documents that boundary (`RPGPlayerParry.h:12-15,58-59`), but this audit does not establish the pack Blueprint's dodge-versus-parry precedence. D16/KI-153 remains the separate real pack-boss arena proof dependency.

## Coverage and limits

`OneBossFight.Framework.Parry.Rules` includes a pure case with both `bTargetInvulnerable` and `bTargetParrying` true and expects `RejectedInvulnerable` (`Source/OneBossFight/Tests/RPGParryTests.cpp:31-39`). That proves the boolean decision precedence, not actual overlapping tag/component windows, skipped grade/refund notification, or the unspent-key recontact behavior in a stateful resolver. No combined runtime overlap is claimed. Tests/evidence were read only.
