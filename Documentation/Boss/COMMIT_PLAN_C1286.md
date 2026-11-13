# C-1286 / C-1288 / C-1291 Local Commit Plan (`0` Push, `0` Media, `0` `suite.log`)

**Authority:** [`[C-1286]`](file:///C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md), [`[C-1287]`](file:///C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md), [`[C-1288]`](file:///C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md), [`[C-1291]`](file:///C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md)  
**Status:** Held per `<RULE[AGENTS.md]>` (`"Rules: the user commits on their own, never commit or push unless asked"`) until explicit Owner authorization (`"Antigravity: commit locally"`). Zero commits or pushes executed here.

---

## Pre-Commit Safety Warning (Live Working-Tree State @ `2026-11-11 11:15`)

1. **Build-Green `BK-01..46` + `BUILD-299` Recovery + `X26` R4 Build (`B_C1297_PHASE2_BUILD_1127Z`, `[X-1978]`):**
   - `BK-01..46` (`[X-1951]`), `B_C1297_RECOVERY_0315Z`, `B_C1297_RECOVERY2_0338Z` (`[C-1298]`), AND `B_C1297_PHASE2_BUILD_1127Z` (`[X-1978]`, `BUILD exit 0; SUITE exit 0; success=511 fail=0`, pinned `DD27j=cd088e39...`) are **build-green**; `X26` is Lead-verified complete across `P_C1297_X26R3_A..D` + `P_C1297_X26R4_E`. Notice `B_C1294_BKACCEPT` (earlier UHT `exit 6` fail) is superseded by `B_C1297_*`.
   - `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h`/`.cpp`, `Scripts/Editor/pie_sevarog_framework_live.py`, `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h`/`.cpp`, `Scripts/Tools/verify_bf_x05_selected_route.py`, `Scripts/Tools/test_bk3_bf_x05_verifier.py`, `Scripts/Editor/author_framework_encounter_definition.py`, `Scripts/Tools/test_bk51_bk55_framework_deferred_selection_contract.py`, and `Documentation/Boss/BK_51_55_DEFERRED_FRAMEWORK_SELECTION.md` stay cleanly isolated in **Holdout / Group C** until the separate `BK-3` deferred-selection arm & Lead implementation batches close.
   - **Rule:** Group A is 100% isolated. Group B + Group B-BK keep `BK-51..55` / `X26-IMPL-B1` shared C++/driver files and Lead/X26 live-run artifacts (`C-1289`, `P_C1292_X26_*`, `P_C1296_X26R2_*`, `P_C1297_X26R3*`, `P_C1297_X26R4_E`) separated cleanly until staged together in Group C.
2. **Never Stage (`0` media, `0` oversized logs, `0` lock files):**
   - `ENGINE_LOCK.json`
   - Any `suite*.log` (`> 1 MB`)
   - Any `.png`, `.mp4`, `.wav`, `.mp3` (`P_FIGHTVIDEO/`, `P_SHOWCASE/`, `P_C1072_AURACOMPARE/`)
   - `Documentation/TEAM_MAILBOX.md` (`4.79 MB`; only stage if explicitly requested for mailbox ledger snapshot)

---

## Group A — Safe Offline Antigravity Deliverables (`BD_AG..BJ_AG` + `[C-1289]`)

Ready to run immediately on Owner go-ahead (`broken_links=0`, `test_bi_*` `14/14`, `test_bh_*` `12/12`, `test_bd_*` `10/10`, `test_c1289_greystone_pairing_contract` `3/3`):

```powershell
git reset
git add -- `
  "Documentation/Boss/BB_A26_A30_EVIDENCE_INDEX_C1227_ONWARD.md" `
  "Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md" `
  "Documentation/Boss/CL1_ORPHAN_DOCS_AUDIT.md" `
  "Documentation/Boss/COMMIT_PLAN_C1286.md" `
  "Documentation/Boss/BD_A01_A05_BATCH1_RECEIPT.md" `
  "Documentation/Boss/BD_A07_X26_DRYRUN_RECONCILE.md" `
  "Documentation/Boss/BD_A12_SEVAROG_S6_S8_DODGE_FAIRNESS.md" `
  "Documentation/Boss/BD_A16_A20_BATCH4_RECEIPT.md" `
  "Documentation/Boss/BD_A24_GREYSTONE_READINESS_MATRIX.md" `
  "Documentation/Boss/BD_A28_A29_SFX_AURA_PREWIRING_CHECK.md" `
  "Documentation/Boss/BD_A36_A40_HYGIENE_AND_DRIFT_TRIAGE.md" `
  "Documentation/Boss/BD_A41_A45_BATCH9_PACKAGING_MANIFEST.md" `
  "Documentation/Boss/BE_A01_A05_BATCH1_RM_DRYRUN_AUDIT.md" `
  "Documentation/Boss/BE_A06_A10_BATCH2_RECEIPT.md" `
  "Documentation/Boss/BE_A11_A15_S1_S2_DRYRUN_RECONCILE.md" `
  "Documentation/Boss/BE_A16_A20_BATCH4_RECEIPT.md" `
  "Documentation/Boss/BE_A21_A30_BLOCKED_DISPOSITIONS.md" `
  "Documentation/Boss/BE_A37_A43_STAGED_AND_DRIFT_AUDIT.md" `
  "Documentation/Boss/BE_A41_A45_CONSOLIDATED_MANIFEST.md" `
  "Documentation/Boss/BF_A01_A05_BATCH1_RETARGET_SOURCE_AUDIT.md" `
  "Documentation/Boss/BF_A06_A10_BATCH2_RECEIPT.md" `
  "Documentation/Boss/BF_A11_A30_DISPOSITIONS_AND_RECHECKS.md" `
  "Documentation/Boss/BF_A36_A45_CONSOLIDATED_MANIFEST.md" `
  "Documentation/Boss/BG_A01_A10_BATCH1_2_RECEIPT.md" `
  "Documentation/Boss/BG_A11_A40_DISPOSITIONS_AND_CHECKS.md" `
  "Documentation/Boss/BH_A01_A05_MEDIA_ARCHIVE_AUDIT.md" `
  "Documentation/Boss/BH_A06_A10_SIGNATURE_ANCHORS.md" `
  "Documentation/Boss/BH_A11_A15_SFX_DISK_AUDIT.md" `
  "Documentation/Boss/BH_A16_A20_PARAGON_GREYSTONE_SHA_AUDIT.md" `
  "Documentation/Boss/BH_A21_A25_VFX_AND_CONFIG_AUDIT.md" `
  "Documentation/Boss/BH_A26_A30_OVERSIZED_LOG_AND_INDEX_AUDIT.md" `
  "Documentation/Boss/BH_A31_UNBLOCK_SEQUENCE_BRIEF.md" `
  "Documentation/Boss/BH_A36_A40_INVENTORY_AND_VERIFICATION.md" `
  "Documentation/Boss/BH_A41_A45_FINAL_CONSOLIDATED_MANIFEST.md" `
  "Documentation/Boss/BI_A01_A05_PYTHON_SYNTAX_AND_RETARGET_AUDIT.md" `
  "Documentation/Boss/BI_A06_A10_EDITOR_SAFETY_AUDIT.md" `
  "Documentation/Boss/BI_A11_A15_POWERSHELL_RUNNER_AUDIT.md" `
  "Documentation/Boss/BI_A16_A20_CLI_TOOLING_AUDIT.md" `
  "Documentation/Boss/BI_A21_A25_MARKDOWN_UTF8_HYGIENE.md" `
  "Documentation/Boss/BI_A26_A30_PACK_AND_LICENSE_AUDIT.md" `
  "Documentation/Boss/BI_A31_A35_PROJECT_CONTENT_LFS_AUDIT.md" `
  "Documentation/Boss/BI_A36_A40_IMPORT_AND_KIT_PROVENANCE.md" `
  "Documentation/Boss/BI_A41_A45_CONSOLIDATED_BI_MANIFEST.md" `
  "Documentation/Boss/BJ_A01_A05_DAMAGE_AND_PARRY_AUDIT.md" `
  "Documentation/Boss/BJ_A06_A10_DODGE_AND_TRACKER_AUDIT.md" `
  "Documentation/Boss/BJ_A11_A15_HIT_INTAKE_AND_STATE_AUDIT.md" `
  "Documentation/Boss/BJ_A16_A20_ENCOUNTER_SELECTION_LIFECYCLE_AUDIT.md" `
  "Documentation/Boss/BJ_A21_A25_CARDS_SELECTOR_COMBO_AUDIT.md" `
  "Documentation/Boss/BJ_A26_A30_EXECUTOR_AND_TIMING_AUDIT.md" `
  "Documentation/Boss/BJ_A31_A35_TARGET_TRACE_AND_NAV_AUDIT.md" `
  "Documentation/Boss/BJ_A36_A40_PHASE_EFFECTS_AND_CLEANUP_AUDIT.md" `
  "Documentation/Boss/BJ_A41_A45_HUD_GUARDS_AND_TEST_QUALITY_AUDIT.md" `
  "Documentation/Boss/QUEUE_BD_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BE_AG.md" `
  "Documentation/Boss/QUEUE_BE_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BF_AG.md" `
  "Documentation/Boss/QUEUE_BF_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BG_AG.md" `
  "Documentation/Boss/QUEUE_BG_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BH_AG.md" `
  "Documentation/Boss/QUEUE_BH_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BI_AG.md" `
  "Documentation/Boss/QUEUE_BI_AG_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BJ_AG.md" `
  "Documentation/Boss/QUEUE_BJ_AG_CLOSEOUT.md" `
  "Documentation/Boss/X26_RUN2_REVIEW_SHEET.md" `
  "Scripts/Tools/test_bb_x31_greystone_wrapper_readback_contract.py" `
  "Scripts/Tools/test_bd_a07_x26_dryrun_contract.py" `
  "Scripts/Tools/test_bd_a14_sevarog_s1_s8_fairness_contract.py" `
  "Scripts/Tools/test_bd_a19_cook_coverage_contract.py" `
  "Scripts/Tools/test_bd_a24_greystone_readiness_contract.py" `
  "Scripts/Tools/test_bd_a28_sfx_aura_precheck_contract.py" `
  "Scripts/Tools/test_bd_a32_evidence_index_contract.py" `
  "Scripts/Tools/test_be_a02_rootfix_dryrun_contract.py" `
  "Scripts/Tools/test_be_a07_x26_phase_model_contract.py" `
  "Scripts/Tools/test_be_a13_s1_s2_dryrun_contract.py" `
  "Scripts/Tools/test_bf_a02_retarget_rootfix_source_contract.py" `
  "Scripts/Tools/test_bf_a43_cross_queue_contract.py" `
  "Scripts/Tools/test_bg_a09_bf_x16_contract.py" `
  "Scripts/Tools/test_bh_a03_media_archive_contract.py" `
  "Scripts/Tools/test_bh_a08_anchor_socket_contract.py" `
  "Scripts/Tools/test_bh_a13_sfx_disk_bytes_contract.py" `
  "Scripts/Tools/test_bh_a18_greystone_sha256_contract.py" `
  "Scripts/Tools/test_bh_a23_graphics_config_contract.py" `
  "Scripts/Tools/test_bh_a28_oversized_log_guard_contract.py" `
  "Scripts/Tools/test_bi_a04_python_ast_contract.py" `
  "Scripts/Tools/test_bi_a09_editor_safety_contract.py" `
  "Scripts/Tools/test_bi_a14_ps1_syntax_contract.py" `
  "Scripts/Tools/test_bi_a19_cli_tooling_contract.py" `
  "Scripts/Tools/test_bi_a24_markdown_utf8_contract.py" `
  "Scripts/Tools/test_bi_a29_pack_ignore_contract.py" `
  "Scripts/Tools/test_bi_a34_project_content_lfs_contract.py" `
  "Scripts/Tools/test_bi_a39_import_and_kit_contract.py" `
  "Scripts/Tools/test_c1289_greystone_pairing_contract.py" `
  "Scripts/Tools/test_greystone_wrapper_readback_readonly.py"
git diff --cached --name-only
git commit -m "BD_AG..BJ_AG + C-1289: Antigravity offline audit queues, RM4 pairing contract, and readiness/evidence sync"
```

---

## Group B — Accepted `[C-1286]`/`[C-1287]` Build-298 Code, Scripts, Docs & Small Evidence

> **Important:** Run **before** or **together with** Group B-BK (`BK-01..46` below, build-green per `[X-1951]`). `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h`/`.cpp`, `Scripts/Editor/pie_sevarog_framework_live.py`, `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h`/`.cpp`, `Scripts/Tools/verify_bf_x05_selected_route.py`, `Scripts/Tools/test_bk3_bf_x05_verifier.py`, and `BK-51..55` files carry in-flight `BK-51..55` (`[C-1295]`) edits and stay in **Holdout** below. Note `Scripts/Editor/pie_er_*.py`, `pie_full_fight.py`, `pie_player_tags.py`, `pie_jump_probe.py`, and `pie_remains.py` now carry build-green `BK-41..45` driver-hygiene edits (`Group B-BK`); stage them cleanly in Group B-BK (or fold Group B-BK into Group B after Lead run-2 acceptance).

```powershell
git reset
git add -- `
  "README.md" `
  "Documentation/DECISIONS.md" `
  "Documentation/GATE4_RUNBOOK.md" `
  "Documentation/KNOWN_ISSUES.md" `
  "Documentation/PROJECT_STATE.md" `
  "Documentation/TASKS.md" `
  "Documentation/TEST_PLAN.md" `
  "Documentation/Boss/BB_A31_A35_OWNER_PROGRESS_DIGEST_DRAFT.md" `
  "Documentation/Boss/FULL_SUITE_EVIDENCE_HOWTO.md" `
  "Documentation/Boss/NEW_AGENT_ONBOARDING.md" `
  "Documentation/Boss/NEW_BOSS_CHECKLIST.md" `
  "Documentation/Boss/OFFLINE_VALIDATOR_COMMANDS.md" `
  "Documentation/Boss/C1274_SOUL_SIPHON_CHANNEL_DRAIN.md" `
  "Documentation/Boss/C1274_SUBJUGATION_AREA_EFFECT.md" `
  "Documentation/Boss/C1280_X26_PHASE_ELIGIBILITY.md" `
  "Documentation/Boss/BENCHMARK_RUN_RECEIPT_V1.schema.json" `
  "Documentation/Boss/SFX_OWNER_PICK_INTAKE_V1.schema.json" `
  "Documentation/Boss/BB_X11_X15_SEVAROG_DESIGN.md" `
  "Documentation/Boss/BB_X26_X30_FRAMEWORK_BINDING_AUDIT.md" `
  "Documentation/Boss/BB_X31_X35_GREYSTONE_FOLLOWUP.md" `
  "Documentation/Boss/BB_X36_X40_FRAMEWORK_AUDIT.md" `
  "Documentation/Boss/BB_X41_X45_TEST_HARDENING_AND_NEXT_QUEUE.md" `
  "Documentation/Boss/BB_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BC.md" `
  "Documentation/Boss/BC_X01_X05_PROPERTY_HARDENING.md" `
  "Documentation/Boss/BC_X06_X10_SEVAROG_PROOF_AUDIT.md" `
  "Documentation/Boss/BC_X11_X15_FRAMEWORK_LIFECYCLE.md" `
  "Documentation/Boss/BC_X16_X20_GREYSTONE_READINESS.md" `
  "Documentation/Boss/BC_X21_X25_DAMAGE_PARRY_LIFECYCLE.md" `
  "Documentation/Boss/BC_X26_X30_OFFLINE_VALIDATOR_HARDENING.md" `
  "Documentation/Boss/BC_X31_X35_ADDON_SAFETY.md" `
  "Documentation/Boss/BC_X36_X40_SURFACE_LOCKS_READONLY.md" `
  "Documentation/Boss/BC_X41_X45_REVIEW_QUEUE_AND_SYNC.md" `
  "Documentation/Boss/BC_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BD.md" `
  "Documentation/Boss/BD_X01_X05_FRAMEWORK_INTEGRATION_MAP.md" `
  "Documentation/Boss/BD_X06_X10_SEVAROG_CARD_SELECTOR_AUDIT.md" `
  "Documentation/Boss/BD_X11_X15_GREYSTONE_AUTHORING_GATES.md" `
  "Documentation/Boss/BD_X16_X20_DAMAGE_STATUS_LIFECYCLE.md" `
  "Documentation/Boss/BD_X21_X25_TEST_HOOK_SHIPPING_SURFACE.md" `
  "Documentation/Boss/BD_X26_X30_VALIDATOR_AUDIT.md" `
  "Documentation/Boss/BD_X31_X35_DOCUMENTATION_CONSISTENCY.md" `
  "Documentation/Boss/BD_X36_X40_OBSERVABILITY_PERFORMANCE_AUDIT.md" `
  "Documentation/Boss/BD_X41_X45_REVIEW_QUEUE_AND_SYNC.md" `
  "Documentation/Boss/BD_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BE.md" `
  "Documentation/Boss/QUEUE_BE_PRE_C1274_SUPERSEDED.md" `
  "Documentation/Boss/BE_X01_X05_FRAMEWORK_INTEGRATION_AUDIT.md" `
  "Documentation/Boss/BE_X06_X10_FRAMEWORK_SELECTION.md" `
  "Documentation/Boss/BE_X11_X15_AUTONOMOUS_SELECTOR.md" `
  "Documentation/Boss/BE_X16_X20_NAVIGATION_DIAGNOSIS.md" `
  "Documentation/Boss/BE_X21_X25_SHIPPING_REFLECTION.md" `
  "Documentation/Boss/BE_X26_X30_S1_S2_RANGE.md" `
  "Documentation/Boss/BE_X31_X35_ADDON_LIFECYCLE.md" `
  "Documentation/Boss/BE_X36_X40_OWNED_TAG_CLEANUP.md" `
  "Documentation/Boss/BE_X41_X45_REVIEW_QUEUE_SYNC.md" `
  "Documentation/Boss/BE_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BF.md" `
  "Documentation/Boss/BF_X01_X05_FRAMEWORK_ROUTE_SUPPORT.md" `
  "Documentation/Boss/BF_X06_X10_NAVIGATION_DRIVER.md" `
  "Documentation/Boss/BF_X11_X15_SHIPPING_REFLECTION.md" `
  "Documentation/Boss/BF_X16_X20_MOVE_CARD_VALIDATION.md" `
  "Documentation/Boss/BF_X21_X25_DAMAGE_CLEANUP_AUDIT.md" `
  "Documentation/Boss/BF_X26_X30_SEVAROG_CARD_AND_LIVE_EVIDENCE_AUDIT.md" `
  "Documentation/Boss/BF_X31_X35_GREYSTONE_AUTHORING_AND_MOTION_GATES.md" `
  "Documentation/Boss/BF_X36_X40_QUEUE_AND_EVIDENCE_TOOLING_AUDIT.md" `
  "Documentation/Boss/BF_X41_X45_PERFORMANCE_AND_OWNER_GATES.md" `
  "Documentation/Boss/BF_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BI.md" `
  "Documentation/Boss/BI_X01_X05_BENCHMARK_RECEIPT_SCHEMA.md" `
  "Documentation/Boss/BI_X06_X10_PERFORMANCE_CANDIDATES.md" `
  "Documentation/Boss/BI_X11_X15_SEVAROG_AURA_SOURCE_GATE.md" `
  "Documentation/Boss/BI_X16_X20_SFX_OWNER_PICK_INTAKE.md" `
  "Documentation/Boss/BI_X21_X25_FRAMEWORK_ACCEPTANCE_READINESS.md" `
  "Documentation/Boss/BI_X26_X30_GREYSTONE_MOTION_EVIDENCE_AUDIT.md" `
  "Documentation/Boss/BI_X31_X35_OFFLINE_TOOL_PORTABILITY_AUDIT.md" `
  "Documentation/Boss/BI_X36_X40_SHIPPING_PACKAGE_READINESS.md" `
  "Documentation/Boss/BI_X41_X45_STATUS_SYNC_AND_NEXT_QUEUE.md" `
  "Documentation/Boss/BI_X46_X50_CLOSEOUT.md" `
  "Documentation/Boss/QUEUE_BJ.md" `
  "Documentation/Boss/BJ_X01_X05_FRAMEWORK_ROUTE_ACCEPTANCE_RECORD.md" `
  "Documentation/Boss/BJ_X06_X10_SEVAROG_S1_S2_APPROACH_EVIDENCE.md" `
  "Documentation/Boss/BJ_X11_X15_SEVAROG_S3_S5_SEQUENCE_EVIDENCE.md" `
  "Documentation/Boss/BJ_X16_X20_SEVAROG_S6_S8_PHASE_EVIDENCE.md" `
  "Documentation/Boss/BJ_X21_X25_GREYSTONE_RETARGET_MOTION_GATES.md" `
  "Documentation/Boss/BJ_X26_X30_SHIPPING_IDENTITY_REFLECTION_EVIDENCE.md" `
  "Documentation/Boss/BJ_X31_X35_PERFORMANCE_TARGET_AND_PROVENANCE.md" `
  "Documentation/Boss/BJ_X36_X40_OWNER_CHOICE_STATUS.md" `
  "Documentation/Boss/BJ_X41_X45_STATUS_SYNC_AND_QUEUE_BK.md" `
  "Documentation/Boss/BJ_X46_X50_CLOSEOUT.md" `
  "Scripts/author_brief13_anims.py" `
  "Scripts/Editor/author_greystone_player.py" `
  "Scripts/Editor/author_sevarog_draft_cards.py" `
  "Scripts/Editor/pie_sevarog_clip_frames.py" `
  "Scripts/Editor/retarget_er_fit_candidate.py" `
  "Scripts/Editor/retarget_pack_to_greystone.py" `
  "Scripts/Editor/sevarog_pack_02_montages_abilities.py" `
  "Scripts/Editor/test_author_sevarog_draft_cards_contract.py" `
  "Scripts/Editor/dryrun_sevarog_s6_ultimate.py" `
  "Scripts/Editor/fix_greystone_fit_root_motion.py" `
  "Scripts/Editor/pie_greystone_root_motion.py" `
  "Scripts/Editor/probe_greystone_root_bone.py" `
  "Scripts/Editor/probe_greystone_root_motion_flags.py" `
  "Scripts/Editor/run_be_x01_x05_locked_build.ps1" `
  "Scripts/Editor/run_be_x06_x10_locked_build.ps1" `
  "Scripts/Editor/run_be_x11_x15_locked_build.ps1" `
  "Scripts/Editor/run_be_x16_x20_locked_build.ps1" `
  "Scripts/Editor/run_be_x21_x25_locked_build.ps1" `
  "Scripts/Editor/run_be_x26_x30_locked_validation.ps1" `
  "Scripts/Editor/run_be_x31_x35_locked_build.ps1" `
  "Scripts/Editor/run_be_x36_x40_locked_build.ps1" `
  "Scripts/Editor/run_bf_x01_x05_locked_build.ps1" `
  "Scripts/Editor/run_bf_x11_x15_locked_build.ps1" `
  "Scripts/Editor/run_bf_x16_x20_locked_build.ps1" `
  "Scripts/Editor/run_c1257a_author.ps1" `
  "Scripts/Editor/run_c1257a_dry_run.ps1" `
  "Scripts/Editor/run_c1257b_locked_build.ps1" `
  "Scripts/Editor/run_c1265b_clip_trace.ps1" `
  "Scripts/Editor/run_c1274_area_effect_validation.ps1" `
  "Scripts/Editor/run_c1274_channel_drain_validation.ps1" `
  "Scripts/Editor/run_c1274_s6_locked_dryrun.ps1" `
  "Scripts/Editor/run_c1275a_locked_validation.ps1" `
  "Scripts/Editor/run_c1280_x26_locked_validation.ps1" `
  "Scripts/Tools/test_validate_a5_receipt_directory.py" `
  "Scripts/Tools/test_validate_queue_batches.py" `
  "Scripts/Tools/validate_a5_receipt_directory.py" `
  "Scripts/Tools/validate_queue_batches.py" `
  "Scripts/Tools/verify_evidence_manifest.py" `
  "Scripts/Tools/test_verify_evidence_manifest.py" `
  "Scripts/Tools/test_be_x01_x05_framework_integration_contract.py" `
  "Scripts/Tools/test_be_x11_x15_autonomous_selector_contract.py" `
  "Scripts/Tools/test_be_x16_x20_navigation_diagnostics_contract.py" `
  "Scripts/Tools/test_be_x21_x25_shipping_reflection_contract.py" `
  "Scripts/Tools/test_be_x26_x30_s1_s2_range_contract.py" `
  "Scripts/Tools/test_be_x31_x35_addon_lifecycle_contract.py" `
  "Scripts/Tools/test_be_x36_x40_owned_tag_cleanup_contract.py" `
  "Scripts/Tools/test_bf_x06_x10_navigation_driver_contract.py" `
  "Scripts/Tools/test_bf_x11_x15_shipping_reflection_contract.py" `
  "Scripts/Tools/test_bf_x16_x20_move_card_contract.py" `
  "Source/OneBossFight/Audio/RPGBossMusic.cpp" `
  "Source/OneBossFight/Boss/RPGBossNavigationDiagnostics.h" `
  "Source/OneBossFight/Boss/RPGFrameworkBossController.cpp" `
  "Source/OneBossFight/Boss/RPGFrameworkBossController.h" `
  "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h" `
  "Source/OneBossFight/Boss/RPGFrameworkProofFixture.h" `
  "Source/OneBossFight/Player/RPGBossChannelDrainRules.h" `
  "Source/OneBossFight/Player/RPGBossEncounterDefinition.cpp" `
  "Source/OneBossFight/Player/RPGBossEncounterDefinition.h" `
  "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp" `
  "Source/OneBossFight/Player/RPGBossFrameworkProfile.h" `
  "Source/OneBossFight/Player/RPGBossMoveCard.cpp" `
  "Source/OneBossFight/Player/RPGBossMoveCard.h" `
  "Source/OneBossFight/Player/RPGBossMoveModel.cpp" `
  "Source/OneBossFight/Player/RPGBossPunishRules.h" `
  "Source/OneBossFight/Player/RPGDamageResolver.h" `
  "Source/OneBossFight/Player/RPGDodgeTiming.h" `
  "Source/OneBossFight/Player/RPGEncounterBinding.h" `
  "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.h" `
  "Source/OneBossFight/Player/RPGIFrameMonitor.h" `
  "Source/OneBossFight/Player/RPGNativeBossHealth.h" `
  "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp" `
  "Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp" `
  "Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp" `
  "Source/OneBossFight/Tests/RPGBossStartupActivationTests.cpp" `
  "Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp" `
  "Source/OneBossFight/Tests/RPGOwnedTagCleanupTests.cpp" `
  "Source/OneBossFight/Tests/RPGNativeBossHealthTests.cpp" `
  "Source/OneBossFight/UI/RPGBossHud.cpp" `
  "Source/OneBossFight/UI/RPGBossHud.h" `
  "Docs/BossCombatReview/Execution/Claude/A_C1285_GREYSTONE_ROOTFIX" `
  "Docs/BossCombatReview/Execution/Claude/B_C1280_GREYSTONE2" `
  "Docs/BossCombatReview/Execution/Claude/B_C1286_BEACCEPT" `
  "Docs/BossCombatReview/Execution/Claude/P_C1278_SEVAROGDEATH" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM_GREYSTONE" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM_MANNEQUIN" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM2_GREYSTONE" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM2_MANNEQUIN" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM3_GREYSTONE" `
  "Docs/BossCombatReview/Execution/Claude/P_C1282_GREYSTONE_RM3_MANNEQUIN" `
  "Docs/BossCombatReview/Execution/Claude/P_C1283_GREYSTONE_RMPROBE" `
  "Docs/BossCombatReview/Execution/Claude/P_C1284_GREYSTONE_ROOTBONE" `
  "Docs/BossCombatReview/Execution/Codex/BE_X01_X05_FRAMEWORK_INTEGRATION" `
  "Docs/BossCombatReview/Execution/Codex/BE_X06_X10_FRAMEWORK_SELECTION" `
  "Docs/BossCombatReview/Execution/Codex/BE_X11_X15_AUTONOMOUS_SELECTOR" `
  "Docs/BossCombatReview/Execution/Codex/BE_X16_X20_NAVIGATION_DIAGNOSTICS" `
  "Docs/BossCombatReview/Execution/Codex/BE_X21_X25_SHIPPING_REFLECTION" `
  "Docs/BossCombatReview/Execution/Codex/BE_X26_X30_S1_S2_RANGE" `
  "Docs/BossCombatReview/Execution/Codex/BE_X31_X35_ADDON_LIFECYCLE" `
  "Docs/BossCombatReview/Execution/Codex/BE_X36_X40_OWNED_TAG_CLEANUP" `
  "Docs/BossCombatReview/Execution/Codex/BF_X01_X05_FRAMEWORK_ROUTE_SUPPORT" `
  "Docs/BossCombatReview/Execution/Codex/BF_X11_X15_SHIPPING_REFLECTION" `
  "Docs/BossCombatReview/Execution/Codex/BF_X16_X20_MOVE_CARD_VALIDATION" `
  "Docs/BossCombatReview/Execution/Codex/C1257A_GREYSTONE_DRY_RUN" `
  "Docs/BossCombatReview/Execution/Codex/C1257B_GREYSTONE_ROOT_MOTION" `
  "Docs/BossCombatReview/Execution/Codex/C1274_AREA_EFFECT" `
  "Docs/BossCombatReview/Execution/Codex/C1274_CHANNEL_DRAIN" `
  "Docs/BossCombatReview/Execution/Codex/C1274_S6_DRYRUN" `
  "Docs/BossCombatReview/Execution/Codex/C1275A_TRANSIENT_NOTIFY_READBACK" `
  "Docs/BossCombatReview/Execution/Codex/C1280_X26_PHASE_ELIGIBILITY"
git reset -- ":(glob)**/*suite*" ":(glob)**/*.png" ":(glob)**/*.mp4"
git diff --cached --name-only | ForEach-Object { if ((Test-Path $_) -and (Get-Item $_).Length -gt 1048576) { throw "OVERSIZED: $_" } }
git commit -m "C-1286/C-1287 BUILD-298: Codex X26/BE/BF X01-X20, Lead RM1-3/rootfix scripts, core docs & receipts (ex BK-51..55 holdout)"
```

---

## Group B-BK — Build-Green `BK-01..46` Source, Drivers & Tooling (`[C-1294]` + `[X-1951]`, ex `BK-51..55` Shared Files)

Ready to stage after `[C-1294]` source acceptance + `[X-1951]` (`BUILD_EXIT=0`, `511/511`, bounded S1+S6 self-test `PASS`, `NO_ASSET_SAVES=1`), once Lead finishes X26 run 2 (`P_C1296_X26R2_*`) / BUILD-299 acceptance:

```powershell
git reset
git add -- `
  "Documentation/Boss/QUEUE_BK.md" `
  "Documentation/Boss/BK_01_05_GREYSTONE_PACK_ROLL_RM.md" `
  "Documentation/Boss/BK_06_10_X26_DRIVER_SUPPORT.md" `
  "Documentation/Boss/BK_21_25_BF_X05_SELECTED_ROUTE_VERIFIER.md" `
  "Documentation/Boss/BK_26_30_SELECTOR_DIAGNOSTICS_TAG_GENERATION_FENCE.md" `
  "Documentation/Boss/BK_31_35_FRAMEWORK_PERF_ATTRIBUTION.md" `
  "Documentation/Boss/BK_36_40_SHIPPING_PIPELINE.md" `
  "Documentation/Boss/BK_41_45_PIE_DRIVER_SAFETY.md" `
  "Documentation/Boss/BK_46_50_INTEGRATION_STATUS.md" `
  "Documentation/Boss/bk7_shipping_receipt.schema.json" `
  "Documentation/Boss/framework_perf_attribution.schema.json" `
  "Source/OneBossFight/Pack/RPGOwnedTagCleanup.h" `
  "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp" `
  "Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp" `
  "Source/OneBossFight/Boss/RPGFrameworkPerfAttribution.h" `
  "Source/OneBossFight/Tests/RPGFrameworkPerfAttributionTests.cpp" `
  "Scripts/Editor/pie_driver_support.py" `
  "Scripts/Editor/pie_er_air_hits.py" `
  "Scripts/Editor/pie_er_air_reach.py" `
  "Scripts/Editor/pie_er_inputs.py" `
  "Scripts/Editor/pie_er_block_probe.py" `
  "Scripts/Editor/pie_er_control_latency.py" `
  "Scripts/Editor/pie_er_a4_guard_counter.py" `
  "Scripts/Editor/pie_full_fight.py" `
  "Scripts/Editor/pie_player_tags.py" `
  "Scripts/Editor/pie_jump_probe.py" `
  "Scripts/Editor/pie_remains.py" `
  "Scripts/Editor/retarget_greystone_pack_rolls_rm.py" `
  "Scripts/Editor/run_bk2_x26_locked_validation.ps1" `
  "Scripts/Editor/run_bk7_shipping_pipeline.ps1" `
  "Scripts/Tools/scan_pie_driver_safety.py" `
  "Scripts/Tools/test_pie_driver_support.py" `
  "Scripts/Tools/test_scan_pie_driver_safety.py" `
  "Scripts/Tools/test_bk1_greystone_roll_rm_contract.py" `
  "Scripts/Tools/test_bk2_x26_driver_contract.py" `
  "Scripts/Tools/test_bk4_bk5_cleanup_source_contract.py" `
  "Scripts/Tools/test_bk6_perf_attribution_contract.py" `
  "Scripts/Tools/test_bk7_shipping_runner_contract.py" `
  "Scripts/Tools/verify_bk7_shipping_receipt.py" `
  "Scripts/Tools/test_verify_bk7_shipping_receipt.py" `
  "Scripts/Tools/verify_framework_perf_receipt.py" `
  "Scripts/Tools/test_verify_framework_perf_receipt.py" `
  "Scripts/Tools/verify_c1278_x26_live_log.py" `
  "Scripts/Tools/test_verify_c1278_x26_live_log.py" `
  "Scripts/Tools/test_c1278_x26_acceptance_contract.py" `
  "Docs/BossCombatReview/Execution/Codex/BK2_X26_DRIVER/Run_20261111_022223" `
  "Docs/BossCombatReview/Execution/Claude/B_C1294_BKACCEPT" `
  "Docs/BossCombatReview/Execution/Codex/B_C1297_RECOVERY_0315Z" `
  "Docs/BossCombatReview/Execution/Codex/B_C1297_RECOVERY2_0338Z" `
  "Docs/BossCombatReview/Execution/Codex/B_C1297_PHASE2_BUILD_1127Z"
git reset -- ":(glob)**/*suite*" ":(glob)**/*.png" ":(glob)**/*.mp4"
git diff --cached --name-only | ForEach-Object { if ((Test-Path $_) -and (Get-Item $_).Length -gt 1048576) { throw "OVERSIZED: $_" } }
git commit -m "BK-01..46 + BUILD-299 recovery + X26 R4 build (X-1951 / C-1298 / X-1978): Build-green 511/511 source, perf/tag guards, PIE driver safety, Shipping runner & receipts"
```

---

## Holdout / `BK-51..55` + `X26-IMPL-B1` Shared Files & Post-`C-1286` Live Runs *(Do Not Mix With Group A, B, or B-BK)*

1. **`BK-51..55` & `X26-IMPL-B1` (`[C-1295]` / `[C-1298]` / `[X-1978]`, Build-Green in `B_C1297_PHASE2_BUILD_1127Z`, Deferred Arm Pending):**
   - `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h` & `.cpp` *(carries `C-1286` + `BK-2`/`A-827` `X-1945` + `BK-51..55` `InitializeSelectedEncounterForTest` + `X-1962` `bAllowDevTest=true` + `X26-IMPL-B1` `GetCurrentPhaseForTest`)*
   - `Scripts/Editor/pie_sevarog_framework_live.py` *(carries `C-1286` + `BK-2`/`KI-150` `X-1949` `PACK_STYLE_READY` + `BK-51..55` deferred selection + `X-1962` `boss.initialize_with_profile_for_test` + `X26-IMPL-B1` `SEVAROG_LIVE_PHASE2_PROBES=1`)*
   - `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h` & `.cpp` *(BK-51..55 `ActivateDeferredSelectionForTest`)*
   - `Scripts/Editor/author_framework_encounter_definition.py` *(BK-51..55 dry-run/author tool for `DA_Sevarog_Framework_Encounter`)*
   - `Documentation/Boss/BK_51_55_DEFERRED_FRAMEWORK_SELECTION.md`
   - `Scripts/Tools/verify_bf_x05_selected_route.py`, `Scripts/Tools/test_bk3_bf_x05_verifier.py`, `Scripts/Tools/test_bk51_bk55_framework_deferred_selection_contract.py`
2. **Post-`C-1286` Lead / Codex `[C-1288]`..`[X-1978]` Live Runs & Assets (Hold for Group C once `BK-1` / `BK-3` deferred arm settle):**
   - `Content/OneBossFight/Player/FitTest/Greystone/*`, `Content/OneBossFight/Player/Greystone/*`, `Content/OneBossFight/Data/Sevarog/*`
   - `Scripts/Editor/replace_greystone_er_assets.py`, `Scripts/Editor/replace_sevarog_draft_assets.py`
   - `Saved/ERFitRM_20261111_023747.json`
   - `Docs/BossCombatReview/Execution/Claude/B_C1286_GREYSTONE_RM/`, `A_C1286_SEVAROG_X26/`, `P_C1282_GREYSTONE_RM4_MANNEQUIN/`, `P_C1282_GREYSTONE_RM4_GREYSTONE/`, `P_C1292_X26_*`, `P_C1296_X26R2_*`, `P_C1297_X26R3*`, `P_C1297_X26R4_E/`
