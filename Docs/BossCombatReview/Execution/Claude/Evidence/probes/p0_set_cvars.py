"""P0 helper: sets the console variables named in Saved/p0_cvars.txt (one 'name value' per line) for the running editor process and logs the values read back. Log prefix [P0Cvar].
Console variables are process-wide and not saved to any asset or ini by this script."""
import os
import unreal

path = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved", "p0_cvars.txt")
for line in open(path).read().splitlines():
    if not line.strip():
        continue
    if line.startswith("cmd "):
        # raw console command (for example a log verbosity change); logged, nothing is read back
        unreal.SystemLibrary.execute_console_command(None, line[4:])
        unreal.log("[P0Cvar] executed console command: %s" % line[4:])
        continue
    name, value = line.split()
    unreal.SystemLibrary.execute_console_command(None, "%s %s" % (name, value))
    unreal.log("[P0Cvar] set %s %s -> reads back %s" % (name, value, unreal.SystemLibrary.get_console_variable_float_value(name)))
