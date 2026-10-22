"""Clears the console variable rpg.Build (the build of the player, process wide: a value left by an aborted pie_builds.py run would equip a weapon in every later PIE). Part of the warm-up of RunDrivers.ps1."""
import unreal

unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(), 'rpg.Build ""')
unreal.log("[BuildOff] rpg.Build cleared")
