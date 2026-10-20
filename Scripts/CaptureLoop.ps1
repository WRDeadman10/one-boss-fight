<#
 Captures the editor window (PrintWindow, so nothing else on the desktop is in the picture) every -IntervalMs while
 Saved\m7_flag.txt exists; the flag file's text becomes part of the file name. Stops when the editor exits.
 Usage: powershell -File Scripts/CaptureLoop.ps1 -OutDir Documentation/M7Captures -IntervalMs 500
#>
param([string]$OutDir = 'Documentation\M7Captures', [int]$IntervalMs = 500, [string]$Process = 'UnrealEditor', [string]$Flag = 'Saved\m7_flag.txt')
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Drawing; using System.Drawing.Imaging;
public class WinShot3 {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static void Save(IntPtr h, string path) {
    RECT r; GetWindowRect(h, out r); int w = r.R - r.L, hh = r.B - r.T;
    using (Bitmap bmp = new Bitmap(w, hh)) { using (Graphics g = Graphics.FromImage(bmp)) { IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); } bmp.Save(path, ImageFormat.Png); }
  }
}
"@
$root = Split-Path -Parent $PSScriptRoot  # Start-Process does not inherit Set-Location, so resolve everything from the script folder
$OutDir = Join-Path $root $OutDir
$Flag = Join-Path $root $Flag
New-Item -ItemType Directory -Force $OutDir | Out-Null
$n = 0
while ($true) {
	$p = Get-Process $Process -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
	if (-not $p) { if ($n -gt 0 -or (Get-Date).Second -lt 0) { break }; Start-Sleep -Milliseconds 500; continue }
	if (Test-Path $Flag) {
		$tag = (Get-Content $Flag -Raw -ErrorAction SilentlyContinue) -replace '[^A-Za-z0-9_]', ''
		$n++
		[WinShot3]::Save($p.MainWindowHandle, ("$OutDir\{0:D3}_{1}.png" -f $n, $tag))
	}
	Start-Sleep -Milliseconds $IntervalMs
}
Write-Output "captured $n frames"
