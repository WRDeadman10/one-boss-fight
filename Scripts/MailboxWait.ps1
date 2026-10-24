# Waits for the next message from the other side in Documentation/TEAM_MAILBOX.md (Codex runs this after it posts a message; Windows PowerShell 5.1).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MailboxWait.ps1 -Since 10 [-Seconds 300] [-From C]
#   -Since   the highest message number of the sender that you have already read (for Claude's messages: the last C-n you saw)
#   -Seconds how long to wait (default 300)
#   -From    the sender to wait for: C (Claude, default) or X (Codex)
# A message of the sender that contains a line "WAIT: <minutes>" is an extension request: the script restarts its deadline with that many minutes and keeps waiting (the owner sees EXTENDED lines).
# Exit codes: 0 = a new message arrived (printed in full), 2 = the deadline passed with nothing new (take the next queue item), 1 = the mailbox could not be read.
param(
    [Parameter(Mandatory = $true)][int]$Since,
    [int]$Seconds = 300,
    [ValidateSet('C', 'X')][string]$From = 'C',
    [string]$Mailbox = ''
)

# $PSScriptRoot is empty when the script is started some ways (a sandboxed shell, dot sourcing): fall back to the script's own path, then to the working directory (the repository root).
if (-not $Mailbox) {
    $scriptDir = $PSScriptRoot
    if (-not $scriptDir -and $MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
    $Mailbox = if ($scriptDir) { Join-Path $scriptDir '..\Documentation\TEAM_MAILBOX.md' } else { Join-Path (Get-Location).Path 'Documentation\TEAM_MAILBOX.md' }
}

$deadline = (Get-Date).AddSeconds($Seconds)
$seen = $Since
$failures = 0
Write-Output ("MailboxWait: waiting for a message {0}-{1} or later, up to {2} s" -f $From, ($seen + 1), $Seconds)
while ($true) {
    $text = $null
    try {
        $text = [System.IO.File]::ReadAllText($Mailbox)
        $failures = 0
    }
    catch {
        $failures++ # the file may be locked for a moment while the other side appends
        if ($failures -ge 12) {
            Write-Output "MailboxWait: the mailbox could not be read: $($_.Exception.Message)"
            exit 1
        }
    }
    if ($text) {
        $heads = [regex]::Matches($text, '(?m)^### \[(?<p>[A-Z]+)-(?<n>\d+)\][^\r\n]*')
        for ($i = 0; $i -lt $heads.Count; $i++) {
            $head = $heads[$i]
            $number = [int]$head.Groups['n'].Value
            if ($head.Groups['p'].Value -ne $From -or $number -le $seen) { continue }
            $end = if ($i + 1 -lt $heads.Count) { $heads[$i + 1].Index } else { $text.Length }
            $body = $text.Substring($head.Index, $end - $head.Index)
            $seen = $number
            if ($body -match '(?m)^WAIT:\s*(\d+)') {
                $minutes = [int]$Matches[1]
                $deadline = (Get-Date).AddMinutes($minutes)
                Write-Output ("MailboxWait: {0}-{1} asks for more time: EXTENDED by {2} min (until {3:HH:mm:ss})" -f $From, $number, $minutes, $deadline)
                continue
            }
            Write-Output ("MailboxWait: NEW MESSAGE {0}-{1}" -f $From, $number)
            Write-Output $body
            exit 0
        }
    }
    if ((Get-Date) -ge $deadline) {
        Write-Output ("MailboxWait: TIMEOUT, nothing new from {0} after {1}-{2}" -f $From, $From, $seen)
        exit 2
    }
    Start-Sleep -Seconds 5
}
