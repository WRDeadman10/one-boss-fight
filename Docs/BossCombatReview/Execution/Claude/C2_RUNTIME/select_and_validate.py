# C2 runtime check (lead, Claude, 2026-11-04): select one known-valid framework profile in the Content Browser,
# then run the unchanged Codex C2 dispatcher. Read-only: the C2 actions report saved=false / compiled=false.
import os
import unreal

TARGET = os.environ.get('C2_RUNTIME_TARGET', '/Game/OneBossFight/FrameworkProof/DA_Sevarog_ComboOutcome_FAG23d')
DISPATCHER = 'C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/run_validate_boss.py'

asset = unreal.load_asset(TARGET)
assert asset is not None, 'target profile missing'
# The Content Browser selection does not take during a scripted startup (first attempt: selected=[]), so the selection
# getter is replaced by one returning the real loaded asset; everything else runs against real engine objects.
# (the engine type is immutable, so the module attribute is swapped for a stand-in; C2 only calls get_selected_assets)
class _SelectionStandIn:
    @staticmethod
    def get_selected_assets():
        return [asset]
unreal.EditorUtilityLibrary = _SelectionStandIn
selected = [a.get_path_name() for a in unreal.EditorUtilityLibrary.get_selected_assets()]
unreal.log('[C2_RUNTIME] selected=%s' % selected)
assert len(selected) == 1 and selected[0].split('.')[0] == TARGET, 'selection did not take: %s' % selected
exec(open(DISPATCHER, encoding='utf-8').read())
unreal.log('[C2_RUNTIME] dispatcher returned')
