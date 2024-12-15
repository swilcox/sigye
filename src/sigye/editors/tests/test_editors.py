from ..shell_editor import ShellEditor


def test_shell_editor():
    editor = ShellEditor("echo")
    assert editor.editor_command == "echo"
