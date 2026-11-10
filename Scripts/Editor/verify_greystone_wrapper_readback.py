"""Non-saving source-vs-transient-wrapper notify audit for C-1275a.

Run in UE Editor Python. This script creates each retarget wrapper in the
transient package and never saves or edits content assets.
"""
import os
import sys
import traceback

import unreal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import author_greystone_player as author

PREFIX = "[GreystoneWrapperReadback] "


def main():
    wrapper_library = getattr(unreal, "RPGMontageWrapperLibrary", None)
    author.require(wrapper_library is not None, "editor C++ montage wrapper/readback library is unavailable")
    checked = 0
    for spec in author.MONTAGES:
        source, sequence, source_info, source_desc, slot, sections = author.source_readback(spec)
        result = wrapper_library.create_retarget_wrapper(
            source, sequence, unreal.load_asset(author.SKELETON_PATH), "")
        author.require(isinstance(result, tuple) and len(result) >= 2 and result[0] is not None,
                       "transient C++ wrapper creation failed: " + repr(result))
        wrapper = result[0]
        author.require(not str(result[1]), "transient C++ wrapper returned an error: " + str(result[1]))
        outer_path = wrapper.get_outermost().get_path_name() if wrapper else ""
        author.require(wrapper is not None and outer_path.endswith("/Transient"),
                       "wrapper was not created in the transient package: " + outer_path)
        author.readback_montage(spec, wrapper, slot, source_desc, sequence, sections)
        source_rows = author.wrapper_notify_rows(source)
        target_rows = author.wrapper_notify_rows(wrapper)
        matched = author.compare_wrapper_notify_rows(spec, source_rows, target_rows, sequence)
        for source_row, target_row in zip(source_rows, target_rows):
            unreal.log(PREFIX + "SOURCE " + source_row)
            unreal.log(PREFIX + "TARGET " + target_row)
            unreal.log(PREFIX + "MATCH=1")
        unreal.log(PREFIX + "PASS source=%s wrapper=%s notify_count=%d transient=1" %
                   (source.get_path_name(), wrapper.get_path_name(), matched))
        checked += 1
    unreal.log(PREFIX + "RESULT=PASS wrappers=%d transient=1 saves=0" % checked)


try:
    main()
except Exception as error:
    unreal.log_error(PREFIX + "RESULT=FAIL " + str(error))
    unreal.log_error(traceback.format_exc())
finally:
    try:
        unreal.SystemLibrary.execute_console_command(None, "Quit")
    except Exception:
        pass
