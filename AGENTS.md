# One Boss Fight

UE 5.5.4 Soulslike boss duel: Greystone vs Sevarog in `L_SevarogArena`, built on the Advanced ARPG Combat pack. Target packaged 1080p / 60 FPS, p99 <= 16.67 ms (RTX 2060 Super; 120 FPS is stretch only, DECISIONS.md 2026-10-20).

Read `Documentation/PROJECT_STATE.md` first (state, layout, commands, gotchas), then `Documentation/TASKS.md`. Other docs only when needed: `DECISIONS.md` (why), `KNOWN_ISSUES.md`, `TEST_PLAN.md`, `PERFORMANCE_LOG.md`, `PROGRESS_LOG.md`.

Rules: the user commits on their own, never commit or push unless asked. Write C++ directly (codex-aider-bridge waived). Close the editor before building. Launch the editor with `-nosound`. Never delete and recreate assets that other assets reference. Update the docs when you finish a piece of work (TASKS.md, DECISIONS.md, KNOWN_ISSUES.md, TEST_PLAN.md).

Kanban Board Synchronization: All agents (Claude, Codex, Antigravity) must keep work synchronized on the MailSocketTactics Kanban board:
1. Lead breaks down work and creates tasks via `create_board_task(title, description, column, assignee, priority, labels)`.
2. When starting an assigned task: move to in-progress via `move_board_task(taskId, 'in-progress')`.
3. For progress notes, blockers, or discussion: record via `add_board_comment(taskId, text)`.
4. When implementation is ready for critique/review: move to review via `move_board_task(taskId, 'review')`.
5. When verified and approved: move to done via `move_board_task(taskId, 'done')`.

Team work with Claude: read the section "Team protocol (Claude and Codex, relayed by the owner)" at the end of `Documentation/PROJECT_STATE.md` (claims, message format, the Codex handoff). Messages go through the append-only `Documentation/TEAM_MAILBOX.md` (read its end at the start of every cycle); the owner can answer there.
