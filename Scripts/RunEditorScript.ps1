<#
 Runs a Python script inside a real (rendering) editor, for scripts that need Slate (batch retarget, thumbnails).
 Uses the 'py' console command (-ExecutePythonScript would exit the editor as soon as the script returns, killing tick-driven
 drivers), so the script must quit the editor itself when done (rpg_content_lib.quit_editor_soon). The log lines tagged with -Tag are echoed.
 Usage: powershell -File Scripts/RunEditorScript.ps1 -Script Scripts/Editor/setup_m7_roll.py -Tag M7Roll
#>
param(
	[Parameter(Mandatory = $true)][string]$Script,
	[string]$Tag = 'LogPython',
	[int]$TimeoutSeconds = 600,
	[string]$StopPattern = '',  # stop the editor once this regex shows up in the log (for drivers that do not quit by themselves)
	[string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.5'
)
$project = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$full = (Resolve-Path (Join-Path $project $Script)).Path
# The 8.3 short path has no spaces, so it survives inside -ExecCmds; the py command wants a lower-case .py extension.
$short = (New-Object -ComObject Scripting.FileSystemObject).GetFile($full).ShortPath.ToLower() -replace '\\', '/'
$log = Join-Path $project ('Saved\' + [IO.Path]::GetFileNameWithoutExtension($Script) + '.log')
$proc = Start-Process -FilePath "$EngineRoot\Engine\Binaries\Win64\UnrealEditor.exe" -PassThru -ArgumentList @(
	"`"$project\OneBossFight.uproject`"", "-ExecCmds=`"py $short`"", '-unattended', '-nosplash', "-abslog=`"$log`"")
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while (-not $proc.HasExited -and (Get-Date) -lt $deadline) {
	Start-Sleep -Seconds 2
	if ($StopPattern -and (Test-Path $log) -and (Select-String -Path $log -Pattern $StopPattern -Quiet)) {
		Start-Sleep -Seconds 3
		if (-not $proc.HasExited) { $proc.Kill() }
	}
}
if (-not $proc.HasExited) {
	Write-Output "Timed out after $TimeoutSeconds s; killing the editor."
	$proc.Kill()
}
Write-Output "editor exit code: $($proc.ExitCode)"
Select-String -Path $log -Pattern "$Tag|LogPython: Error|Fatal error|Assertion failed" | ForEach-Object { $_.Line } | Select-Object -First 80
