param([Parameter(Mandatory = $true)][string]$OutRoot)
$ErrorActionPreference = 'Stop'
$runner = Join-Path $PSScriptRoot 'RunA5ParityPair.ps1'
& $runner -Driver 'pie_player_death_reset' -OutRoot $OutRoot -DeathResetRepetitions 3
if ($LASTEXITCODE -ne 0) { throw "death-reset x3 pair failed with exit $LASTEXITCODE" }
