# Fake-mailbox tests only; never invokes engine/git or writes the real mailbox.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'AppendCodexMailbox.ps1')
$testPath = Join-Path ([IO.Path]::GetTempPath()) ('codex-mailbox-' + [guid]::NewGuid().ToString('N') + '.md')
$encoding = [Text.UTF8Encoding]::new($false, $true)
$checks = [Collections.Generic.List[string]]::new()
function Assert-Check([string]$Name, [bool]$Condition) {
    if (-not $Condition) { throw "FAIL: $Name" }
    $checks.Add($Name)
}
function Expect-Reject([string]$Name, [scriptblock]$Action) {
    $before = [Convert]::ToBase64String([IO.File]::ReadAllBytes($testPath))
    $rejected = $false
    try { & $Action | Out-Null } catch { $rejected = $true }
    Assert-Check $Name $rejected
    Assert-Check "$Name preserves bytes" ($before -eq [Convert]::ToBase64String([IO.File]::ReadAllBytes($testPath)))
}
try {
    $initial = "preamble résumé`r`n### [X-7] earlier`r`nbody`r`n### [A-9] foreign`r`nconcurrent body"
    [IO.File]::WriteAllText($testPath, $initial, $encoding)
    $beforeBytes = [IO.File]::ReadAllBytes($testPath)
    $result = Add-CodexMailboxMessage -MailboxPath $testPath -ExpectedSeenCount 2 -Message "### [X-8] test`nnew body"
    $afterBytes = [IO.File]::ReadAllBytes($testPath)
    Assert-Check 'old byte prefix unchanged including unicode' ([Convert]::ToBase64String($beforeBytes) -eq [Convert]::ToBase64String($afterBytes[0..($beforeBytes.Length-1)]))
    Assert-Check 'new entry at actual EOF' ([IO.File]::ReadAllText($testPath).EndsWith("new body`r`n"))
    Assert-Check 'cursor advances one' ($result.NextSeenCount -eq 3)
    Assert-Check 'tail read under lock' ($result.PreviousTailHeader -eq '### [A-9] foreign')
    Expect-Reject 'stale cursor' { Add-CodexMailboxMessage $testPath 2 '### [X-9] stale' }
    Expect-Reject 'duplicate ID' { Add-CodexMailboxMessage $testPath 3 '### [X-8] duplicate' }
    Expect-Reject 'skipped ID' { Add-CodexMailboxMessage $testPath 3 '### [X-10] skipped' }
    Expect-Reject 'foreign header' { Add-CodexMailboxMessage $testPath 3 '### [A-10] wrong author' }
    Expect-Reject 'multiple headings' { Add-CodexMailboxMessage $testPath 3 "### [X-9] one`n### [X-10] two" }
    $lock = [IO.File]::Open($testPath, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::Read)
    try {
        $blocked = $false
        try { Add-CodexMailboxMessage $testPath 3 '### [X-9] blocked' | Out-Null } catch { $blocked=$true }
        Assert-Check 'competing writer is refused' $blocked
    } finally { $lock.Dispose() }
    Assert-Check 'competing writer leaves bytes unchanged' ([Convert]::ToBase64String($afterBytes) -eq [Convert]::ToBase64String([IO.File]::ReadAllBytes($testPath)))
    # Emulate another party posting before our next check: stale snapshot must reject.
    [IO.File]::AppendAllText($testPath, "`r`n### [A-10] arrived`r`nbody", $encoding)
    Expect-Reject 'foreign concurrent append invalidates cursor' { Add-CodexMailboxMessage $testPath 3 '### [X-9] stale after foreign post' }
    $result = Add-CodexMailboxMessage $testPath 4 '### [X-9] reconciled'
    Assert-Check 'reconciled cursor and next ID succeed' ($result.NextSeenCount -eq 5)
    [IO.File]::WriteAllText($testPath, '### [X-1] BOM mailbox', [Text.UTF8Encoding]::new($true))
    $bomPrefix = [IO.File]::ReadAllBytes($testPath)
    $result = Add-CodexMailboxMessage $testPath 1 '### [X-2] follows BOM'
    $bomAfter = [IO.File]::ReadAllBytes($testPath)
    Assert-Check 'UTF8 BOM heading counted and original bytes preserved' ($result.NextSeenCount -eq 2 -and [Convert]::ToBase64String($bomPrefix) -eq [Convert]::ToBase64String($bomAfter[0..($bomPrefix.Length-1)]))
    [pscustomobject]@{ Scope='fake-mailbox coordination tests; NOT Unreal tests'; Passed=$checks.Count; Total=$checks.Count; Checks=$checks } | ConvertTo-Json -Depth 3
} finally {
    # Single explicitly named temp file only; no recursive path operations.
    if (Test-Path -LiteralPath $testPath) { Remove-Item -LiteralPath $testPath }
}
