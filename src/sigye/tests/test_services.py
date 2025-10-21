from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ..config.settings import AutoTagRule, Settings
from ..editors import Editor
from ..editors.shell_editor import ShellEditor
from ..models import EntryListFilter
from ..repositories import TimeEntryRepositoryFile
from ..services import TimeTrackingService


class DummyEditorService(Editor):
    def edit_entry(self, entry):
        entry.comment = "edited by dummy editor"
        return entry


def create_test_settings(tmp_path: Path) -> Settings:
    """Create test settings with a specific configuration"""
    settings = Settings(data_filename=str(tmp_path / "test.yaml"), locale="en_US")
    settings.auto_tag_rules = [
        AutoTagRule(pattern="^abc", match_type="regex", tags=["learning"]),
        AutoTagRule(pattern="^PROJ-\\d+", match_type="regex", tags=["work", "billable"]),
        AutoTagRule(pattern="(feature|bugfix)/", match_type="regex", tags=["development"]),
        AutoTagRule(pattern="-urgent$", match_type="regex", tags=["priority"]),
    ]
    return settings


def test_initialization(tmp_path):
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(settings=settings)
    assert tts.settings == settings
    assert tts.repository.filename == tts.settings.data_filename
    assert isinstance(tts.editor, ShellEditor)
    tts = TimeTrackingService(settings=settings, editor=DummyEditorService("nothing"))
    assert isinstance(tts.editor, DummyEditorService)


def test_basic_time_tracking(tmp_path):
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)
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


def test_auto_tagging(tmp_path):
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    # Test regex matching with '^abc' pattern
    entry1 = tts.start_tracking("abc-learning-task")
    assert "learning" in entry1.tags
    tts.stop_tracking()

    # Test regex matching with '^PROJ-\d+' pattern
    entry2 = tts.start_tracking("PROJ-123")
    assert "work" in entry2.tags
    assert "billable" in entry2.tags
    tts.stop_tracking()

    # Test regex matching with '(feature|bugfix)/' pattern
    entry3 = tts.start_tracking("feature/new-ui")
    assert "development" in entry3.tags
    tts.stop_tracking()

    entry4 = tts.start_tracking("bugfix/issue-123")
    assert "development" in entry4.tags
    tts.stop_tracking()

    # Test regex matching with '-urgent$' pattern
    entry5 = tts.start_tracking("task-urgent")
    assert "priority" in entry5.tags
    tts.stop_tracking()

    # Test no auto-tagging for non-matching project
    entry6 = tts.start_tracking("regular-task")
    assert len(entry6.tags) == 0
    tts.stop_tracking()

    # Test merging auto-tags with user-provided tags
    entry7 = tts.start_tracking("abc-task", tags={"custom-tag"})
    assert "learning" in entry7.tags
    assert "custom-tag" in entry7.tags
    tts.stop_tracking()


def test_start_stop(tmp_path):
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    d2 = tts.start_tracking("test-project-2")
    assert d2.end_time is None
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None


def test_filtered_list(tmp_path):
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    # Create entries with different projects and tags
    d1 = tts.start_tracking("test-project", tags={"tag1", "tag2"})
    tts.stop_tracking()
    d2 = tts.start_tracking("test-project-2", tags={"tag2", "tag3"})
    tts.stop_tracking()
    d3 = tts.start_tracking("test-project-3", tags={"tag1", "tag3"})
    tts.stop_tracking()
    assert all(entry is not None for entry in [d1, d2, d3])

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
    combined_filter = EntryListFilter(projects={"test-project"}, tags={"tag1"}, start_date=yesterday.date())
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
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    tts.stop_tracking()
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None

    with pytest.raises(KeyError):
        _ = tts.get_entry("invalid value here!")


def test_delete_entry(tmp_path):
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    tts.stop_tracking()
    d1 = tts.get_entry(d1.id)
    assert d1.end_time is not None

    tts.delete_entry(d1.id)

    with pytest.raises(KeyError):
        _ = tts.get_entry(d1.id)


def test_configuration_loading(tmp_path):
    """Test that configuration is properly loaded and applied"""
    # Create a config file in the test directory
    config_file = tmp_path / ".sigye" / "config.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_content = f"""
locale: ko_KR
data_filename: {str(tmp_path / "test.yaml")}
auto_tag_rules:
  - pattern: "^test-"
    match_type: "regex"
    tags: ["testing"]
"""
    config_file.write_text(config_content)

    # Create settings with the test directory as home
    settings = Settings.load_from_file(config_file)

    assert settings.locale == "ko_KR"  # Verify locale override

    # Create service and test auto-tagging
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(settings.data_filename), settings=settings)

    entry = tts.start_tracking("test-project")
    assert "testing" in entry.tags


def test_edit_command(tmp_path):
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(settings=settings, editor=DummyEditorService("nothing"))

    d1 = tts.start_tracking("test-project")
    assert d1.end_time is None
    d1 = tts.edit_entry(d1.id)
    d1 = tts.get_entry(d1.id)
    assert d1.comment == "edited by dummy editor"


def test_export(tmp_path):
    filename = tmp_path / "test.yaml"
    export_filename = tmp_path / "export.toml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    # Create entries with different projects and tags
    d1 = tts.start_tracking("test-project", tags={"tag1", "tag2"})
    tts.stop_tracking()
    d2 = tts.start_tracking("test-project-2", tags={"tag2", "tag3"})
    tts.stop_tracking()
    d3 = tts.start_tracking("test-project-3", tags={"tag1", "tag3"})
    tts.stop_tracking()
    assert all(entry is not None for entry in [d1, d2, d3])

    # Export entries
    entry_count = tts.export_entries(export_filename)
    assert entry_count == 3

    # Verify exported file
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(export_filename), settings=settings)
    entries = tts.list_entries()
    assert len(entries) == 3
    assert all(e.project in {"test-project", "test-project-2", "test-project-3"} for e in entries)

    # Verify exported file using sqlite.db
    export_filename = tmp_path / "export.db"
    entry_count = tts.export_entries(export_filename)
    assert entry_count == 3


def test_default_list_with_active_entry_from_previous_date(tmp_path):
    """Test that default list shows today's entries plus active entry from previous date"""
    from ..models import TimeEntry

    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    now = datetime.now().astimezone()
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)

    # Create a completed entry from two days ago
    two_days_entry = TimeEntry(
        project="two-days-project", start_time=two_days_ago, end_time=two_days_ago + timedelta(hours=2)
    )
    tts.repository.save(two_days_entry)

    # Create an active entry from yesterday (still running - no end_time)
    yesterday_active = TimeEntry(project="yesterday-project", start_time=yesterday)
    tts.repository.save(yesterday_active)

    # Create completed entries for today
    today_entry1 = TimeEntry(project="today-project-1", start_time=now, end_time=now + timedelta(hours=1))
    tts.repository.save(today_entry1)

    today_entry2 = TimeEntry(
        project="today-project-2", start_time=now + timedelta(hours=2), end_time=now + timedelta(hours=3)
    )
    tts.repository.save(today_entry2)

    # Test default list (time_period="")
    # Should show: yesterday's active entry + today's entries (not the two-days-ago entry)
    default_filter = EntryListFilter(time_period="")
    entries = tts.list_entries(filter=default_filter)
    assert len(entries) == 3
    entry_ids = {e.id for e in entries}
    assert yesterday_active.id in entry_ids
    assert today_entry1.id in entry_ids
    assert today_entry2.id in entry_ids
    assert two_days_entry.id not in entry_ids

    # Test "all" time period - should show everything
    all_filter = EntryListFilter(time_period="all")
    all_entries = tts.list_entries(filter=all_filter)
    assert len(all_entries) == 4


def test_default_list_without_active_entry_from_previous_date(tmp_path):
    """Test that default list shows only today's entries when there's no active entry from previous date"""
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    now = datetime.now().astimezone()
    yesterday = now - timedelta(days=1)

    # Create a completed entry from yesterday
    yesterday_entry = tts.start_tracking("yesterday-project", start_time=yesterday)
    tts.stop_tracking(stop_time=yesterday + timedelta(hours=2))

    # Create today's entries
    today_entry1 = tts.start_tracking("today-project-1")
    tts.stop_tracking()
    today_entry2 = tts.start_tracking("today-project-2")
    tts.stop_tracking()

    # Test default list (time_period="")
    # Should show only today's entries (yesterday's is completed, not active)
    default_filter = EntryListFilter(time_period="")
    entries = tts.list_entries(filter=default_filter)
    assert len(entries) == 2
    entry_ids = {e.id for e in entries}
    assert today_entry1.id in entry_ids
    assert today_entry2.id in entry_ids
    assert yesterday_entry.id not in entry_ids

    # Test "all" time period - should show everything
    all_filter = EntryListFilter(time_period="all")
    all_entries = tts.list_entries(filter=all_filter)
    assert len(all_entries) == 3


def test_default_list_with_active_entry_from_today(tmp_path):
    """Test that default list shows today's entries when active entry is from today"""
    filename = tmp_path / "test.yaml"
    settings = create_test_settings(tmp_path)
    tts = TimeTrackingService(repository=TimeEntryRepositoryFile(filename), settings=settings)

    now = datetime.now().astimezone()
    yesterday = now - timedelta(days=1)

    # Create a completed entry from yesterday
    yesterday_entry = tts.start_tracking("yesterday-project", start_time=yesterday)
    tts.stop_tracking(stop_time=yesterday + timedelta(hours=2))

    # Create today's entries, including one that's still active
    today_entry1 = tts.start_tracking("today-project-1")
    tts.stop_tracking()
    today_active = tts.start_tracking("today-project-active")  # Still active

    # Test default list (time_period="")
    # Should show only today's entries (active entry is from today, not a previous date)
    default_filter = EntryListFilter(time_period="")
    entries = tts.list_entries(filter=default_filter)
    assert len(entries) == 2
    entry_ids = {e.id for e in entries}
    assert today_entry1.id in entry_ids
    assert today_active.id in entry_ids
    assert yesterday_entry.id not in entry_ids
