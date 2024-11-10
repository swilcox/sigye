import pytest
from datetime import datetime, timedelta

from ..services import TimeTrackingService
from ..repositories.time_entry_repo_yaml import TimeEntryRepositoryYaml
from ..models import EntryListFilter


def test_basic_time_tracking(tmp_path):
    filename = tmp_path / "test.yaml"
    tts = TimeTrackingService(repository=TimeEntryRepositoryYaml(filename))
    assert tts.list_entries() == []
    a = tts.start_tracking("test-project")
    assert a.end_time is None
    assert tts.get_active_entry() == a
    b = tts.stop_tracking()
    assert b.start_time == a.start_time
    assert b.end_time is not None
    c = tts.stop_tracking()
    assert c is None

    entries = tts.list_entries()
    assert len(entries) == 1
    assert entries[0] == b


def test_start_stop(tmp_path):
    filename = tmp_path / "test.yaml"
    tts = TimeTrackingService(repository=TimeEntryRepositoryYaml(filename))

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    d2 = tts.start_tracking("test-project-2")
    assert d2.end_time is None
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None


def test_filtered_list(tmp_path):
    filename = tmp_path / "test.yaml"
    tts = TimeTrackingService(repository=TimeEntryRepositoryYaml(filename))

    # Create entries with different projects and tags
    d1 = tts.start_tracking("test-project", tags={"tag1", "tag2"})
    tts.stop_tracking()
    d2 = tts.start_tracking("test-project-2", tags={"tag2", "tag3"})
    tts.stop_tracking()
    d3 = tts.start_tracking("test-project-3", tags={"tag1", "tag3"})
    tts.stop_tracking()

    # Test no filter
    l1 = tts.list_entries(filter=None)
    assert len(l1) == 3

    # Test project filter
    filter_by_projects = EntryListFilter(projects={"test-project", "test-project-2"})
    l2 = tts.list_entries(filter=filter_by_projects)
    assert len(l2) == 2
    assert all(e.project in {"test-project", "test-project-2"} for e in l2)

    # Test tag filter
    filter_by_tags = EntryListFilter(tags={"tag1"})
    l3 = tts.list_entries(filter=filter_by_tags)
    assert len(l3) == 2
    assert all("tag1" in e.tags for e in l3)

    # Test date filter
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    filter_by_date = EntryListFilter(start_date=yesterday.date())
    l5 = tts.list_entries(filter=filter_by_date)
    assert len(l5) == 3

    # Test combined filters
    combined_filter = EntryListFilter(
        projects={"test-project"}, tags={"tag1"}, start_date=yesterday.date()
    )
    l6 = tts.list_entries(filter=combined_filter)
    assert len(l6) == 1
    assert l6[0].project == "test-project"
    assert "tag1" in l6[0].tags

    # Test time period filter
    period_filter = EntryListFilter(time_period="today")
    l7 = tts.list_entries(filter=period_filter)
    assert len(l7) == 3
    assert all(e.start_time.date() == now.date() for e in l7)


def test_invalid_entry_fetch(tmp_path):
    filename = tmp_path / "test.yaml"
    tts = TimeTrackingService(repository=TimeEntryRepositoryYaml(filename))

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    tts.stop_tracking()
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None

    with pytest.raises(KeyError):
        _ = tts.get_entry("invalid value here!")
