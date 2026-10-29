# Offline test verifying PowerShell process exit code capture pattern
# Validates $proc.Handle caching before WaitForExit and $proc.Refresh()
$ErrorActionPreference = 'Stop'

function Test-ProcessExitCapture([int]$TargetExitCode) {
    Write-Host "Testing exit code capture for target code: $TargetExitCode..."
    $proc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', "exit $TargetExitCode") -PassThru -NoNewWindow
    $pidVal = $proc.Id
    $handle = $proc.Handle
    $completed = $proc.WaitForExit(5000)
    $proc.Refresh()
    $actualExitCode = $proc.ExitCode

    $matched = ($actualExitCode -eq $TargetExitCode)
    Write-Host "Result: PID=$pidVal, Handle=$handle, Completed=$completed, ExitCode=$actualExitCode, Expected=$TargetExitCode, Match=$matched"
    
    if (-not $matched) {
        throw "Exit code mismatch! Expected $TargetExitCode but got $actualExitCode"
    }
}

Test-ProcessExitCapture 0
Test-ProcessExitCapture 42
Test-ProcessExitCapture 1

Write-Host "ALL EXIT CODE CAPTURE TESTS PASSED (0, 42, 1 verified)"
