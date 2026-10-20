"""Turns off the editor's background CPU throttling for this session (the viewport and PIE otherwise render at a crawl when the window is not focused)."""
import unreal
unreal.get_default_object(unreal.load_class(None, "/Script/UnrealEd.EditorPerformanceSettings")).set_editor_property("bThrottleCPUWhenNotForeground", False)
unreal.log("[Throttle] off")
