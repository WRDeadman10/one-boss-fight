param([Parameter(Mandatory = $true)][string]$OutDir, [Parameter(Mandatory = $true)][string]$Tag)
# The exact command Scripts\Rebuild.ps1 runs (editor target, Development), with the whole output kept in the evidence directory.
$ErrorActionPreference = 'Continue'
Set-Location C:\UnrealProject\OneBossFight
$log = Join-Path $OutDir "build_$Tag.log"
$cmd = Join-Path $OutDir "build_$Tag.cmd"
$rec = Join-Path $OutDir "build_${Tag}_job_record.txt"
$engine = 'C:\Program Files\Epic Games\UE_5.5\Engine'
$proj = 'C:\UnrealProject\OneBossFight\OneBossFight.uproject'
"@echo off`r`n`"$engine\Build\BatchFiles\Build.bat`" OneBossFightEditor Win64 Development `"-Project=$proj`" -WaitMutex > `"$log`" 2>&1`r`nexit /b %ERRORLEVEL%`r`n" | Out-File $cmd -Encoding ascii
$start = Get-Date
"start $start" | Out-File $rec -Encoding ascii
$p = Start-Process -FilePath cmd.exe -ArgumentList '/c', "`"$cmd`"" -PassThru -Wait -WindowStyle Hidden
"end $(Get-Date) exit $($p.ExitCode) seconds $([int]((Get-Date) - $start).TotalSeconds)" | Out-File $rec -Encoding ascii -Append
