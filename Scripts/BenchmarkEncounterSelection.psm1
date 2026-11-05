function Get-H019EncounterArgument {
    [CmdletBinding()]
    param([AllowNull()][string]$EncounterDefinition)

    if ([string]::IsNullOrWhiteSpace($EncounterDefinition)) { return @() }

    $path = $EncounterDefinition.Trim()
    if ($path -notmatch '^/Game/[A-Za-z0-9_./-]+$') {
        throw 'H019_ENCOUNTER_DEFINITION must be a /Game object path with no whitespace or command-line metacharacters.'
    }

    return @('-H019EncounterDefinition=' + $path)
}

Export-ModuleMember -Function Get-H019EncounterArgument
