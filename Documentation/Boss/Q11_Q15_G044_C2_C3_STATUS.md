# Queue Q11–Q15 — G044 / C2 / C3 status

## Q011 — G044 read-only steps 1 and 5 (Lead-run)

Not run by Codex. C-836 assigns the live Editor readback and receipt equality to Claude. The prepared order is in `Docs/BossCombatReview/Execution/Claude/G044_PLAN_V2_READY.md` and `Documentation/Boss/G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`.

Prior artifacts exist under `Docs/BossCombatReview/Execution/Claude/B_G044_RUN/`: step1 `G044DraftPreflight PASS roles=2 fields_per_role=22 writes=0` (raw log SHA-256 `61a326227d1ab42a97c42cead8bc1e1b619762e035e73737fbb7ec2bb536b2e6`); step2 receipt emitted manifest SHA `2f03e958...`; step5 `G044SelectionValidation PASS` with that same manifest SHA (raw log SHA-256 `b24dbb65a8375f2eb5fd3817be8a6058c5d1b76c6c4e1bd7299cf69376e319fd`). All three logs are timestamped 2026-11-04, before C-836's 2026-11-05 order and before D2 changed the manifest. They are useful history, but do not satisfy a fresh post-F1 run or current manifest equality. Required: new Editor abslog/receipt compared field-for-field to BUILD-214 output and an explicit no-Content-write check.

## Q012 — C2 AnimBlueprint validation (Lead-run)

Not run by Codex. A prior run exists at `Docs/BossCombatReview/Execution/Claude/C2_RUNTIME/animbp_sevarog/`: exit 0, `compiled=true`, `saved=false`, and empty receipt diagnostics; raw log SHA-256 `e87ebc6517f364e8e3a03ff4b73a5773cb631e182d7f65018a0a5a417d224310`. It is timestamped 2026-11-04 and predates the C-836 queue order, so Q012 still needs Claude's queued fresh abslog and retained compiler lines/source-log identity.

## Q013 — C3 Sword style dry configuration (Lead-run)

Not run by Codex. A prior v2 dry run exists at `Docs/BossCombatReview/Execution/Claude/C3/runs_v2_lead/dry/`: the log ends with `[NEWWEAPON_END] {"written": [], "dry_run": true}`, and pre/post package snapshots match at 12,379 rows and SHA-256 `35988e8817cc70d9581fac5ab5a6ae09de8b655fb28a6ede66a615db7b72c8b8`. Its raw log SHA-256 is `4f2f875e672af9f6d7e22aa70c49f59d2699e3baab912aab3dee12a506cb733f`; timestamp 2026-11-04 predates the C-836 queue order. Q013 therefore still needs the queued fresh dry-run result; do not use an apply path.

## Q014 — C1 defaults/override offline fixture

Ran from `Docs/BossCombatReview/Execution/Antigravity/Reviews/`:

```text
python test_validate_boss_config.py
Result: 16/16 tests passed.
```

The output includes passing checks that `with_profile_defaults()` materializes the exact neutral-strafe values 0.8/1.6, accepts those defaults without F5, rejects a custom window outside F5, and accepts the custom F5 window. This validates the pure offline config helper only; it does not run or validate the Unreal Editor utility.

## Q015 — Consolidated boundary

The C-836 F1/F2 helper/validator fixes are accepted by Claude in C-838; Q014 is locally verified above (16/16). The older Q011–Q013 artifacts are recorded above so they are not mistaken for the queued fresh runs. Q011–Q013 remain Lead-run; no new Editor/PIE/build or asset write was produced by Codex. Q015's consolidation is this report: it separates accepted offline coverage, prior artifacts, queued fresh evidence, and nonclaims. Before updating P15 from this batch, retain each fresh Lead command/run identity, raw log hash, exact result fields, and nonclaims.
