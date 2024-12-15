import os
import subprocess
import tempfile

import rtoml as toml
import ryaml

from ..models import TimeEntry
from . import Editor, EditorError


class EditFormat:
    """Base class for file formats used in editing"""

    def __init__(self, extension: str):
        self.extension = extension

    def __repr__(self):
        return f"{self.__class__.__name__}({self.extension!r})"

    @property
    def suffix(self):
        return f".{self.extension}"


class YAMLFormat(EditFormat):
    """YAML file format"""

    def __init__(self):
        super().__init__("yaml")

    def format_entry_for_edit(self, entry: TimeEntry) -> str:
        """Format a time entry as YAML for editing"""
        entry_dict = entry.model_dump(mode="json")
        return ryaml.dumps(entry_dict)

    def parse_edited_entry(self, content: str) -> TimeEntry:
        """Parse edited YAML content back into a TimeEntry"""
        try:
            data = ryaml.loads(content)
            return TimeEntry(**data)
        except Exception as e:
            raise EditorError(f"Invalid entry format: {str(e)}") from e


class TOMLFormat(EditFormat):
    """TOML file format"""

    def __init__(self):
        super().__init__("toml")

    def format_entry_for_edit(self, entry: TimeEntry) -> str:
        """Format a time entry as TOML for editing"""
        entry_dict = entry.model_dump(mode="json")
        return toml.dumps(entry_dict)

    def parse_edited_entry(self, content: str) -> TimeEntry:
        """Parse edited TOML content back into a TimeEntry"""
        try:
            data = toml.loads(content)
            return TimeEntry(**data)
        except Exception as e:
            raise EditorError(f"Invalid entry format: {str(e)}") from e


class ShellEditor(Editor):
    """Editor for shelling to editor to update time entries"""

    def __init__(self, editor_command: str, format: EditFormat | str | None = None):
        super().__init__(editor_command)
        if isinstance(format, str) and format.lower() == "toml":
            self.format = TOMLFormat()
        elif isinstance(format, EditFormat):
            self.format = format
        else:
            self.format = YAMLFormat()

    def edit_entry(self, entry: TimeEntry) -> TimeEntry:
        """Edit a time entry in the user's preferred editor"""
        # Create temp file with entry content
        with tempfile.NamedTemporaryFile(suffix=self.format.suffix, mode="w+", delete=False) as tmp:
            tmp.write(self.format.format_entry_for_edit(entry))
            tmp.flush()
            tmp_path = tmp.name

        try:
            # Open editor
            subprocess.run([self.editor_command, tmp_path], check=True)

            # Read and parse edited content
            with open(tmp_path) as f:
                edited_content = f.read()
                updated_entry = self.format.parse_edited_entry(edited_content)

            return updated_entry

        finally:
            # Clean up temp file
            os.unlink(tmp_path)
