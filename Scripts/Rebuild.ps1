# Closes the editor safely (accepts the "Save Content" prompt, force-kills only a hung teardown), builds the editor target,
# optionally runs the automation tests (-Tests) and relaunches the editor with -nosound (-NoRelaunch to skip).
# Usage: powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 [-Tests] [-NoRelaunch]
param([switch]$Tests, [switch]$NoRelaunch)

$project = Join-Path (Split-Path $PSScriptRoot -Parent) "OneBossFight.uproject"
$projectFullPath = [System.IO.Path]::GetFullPath($project)
$engine = "C:\Program Files\Epic Games\UE_5.5\Engine"

function Get-ProjectEditorProcesses {
  $processes = Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" -ErrorAction Stop
  foreach ($process in $processes) {
    if ($process.CommandLine -and $process.CommandLine.IndexOf($projectFullPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
      Get-Process -Id $process.ProcessId -ErrorAction SilentlyContinue
    }
  }
}

try { $projectEditors = @(Get-ProjectEditorProcesses) }
catch { throw "Cannot safely identify this project's UnrealEditor processes; no editor was closed: $_" }
foreach ($p in $projectEditors) { $null = $p.CloseMainWindow() }
Start-Sleep -Seconds 6
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @"
using System; using System.Text; using System.Runtime.InteropServices;
public class RebuildWin {
 [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc p, IntPtr l);
 [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 delegate bool EnumProc(IntPtr h, IntPtr l);
 public static IntPtr Find(uint pid, string title) { IntPtr found = IntPtr.Zero; EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h, out p); if (p==pid && IsWindowVisible(h)) { var sb = new StringBuilder(256); GetWindowText(h, sb, 256); if (sb.ToString()==title) found = h; } return true; }, IntPtr.Zero); return found; }
}
"@
foreach ($p in $projectEditors) {
  $h = [RebuildWin]::Find([uint32]$p.Id, "Save Content")
  if ($h -ne [IntPtr]::Zero) { [void][RebuildWin]::SetForegroundWindow($h); Start-Sleep -Milliseconds 600; [System.Windows.Forms.SendKeys]::SendWait("{ENTER}"); "accepted Save Content" }
}
if ($projectEditors.Count -gt 0) { $projectEditors | Wait-Process -Timeout 120 -ErrorAction SilentlyContinue }
try { $left = @(Get-ProjectEditorProcesses) }
catch { throw "Cannot safely recheck this project's UnrealEditor processes; build cancelled without killing processes: $_" }
if ($left.Count -gt 0) {
  "project editor teardown hung, stopping only its process tree(s): $($left.Id -join ', ')"
  foreach ($p in $left) { & taskkill.exe /PID $p.Id /T /F | Out-Null }
  Start-Sleep -Seconds 3
}

$buildLog = Join-Path $env:TEMP ("obf_build_{0:yyyyMMdd_HHmmss}_{1}.log" -f (Get-Date), $PID)
$out = & "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex 2>&1
$buildExit = $LASTEXITCODE
$out | Out-File -LiteralPath $buildLog -Encoding utf8
$out | Select-String -Pattern "error C|: error|Total execution" | Select-Object -Last 8
$buildHasErrors = [bool]($out | Select-String -Pattern "error C|: error")
if ($buildExit -ne 0 -or $buildHasErrors) { "BUILD FAILED (Build.bat exit $buildExit); full log: $buildLog"; exit 1 }
"build log: $buildLog"

if ($Tests) {
  $log = Join-Path $env:TEMP ("obf_tests_{0}.log" -f $PID)
  & "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project -ExecCmds="Automation RunTests OneBossFight; Quit" -unattended -nullrhi -nosound -nosplash -abslog="$log" | Out-Null
  $testExit = $LASTEXITCODE
  $done = if (Test-Path -LiteralPath $log) { @(Select-String -Path $log -Pattern "Test Completed|Expected") } else { @() }
  $complete = $false
  if (Test-Path -LiteralPath $log) { $complete = [bool](Select-String -Path $log -Pattern 'TEST COMPLETE\. EXIT CODE: 0' -Quiet) }
  $done | ForEach-Object { $_.Line.Substring([Math]::Min(30, $_.Line.Length)) }
  $ok = @($done | Where-Object { $_.Line -match "Result=\{Success\}" }).Count
  $finished = @($done | Where-Object { $_.Line -match "Test Completed" }).Count
  "automation tests: $finished finished, $ok passed, terminal marker=$complete (UnrealEditor-Cmd exit $testExit); log: $log"
  if ($testExit -ne 0 -or -not $complete -or $finished -eq 0 -or $ok -ne $finished) {
    'TESTS FAILED OR INCOMPLETE (a disconnected Windows session can stop startup, KI-093; inspect the log above)'
    exit 1
  }
}
if (-not $NoRelaunch) {
  Start-Process -FilePath "$engine\Binaries\Win64\UnrealEditor.exe" -ArgumentList "`"$project`"", '-nosplash', '-nosound'
  'editor relaunched'
}
