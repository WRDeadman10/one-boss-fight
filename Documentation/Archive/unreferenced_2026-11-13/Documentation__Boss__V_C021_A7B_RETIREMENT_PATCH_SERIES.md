# V-C021 — A7-B legacy startup retirement patch series

**Design only.** Owner decision A7=B is to retire legacy startup later, after gates close. The current config stays `bUseLegacyStartup=True`; this file does not authorize implementation or change the route.

| Stage | Candidate touchpoints | Required change if separately authorized | Gate before advancing |
|---|---|---|---|
| 0. Close prerequisites | `J049_OWNER_DECISION_PACKET.md`, `A7_RELEASE_GATE_CHECKLIST.json`, H2/G1/G2 receipts | Reconcile packaged caller/cook closure, target performance, parity, refusal visual, and recovery | Lead accepts each required gate; owner accepts visuals |
| 1. Add caller while fallback remains | Existing approved content entry point selected by V-C024; `RPGEncounterSelectionSubsystem` setter is already public | Caller must set a validated stored-object definition before the world selection boundary; no benchmark CVar in Shipping | First real Shipping caller inventory and packaged setter proof |
| 2. Instrument route/fallback transition | `RPGPlayerMovesSubsystem.cpp:130-135,215-240`; `Config/DefaultGame.ini:17` | Preserve explicit selected route independent of legacy bool; log the deliberate no-selection retirement outcome; keep requested invalid selection fail-closed | Native tests + Lead build; both routes unchanged until opt-in |
| 3. Retire legacy no-selection branch | `RPGPlayerMovesSubsystem.cpp:221-240,334`; declarations `RPGPlayerMovesSubsystem.h:24` | Replace automatic legacy attach only after a valid selection contract exists; no silent fallback on missing/invalid request; preserve player setup and diagnostics | Replacement tests and selected-route parity pass; packaged recovery proof |
| 4. Remove legacy-only test/control assumptions | `RPGBossStartupActivationTests.cpp`, A4/A5 drivers, `RunDrivers.ps1`, benchmark pair scripts | Keep negative/refusal/recovery coverage; drop legacy control only if parity policy and release evidence permit | Full native/offline suite and accepted replacement evidence |
| 5. Configuration and documentation | `Config/DefaultGame.ini`, J049/G1/G2/P15, `KNOWN_ISSUES.md`, `TASKS.md`, `PROJECT_STATE.md`, `TEST_PLAN.md` | Change default only in the separately reviewed retirement change; document rollback to legacy fallback before removal | Lead review plus owner approval of the release disposition |

Do not delete `AttachLegacyBossPrelude`/`AttachLegacyBossBundle`, change config, or edit maps/Blueprints as part of this plan. H3 remains the detailed earlier source inventory; actual content callsites and package manifest must be rechecked immediately before any implementation.
