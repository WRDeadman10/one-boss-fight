"""Switches the authored wake clip off for this editor session: rpg.WakeClip 0 (log prefix [WakeClip]). The console variable is process wide, so it survives PIE sessions; the older drivers call Wake() and attack at once, which the 3.5 s wake gate (B11) would veto. Scripts/RunDrivers.ps1 runs this before every run; pie_dormant_wake.py sets rpg.WakeClip 1 itself and back to 0 when it ends. Run with Scripts/run_in_editor.py."""
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "rpg.WakeClip 0")
unreal.log("[WakeClip] rpg.WakeClip 0: the wake clip is skipped for this session (tests)")
