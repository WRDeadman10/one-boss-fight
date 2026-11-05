# Queue P16–P20 — A6 literal inventory and migration

**Scope:** source and documentation inspection plus one default-preserving F5 profile migration. Codex did not run the C++ suite, build, Unreal, or PIE.

## P16 — fresh inventory

Compared the current framework boss/controller/fixture, typed framework profile, and pure boss-rule helpers against the ten active rows in `G4_A6_ROWS_1_10_REFRESH.md` and Antigravity's `A6_HARDCODED_VALUE_AUDIT.md`.

| Source | Literal(s) | Classification | Disposition |
|---|---|---|---|
| `Boss/RPGFrameworkMoveExecutor.cpp:216` | `1.5` | Playback correctness tolerance | Retain; not a tuning control. |
| `Boss/RPGFrameworkBossCharacter.cpp:897` | `10` | Diagnostic display duration | Retain. |
| `Boss/RPGFrameworkBossController.cpp:34` | `.5` | Derived band midpoint formula | Retain formula under C-801. |
| `Boss/RPGFrameworkProofFixture.cpp:76,97` | `.5`, `10` | Derived midpoint / fixture diagnostics | Retain. |
| `Player/RPGBossDormantWakeRules.h:13` | `.15` | Startup safety bound | Retain. |
| `Player/RPGBossFrameworkProfile.cpp:54,70,155` | `64`, `.5`, `60`, `8` | CPU/schema limits | Retain. |
| `Boss/RPGFrameworkBossCharacter.cpp:503` | `.8`, `1.6` | Seeded neutral-strafe hold window, F5 fixture lane | Candidate: promote to the existing typed `URPGBossFrameworkProfile`, preserving the same seeded rule and exact defaults. |

The `.8`/`1.6` pair is an addition to the prior A6 refresh: they are direct behavioral inputs, not formulas or safety/schema caps. The current runtime already accepts `NeutralStrafeSeconds` as typed F5 profile data; the hold window can use that same profile without introducing another data route. The previous A6 rows remain otherwise correctly classified. Retired `RPGSevarogDirector` entries remain excluded.

## P17–P19 — migration status

Migrated both candidate literals into typed profile defaults (`0.8f`, `1.6f`) and passed those profile values into the existing `DirectionAt` call in the same argument order. Existing defaults therefore preserve seeded behavior. The remaining inventory found no additional eligible literal-only gameplay values: other numbers are profile fields, formulas, proof hooks, or safety/schema bounds. No further fields were added artificially.

Added profile-domain checks (finite, positive, ordered) and regression coverage for exact defaults and rejection of invalid windows. C++ execution remains Lead-owned and was not performed here.

## P20 — receipt boundary

The migrated values belong to `URPGBossFrameworkProfile`'s F5 proof-fixture authoring route. They are not fields in the selected-route G044 `URPGBossDefinition` receipt. A G044 receipt cannot truthfully claim native-default provenance for these fields without changing the selected-route schema/consumer, which is outside the literal-only C-801 migration. P20's requested G044 receipt readback is therefore **blocked on route applicability / Lead decision**; no synthetic or mismatched receipt was written. Lead can verify the F5 defaults through profile readback and suite after build.

## Evidence and limits

- Static source comparison only; no build, automation tests, Unreal session, PIE capture, or asset inspection by Codex.
- P16 inventory excludes retired code and separates authorable values from formulas, diagnostic constants, and safety/schema limits.
