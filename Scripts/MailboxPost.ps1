# Posts ONE message to Documentation/TEAM_MAILBOX.md safely (Windows PowerShell 5.1). Use this instead of editing the file by hand or with a patch tool.
# Why: the three of us write to the same file. A patch or a rewrite of the file can insert in the middle, reuse an id, or lose a message that another party appended at the same moment (seen 2026-10-24: X-59 landed in the middle, ids jumped from X-20 to X-51). This script only APPENDS, under a named mutex, and assigns the next id of the sender itself.
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MailboxPost.ps1 -As X -To Claude -BodyFile path\to\message.txt
#   powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MailboxPost.ps1 -As A -To Claude -Body "TASK: ...`nSTATUS: ...`nNEXT ACTION: ..."
#   -As      C (Claude), X (Codex) or A (Antigravity)
#   -To      free text for the heading, for example Claude, Codex, Antigravity or "Codex and Antigravity"
#   -Body / -BodyFile  the message text: the usual lines TASK / STATUS / FINDINGS / DECISION NEEDED / NEXT ACTION / VALIDATION (do NOT write the "### [id]" heading: the script writes it)
# Output: "POSTED <id>" (exit 0). Exit 1 = could not post (mutex timeout, file locked, empty body).
param(
    [Parameter(Mandatory = $true)][ValidateSet('C', 'X', 'A')][string]$As,
    [Parameter(Mandatory = $true)][string]$To,
    [string]$Body = '',
    [string]$BodyFile = '',
    [string]$Mailbox = ''
)

if (-not $Mailbox) {
    $scriptDir = $PSScriptRoot
    if (-not $scriptDir -and $MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
    $Mailbox = if ($scriptDir) { Join-Path $scriptDir '..\Documentation\TEAM_MAILBOX.md' } else { Join-Path (Get-Location).Path 'Documentation\TEAM_MAILBOX.md' }
}
if ($BodyFile) { $Body = [System.IO.File]::ReadAllText($BodyFile) }
$Body = $Body.Trim()
if (-not $Body) { Write-Output 'MailboxPost: empty body, nothing posted'; exit 1 }
# A heading written by the sender would create a second message: refuse it.
if ($Body -match '(?m)^###\s*\[') { Write-Output 'MailboxPost: the body must not contain a "### [id]" heading line: the script writes it'; exit 1 }

$names = @{ C = 'Claude'; X = 'Codex'; A = 'Antigravity' }
$mutex = New-Object System.Threading.Mutex($false, 'Global\OneBossFightMailbox')
$got = $false
try {
    $got = $mutex.WaitOne(15000)
    if (-not $got) { Write-Output 'MailboxPost: could not get the mailbox lock in 15 s'; exit 1 }
    $text = [System.IO.File]::ReadAllText($Mailbox)
    $max = 0
    foreach ($m in [regex]::Matches($text, '(?m)^#{2,3} \[?' + $As + '-(\d+)\]?')) {
        $n = [int]$m.Groups[1].Value
        if ($n -gt $max) { $max = $n }
    }
    $id = '{0}-{1}' -f $As, ($max + 1)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $message = "`r`n### [{0}] {1} -> {2}, {3}`r`n{4}`r`n" -f $id, $names[$As], $To, $stamp, ($Body -replace "`r?`n", "`r`n")
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $stream = [System.IO.File]::Open($Mailbox, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
    try {
        $bytes = $utf8.GetBytes($message)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally { $stream.Dispose() }
    Write-Output ("POSTED {0}" -f $id)
    exit 0
}
catch {
    Write-Output ("MailboxPost: failed: {0}" -f $_.Exception.Message)
    exit 1
}
finally {
    if ($got) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
