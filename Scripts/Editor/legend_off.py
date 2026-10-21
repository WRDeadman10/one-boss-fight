"""Switches the legend pass off for this editor session: rpg.Legend 0 (log prefix [Legend]). The console variable is process wide, so it survives PIE sessions; every older driver measures timings that hit stop, slow motion and
camera shake would change, so Scripts/RunDrivers.ps1 runs this once after an editor start, next to no_throttle.py. pie_legend.py sets rpg.Legend 1 itself and always sets it back to 0 when it ends.
Run with Scripts/run_in_editor.py."""
import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "rpg.Legend 0")
unreal.log("[Legend] rpg.Legend 0: hit stop, slow motion, camera shake and the music swap are off for this session")
