"""C-1618 stage adapter: run one allowlisted Greystone repair script, then close full Editor.

Invoked only by run_B_GREYSTONE_FIX_locked.ps1 under C-1155. The allowlist and
stage names prevent the runner from turning this into a generic Python launcher.
"""
import os
import traceback

import unreal

PREFIX = "[GreystoneFixStage] "
STAGES = {
    "layer": "repair_grey_layer_parents.py",
    "rolls": "retarget_greystone_pack_rolls_rm.py",
    "repoint": "repoint_greystone_rolls_rm.py",
}


def main():
    command_line = unreal.SystemLibrary.get_command_line().split()
    requested = next((token.split("=", 1)[1] for token in command_line if token.startswith("-BGreystoneStage=")), None)
    if requested not in STAGES:
        raise RuntimeError("missing or unknown -BGreystoneStage; refusing")
    target = os.path.join(unreal.Paths.project_dir(), "Scripts", "Editor", STAGES[requested])
    unreal.log(PREFIX + "BEGIN stage=%s script=%s" % (requested, target))
    with open(target, "r", encoding="utf-8") as handle:
        source = handle.read()
    namespace = {"__name__": "__main__", "__file__": target}
    exec(compile(source, target, "exec"), namespace, namespace)


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
