import io
import json

import pytest
import rtoml as toml
import ryaml

from ...models import TimeEntry
from ..time_entry_repo_file import FormatFactory, JSONFormat, TimeEntryRepositoryFile, TOMLFormat, YAMLFormat


def test_file_format_factory():
    factory = FormatFactory()
    assert isinstance(factory.get_format("yaml"), YAMLFormat)
    assert isinstance(factory.get_format("toml"), TOMLFormat)
    assert isinstance(factory.get_format("json"), JSONFormat)
    assert isinstance(factory.get_format("yml"), YAMLFormat)
    with pytest.raises(ValueError):
        factory.get_format("unknown")


def test_yaml_format():
    fmt = YAMLFormat()
    data = {"key": "value"}
    assert fmt.load_data(io.StringIO(ryaml.dumps(data))) == data
    with io.StringIO() as f:
        fmt.save_data(data, f)
        f.seek(0)
        assert ryaml.dumps(data) == f.read()


def test_toml_format():
    fmt = TOMLFormat()
    data = {"key": "value"}
    assert fmt.load_data(io.StringIO(toml.dumps(data))) == data
    with io.StringIO() as f:
        fmt.save_data(data, f)
        f.seek(0)
        assert toml.dumps(data) == f.read()


def test_json_format():
    fmt = JSONFormat()
    data = {"key": "value"}
    assert fmt.load_data(io.StringIO(json.dumps(data))) == data
    with io.StringIO() as f:
        fmt.save_data(data, f)
        f.seek(0)
        assert json.dumps(data) == f.read()


def test_supported_formats():
    assert FormatFactory.get_supported_formats() == ["yaml", "yml", "toml", "json"]


def test_time_entry_repo_file(tmp_path):
    for fmt in ["yaml", "toml", "json"]:
        filename = tmp_path / f"test.{fmt}"
        repo = TimeEntryRepositoryFile(filename)
        assert repo._format.suffix == f".{fmt}"

        assert repo.get_all() == []
        with pytest.raises(KeyError):
            repo.get_entry_by_id("1")

        entry = TimeEntry(
            project="test", start_time="2021-01-01T00:00:00", end_time="2021-01-01T01:00:00", comment="test comment"
        )
        repo.save(entry)

        assert repo.get_entry_by_id(entry.id) == entry

        entry2 = TimeEntry(project="test2", start_time="2021-01-02T00:00:00", comment="test comment 2")

        repo.save(entry2)
        assert repo.get_entry_by_id(entry2.id) == entry2

        repo.delete_entry(entry2.id)
        with pytest.raises(KeyError):
            repo.get_entry_by_id(entry2.id)

        with pytest.raises(KeyError):
            repo.delete_entry(entry2.id)

        assert repo.filter(filter=None) == [entry]

        assert repo.get_by_project("test") == [entry]
