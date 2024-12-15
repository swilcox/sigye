import io
import json

import pytest
import rtoml as toml
import ryaml

from ..time_entry_repo_file import FormatFactory, JSONFormat, TOMLFormat, YAMLFormat


def test_file_format_factory():
    factory = FormatFactory()
    assert isinstance(factory.get_format("yaml"), YAMLFormat)
    assert isinstance(factory.get_format("toml"), TOMLFormat)
    assert isinstance(factory.get_format("json"), JSONFormat)
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
