# Boss01 field-source manifest

2026-10-26, X-T4 / WP13. CSV is the source-addressed inventory, not a runtime configuration or permission to promote. **Static corpus delivered; effective-instance closure and complete semantic field assignment remain OPEN.** Never use its row count as a count of independently authorable knobs.

## Coverage and counts

7,006 records, 43 native files, 59 serialized text exports. Counts: **103 HYDRATABLE_NOW; 1,365 NEEDS_SEAM; 5,538 NEEDS_EDITOR**. Native corpus includes all current `Player/RPGBoss*`, AttackTracker, PlayerMovesSubsystem, TelegraphRules cpp/h and BossHud cpp/h. This extends the board's named eight families to include native death/look/bleed/posture/clip/rules dependencies. Exact files and SHA256 pins: `WP6Support/manifest_inventory.json`. CSV SHA256 `1d1db245559fed8da510fdabd347ba310db53a10446246dca216577fcc54e4fd`.

Serialized corpus: shipped-boss CDOs, info/style/BT, PR2/3 CDOs plus style, grab data, montage and related sequence exports. Retains full nested object context and line. PR2/3 Blueprint graph pin defaults/derived values are a different representation, reviewed in X-T5; this CSV does not pretend to be their execution closure. It is not a dump of every reachable pack asset. Unexported dependencies / computed graph values require editor evidence below.

One row represents a reflected property, a literal-bearing native source line, or a serialized property record. Entire AddClose rows preserve the parameter tuple and exact source; individual A2/A4/A5/A6 assignment rows identify move + member. Private runtime seeds, diagnostic strings and numerical invariants are retained to prevent silent omissions but are explicitly not automatically data. Constructors can override header defaults. No row labelled CXX_DEFAULT or SERIALIZED_EXPORT is asserted to be effective instance state.

## Class rules

- HYDRATABLE_NOW: public reflected editable native scalar/struct property writable before RegisterComponent. Means a typed assignment can be implemented with existing access, **not that the staged adapter already covers it** or that it is safe to hot-edit.
- NEEDS_SEAM: private data, inline behavior literals/tables, state seeds, ABI strings, scheduling/debug policy or diagnostics. Decide content versus invariant; add a narrow typed configure seam only for actual content. Do not replace thresholds indiscriminately or turn strings into executable arbitrary-field bindings.
- NEEDS_EDITOR: soft reference to verify, or serialized asset/CDO/BT value. Need full object/ancestry/skeleton/instance readback and provenance; export text is not a live actor value. No pack edit authorized.

## Definition ownership and unresolved mappings

The DefinitionField column maps clear public fields to D02 groups and exact members (e.g. Stats.MaxHealth, Phase2.HealthThreshold, Riposte.Range). Move timing tuples map ExplicitCompatibility, **not AnimationCompiled**. Other existing names under D02 groups retain a proposed member of the same name. D02 defines groups, not a finalized USTRUCT ABI.

`REVIEW_REQUIRED[file:line]` is an explicit unresolved semantic assignment, NOT a proposed runtime map keyed by source line. It covers diagnostic text, state seeds, math constants and mixed code expressions whose appropriate policy cannot be inferred mechanically. This prevents claiming the lexical scan is a complete approved hydration specification. These records must be reviewed/classified before X-T6 can be called one-pass production promotion. No generated per-line field bag should be added to the game.

## Spot checks against source

| Source | Source value | D02 owner / consumer / parity |
|---|---|---|
| BossEncounter.h:28,40,104 | Gate1200cm, maxHP2000, startup enforce4s | Encounter.Activation.Radius, Boss.Stats.MaxHealth, startup compatibility policy. Read instance before/after attach + wake/reset. Pack Info500 is distinct, not a contradiction to silently normalize. |
| BossPhases.h:31,58-66 | threshold0.6, movement1.2, attack-rate1.2, damage1.25 | Phase2 data. Compare threshold crossing, modifier application/reversal/reset exactly once. |
| BossStagger.h:36,87,91 | down2.5s, impact0.8s, base40 | Stagger/Riposte. Critical multiplier2.5 remains100 damage; reverse-Fall getup is not standalone GetUp replacement. |
| BossLowSweep.h:37 | damage20 | A4 planar effect damage; source geometry/time-domain queried separately from visible blade. |
| BossHealPunish.h:48,54 | damage12, nominal flight1.2s | A5 projectile; speed clamps450..2500, radius25, maxrange3000 retained. FlightTime is intent for choosing speed, not observed impact time. |
| BossShockwave.h:39 | damage48 | A6 radial effect; central-hit priority retained in compatibility path, not corrected by data hydration. |
| BossDormantWake.h:58 and cpp:21 | WakeClip declaration then constructor path | Lifecycle playback; verify loaded skeleton/length plus Shipping enabled / Development skipped configurations. |
| AttackTracker.cpp:60-63 | all four exact AddClose tuples | Variant-specific commit/active/recovery compatibility timings. A1b fallback0.12/0.16 is not AG's proposed0.20 commit. |
| AttackTracker.cpp:33-36 | A2 commit1.68, active1.93..2.11, recovery3.14 | Code observer compatibility timeline, distinct from engine two collision windows and length3.4. Do not overwrite from sidecar. |

## EDITOR NEEDED: effective-value closure

Claude: export read-only instantiated Boss01 components after attachment, before wake, after initial pack setup4s, after phase2, and after reset. Include actor full path/world/GI/generation, exact class, all editable properties in CSV, AttackTracker.Attacks tuples, current ability object full paths and their effective montage arrays/rates/cooldowns, BT/BB and active style. Correlate source/export asset hashes, source-selection mode and startup cvars (especially CloseTelegraph and WakeClip). Mark test overrides explicitly.

Also export typed reference closure of actual granted abilities/montages/attack-data/notify classes; assets named by unloaded fallback paths are not proved by CDO strings. Missing closure must remain NEEDS_EDITOR. No Codex editor call is authorized. This is the blocking evidence request, not a request to change content.

## Reproduction / QA

Artifact Tool builder `WP6Support/manifest_builder.mjs` reads source/export files only, records SHA256 and assigns rows. It creates a value-only worksheet, recalculates, inspects sample labels, renders a small readable identity preview, emits the requested CSV and reimports it through Artifact Tool. 7,006 unique RecordIds and row count checked; PowerShell Import-Csv independently sampled HP/gate/phase/stagger/special damage/flight/WakeClip and all four AddClose rows. CSV has no formatting/formulas and no additional xlsx deliverable.

Remaining review work: semantic classification of REVIEW_REQUIRED records, dependency closure, public-field consumer anchors beyond declaration, and actual instance witnesses. **WP13 is not CLOSED as an all-runtime-field migration contract.** Antigravity should review art-tied source/intent/timing classification now and flag missing animation/socket dependencies; no need to wait for runtime closure to begin that review.

## C-143 filtered native view

`WP13_BOSS01_NATIVE_FIELDS.csv`: exactly1,534 non-export rows, same12 columns and original RecordIds, sorted by Source then numeric Line (consumer-file groups). **103 HYDRATABLE_NOW /1,365 NEEDS_SEAM /66 NEEDS_EDITOR**. SHA256 `b338b5bf43594b80024013bf852fc8b93e877cdbadef67e6625184c44cafecfc`. 41 files with records out of43 scanned; files with no captured literal/property are not fabricated as records. Per-file class counts: `WP6Support/native_field_counts.json`. Original full CSV retained unchanged. Artifact Tool filtered/recalculated/authored and reimported count1535 including header.

This is the primary review population for AG33, but it still includes diagnostics, runtime state seeds and code invariants. It is **not**1,534 tunable gameplay numbers. ObjectOrFunction is lexical context (can be a called qualified function on a mixed expression), not a compiler-resolved enclosing-function/consumer proof. Source+Line+hash+full expression are the authoritative anchors. Do not infer "safe to tune freely" from a writable property or treat hydration parity as tuning authorization.
