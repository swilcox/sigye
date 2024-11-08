from abc import ABC, abstractmethod
from ..models import TimeEntry, EntryListFilter


class TimeEntryRepository(ABC):
    @abstractmethod
    def save(self, entry: TimeEntry) -> TimeEntry:
        pass

    @abstractmethod
    def get_active_entry(self) -> TimeEntry | None:
        pass

    @abstractmethod
    def get_by_project(self, project: str) -> list[TimeEntry]:
        pass

    @abstractmethod
    def get_all(self) -> list[TimeEntry]:
        pass

    @abstractmethod
    def filter(self, *, filter: EntryListFilter):
        pass

    @abstractmethod
    def get_entry_by_id(self) -> TimeEntry:
        pass
