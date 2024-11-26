# domain/services.py
from datetime import datetime
import os
import subprocess
import tempfile
import yaml
from .models import EntryListFilter, TimeEntry
from .repositories.time_entry_repo import TimeEntryRepository
from .config.settings import Settings


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
            raise EditorServiceError(f"Invalid entry format: {str(e)}")

    def edit_entry(self, entry: TimeEntry) -> TimeEntry:
        """Edit a time entry in the user's preferred editor"""
        # Create temp file with entry content
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", mode="w+", delete=False
        ) as tmp:
            tmp.write(self._format_entry_for_edit(entry))
            tmp.flush()
            tmp_path = tmp.name

        try:
            # Open editor
            subprocess.run([self.editor_command, tmp_path], check=True)

            # Read and parse edited content
            with open(tmp_path, "r") as f:
                edited_content = f.read()
                updated_entry = self._parse_edited_entry(edited_content)

            return updated_entry

        finally:
            # Clean up temp file
            os.unlink(tmp_path)


class TimeTrackingService:
    def __init__(self, repository: TimeEntryRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def start_tracking(
        self,
        project: str,
        start_time: datetime | None = None,
        comment: str = "",
        tags: set[str] = None,
    ) -> TimeEntry:
        # Stop any active entry first
        active_entry = self.repository.get_active_entry()
        if active_entry:
            active_entry.stop()
            self.repository.save(active_entry)

        # Apply auto-tagging rules
        auto_tags = self.settings.apply_auto_tags(project)
        final_tags = (tags or set()) | auto_tags

        # Create and save new entry
        new_entry = TimeEntry(
            project=project,
            start_time=start_time or datetime.now().astimezone(),
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
        edit_service = YAMLEditorService(self.settings.editor)
        updated_entry = edit_service.edit_entry(entry)
        return self.update_entry(updated_entry)


# start
# stop
# status
# list (today, this week, this month, )
