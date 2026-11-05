$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$targets = @(
    (Join-Path $root 'Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1'),
    (Join-Path $PSScriptRoot 'write_evidence_hashes.ps1'),
    (Join-Path $PSScriptRoot 'test_run_editor_script_guard.ps1'),
    (Join-Path $PSScriptRoot 'test_evidence_hashes.ps1')
)
foreach ($target in $targets) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($target, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count) { throw "$target parse failed: $($errors -join '; ')" }
}
'PASS PowerShell AST parse'
