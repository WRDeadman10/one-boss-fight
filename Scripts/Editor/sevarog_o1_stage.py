"""C-1619 allowlisted full-Editor stages; the C-1155 PowerShell runner owns locks."""
import os
import sys
import traceback
import unreal

PREFIX = "[SevarogO1Stage] "
STAGES = {
    "phase_dry": ("ensure_bk56_60_sevarog_initial_phase.py", False, False, []),
    "phase_write": ("ensure_bk56_60_sevarog_initial_phase.py", True, False, []),
    "phase_readback": ("ensure_bk56_60_sevarog_initial_phase.py", False, True, []),
    "encounter_dry": ("author_framework_encounter_definition.py", False, False, []),
    "encounter_write": ("author_framework_encounter_definition.py", False, False, ["--write"]),
    "encounter_readback": ("author_framework_encounter_definition.py", False, False, ["--readback"]),
}


def main():
    args = unreal.SystemLibrary.get_command_line().split()
    stage = next((x.split("=", 1)[1] for x in args if x.startswith("-BSevarogO1Stage=")), None)
    if stage not in STAGES:
        raise RuntimeError("missing/unknown -BSevarogO1Stage")
    filename, write, readback, argv = STAGES[stage]
    target = os.path.join(unreal.Paths.project_dir(), "Scripts", "Editor", filename)
    os.environ["BK56_AUTHOR_PHASE_WRITE"] = "1" if write else "0"
    os.environ["BK56_AUTHOR_PHASE_READBACK"] = "1" if readback else "0"
    sys.argv = [target] + argv
    unreal.log(PREFIX + "BEGIN stage=%s" % stage)
    with open(target, "r", encoding="utf-8") as handle:
        source = handle.read()
    namespace = {"__name__": "__main__", "__file__": target}
    exec(compile(source, target, "exec"), namespace, namespace)
    unreal.log(PREFIX + "RESULT=PASS stage=%s" % stage)


try:
    main()
except Exception as error:
    unreal.log_error(PREFIX + "RESULT=FAIL " + repr(error))
    unreal.log_error(traceback.format_exc())
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception as error:
        unreal.log_error(PREFIX + "QUIT_REQUEST_FAILED " + repr(error))
