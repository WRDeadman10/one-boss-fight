"""Editor Python action: compile the one selected boss AnimBlueprint and report structured status."""
import importlib.util
import os
import re
import time

import unreal

RECEIPT_SCHEMA_PATH = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/receipt_schema.py'
RECEIPT_ACTION = 'compile_selected_anim_blueprint'
_schema_spec = importlib.util.spec_from_file_location('c2_receipt_schema', RECEIPT_SCHEMA_PATH)
_receipt_schema = importlib.util.module_from_spec(_schema_spec)
_schema_spec.loader.exec_module(_receipt_schema)


def emit(report):
    report['compiled'] = True
    text = _receipt_schema.serialize_receipt(report, RECEIPT_ACTION)
    unreal.log('[C2_VALIDATE] ' + text)
    try:
        details = [report['summary']]
        if report.get('asset_path'):
            details.append('Asset: ' + report['asset_path'])
        for field, value in report.get('fields', {}).items():
            details.append('%s: %s' % (field, value))
        for diagnostic in report.get('diagnostics', []):
            details.append('%s [%s]: %s' % (diagnostic.get('field'), diagnostic.get('code'), diagnostic.get('message')))
        unreal.EditorDialog.show_message('Validate Boss AnimBlueprint', '\n'.join(details), unreal.AppMsgType.OK)
    except Exception as exc:
        unreal.log_warning('[C2_VALIDATE] dialog_unavailable error=%s' % str(exc)[:180])


def issue(code, message, asset_path='', field='selection'):
    return {'code': code, 'message': message, 'asset_path': asset_path, 'field': field}


def editor_log_path():
    override = os.environ.get('C2_EDITOR_LOG_PATH', '').strip()
    if override:
        return override
    try:
        command_line = str(unreal.SystemLibrary.get_command_line())
        match = re.search(r'(?:^|\s)-abslog(?:=|\s+)(?:"([^"]+)"|([^\s]+))', command_line, re.IGNORECASE)
        if match:
            return (match.group(1) or match.group(2)).strip('"')
    except Exception:
        pass
    project_file = unreal.Paths.get_project_file_path()
    project_name = unreal.Paths.get_base_filename(project_file)
    return os.path.join(unreal.Paths.project_log_dir(), project_name + '.log')


def editor_session_start_epoch():
    """Return this Editor process creation time, or an explicit wrapper value."""
    configured = os.environ.get('C2_EDITOR_SESSION_START_EPOCH', '').strip()
    if configured:
        try:
            return float(configured)
        except ValueError:
            return None
    if os.name == 'nt':
        try:
            import ctypes
            from ctypes import wintypes
            creation = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            get_current_process = kernel.GetCurrentProcess
            get_current_process.restype = wintypes.HANDLE
            get_process_times = kernel.GetProcessTimes
            get_process_times.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME),
                                          ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
                                          ctypes.POINTER(wintypes.FILETIME)]
            get_process_times.restype = wintypes.BOOL
            if not get_process_times(get_current_process(), ctypes.byref(creation), ctypes.byref(exit_time),
                                     ctypes.byref(wintypes.FILETIME()), ctypes.byref(wintypes.FILETIME())):
                return None
            ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
            return ticks / 10000000.0 - 11644473600.0
        except Exception:
            return None
    return None


def snapshot_compiler_lines(path, offset):
    if offset is None:
        return []
    try:
        with open(path, 'rb') as stream:
            stream.seek(offset)
            text = stream.read().decode('utf-8', errors='replace')
            return [line for line in text.splitlines() if '[Compiler]' in line]
    except Exception:
        return []


def main():
    try:
        selected = list(unreal.EditorUtilityLibrary.get_selected_assets())
    except Exception as exc:
        emit({'ok': False, 'summary': 'Could not read Content Browser selection.', 'diagnostics': [
            issue('Selection.ReadFailed', str(exc), field='ContentBrowserSelection')],
            'compiler_message_capture': 'BlueprintEditorLibrary.compile_blueprint returns None; per-node compiler messages are not exposed by this Python call.'})
        return

    if len(selected) != 1:
        emit({'ok': False, 'summary': 'Select exactly one AnimBlueprint asset in the Content Browser.', 'diagnostics': [
            issue('Selection.Count', 'Expected exactly one selected asset; found %d.' % len(selected), field='ContentBrowserSelection')],
            'compiler_message_capture': 'not_applicable'})
        return

    asset = selected[0]
    asset_path = asset.get_path_name()
    if not isinstance(asset, unreal.AnimBlueprint):
        emit({'ok': False, 'summary': 'Selected asset is not an AnimBlueprint.', 'diagnostics': [
            issue('Selection.WrongAssetType', 'Select the boss AnimBlueprint asset.', asset_path, 'AssetClass')],
            'asset_class': asset.get_class().get_name(), 'compiler_message_capture': 'not_started'})
        return

    diagnostics = []
    log_path = editor_log_path()
    session_start = editor_session_start_epoch()
    try:
        log_offset = os.path.getsize(log_path)
        log_mtime_before = os.path.getmtime(log_path)
    except OSError:
        log_offset = None
        log_mtime_before = None
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(asset)
    except Exception as exc:
        diagnostics.append(issue('BlueprintCompile.Exception', str(exc), asset_path, 'Compile'))

    try:
        generated = unreal.BlueprintEditorLibrary.generated_class(asset)
        generated_path = generated.get_path_name() if generated else ''
    except Exception as exc:
        generated_path = ''
        diagnostics.append(issue('BlueprintCompile.GeneratedClassReadFailed', str(exc), asset_path, 'GeneratedClass'))

    if not generated_path:
        diagnostics.append(issue('BlueprintCompile.Failed', 'Compile completed without an accessible generated class.', asset_path, 'generated_class'))

    log_grew = False
    log_mtime_after = None
    if log_offset is not None:
        deadline = time.time() + 0.5
        while time.time() <= deadline:
            try:
                current_size = os.path.getsize(log_path)
                log_mtime_after = os.path.getmtime(log_path)
                if current_size > log_offset:
                    log_grew = True
                    break
            except OSError:
                break
            time.sleep(0.025)

    compile_lines = snapshot_compiler_lines(log_path, log_offset)
    asset_name = asset.get_name().casefold()
    compiler_diagnostics = []
    for line in compile_lines:
        severity = 'error' if 'error' in line.casefold() else 'warning' if 'warning' in line.casefold() else 'message'
        compiler_diagnostics.append({'code': 'BlueprintCompile.CompilerLog', 'severity': severity,
                                     'asset_match': asset_name in line.casefold() or asset_path.casefold() in line.casefold(),
                                     'asset_path': asset_path, 'field': 'CompilerLog', 'message': line})
    diagnostics.extend(compiler_diagnostics)

    has_error = any(d.get('severity') == 'error' for d in compiler_diagnostics)
    if log_offset is None:
        diagnostics.append(issue('BlueprintCompile.CompilerLogUnavailable', 'Could not snapshot the Editor log before compiling; compile health cannot be verified.', asset_path, 'CompilerLog'))
    elif session_start is not None and log_mtime_before < session_start:
        diagnostics.append(issue('BlueprintCompile.CompilerLogStale', 'The selected Editor log predates this Editor process session.', asset_path, 'CompilerLog'))
    elif not log_grew:
        diagnostics.append(issue('BlueprintCompile.CompilerLogStale', 'The selected Editor log did not grow during compile; it may be stale or not be this Editor process log.', asset_path, 'CompilerLog'))
    ok = not any(d.get('code') != 'BlueprintCompile.CompilerLog' for d in diagnostics) and not has_error
    emit({
        'ok': ok,
        'summary': ('AnimBlueprint compile completed with warnings.' if any(d.get('severity') == 'warning' for d in compiler_diagnostics) else 'AnimBlueprint compile completed.') if ok else 'AnimBlueprint validation failed; inspect the diagnostic fields and Editor compiler output.',
        'asset_path': asset_path,
        'asset_class': asset.get_class().get_name(),
        'fields': {'compile_api': 'unreal.BlueprintEditorLibrary.compile_blueprint', 'compile_attempted': True, 'generated_class': generated_path},
        'diagnostics': diagnostics,
        'compiler_log_path': log_path,
        'compiler_message_capture': 'The log path uses C2_EDITOR_LOG_PATH, then the current process -abslog argument, then the project default. Verification requires the file to grow during compile; new [Compiler] lines are structured and asset_match is textual best-effort attribution.',
        'compiler_log_size_before': log_offset,
        'compiler_log_mtime_before': log_mtime_before,
        'compiler_log_mtime_after': log_mtime_after,
        'editor_session_start_epoch': session_start,
        'compiler_log_grew_during_compile': log_grew,
        'saved': False,
    })


main()
