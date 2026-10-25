"""P0 read-only probe: logs the editor performance settings that can throttle PIE (no property is set). Log prefix [P0Perf]."""
import unreal
cls = unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings")
cdo = unreal.get_default_object(cls)
for name in ("bThrottleCPUWhenNotForeground", "bMonitorEditorPerformance", "bShowFrameRateAndMemory", "bDisableRealtimeViewportsInRemoteSessions", "bOverrideMaxViewportRenderingFPS", "MaxViewportRenderingFPS", "bEnableScalabilityWarningIndicator"):
    try:
        unreal.log("[P0Perf] %s = %s" % (name, cdo.get_editor_property(name)))
    except Exception as e:
        unreal.log("[P0Perf] %s: %s" % (name, str(e)[:90]))
