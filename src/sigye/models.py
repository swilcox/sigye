from datetime import date, datetime, timedelta
from typing import Literal, Self
from uuid import uuid4

import humanize
import humanize.i18n
from pydantic import BaseModel, Field, model_validator


class TimeEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    start_time: datetime
    end_time: datetime | None = None
    project: str
    tags: set[str] = Field(default_factory=set)
    comment: str = ""

    @model_validator(mode="after")
    def check_times_valid(self) -> Self:
        if self.end_time and self.end_time < self.start_time:
            raise ValueError("end time is before start time")
        return self

    @property
    def humanized_duration(self):
        td = self.end_time - self.start_time if self.end_time else datetime.now().astimezone() - self.start_time

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
        if self.end_time is None or (self.end_time is not None and self.end_time < self.start_time):
            self.end_time = end_time or datetime.now().astimezone()
        else:
            raise ValueError("already stopped")
        self.__class__.model_validate(self.model_dump())

    @property
    def duration(self):
        return self.end_time - self.start_time if self.end_time else datetime.now().astimezone() - self.start_time


class EntryListFilter(BaseModel):
    id: str = ""
    projects: set[str] = Field(default_factory=set)
    start_date: date | None = None
    end_date: date | None = None
    tags: set[str] = Field(default_factory=set)
    time_period: Literal["today", "yesterday", "week", "month", "all", ""] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.time_period:
            self._apply_time_period()

    def _apply_time_period(self):
        """Apply date filters based on time period"""
        now = datetime.now()
        if self.time_period == "all":
            return  # No need to set date filters
        if self.time_period == "today":
            self.start_date = now.date()
        if self.time_period == "yesterday":
            self.start_date = now.date() - timedelta(days=1)
            self.end_date = now.date() - timedelta(days=1)
        elif self.time_period == "week":
            self.start_date = now.date() - timedelta(days=now.date().weekday())  # Monday
        elif self.time_period == "month":
            self.start_date = now.date() - timedelta(days=(now.date().day - 1))  # 1st of current month
