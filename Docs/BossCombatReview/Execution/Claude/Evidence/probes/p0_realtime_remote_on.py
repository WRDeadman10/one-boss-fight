"""P0 harness helper: sets EditorPerformanceSettings.bDisableRealtimeViewportsInRemoteSessions to False for this editor process (in memory, same mechanism as Scripts/Editor/no_throttle.py; nothing is saved by this script). Log prefix [P0Perf]."""
import unreal
cdo = unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings"))
cdo.set_editor_property("bDisableRealtimeViewportsInRemoteSessions", False)
unreal.log("[P0Perf] bDisableRealtimeViewportsInRemoteSessions now %s" % cdo.get_editor_property("bDisableRealtimeViewportsInRemoteSessions"))
