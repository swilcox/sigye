import pytest

from ...models import EntryListFilter, TimeEntry
from ..time_entry_repo_orm import TimeEntryRepositoryORM


def test_entry_repo_orm_empty():
    """Test ORM repo with no entries."""
    repo = TimeEntryRepositoryORM(":memory:")

    assert repo.get_all() == []
    assert repo.get_by_project("test") == []
    with pytest.raises(KeyError):
        repo.get_entry_by_id("test")
    assert repo.filter() == []


def test_entry_repo_orm_standard():
    repo = TimeEntryRepositoryORM(":memory:")
    entry = TimeEntry(project="test", start_time="2021-01-01T00:00:00", tags=["tag1", "tag2"])
    repo.save(entry)
    assert repo.get_active_entry() == entry


def test_entry_repo_orm_filter():
    repo = TimeEntryRepositoryORM(":memory:")
    entry1 = TimeEntry(
        project="test",
        start_time="2021-01-01T00:00:00",
        end_time="2021-01-01T01:00:00",
        tags=["tag1", "tag2"],
        comment="test",
    )
    entry2 = TimeEntry(
        project="test2", start_time="2021-01-02T00:00:00", end_time="2021-01-02T01:30:00", tags=["tag2", "tag3"]
    )
    entry3 = TimeEntry(
        project="test3", start_time="2021-01-03T00:00:00", end_time="2021-01-03T02:00:00", tags=["tag1", "tag3"]
    )
    repo.save(entry1)
    repo.save(entry2)
    repo.save(entry3)
    filter1 = EntryListFilter(projects=["test"])
    assert repo.filter(filter=filter1) == [entry1]
    filter2 = EntryListFilter(tags=["tag1"])
    assert repo.filter(filter=filter2) == [entry1, entry3]
    filter3 = EntryListFilter(start_date="2021-01-02")
    assert repo.filter(filter=filter3) == [entry2, entry3]
    assert repo.filter() == [entry1, entry2, entry3]
    filter4 = EntryListFilter(end_date="2021-01-02")
    assert repo.filter(filter=filter4) == [entry1, entry2]
    filter5 = EntryListFilter(id=entry1.id[0:4])
    assert repo.filter(filter=filter5) == [entry1]
    filter6 = EntryListFilter(tags=["blah"])
    assert repo.filter(filter=filter6) == []


def test_entry_repo_orm_delete():
    repo = TimeEntryRepositoryORM(":memory:")
    entry1 = TimeEntry(
        project="test",
        start_time="2021-01-01T00:00:00",
        stop_time="2021-01-01T01:00:00",
        tags=["tag1", "tag2"],
        comment="test",
    )
    repo.save(entry1)
    assert repo.get_all() == [entry1]
    d_entry = repo.delete_entry(entry1.id)
    assert d_entry == entry1
    assert repo.get_all() == []
    with pytest.raises(KeyError):
        repo.delete_entry("test")
