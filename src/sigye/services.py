# domain/services.py
from datetime import datetime
from .models import EntryListFilter, TimeEntry
from .repositories.time_entry_repo import TimeEntryRepository


class TimeTrackingService:
    def __init__(self, repository: TimeEntryRepository):
        self.repository = repository

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

        # Create and save new entry
        new_entry = TimeEntry(
            project=project,
            start_time=start_time or datetime.now().astimezone(),
            comment=comment,
            tags=tags or set(),
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


# start
# stop
# status
# list (today, this week, this month, )
