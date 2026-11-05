# Lead hotfix intake guide (S192)

Use this flow when Claude marks a task `HOTFIX`, `PARTIAL`, or `REJECTED`. The purpose is to make the correction traceable to its exact acceptance gap and keep it reviewable as its own change.

## Intake and correction

1. **Capture the verdict.** Record the mailbox message ID, task ID, exact rejected/partial acceptance criterion, quoted finding or file/line, and any required verification. Do not infer that silence or a new queue message means acceptance.
2. **Freeze the task scope.** List only files and evidence needed to correct that criterion. Preserve the original result and any failed run; do not delete, relabel, or overwrite evidence to make the correction look clean.
3. **Apply one isolated correction.** Keep hotfix edits and tests attributable to the original task. Do not add later queue changes to the same review submission. If an unrelated change already exists in a shared file, preserve it and identify the exact lines/diff attributable to the hotfix.
4. **Verify at the allowed layer.** Run only the bounded check the Lead requested and the task authorizes. Record the exact command, output, exit status, build/run ID, and log path. If verification belongs to Claude (build, Unreal, PIE, packaging), leave it explicit and do not claim it passed.
5. **Resubmit immediately.** Post one X- correction receipt to Claude naming the original task/verdict message, the criterion fixed, exact changed paths, evidence/verification and remaining limit. Ask for re-review in the message; do not mark the task accepted yourself.
6. **Keep the queue ledger honest.** Mark the original task `HOTFIX IN REVIEW` until Claude returns a verdict. On acceptance, link the verdict to the original task. If rejected again, repeat this flow against the new exact gap; preserve prior receipts.
7. **Resume queued work cleanly.** After the hotfix is submitted, keep subsequent task changes separate. Record whether the queue resumed immediately or is awaiting the Lead's stated review gate; never bury an unreviewed correction in a later five-task batch.

## Submission template

```text
HOTFIX FOR S<id> — original Lead verdict <C-/message ID>
Acceptance gap: <exact criterion and finding>
Correction: <what changed>
Paths: <files>
Verification: <command, result, exit status, evidence path; or not run and why>
Open limit: <none or exact Lead-owned verification>
Status: hotfix submitted for Claude re-review; not yet accepted
```

## Guardrails

- No commit, push, broad cleanup, destructive asset replacement, build, or Editor action unless separately authorized by the owner/Lead protocol.
- Keep any pre-fix artifact and its hash manifest intact. A changed log or binary becomes a distinct run/build identity per `EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md`.
- Update TASKS/TEST_PLAN only with the correction's actual status; preserve `PARTIAL` or `HOTFIX IN REVIEW` until a Lead verdict arrives.
- If no bounded correction can be made without a new owner choice, unavailable asset/account, or destructive action, post a one-line blocker naming that dependency instead of guessing.
