import click
import pytest

from ..output_utils import validate_output_format


def test_validate_output_format():
    assert validate_output_format(None, None, "json") == "json"
    with pytest.raises(click.BadParameter):
        validate_output_format(None, None, "invalid")
    assert validate_output_format(None, None, None) is None
    assert validate_output_format(None, None, "YAML") == "yaml"
    with pytest.raises(click.BadParameter):
        validate_output_format(None, None, "INVALID")
