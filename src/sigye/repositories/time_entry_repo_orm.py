import json
from datetime import datetime
from typing import Self

from peewee import CharField, DateTimeField, Model, fn
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from ..models import EntryListFilter, TimeEntry
from .time_entry_repo import TimeEntryRepository

db = SqliteExtDatabase(None)


class TimeEntryORM(Model):
    id = CharField(primary_key=True)
    start_time = DateTimeField()
    end_time = DateTimeField(null=True)
    project = CharField()
    comment = CharField()
    tags = JSONField()

    class Meta:
        database = db
        table_name = "time_entries"

    def to_model(self) -> TimeEntry:
        return TimeEntry(
            id=self.id,
            start_time=self.start_time,
            end_time=self.end_time,
            project=self.project,
            comment=self.comment,
            tags=set(self.tags),
        )

    @classmethod
    def create_from_model(cls, entry: TimeEntry) -> Self:
        return cls.create(
            id=entry.id,
            start_time=entry.start_time,
            end_time=entry.end_time,
            project=entry.project,
            comment=entry.comment,
            tags=list(entry.tags),
        )


def json_array_contains(json_array, value):
    return value in json.loads(json_array) if json_array else False


class TimeEntryRepositoryORM(TimeEntryRepository):
    def __init__(self, db_path: str):
        db.init(db_path)
        db.connect()
        db.create_tables([TimeEntryORM])
        db.connection().create_function("json_array_contains", 2, json_array_contains)

    def get_all(self) -> list[TimeEntry]:
        return [entry.to_model() for entry in TimeEntryORM.select().order_by(TimeEntryORM.start_time.asc())]

    def get_by_project(self, project: str) -> list[TimeEntry]:
        return [entry.to_model() for entry in TimeEntryORM.select().where(TimeEntryORM.project == project)]

    def get_entry_by_id(self, id: str) -> TimeEntry:
        try:
            return TimeEntryORM.get(TimeEntryORM.id == id).to_model()
        except TimeEntryORM.DoesNotExist as e:
            raise KeyError("record id not found") from e

    def delete_entry(self, id: str) -> TimeEntry:
        try:
            entry = TimeEntryORM.get(TimeEntryORM.id == id)
            entry.delete_instance()
            return entry.to_model()
        except TimeEntryORM.DoesNotExist as e:
            raise KeyError("record id not found") from e

    def get_active_entry(self):
        return TimeEntryORM.get(TimeEntryORM.end_time.is_null()).to_model()

    def filter(self, *, filter: EntryListFilter | None = None) -> list[TimeEntry]:
        query = TimeEntryORM.select().order_by(TimeEntryORM.start_time.asc())
        if filter:
            if filter.id:
                query = query.where(TimeEntryORM.id.startswith(filter.id))
            if filter.projects:
                query = query.where(TimeEntryORM.project.in_(filter.projects))
            if filter.start_date:
                query = query.where(TimeEntryORM.start_time >= filter.start_date)
            if filter.end_date:
                query = query.where(TimeEntryORM.start_time <= datetime.combine(filter.end_date, datetime.max.time()))
            if filter.tags:
                for tag in filter.tags:
                    query = query.where(fn.json_array_contains(TimeEntryORM.tags, tag))
        return [entry.to_model() for entry in query]

    def save(self, entry: TimeEntry) -> None:
        try:
            orm_entry = TimeEntryORM.get(TimeEntryORM.id == entry.id)
        except TimeEntryORM.DoesNotExist:
            orm_entry = TimeEntryORM.create_from_model(entry)
        orm_entry.save()

    def save_all(self, entries: list[TimeEntry]) -> None:
        with db.atomic():
            data = [entry.model_dump(mode="json") for entry in entries]
            TimeEntryORM.insert_many(data).execute()
