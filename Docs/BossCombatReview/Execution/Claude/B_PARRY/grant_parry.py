# PARRY (lead, Claude, owner decision 2026-11-02: the player needs a parry): adds ONE AbilitiesSet entry (InputTag.Parry -> GA_PlayerParry_C) to each player combat style that already grants the block (InputTag.Block -> GA_PlayerGuardBlock_C).
# The new entry is a copy of the style's own block entry with the two names swapped, so the struct layout is the pack's. Idempotent (skips a style that already has the parry), reads back, saves only the styles it changed. Never deletes or recreates an asset.
import unreal
W = '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/'
STYLES = ['Sword/SwordCombatStyle', 'Claymore/ClaymoreCombatStyle', 'DualSwords/DualSwordCombatStyle', 'Polearms/PolearmCombatStyle']


def tag(t, payload):
    unreal.log('[PARRY_GRANT_%s] %s' % (t, payload))


changed = []
for name in STYLES:
    a = unreal.load_asset(W + name)
    if a is None:
        tag('MISSING', name)
        continue
    entries = list(a.get_editor_property('AbilitiesSet'))
    texts = [e.export_text() for e in entries]
    if any('GA_PlayerParry' in t for t in texts):
        tag('SKIP_ALREADY', name)
        continue
    block = [i for i, t in enumerate(texts) if 'GA_PlayerGuardBlock' in t and 'InputTag.Block' in t]
    if len(block) != 1:
        tag('SKIP_NO_SINGLE_BLOCK_ENTRY', '%s %s' % (name, block))
        continue
    new = entries[block[0]].copy()
    text = texts[block[0]].replace('InputTag.Block', 'InputTag.Parry').replace('GA_PlayerGuardBlock', 'GA_PlayerParry')
    new.import_text(text)
    if 'GA_PlayerParry_C' not in new.export_text() or 'InputTag.Parry' not in new.export_text():
        tag('FATAL_IMPORT', '%s %s' % (name, new.export_text()[:300]))
        continue
    a.set_editor_property('AbilitiesSet', entries + [new])
    back = [e.export_text() for e in a.get_editor_property('AbilitiesSet')]
    ok = len(back) == len(entries) + 1 and any('GA_PlayerParry_C' in t and 'InputTag.Parry' in t for t in back) and any('GA_PlayerGuardBlock_C' in t for t in back)
    tag('READBACK', '%s n_before=%d n_after=%d ok=%s' % (name, len(entries), len(back), ok))
    if not ok:
        continue
    if not unreal.EditorAssetLibrary.save_loaded_asset(a):
        tag('FATAL_SAVE', name)
        continue
    changed.append(name)
tag('END', changed)
