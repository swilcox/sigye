from ..models import TimeEntry


class EditorError(Exception): ...


class Editor:
    """Base Editor Service class"""

    def __init__(self, editor_command: str):
        self.editor_command = editor_command

    def edit_entry(self, entry: TimeEntry) -> TimeEntry:
        raise NotImplementedError()
