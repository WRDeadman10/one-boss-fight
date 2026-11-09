"""C-1235 Lead read-only probe: print play length and sections of the Ember montages. Saves nothing."""
import unreal

for name in ("AM_Boss01_A1", "AM_Boss01_A2", "AM_Boss01_A3a", "AM_Boss01_A3b"):
    m = unreal.EditorAssetLibrary.load_asset("/Game/OneBossFight/Boss01/Animations/" + name)
    if m is None:
        unreal.log("[A2Probe] MISSING " + name)
        continue
    unreal.log("[A2Probe] %s play_length=%.6f sections=%d" % (name, m.get_play_length(), m.get_num_sections()))
