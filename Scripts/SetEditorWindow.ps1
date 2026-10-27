<#
 Moves and resizes the main window of the running Unreal Editor (user32 MoveWindow, no focus needed), used to measure the PIE viewport at a large and at a constrained size.
 Usage: powershell -File Scripts/SetEditorWindow.ps1 -Width 1000 -Height 520 [-X 20] [-Y 20]
#>
param([int]$Width = 1920, [int]$Height = 1080, [int]$X = 0, [int]$Y = 0)
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class WinMove { [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool repaint); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c); }
"@
$p = Get-Process UnrealEditor | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { throw 'no editor window' }
[WinMove]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[WinMove]::MoveWindow($p.MainWindowHandle, $X, $Y, $Width, $Height, $true) | Out-Null
"editor window set to ${Width}x${Height} at ($X,$Y)"
