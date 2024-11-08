import os
import yaml
from ..models import TimeEntry, EntryListFilter
from .time_entry_repo import TimeEntryRepository


class TimeEntryRepositoryYaml(TimeEntryRepository):
    def __init__(self, filename: str = "timesheet.yaml"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            self._save_data({"entries": []})

    def _load_data(self) -> list[TimeEntry]:
        with open(self.filename, "r") as f:
            return yaml.load(f, yaml.FullLoader)

    def _save_data(self, data: dict):
        with open(self.filename, "w") as f:
            yaml.dump(data, f)

    def get_active_entry(self) -> TimeEntry | None:
        data = self._load_data()
        active = next((e for e in data["entries"] if not e.get("end_time")), None)
        return TimeEntry(**active) if active else None

    def get_all(self):
        data = self._load_data()
        return [TimeEntry(**entry) for entry in data["entries"]]

    def get_by_project(self, project):
        data = self._load_data()
        return [
            TimeEntry(**entry)
            for entry in data["entries"]
            if entry["project"] == project
        ]

    def get_entry_by_id(self, id: str):
        data = self._load_data()
        for entry in data["entries"]:
            if entry["id"] == id:
                return TimeEntry(**entry)
        raise KeyError("record id not found")

    def filter(self, *, filter: EntryListFilter | None = None) -> list[TimeEntry]:
        # QUESTION: are multiple fields in a filter an AND or an OR?
        time_entries = self.get_all()
        if filter is None:
            return time_entries
        filtered_entries = []
        for entry in time_entries:
            if filter.project and filter.project == entry.project:
                filtered_entries.append(entry)
            elif filter.project__starts_with and entry.project.startswith(
                filter.project__starts_with
            ):
                filtered_entries.append(entry)
            elif filter.start_date and entry.start_time.date() >= filter.start_date:
                filtered_entries.append(entry)
            elif (
                filter.end_date
                and entry.end_time
                and entry.end_time.date() <= filter.end_date
            ):
                filtered_entries.append(entry)
        return filtered_entries

    def save(self, entry: TimeEntry) -> None:
        data = self._load_data()
        entry_dict = entry.model_dump(mode="json")
        found = False
        entries = []
        for e in data["entries"]:
            if e["id"] == entry.id:
                entries.append(entry_dict)
                found = True
            else:
                entries.append(e)
        if not found:
            entries.append(entry_dict)
        data["entries"] = entries
        self._save_data(data)
