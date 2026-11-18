from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = (ROOT / "Scripts/Editor/run_c1619_route_build_locked.ps1").read_text(encoding="utf-8")
PIE_RUNNER = (ROOT / "Scripts/Editor/run_sevarog_arena_route_acceptance.ps1").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


require("C-1619 route source build" in RUNNER and "lead -cne 'Codex'" in RUNNER,
        "build runner must require an explicit current Codex lead receipt")
require("subsystem_cpp_sha256" in RUNNER and "subsystem_h_sha256" in RUNNER
        and "boss_cpp_sha256" in RUNNER and "boss_h_sha256" in RUNNER
        and "blueprint_call_h_sha256" in RUNNER
        and "source changed after approval preflight" in RUNNER,
        "build approval and execution must remain bound to all five current route source hashes")
require("CreateNew" in RUNNER and "[IO.File]::Move($temp,$Path)" in RUNNER
        and "owner_token" in RUNNER and "$locks" in RUNNER,
        "build runner must acquire locks atomically and release only matching owner tokens")
require("Test-UnrealRunning" in RUNNER and "Development" in RUNNER
        and "DD27jManifestHash=$manifest" in RUNNER and "Test Started\\. Name=" in RUNNER
        and "TEST COMPLETE\\. EXIT CODE: 0" in RUNNER,
        "runner must refuse an active Editor and require the pinned, complete suite after build")
require("route_lead_approval.json" in RUNNER and "suite_result='PASS'" in RUNNER
        and "source_build_exit=$buildExit" in RUNNER
        and "blueprint_call_h_sha256=$hashes.blueprint_call_h" in RUNNER,
        "route approval receipt must only be emitted from the successful build/suite path with all five source hashes")
require("$afterHashes.blueprint_call_h -cne $hashes.blueprint_call_h" in RUNNER,
        "build runner must fail closed if helper header hash changes during build/suite")
require("$approval.lead -notin @('Claude','Codex')" in PIE_RUNNER,
        "route PIE runner must accept the active lead without dropping explicit receipt checks")
require("subsystem_cpp_sha256" in PIE_RUNNER and "subsystem_h_sha256" in PIE_RUNNER
        and "boss_cpp_sha256" in PIE_RUNNER and "boss_h_sha256" in PIE_RUNNER
        and "blueprint_call_h_sha256" in PIE_RUNNER,
        "PIE runner must retain exact source-hash binding for all five runtime sources")
require("runtime sources changed after lock acquisition" in PIE_RUNNER
        and "$approval.blueprint_call_h_sha256 -cne $lockedHashes.blueprint_call_h" in PIE_RUNNER,
        "PIE runner must verify helper header hash after lock acquisition")
require("runtime sources modified during Editor PIE run" in PIE_RUNNER
        and "$postRunHashes.blueprint_call_h -cne $lockedHashes.blueprint_call_h" in PIE_RUNNER,
        "PIE runner must verify helper header hash after Editor exit")
post_run_idx = PIE_RUNNER.find("$postRunHashes = Get-RuntimeHashes")
receipt_read_idx = PIE_RUNNER.find("Get-Content -Raw -LiteralPath $receipt")
require(post_run_idx != -1 and receipt_read_idx != -1 and post_run_idx < receipt_read_idx,
        "PIE runner must verify source hashes after Editor exit before reading or validating the receipt")
require("-rpg.Build=Starter" in PIE_RUNNER and "$Mode -eq 'Smoke'" in PIE_RUNNER,
        "PIE runner must supply -rpg.Build=Starter argument for Smoke mode")
require("acceptance_runner_sha256=$hashes.acceptance_runner" in RUNNER
        and "acceptance_driver_sha256=$hashes.acceptance_driver" in RUNNER,
        "build runner must bind acceptance runner and driver hashes in route receipt")
require("$approval.acceptance_runner_sha256 -cne $lockedHashes.acceptance_runner" in PIE_RUNNER
        and "$approval.acceptance_driver_sha256 -cne $lockedHashes.acceptance_driver" in PIE_RUNNER,
        "PIE runner must verify acceptance runner and driver hashes after lock acquisition")
require("$postRunHashes.acceptance_runner -cne $lockedHashes.acceptance_runner" in PIE_RUNNER
        and "$postRunHashes.acceptance_driver -cne $lockedHashes.acceptance_driver" in PIE_RUNNER,
        "PIE runner must verify acceptance runner and driver hashes after Editor exit")
require("$approval.acceptance_runner_sha256 -cne $hashes.acceptance_runner" in RUNNER
        and "$approval.acceptance_driver_sha256 -cne $hashes.acceptance_driver" in RUNNER,
        "build runner must verify incoming lead approval acceptance runner and driver hashes pre-lock and post-lock")
require("framework_profile_cpp_sha256" in RUNNER and "framework_runtime_tests_cpp_sha256" in RUNNER
        and "framework_profile_cpp_sha256" in PIE_RUNNER and "framework_runtime_tests_cpp_sha256" in PIE_RUNNER,
        "both runners must bind framework profile and runtime tests cpp hashes")
require("$approval.framework_profile_cpp_sha256 -cne $hashes.framework_profile_cpp" in RUNNER
        and "$approval.framework_runtime_tests_cpp_sha256 -cne $hashes.framework_runtime_tests_cpp" in RUNNER
        and "$afterHashes.framework_profile_cpp -cne $hashes.framework_profile_cpp" in RUNNER
        and "$afterHashes.framework_runtime_tests_cpp -cne $hashes.framework_runtime_tests_cpp" in RUNNER,
        "build runner must verify framework profile and tests cpp hashes pre-lock, post-lock and post-build")
require("$approval.framework_profile_cpp_sha256 -cne $lockedHashes.framework_profile_cpp" in PIE_RUNNER
        and "$approval.framework_runtime_tests_cpp_sha256 -cne $lockedHashes.framework_runtime_tests_cpp" in PIE_RUNNER
        and "$postRunHashes.framework_profile_cpp -cne $lockedHashes.framework_profile_cpp" in PIE_RUNNER
        and "$postRunHashes.framework_runtime_tests_cpp -cne $lockedHashes.framework_runtime_tests_cpp" in PIE_RUNNER,
        "PIE runner must verify framework profile and tests cpp hashes after lock acquisition and after Editor exit")

require("[ValidateRange(1, 86400)][int]$FullTimeoutSeconds = 3600" in PIE_RUNNER
        and "$deadline = if ($Mode -eq 'Smoke')" in PIE_RUNNER
        and "throw \"TIMEOUT: full-mode driver timed out at $FullTimeoutSeconds seconds\"" in PIE_RUNNER,
        "PIE runner must support validated FullTimeoutSeconds defaulting to 3600s with fail-closed timeout")

require("if ($hasTimedOut) {" in PIE_RUNNER
        and "if ($hasTimedOut -and -not (Test-Path" not in PIE_RUNNER
        and "$receiptWriteTime = [IO.File]::GetLastWriteTimeUtc($receipt)" in PIE_RUNNER
        and "if ($receiptWriteTime -gt $deadline) {" in PIE_RUNNER
        and "$hasTimedOut = $true" in PIE_RUNNER,
        "PIE runner timeout guard must check receipt last write time against deadline to reject late receipts")

print("C-1619 route build runner source contract: 22 checks")
