# Closes the editor safely (accepts the "Save Content" prompt, force-kills only a hung teardown), builds the editor target,
# optionally runs the automation tests (-Tests) and relaunches the editor with -nosound (-NoRelaunch to skip).
# Usage: powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 [-Tests] [-NoRelaunch]
param([switch]$Tests, [switch]$NoRelaunch)

$project = Join-Path (Split-Path $PSScriptRoot -Parent) "OneBossFight.uproject"
$engine = "C:\Program Files\Epic Games\UE_5.5\Engine"

foreach ($p in @(Get-Process UnrealEditor -ErrorAction SilentlyContinue)) { $null = $p.CloseMainWindow() }
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
foreach ($p in @(Get-Process UnrealEditor -ErrorAction SilentlyContinue)) {
  $h = [RebuildWin]::Find([uint32]$p.Id, "Save Content")
  if ($h -ne [IntPtr]::Zero) { [void][RebuildWin]::SetForegroundWindow($h); Start-Sleep -Milliseconds 600; [System.Windows.Forms.SendKeys]::SendWait("{ENTER}"); "accepted Save Content" }
}
Get-Process UnrealEditor -ErrorAction SilentlyContinue | Wait-Process -Timeout 120 -ErrorAction SilentlyContinue
$left = @(Get-Process UnrealEditor -ErrorAction SilentlyContinue)
if ($left.Count -gt 0) { "teardown hung, killing $($left.Count) process(es)"; $left | Stop-Process -Force; Start-Sleep -Seconds 3 }

$out = & "$engine\Build\BatchFiles\Build.bat" OneBossFightEditor Win64 Development "-Project=$project" -WaitMutex 2>&1
$out | Select-String -Pattern "error C|: error|Total execution" | Select-Object -Last 8
if ($out | Select-String -Pattern "error C|: error") { 'BUILD FAILED'; return }

if ($Tests) {
  $log = Join-Path $env:TEMP "obf_tests.log"
  & "$engine\Binaries\Win64\UnrealEditor-Cmd.exe" $project -ExecCmds="Automation RunTests OneBossFight; Quit" -unattended -nullrhi -nosound -nosplash -abslog="$log" | Out-Null
  $done = @(Select-String -Path $log -Pattern "Test Completed|Expected")
  $done | ForEach-Object { $_.Line.Substring([Math]::Min(30, $_.Line.Length)) }
  $ok = @($done | Where-Object { $_.Line -match "Result=\{Success\}" }).Count
  $finished = @($done | Where-Object { $_.Line -match "Test Completed" }).Count
  "automation tests: $finished finished, $ok passed"
  if ($finished -eq 0) { 'TESTS DID NOT RUN (no Test Completed line in the log: a disconnected Windows session makes the engine exit at startup, KI-093; see ' + $log + ')' }
}
if (-not $NoRelaunch) {
  Start-Process -FilePath "$engine\Binaries\Win64\UnrealEditor.exe" -ArgumentList "`"$project`"", '-nosplash', '-nosound'
  'editor relaunched'
}
