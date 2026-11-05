"""Dispatch one selected Content Browser asset to its C2 validation action."""
import importlib.util
import os

import unreal

ROOT = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2'
SCHEMA_PATH = ROOT + '/receipt_schema.py'
_spec = importlib.util.spec_from_file_location('c2_receipt_schema', SCHEMA_PATH)
schema = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(schema)


def stop(code, message):
    receipt = {
        'ok': False,
        'summary': message,
        'diagnostics': [{'code': code, 'field': 'ContentBrowserSelection', 'message': message}],
    }
    unreal.log('[C2_VALIDATE_BOSS] ' + schema.serialize_receipt(receipt, 'dispatch'))
    try:
        unreal.EditorDialog.show_message('Validate Boss', message, unreal.AppMsgType.OK)
    except Exception as exc:
        unreal.log_warning('[C2_VALIDATE_BOSS] dialog_unavailable error=%s' % str(exc)[:160])


try:
    selected = list(unreal.EditorUtilityLibrary.get_selected_assets())
except Exception as exc:
    stop('Selection.ReadFailed', 'Could not read Content Browser selection: ' + str(exc))
else:
    class_name = selected[0].get_class().get_name() if len(selected) == 1 else ''
    action, error = schema.dispatch_action(len(selected), class_name)
    if error:
        message = 'Select exactly one RPGBossFrameworkProfile or AnimBlueprint.' if error == 'Selection.Count' else 'Unsupported selected asset class: ' + class_name
        stop(error, message)
    else:
        action_path = os.path.join(ROOT, action)
        with open(action_path, 'r', encoding='utf-8') as stream:
            source = stream.read()
        exec(compile(source, action_path, 'exec'), {'__name__': '__main__'})
