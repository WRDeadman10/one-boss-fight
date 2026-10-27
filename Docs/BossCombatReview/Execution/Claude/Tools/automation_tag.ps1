param([Parameter(Mandatory = $true)][string]$OutDir, [Parameter(Mandatory = $true)][string]$Tag, [string]$Filter = 'OneBossFight')
# Headless automation, same command shape as the earlier gate runs (X-230), filter and log path parameterised.
$ErrorActionPreference = 'Continue'
Set-Location C:\UnrealProject\OneBossFight
$log = Join-Path $OutDir "automation_$Tag.log"
$rec = Join-Path $OutDir "automation_${Tag}_job_record.txt"
$exe = 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$start = Get-Date
"start $start filter=$Filter" | Out-File $rec -Encoding ascii
$p = Start-Process -FilePath $exe -ArgumentList @(
    '"C:\UnrealProject\OneBossFight\OneBossFight.uproject"',
    "`"-ExecCmds=Automation RunTests $Filter; Quit`"",
    '-unattended', '-nullrhi', '-nosound', '-nosplash',
    "`"-abslog=$log`"") -PassThru -Wait -NoNewWindow
"end $(Get-Date) exit $($p.ExitCode) seconds $([int]((Get-Date) - $start).TotalSeconds)" | Out-File $rec -Encoding ascii -Append
