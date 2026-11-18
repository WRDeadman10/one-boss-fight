"""C-1155 Editor adapter for explicit Greystone retarget authoring."""
import os
import sys
import traceback
import unreal

PREFIX = "[GreystoneRuntimeRetargetStage] "


def main():
    args = unreal.SystemLibrary.get_command_line().split()
    mode = next((arg.split("=", 1)[1] for arg in args if arg.startswith("-BGreystoneRetargetWrite=")), "0")
    if mode not in ("0", "1"):
        raise RuntimeError("invalid -BGreystoneRetargetWrite value")
    target = os.path.join(unreal.Paths.project_dir(), "Scripts", "Editor", "author_greystone_runtime_retarget.py")
    sys.argv = [target] + (["--write"] if mode == "1" else [])
    unreal.log(PREFIX + "BEGIN mode=" + ("write" if mode == "1" else "dry_run"))
    with open(target, "r", encoding="utf-8") as handle:
        source = handle.read()
    namespace = {"__name__": "__main__", "__file__": target}
    exec(compile(source, target, "exec"), namespace, namespace)
    if namespace.get("RUN_RESULT") != "PASS":
        raise RuntimeError("author script did not report PASS")
    unreal.log(PREFIX + "RESULT=PASS")


try:
    main()
except Exception as exc:
    unreal.log_error(PREFIX + "RESULT=FAIL " + repr(exc))
    unreal.log_error(traceback.format_exc())
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception as exc:
        unreal.log_error(PREFIX + "QUIT_REQUEST_FAILED " + repr(exc))
