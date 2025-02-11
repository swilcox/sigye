from abc import ABC, abstractmethod

from ..models import EntryListFilter, TimeEntry


class TimeEntryRepository(ABC):
    @abstractmethod
    def save(self, entry: TimeEntry) -> None:
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
    def filter(self, *, filter: EntryListFilter) -> list[TimeEntry]:
        pass

    @abstractmethod
    def get_entry_by_id(self) -> TimeEntry:
        pass

    @abstractmethod
    def delete_entry(self, id: str) -> TimeEntry:
        pass

    @abstractmethod
    def save_all(self, entries: list[TimeEntry]) -> None:
        pass
