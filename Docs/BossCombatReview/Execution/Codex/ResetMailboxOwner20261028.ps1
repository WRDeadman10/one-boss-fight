# One-time, owner-authorized mailbox body archive. No Source/Scripts/engine/git changes.
$ErrorActionPreference = 'Stop'
$root = 'C:\UnrealProject\OneBossFight'
$mailbox = Join-Path $root 'Documentation\TEAM_MAILBOX.md'
$archiveDir = Join-Path $root 'Docs\BossCombatReview\Execution\Codex\MailboxArchive'
$archive = Join-Path $archiveDir 'TEAM_MAILBOX_before_owner_reset_2026-10-28.md'
$receipt = Join-Path $archiveDir 'OWNER_RESET_2026-10-28.json'
$handledCount = 630
$utf8 = [Text.UTF8Encoding]::new($false)
$mutex = [Threading.Mutex]::new($false, 'Global\OneBossFightMailbox')
$got = $false
$stream = $null
try {
    $got = $mutex.WaitOne(15000)
    if (-not $got) { throw 'Could not acquire mailbox writer mutex.' }
    if (Test-Path -LiteralPath $archive) { throw 'Archive already exists; refusing to repeat rotation.' }
    $stream = [IO.File]::Open($mailbox, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    $memory = [IO.MemoryStream]::new()
    $stream.CopyTo($memory)
    $original = $memory.ToArray()
    $memory.Dispose()
    $text = $utf8.GetString($original)
    $heads = [regex]::Matches($text, '(?m)^### \[(?<p>[A-Z]+)-(?<n>\d+)\][^\r\n]*')
    if ($heads.Count -lt $handledCount) { throw 'Mailbox shorter than handled cursor; refusing reset.' }
    $pending = if ($heads.Count -gt $handledCount) { $text.Substring($heads[$handledCount].Index) } else { '' }
    $markers = @($heads | Select-Object -First $handledCount | ForEach-Object { $_.Value.Replace('-->', '-- >') }) -join "`r`n"
    [IO.Directory]::CreateDirectory($archiveDir) | Out-Null
    [IO.File]::WriteAllBytes($archive, $original)
    $sha = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ([IO.File]::ReadAllBytes($archive).Length -ne $original.Length) { throw 'Archive size mismatch.' }
    $newText = @"
# Team mailbox - fresh task checkpoint (owner reset, 2026-10-28)

Current task: Codex reviews Claude C-229 DD13 combined preflight source/tests before any build. DD12 is the last independently verified baseline (105 full-suite tests). Claude awaits the source decision; Antigravity stands by. No runtime activation or commit batch is released.

Full prior mailbox archived byte-for-byte: [$([IO.Path]::GetFileName($archive))]($($archive.Replace('\','/'))).
Archive SHA256: ``$sha``. Historical failures, decisions and evidence remain binding.

Only old message bodies were cleared. Unread messages are preserved below. The hidden archived heading index keeps existing sender IDs and watcher counters valid; do not reset cursors or numbering. Continue using MailboxPost.ps1.

<!-- ARCHIVED MESSAGE HEADING INDEX: cursor/ID continuity only, no active work orders.
$markers
END ARCHIVED MESSAGE HEADING INDEX -->

## Unread deliveries preserved during reset

$pending
"@
    $newBytes = $utf8.GetBytes(($newText -replace "`r?`n", "`r`n"))
    $newCount = [regex]::Matches($utf8.GetString($newBytes), '(?m)^### \[(?<p>[A-Z]+)-(?<n>\d+)\][^\r\n]*').Count
    if ($newCount -ne $heads.Count) { throw 'Heading count changed; refusing rotation.' }
    try {
        $stream.Position = 0
        $stream.Write($newBytes, 0, $newBytes.Length)
        $stream.SetLength($newBytes.Length)
        $stream.Flush($true)
    } catch {
        $stream.Position = 0
        $stream.Write($original, 0, $original.Length)
        $stream.SetLength($original.Length)
        $stream.Flush($true)
        throw
    }
    $record = [ordered]@{ reason='Direct owner requested clearing mailbox and fresh task statement'; archive=$archive; archive_sha256=$sha; original_bytes=$original.Length; fresh_bytes=$newBytes.Length; preserved_heading_count=$heads.Count; archived_body_count=$handledCount; pending_ids=@($heads | Select-Object -Skip $handledCount | ForEach-Object {$_.Value}); watcher_cursor_retained=$handledCount; numbering_reset=$false }
    [IO.File]::WriteAllText($receipt, ($record | ConvertTo-Json -Depth 5), $utf8)
    $record | ConvertTo-Json -Depth 5
} finally {
    if ($stream) { $stream.Dispose() }
    if ($got) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
