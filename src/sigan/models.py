from datetime import datetime, date
from uuid import uuid4

from pydantic import BaseModel, Field
import humanize


class TimeEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    start_time: datetime
    end_time: datetime | None = None
    project: str
    tags: set[str] = Field(default_factory=set)
    comment: str = ""

    @property
    def humanized_duration(self):
        td = (
            self.end_time - self.start_time
            if self.end_time
            else datetime.now().astimezone() - self.start_time
        )
        return humanize.precisedelta(
            td,
            suppress=("seconds", "milliseconds", "microseconds"),
            minimum_unit="hours",
            format="%0.1f",
        )

    @staticmethod
    def _get_naive_time(ts: datetime) -> datetime | None:
        """remove the tzinfo so we get the original hour"""
        return ts.replace(tzinfo=None) if ts else None

    @property
    def naive_start_time(self):
        return self._get_naive_time(self.start_time)

    @property
    def naive_end_time(self):
        return self._get_naive_time(self.end_time)

    def stop(self, end_time: datetime = None):
        if self.end_time is None or (
            self.end_time is not None and self.end_time < self.start_time
        ):
            self.end_time = end_time or datetime.now().astimezone()
        else:
            raise ValueError("already stopped")

    @property
    def duration(self):
        return (
            self.end_time - self.start_time
            if self.end_time
            else datetime.now().astimezone() - self.start_time
        )


class EntryListFilter(BaseModel):
    project: str | None = None
    project__starts_with: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    tags: set[str] | None = None
