# Codex coordination helper only. Dot-source; no top-level action or live Scripts change.
# Append is not crash-atomic: on I/O failure inspect the mailbox; never truncate to retry.
function Add-CodexMailboxMessage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$MailboxPath,
        [Parameter(Mandatory=$true)][ValidateRange(0,2147483647)][int]$ExpectedSeenCount,
        [Parameter(Mandatory=$true)][string]$Message
    )
    $ErrorActionPreference = 'Stop'
    $fullPath = (Resolve-Path -LiteralPath $MailboxPath).Path
    $encoding = [Text.UTF8Encoding]::new($false, $true)
    $messageHeads = [regex]::Matches($Message, '(?m)^### \[(?<party>[A-Z]+)-(?<number>\d+)\][^\r\n]*')
    if ($messageHeads.Count -ne 1 -or $messageHeads[0].Index -ne 0 -or $messageHeads[0].Groups['party'].Value -ne 'X') {
        throw 'Message must start with exactly one X-n heading; no other message headings permitted.'
    }
    $newId = [long]$messageHeads[0].Groups['number'].Value
    $writer = [IO.File]::Open($fullPath, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::Read)
    try {
        # A ReadAllText reader shares Read only and conflicts with our existing writer.
        $readerStream = [IO.File]::Open($fullPath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
        try {
            $bytes = [byte[]]::new($readerStream.Length)
            $offset = 0
            while ($offset -lt $bytes.Length) {
                $read = $readerStream.Read($bytes, $offset, $bytes.Length - $offset)
                if ($read -eq 0) { throw 'Unexpected EOF while reading locked mailbox.' }
                $offset += $read
            }
        } finally { $readerStream.Dispose() }
        # Strict UTF8 decoding prevents appending UTF8 to a UTF16/invalid byte stream.
        $text = $encoding.GetString($bytes)
        if ($text.Length -gt 0 -and $text[0] -eq [char]0xfeff) { $text = $text.Substring(1) }
        if ($text.Contains([string][char]0)) { throw 'Mailbox contains NUL bytes; encoding/content requires inspection.' }
        $heads = [regex]::Matches($text, '(?m)^### \[(?<party>[A-Z]+)-(?<number>\d+)\][^\r\n]*')
        if ($heads.Count -ne $ExpectedSeenCount) { throw "Stale cursor: expected $ExpectedSeenCount, actual $($heads.Count). Reconcile before appending." }
        $maxX = 0L
        foreach ($head in $heads) {
            if ($head.Groups['party'].Value -eq 'X') { $maxX = [Math]::Max($maxX, [long]$head.Groups['number'].Value) }
        }
        if ($newId -ne $maxX + 1) { throw "Expected next X-$($maxX + 1), received X-$newId." }
        # Read actual tail under the same lock; no positional patch anchor or file rewrite.
        $lastHeader = if ($heads.Count) { $heads[$heads.Count-1].Value } else { '(no headings)' }
        $tail = ($text -split '\r?\n' | Select-Object -Last 5) -join "`n"
        $append = "`r`n`r`n" + $Message.TrimEnd([char[]]"`r`n") + "`r`n"
        $appendBytes = $encoding.GetBytes($append)
        $writer.Write($appendBytes, 0, $appendBytes.Length)
        $writer.Flush()
        [pscustomobject]@{ MessageId="X-$newId"; PreviousTailHeader=$lastHeader; PreviousTail=$tail; NextSeenCount=$heads.Count+1; AppendedBytes=$appendBytes.Length }
    } finally { $writer.Dispose() }
}
