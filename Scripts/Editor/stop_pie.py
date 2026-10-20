import unreal

sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub.editor_request_end_play()
print("Called editor_request_end_play()")
