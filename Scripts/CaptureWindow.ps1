<#
 Saves a PNG of one process's main window using PrintWindow, so nothing else on the desktop can end up in the picture.
 Usage: powershell -File Scripts/CaptureWindow.ps1 -Process UnrealEditor -Out Saved\shot.png
#>
param([string]$Process = 'UnrealEditor', [string]$Out = 'Saved\shot.png')
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Drawing; using System.Drawing.Imaging;
public class WinShot2 {
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static void Save(IntPtr h, string path) {
    RECT r; GetWindowRect(h, out r); int w = r.R - r.L, hh = r.B - r.T;
    using (Bitmap bmp = new Bitmap(w, hh)) { using (Graphics g = Graphics.FromImage(bmp)) { IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 2); g.ReleaseHdc(dc); } bmp.Save(path, ImageFormat.Png); }
  }
}
"@
$p = Get-Process $Process | Select-Object -First 1
[WinShot2]::Save($p.MainWindowHandle, (Join-Path (Get-Location) $Out))
