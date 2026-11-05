# One Boss Fight: agent onboarding

## Read in this order

1. `AGENTS.md` at the repository root for project constraints.
2. `Documentation/PROJECT_STATE.md` for current project state, gotchas, and the team protocol. The team protocol is near its end.
3. `Documentation/TASKS.md` for accepted work, backlog, and current assignments.
4. If Queue 200 C is active, read `Documentation/Boss/QUEUE_200_C_HANDOVER_S193.md` and the latest mailsocket history; it supersedes Queue B snapshots for the current order. C-737 requires one X- receipt per completed task.
5. `Documentation/Archive/HANDOFF_NEXT_CHAT.md` for longer historical handoff context.
6. `Documentation/TEST_PLAN.md`, `Documentation/KNOWN_ISSUES.md`, and `Documentation/DECISIONS.md` as the task requires.
7. For framework boss work, read `Documentation/Boss/ARCHITECTURE_OVERVIEW.md` and the topic reference/data-flow page before editing.

## Team workflow

Claude is technical lead and owns Unreal Editor, builds, PIE, integration and review. Codex handles bounded source, scripts, docs, or read-only audits. The owner makes product decisions, performs hand tests, and commits. Messages are relayed through append-only `Documentation/TEAM_MAILBOX.md`; make every report self-contained and use `TASK / STATUS / FINDINGS / DECISION NEEDED / NEXT ACTION / VALIDATION`. Check its tail at the beginning of each work cycle, claim files before editing, and report line citations and actual validation evidence.

Never commit or push, discard another agent's work, run two editor/driver chains, edit pack assets, or rebuild/delete an asset other assets reference. Close the editor before a build; launch with `-nosound`. Never call `set_editor_property` on components during PIE. Do not call a test or build passed unless it was run and the result was observed. See `PROJECT_STATE.md`'s team protocol for full rules.

## Useful commands

```powershell
# Build (editor closes first and relaunches with -nosound by default)
powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1

# Build and run the automation suite when the editor owner has authorized the run
powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests

# Run a selected PIE regression driver set in the open editor
powershell -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1 -Only pie_boss_death,pie_remains

# Offline tools have their usage summarized here
Get-Content Documentation\Boss\TOOLS.md
```

Use `Documentation/TEST_PLAN.md` for the current evidence and known limitations. The full PIE driver gate can take around 100 minutes; run selected rows in chunks. Do not launch an editor/build/driver run unless you own the editor handoff.
