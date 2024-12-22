from datetime import datetime

from .config.settings import Settings
from .editors import Editor
from .editors.shell_editor import ShellEditor
from .models import EntryListFilter, TimeEntry
from .repositories import TimeEntryRepository, TimeEntryRepositoryFile, TimeEntryRepositoryORM


class TimeTrackingService:
    def __init__(
        self,
        settings: Settings,
        repository: TimeEntryRepository | None = None,
        editor: Editor | None = None,
    ):
        self.settings = settings
        self.repository = repository or (
            TimeEntryRepositoryORM(settings.data_filename)
            if settings.data_filename.suffix == ".db"
            else TimeEntryRepositoryFile(settings.data_filename)
        )
        self.editor = editor or ShellEditor(settings.editor, settings.editor_format)

    def start_tracking(
        self,
        project: str,
        start_time: datetime | None = None,
        comment: str = "",
        tags: set[str] = None,
    ) -> TimeEntry:
        """Start tracking time for a project"""
        start_time = start_time or datetime.now().astimezone()
        if active_entry := self.repository.get_active_entry():
            active_entry.stop(end_time=start_time)  # Stop any active entry first
            self.repository.save(active_entry)

        # Apply auto-tagging rules
        final_tags = (tags or set()) | self.settings.apply_auto_tags(project)

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
        """Stop the active time entry"""
        active_entry = self.repository.get_active_entry()
        if active_entry:
            active_entry.stop(stop_time)
            self.repository.save(active_entry)
            return active_entry
        return None

    def get_active_entry(self) -> TimeEntry | None:
        """Get the active time entry"""
        return self.repository.get_active_entry()

    def list_entries(self, filter: EntryListFilter | None = None) -> list[TimeEntry]:
        """List time entries based on filter"""
        if filter:
            return self.repository.filter(filter=filter)
        return self.repository.get_all()

    def get_entry(self, id: str) -> TimeEntry:
        """Get an entry by id"""
        return self.repository.get_entry_by_id(id)

    def update_entry(self, entry: TimeEntry) -> TimeEntry:
        """Update an existing time entry"""
        self.get_entry(entry.id)
        self.repository.save(entry)
        return entry

    def delete_entry(self, id: str):
        """Delete an existing time entry"""
        return self.repository.delete_entry(id)

    def edit_entry(self, id: str):
        """Edit an existing time entry"""
        entry = self.get_entry(id)
        updated_entry = self.editor.edit_entry(entry)
        return self.update_entry(updated_entry)

    def get_entry_by_partial_id(self, partial_id: str) -> TimeEntry:
        """Get an entry by a partial id"""
        entries = self.list_entries(EntryListFilter(id=partial_id))
        if len(entries) == 1:
            return entries[0]
        elif len(entries) > 1:
            raise IndexError("Multiple entries found")
        raise KeyError("record id not found")

    def export_entries(self, filename: str) -> int:
        """Export entries to a file"""
        entries = self.list_entries()
        output_repository = (
            TimeEntryRepositoryFile(filename) if filename.suffix != ".db" else TimeEntryRepositoryORM(filename)
        )
        output_repository.save_all(entries)
        return len(entries)
