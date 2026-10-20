<#
 Sends real keyboard events to the foreground window (the PIE viewport) to test key mappings:
 W, S, D, A (1.2 s each), Space (dodge), Left Ctrl (block), with pauses. Run right after starting PIE.
 Usage: powershell -File Scripts/SendKeys.ps1
#>
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class KeySender {
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
    public static void Down(byte vk) { keybd_event(vk, 0, 0, UIntPtr.Zero); }
    public static void Up(byte vk)   { keybd_event(vk, 0, 2, UIntPtr.Zero); }
}
"@
function Hold($vk, $seconds) { [KeySender]::Down($vk); Start-Sleep -Milliseconds ([int]($seconds * 1000)); [KeySender]::Up($vk); Start-Sleep -Milliseconds 1200 }
Start-Sleep -Seconds 6
Hold 0x57 1.2   # W
Hold 0x53 1.2   # S
Hold 0x44 1.2   # D
Hold 0x41 1.2   # A
Hold 0x20 0.2   # Space (dodge)
Start-Sleep -Seconds 1.5
Hold 0xA2 0.6   # Left Ctrl (block)
