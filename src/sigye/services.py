# domain/services.py
import os
import subprocess
import tempfile
from datetime import datetime

import yaml

from .config.settings import Settings
from .models import EntryListFilter, TimeEntry
from .repositories.time_entry_repo import TimeEntryRepository
from .repositories.time_entry_repo_yaml import TimeEntryRepositoryYaml


class EditorServiceError(Exception): ...


class EditorService:
    """Base Editor Service class"""

    def __init__(self, editor_command: str):
        self.editor_command = editor_command

    def edit_entry(self, entry: TimeEntry) -> TimeEntry:
        raise NotImplementedError()


class YAMLEditorService(EditorService):
    """Editor service for YAML-formatted time entries"""

    def _format_entry_for_edit(self, entry: TimeEntry) -> str:
        """Format a time entry as YAML for editing"""
        entry_dict = entry.model_dump(mode="json")
        return yaml.dump(entry_dict)

    def _parse_edited_entry(self, content: str) -> TimeEntry:
        """Parse edited YAML content back into a TimeEntry"""
        try:
            data = yaml.safe_load(content)
            return TimeEntry(**data)
        except Exception as e:
            raise EditorServiceError(f"Invalid entry format: {str(e)}") from e

    def edit_entry(self, entry: TimeEntry) -> TimeEntry:
        """Edit a time entry in the user's preferred editor"""
        # Create temp file with entry content
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as tmp:
            tmp.write(self._format_entry_for_edit(entry))
            tmp.flush()
            tmp_path = tmp.name

        try:
            # Open editor
            subprocess.run([self.editor_command, tmp_path], check=True)

            # Read and parse edited content
            with open(tmp_path) as f:
                edited_content = f.read()
                updated_entry = self._parse_edited_entry(edited_content)

            return updated_entry

        finally:
            # Clean up temp file
            os.unlink(tmp_path)


class TimeTrackingService:
    def __init__(
        self,
        settings: Settings,
        repository: TimeEntryRepository | None = None,
        editor: EditorService | None = None,
    ):
        self.settings = settings
        self.repository = repository or TimeEntryRepositoryYaml(settings.data_filename)
        self.editor = editor or YAMLEditorService(settings.editor)

    def start_tracking(
        self,
        project: str,
        start_time: datetime | None = None,
        comment: str = "",
        tags: set[str] = None,
    ) -> TimeEntry:
        start_time = start_time or datetime.now().astimezone()
        # Stop any active entry first
        if active_entry := self.repository.get_active_entry():
            active_entry.stop(end_time=start_time)
            self.repository.save(active_entry)

        # Apply auto-tagging rules
        auto_tags = self.settings.apply_auto_tags(project)
        final_tags = (tags or set()) | auto_tags

        # Create and save new entry
        new_entry = TimeEntry(
            project=project,
            start_time=start_time,
            comment=comment,
            tags=final_tags,
        )
        self.repository.save(new_entry)
        return new_entry

    def stop_tracking(self, stop_time: datetime | None = None) -> TimeEntry | None:
        active_entry = self.repository.get_active_entry()
        if active_entry:
            active_entry.stop(stop_time)
            self.repository.save(active_entry)
            return active_entry
        return None

    def get_active_entry(self) -> TimeEntry | None:
        return self.repository.get_active_entry()

    def list_entries(self, filter: EntryListFilter | None = None) -> list[TimeEntry]:
        if filter:
            return self.repository.filter(filter=filter)
        return self.repository.get_all()

    def get_entry(self, id: str) -> TimeEntry:
        return self.repository.get_entry_by_id(id)

    def update_entry(self, entry: TimeEntry) -> TimeEntry:
        """Update an existing time entry"""
        # Verify the entry exists first
        self.get_entry(entry.id)
        self.repository.save(entry)
        return entry

    def delete_entry(self, id: str):
        return self.repository.delete_entry(id)

    def edit_entry(self, id: str):
        entry = self.get_entry(id)
        updated_entry = self.editor.edit_entry(entry)
        return self.update_entry(updated_entry)

    def get_entry_by_partial_id(self, partial_id: str) -> TimeEntry:
        entries = self.list_entries(EntryListFilter(id=partial_id))
        if len(entries) == 1:
            return entries[0]
        elif len(entries) > 1:
            raise IndexError("Multiple entries found")
        raise KeyError("record id not found")
