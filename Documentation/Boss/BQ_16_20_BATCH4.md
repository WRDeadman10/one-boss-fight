# BQ-16..20: Queue BQ batch 4, boss move hardening

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**All C++ is written but NOT compiled or run.** Binary acceptance needs the Lead's C-1155 build and suite. No engine, editor, PIE, tool run, asset change or commit.

| Task | Result | Files |
|---|---|---|
| **BQ-16** KI-065 A6 landing bounds | **accepted at source-review level** (X-2340, after the X-2338 hotfix C-1567). Opt-in `URPGBossShockwave::LandingArenaRadiusCm` (0 = off, the default) and `LandingArenaCenter`. Pure `IsLandingAllowed`: every non-finite radius (NaN, +inf, -inf) fails closed, a finite radius <=0 is off, and a NaN landing refuses. `Launch()` starts no wave when the landing is refused. Test `OneBossFight.Boss.ShockwaveLandingBounds` | `Player/RPGBossShockwave.h/.cpp`, `Tests/RPGShockwaveLandingTests.cpp` (new) |
| **BQ-17** KI-067/068 A4/A5/A6 hit reaction | **new, awaiting review.** The three moves already go through `URPGDamageResolver::Resolve`, which writes health directly (`HurtPlayer`). New default-off CVar `rpg.Boss.ProjectHitReaction` (0). A new payload flag `bRequestHitReaction` (default false) is set only at the A4, A5 and A6 call sites. New `URPGDamageResolver::ProjectHitReactionMontage` (unset by default). Pure `RPGDamageRules::ShouldRequestHitReaction`: CVar on, move opted in, outcome Accepted, not lethal (Freeze 1267) and a montage set. When it is true, `ACharacter::PlayAnimMontage` runs after the health write. Behaviour is unchanged while the CVar is 0 or the montage is unset. Test `OneBossFight.Damage.ProjectHitReaction` | `Player/RPGDamageResolver.h/.cpp`, `Player/RPGBossLowSweep.cpp`, `Player/RPGBossJavelin.cpp`, `Player/RPGBossShockwave.cpp`, `Tests/RPGProjectHitReactionTests.cpp` (new) |
| **BQ-18** A4 selection weight hook | **reconciled, no new code.** On the data route the hook already exists: each profile card has an authored `Weight` (`FRPGBossProfileCard`, validated to (0, 1e6] in `RPGBossFrameworkProfile.cpp`), plus the Kite, Hug, BackDodge and Greed multipliers (all default 1). I found no authored A4 card in the profile scripts. Adding one and choosing its weight is a design value (O1/ENG). The legacy pack behaviour tree never picks A4, and fixing that would mean editing a pack asset, which is out of scope. A second, unwired weight field would repeat the X-2320 rejection. Lead: say if you want an explicit default-off A4 weight field anyway | none |
| **BQ-19** KI-074 get-up immunity | **accepted at source-review level** (X-2340). The immunity apply is extracted verbatim into `ApplyHitStunImmunity`. `ReapplyImmunityForGetUp` runs at both get-up starts and is gated by `bReapplyImmunityAtGetUp` (default **off**). The CDO default is asserted in `RPGRiposteInputFlushTests.cpp` | `Player/RPGBossStagger.h/.cpp`, `Tests/RPGRiposteInputFlushTests.cpp` |
| **BQ-20** | this report | |

## Gates still open

1. **The Lead's C-1155 build plus suite** for `ShockwaveLandingBounds`, `ProjectHitReaction` and `Riposte.InputFlushOnRestore`.
2. **ENG/ART:** live landing positions and the arena centre and radius values; the hit-reaction montage asset (a knockdown for A4 per KI-067 versus a flinch) and a PIE check with the CVar on; the KI-074 live late-hit timing.
3. **O1/design:** whether to author an A4 card and what weight it gets.

**Earlier uncommitted edits** in the touched files were preserved. My edits were insertions only.
