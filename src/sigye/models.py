from datetime import datetime, date, timedelta
from uuid import uuid4
from typing import Literal

import humanize.i18n
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
    id: str = ""
    projects: set[str] = Field(default_factory=set)
    start_date: date | None = None
    end_date: date | None = None
    tags: set[str] = Field(default_factory=set)
    time_period: Literal["today", "week", "month"] | None = None
    output_format: str | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.time_period:
            self._apply_time_period()

    def _apply_time_period(self):
        """Apply date filters based on time period"""
        now = datetime.now()
        if self.time_period == "today":
            self.start_date = now.date()
        elif self.time_period == "week":
            self.start_date = now.date() - timedelta(
                days=now.date().weekday()
            )  # Monday
        elif self.time_period == "month":
            self.start_date = now.date() - timedelta(
                days=(now.date().day - 1)
            )  # 1st of current month
