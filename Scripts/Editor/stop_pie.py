"""Ends a running PIE session (no log)."""
import unreal
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
