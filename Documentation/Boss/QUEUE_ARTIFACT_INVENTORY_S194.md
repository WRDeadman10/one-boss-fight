# Queue B and later artifact inventory (S194)

Scope: new task deliverables reported in X-695 through X-725 (Queue B S163–S181 and Queue C S182–S192), the S193 handover files, and the later C-727 combo fallback test. This is an inventory of created deliverables, not every existing document or source file edited for cross-links. “Owner” means the task author/maintainer; Claude remains the reviewer and owns Editor/build/test execution under the team protocol.

## Queue B deliverables

| Task | New file(s) | Owner | Purpose | Review and build/test state |
|---|---|---|---|---|
| S163 | `Documentation/Boss/EDITOR_MAP_SAVE_AUDIT_S163.md` | Codex | Audit editor-script map save destinations and overwrite hazards. | Accepted in C-737 as X-695; no Editor run. The subsequent save-target hotfix changed the existing script, is X-714, and still needs Lead Editor validation. |
| S164 | `Documentation/Boss/EDITOR_PROPERTY_NAME_AUDIT_S164.md` | Codex | Inventory reflected property setter strings and available source/getter evidence. | Accepted in C-737; no Editor/build. The property spelling candidate remains unverified and is recorded for reflected Editor checking. |
| S165 | `Documentation/Boss/EDITOR_BOOLEAN_PROPERTY_AUDIT_S165.md` | Codex | Compare editor Boolean property names with declarations and usage. | Accepted in C-737; static audit, no Editor/build. |
| S166 | `Documentation/Boss/EDITOR_ABSOLUTE_PATH_AUDIT_S166.md` | Codex | Locate machine-specific editor-script paths and document repo-relative alternatives. | Accepted in C-737; static audit, no Editor/build. |
| S167 | `Documentation/Boss/PYTHON_SYNTAX_INVENTORY_S167.md` | Codex | Record non-executing Python parse results and syntax failures. | Accepted in C-737; no scripts executed. Two parse failures remain unverified and are listed for follow-up. |
| S168 | `Documentation/Boss/POWERSHELL_PARSE_AND_EXIT_AUDIT_S168.md` | Codex | Audit PowerShell syntax and child-process exit propagation. | Accepted in C-737; static parse/audit only, no build or game commands. |
| S169 | `Documentation/Boss/SUBPROCESS_EXIT_CODE_AUDIT_S169.md` | Codex | Trace subprocess failure handling in wrappers. | Accepted in C-737; static audit, no subprocess/build execution. |
| S170 | `Scripts/Tools/test_path_normalization_s170.py`; `Documentation/Boss/PATH_NORMALIZATION_AUDIT_S170.md` | Codex | Add temporary-root path normalization fixture and document Windows path risks. | Accepted in C-737. Claude later ran the fixture successfully as part of the reported 33/33 offline tool tests; no game build. |
| S171 | `Scripts/Tools/atomic_io.py`; `Scripts/Tools/test_atomic_io_s171.py`; `Documentation/Boss/JSON_WRITE_ATOMICITY_AUDIT_S171.md` | Codex | Publish offline tool outputs atomically and exercise failure/no-overwrite behavior. | Accepted in C-737. Claude later ran the atomic I/O fixture successfully in the reported 33/33 offline tool tests; no game build. |
| S172 | `Documentation/Boss/TEMP_DIRECTORY_CLEANUP_AUDIT_S172.md` | Codex | Audit scratch cleanup ownership and identify unsafe persistent/shared deletes. | Accepted in C-737; findings retained as low-severity issues, no tests/build. |
| S173 | `Documentation/Boss/CLI_INPUT_VALIDATION_AUDIT_S173.md` | Codex | Audit CLI argument/file validation and side effects on invalid input. | Accepted in C-737; findings retained as low-severity issues, no tests/build. |
| S174 | `Documentation/Boss/OFFLINE_TOOL_NETWORK_AUDIT_S174.md` | Codex | Check offline tool sources for network access. | Accepted in C-737; static search, no tests/build. |
| S175 | `Documentation/Boss/SCRIPT_IMPORT_SIDE_EFFECT_AUDIT_S175.md` | Codex | Audit module-level side effects in offline tools. | Accepted in C-737; static AST scan, no imports/tests/build run. |
| S176 | `Documentation/Boss/DETERMINISTIC_TOOL_OUTPUT_AUDIT_S176.md` | Codex | Compare repeat outputs from temporary fixtures for pure offline tools. | Accepted in C-737; synthetic temporary fixtures were run, no suite/game build. |
| S177 | `Documentation/Boss/REPORT_REDACTION_AUDIT_S177.md` | Codex | Identify personal paths and raw input lines in generated reports. | Accepted in C-737; findings retained as low-severity issues; no report behavior or tests changed. |
| S178 | `Documentation/Boss/SCAFFOLD_HEADER_AUDIT_S178.md` | Codex | Review generated source headers, module paths, and evidence caveats. | Accepted in C-737; static template review, no scaffold/test/build run. |
| S179 | `Documentation/Boss/TOOL_USAGE_CONSISTENCY_AUDIT_S179.md` | Codex | Compare documented CLI examples with tool help. | Accepted in C-737; documentation/help audit, no game build. |
| S180 | `Documentation/Boss/OFFLINE_TOOL_INVENTORY_AUDIT_S180.md` | Codex | Reconcile the maintained offline tool index and support files. | Accepted in C-737; eight `--help` checks, index reported 43 tools and 0 issues; no suite/game build. |
| S181 | `Documentation/Boss/SHIPPING_GUARD_INVENTORY_AUDIT_S181.md` | Codex | Inventory test/proof registrations and Shipping guards. | Accepted in C-737; static source check reported 45 registrations and documented six intentional unguarded controls; no binary/build/test run. |

## Queue C deliverables

| Task | New file(s) | Owner | Purpose | Review and build/test state |
|---|---|---|---|---|
| S182 | `Documentation/Boss/SHIPPING_SYMBOL_RISK_AUDIT_S182.md` | Codex | Identify test-only reflected symbols that may remain visible in Shipping. | X-715 submitted; no Lead verdict in mailbox tail. Static source only; binary/build not inspected. |
| S183 | `Documentation/Boss/PACKAGED_CONTENT_CHECKLIST_AUDIT_S183.md` | Codex | Audit staged-content checking against source asset references. | X-716 submitted; no Lead verdict. Empty temporary manifest probe reported missing references; no actual staged build inspected. |
| S184 | `Documentation/Boss/BUILD_FAILURE_PROPAGATION_AUDIT_S184.md` | Codex | Review `Rebuild.ps1` child exit and test-log failure handling. | X-717 submitted; no Lead verdict. PowerShell parse/diff check only; no build/tests. |
| S185 | `Documentation/Boss/DRIVER_FAILURE_PROPAGATION_AUDIT_S185.md` | Codex | Trace driver timeout and failed-check outcomes to process exit codes. | X-718 submitted; no Lead verdict. Static control-flow and parse only; no Editor/PIE run. |
| S186 | `Documentation/Boss/STALE_PROCESS_LOCK_RUNBOOK_AUDIT_S186.md` | Codex | Document checkout-scoped process identity and safe PID-tree cleanup. | X-719 submitted; no Lead verdict. PowerShell parse/diff check only; no process stopped and no live lock-release test. |
| S187 | `Documentation/Boss/EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md` | Codex | Distinguish source, build/package, and per-run evidence refresh needs. | X-720 submitted; no Lead verdict. Documentation only; no hashes regenerated. |
| S188 | `Documentation/Boss/FEATURE_PROOF_RELEASE_GATE_S188.md` | Codex | Define evidence required before accepting a feature/profile proof claim. | X-721 submitted; no Lead verdict. Documentation only; no test/build/Editor run. |
| S189 | `Documentation/Boss/OPT_IN_DEFAULT_OFF_AUDIT_S189.md` | Codex | Audit default-off fields and group gates; add the missing F5-only refusal. | X-722 submitted; no Lead verdict. C++ and test source changed; tests/build not run. |
| S190 | `Documentation/Boss/OWNER_INDEPENDENT_TASK_AUDIT_S190.md` | Codex | Screen remaining tasks for owner decisions and external dependencies. | X-723 submitted; no Lead verdict. Documentation only. |
| S191 | `Documentation/Boss/QUEUE_C_REVIEW_RECEIPT_TEMPLATE_S191.md` | Codex | Provide a task-by-task Lead review receipt format. | X-724 submitted; no Lead verdict. Documentation only. |
| S192 | `Documentation/Boss/LEAD_HOTFIX_INTAKE_GUIDE_S192.md` | Codex | Keep rejected-task corrections isolated and explicitly pending re-review. | X-725 submitted; no Lead verdict. Documentation only. |
| S193 | `Documentation/Boss/QUEUE_200_C_HANDOVER_S193.md`; `Documentation/Boss/NEW_AGENT_ONBOARDING.md` | Codex | Record fresh-checkout read order, dependencies, review rule, and active task pointer. | Walkthrough complete; its task receipt is separate from S194's; documentation-only, no build/tests/Editor run. |
| S194 | `Documentation/Boss/QUEUE_ARTIFACT_INVENTORY_S194.md` | Codex | Inventory these queue deliverables with owner, purpose, and review/build state. | This inventory is the S194 deliverable; no Lead verdict or build/tests yet. |

## Later cross-queue deliverable

| Task | New file | Owner | Purpose | Review and build/test state |
|---|---|---|---|---|
| C-727 | `Source/OneBossFight/Tests/RPGBossComboFallbackTests.cpp` | Codex | Test model refusal on a fresh snapshot followed by ordinary selector fallback to a different eligible card. | Accepted in C-729 after Claude corrected a compile-time type-name error; subsequent full suite reported 332/332. This state is distinct from the Queue C S182–S194 verdicts. |

## Inventory limits

- C-737 explicitly accepted the original X-695–X-713 submissions (S163–S181) and reported 33/33 offline tool tests. Acceptance does not erase the unresolved limitations/findings recorded above or accept the later S163 source hotfix.
- The mailbox tail available during S194 contains X-725 as the latest Codex receipt and no later Lead verdict for X-715 onward. Treat those Queue C tasks as submitted/in review until Claude posts dispositions.
- Existing cross-link edits and updated shared files are omitted from the “new file(s)” cells; the task receipts and git history remain their source record. No owner/Lead attribution is inferred beyond the receipts and team protocol.
