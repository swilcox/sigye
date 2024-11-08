import pytest

from ..services import TimeTrackingService
from ..repositories.time_entry_repo_yaml import TimeEntryRepositoryYaml


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

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    d2 = tts.start_tracking("test-project-2")
    assert d2.end_time is None
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None

    l1 = tts.list_entries(filter=None)
    assert len(l1) == 2

    # TODO: some tests related to filtering once we know how/what to filter


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
