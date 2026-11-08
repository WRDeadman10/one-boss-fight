import unreal

dest_dir = "/Game/OneBossFight/Player/Animations"
seq_path = f"{dest_dir}/AN_ER_Backstep_Mixamo"
montage_path = f"{dest_dir}/AM_ER_Backstep_Mixamo"

eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
AL = unreal.AnimationLibrary

seq = unreal.load_asset(seq_path)
if not seq:
    raise RuntimeError(f"Missing sequence: {seq_path}")

if eal.does_asset_exist(montage_path):
    eal.delete_asset(montage_path)

factory = unreal.AnimMontageFactory()
factory.set_editor_property("source_animation", seq)
montage = tools.create_asset("AM_ER_Backstep_Mixamo", dest_dir, unreal.AnimMontage, factory)

# 1. Set blend-in time to 0.10s
bi = montage.get_editor_property("blend_in")
try:
    bi.set_editor_property("blend_time", 0.10)
except Exception:
    bi.blend_time = 0.10
montage.set_editor_property("blend_in", bi)

# 2. Add notifies
clip_len = float(seq.get_editor_property("sequence_length"))
base_len = 0.4667
scale = clip_len / base_len

iframe_start = round(0.0750 * scale, 4)
iframe_dur = round((0.3428 - 0.0750) * scale, 4)
buffer_start = round(0.1640 * scale, 4)
buffer_dur = round(0.1874 * scale, 4)

AL.remove_all_animation_notify_tracks(montage)
AL.add_animation_notify_track(montage, "1")
AL.add_animation_notify_track(montage, "2")

iframe_cls = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AnimNotifies/ANS_iFrames.ANS_iFrames_C")
buffer_cls = unreal.load_object(None, "/Game/AdvancedARPGCombat/AdvancedCombatFramework/Input/AnimNotifies/ANS_InputBuffer.ANS_InputBuffer_C")

if iframe_cls:
    AL.add_animation_notify_state_event(montage, "1", iframe_start, iframe_dur, iframe_cls)
if buffer_cls:
    AL.add_animation_notify_state_event(montage, "2", buffer_start, buffer_dur, buffer_cls)

eal.save_loaded_asset(montage)

print(f"AM_ER_Backstep_Mixamo created successfully.")
print(f"  Length: {montage.get_editor_property('sequence_length'):.4f}s")
print(f"  Blend-in: 0.10s")
print(f"  Notifies:")
for ev in AL.get_animation_notify_events(montage):
    st = ev.get_editor_property("notify_state_class")
    no = ev.get_editor_property("notify")
    obj = st if st else no
    if obj:
        t = ev.get_editor_property("trigger_time_offset")
        d = ev.get_editor_property("duration")
        print(f"    {obj.get_class().get_name()} at {t:.4f}s for {d:.4f}s")
