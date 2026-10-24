# Waits for the next message of ANY other party in Documentation/TEAM_MAILBOX.md (Claude = C, Codex = X, Antigravity = A; Windows PowerShell 5.1).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MailboxNext.ps1 -Me X [-SeenCount N] [-Seconds 300]
#   -Me         who you are: C, X or A (messages of your own are never reported)
#   -SeenCount  how many message headings of the mailbox you have already read. Leave it out the first time: the script prints "NEXT_SEEN_COUNT=<n>" and exits at once; pass that number the next time.
#   -Seconds    how long to wait (default 300; use the longest your command limit allows and CALL AGAIN on a timeout: the other side may be busy, a timeout is not the end of the work)
# A message of another party that contains a line "WAIT: <minutes>" is an extension request: the deadline restarts with that many minutes and the script keeps waiting (it prints EXTENDED).
# Output: every new message of the other parties in full, then "NEXT_SEEN_COUNT=<n>": pass n as -SeenCount next time.
# Exit codes: 0 = new message(s), 2 = deadline passed with nothing new (wait again or take the next queue item), 1 = the mailbox could not be read.
param(
    [Parameter(Mandatory = $true)][ValidateSet('C', 'X', 'A')][string]$Me,
    [int]$SeenCount = -1,
    [int]$Seconds = 300,
    [string]$Mailbox = ''
)

if (-not $Mailbox) {
    $scriptDir = $PSScriptRoot
    if (-not $scriptDir -and $MyInvocation.MyCommand.Path) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
    $Mailbox = if ($scriptDir) { Join-Path $scriptDir '..\Documentation\TEAM_MAILBOX.md' } else { Join-Path (Get-Location).Path 'Documentation\TEAM_MAILBOX.md' }
}

function Read-Heads {
    $text = [System.IO.File]::ReadAllText($Mailbox)
    return @{ Text = $text; Heads = [regex]::Matches($text, '(?m)^### \[(?<p>[A-Z]+)-(?<n>\d+)\][^\r\n]*') }
}

$failures = 0
if ($SeenCount -lt 0) {
    try { $r = Read-Heads } catch { Write-Output "MailboxNext: the mailbox could not be read: $($_.Exception.Message)"; exit 1 }
    Write-Output ("MailboxNext: first call, {0} messages exist" -f $r.Heads.Count)
    Write-Output ("NEXT_SEEN_COUNT={0}" -f $r.Heads.Count)
    exit 0
}

$deadline = (Get-Date).AddSeconds($Seconds)
$seen = $SeenCount
Write-Output ("MailboxNext: {0} waiting for a message of another party after message #{1}, up to {2} s" -f $Me, $seen, $Seconds)
while ($true) {
    $r = $null
    try { $r = Read-Heads; $failures = 0 } catch {
        $failures++ # the file may be locked for a moment while another party appends
        if ($failures -ge 12) { Write-Output "MailboxNext: the mailbox could not be read: $($_.Exception.Message)"; exit 1 }
    }
    if ($r -and $r.Heads.Count -gt $seen) {
        $heads = $r.Heads
        $text = $r.Text
        $out = @()
        for ($i = $seen; $i -lt $heads.Count; $i++) {
            $head = $heads[$i]
            if ($head.Groups['p'].Value -eq $Me) { continue }
            $end = if ($i + 1 -lt $heads.Count) { $heads[$i + 1].Index } else { $text.Length }
            $body = $text.Substring($head.Index, $end - $head.Index)
            if ($body -match '(?m)^WAIT:\s*(\d+)') {
                $minutes = [int]$Matches[1]
                $deadline = (Get-Date).AddMinutes($minutes)
                Write-Output ("MailboxNext: {0}-{1} asks for more time: EXTENDED by {2} min (until {3:HH:mm:ss})" -f $head.Groups['p'].Value, $head.Groups['n'].Value, $minutes, $deadline)
                continue
            }
            $out += $body
        }
        $seen = $heads.Count
        if ($out.Count -gt 0) {
            Write-Output ("MailboxNext: {0} NEW MESSAGE(S)" -f $out.Count)
            $out | ForEach-Object { Write-Output $_ }
            Write-Output ("NEXT_SEEN_COUNT={0}" -f $seen)
            exit 0
        }
    }
    if ((Get-Date) -ge $deadline) {
        Write-Output ("MailboxNext: TIMEOUT, nothing new for {0} after message #{1}" -f $Me, $seen)
        Write-Output ("NEXT_SEEN_COUNT={0}" -f $seen)
        exit 2
    }
    Start-Sleep -Seconds 5
}
