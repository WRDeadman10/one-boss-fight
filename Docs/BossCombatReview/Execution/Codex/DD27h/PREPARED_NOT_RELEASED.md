# DD27h / C-328 preparation

BLOCKED pending Claude acceptance of A-218 and an explicit one-launch DD27h release. release_to_run.json is deliberately absent. Do not invoke preflight or run_once until that release is recorded from the actual mailbox.

Copied DD27f capture/preflight/lock/wrapper controls; exact source/copy diffs and original hashes retained. Runtime reads the actual toolkit receipt for draft_boss_profiles.py, authoring_core.py, inspect_authored_assets.py and examples/boss_draft_profiles.json. No old converter hash is hardcoded. Rehash before launch; mismatch stops without retry.

One in-memory --input-json ... --apply command, no --save, -nosound/-nullrhi. Fresh pre/post Source216/DD29 binary/HEAD/Content11752/Data16/Config/toolkit/Saved inventories; Content/Config git clean and accepted dirty Source preserved. Exclusive atomic C-321 lock, never remove another lock. Freeze evidence before releasing own lock. Stop/preserve/report every failure; no fix or retry.

Static Python AST and PowerShell parsing only. No pre-state, command, job, engine log or lock acquired during preparation. No Unreal/build/automation result or asset/gameplay claim.
