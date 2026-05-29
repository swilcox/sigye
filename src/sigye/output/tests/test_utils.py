import cappa
import pytest

from ..output import OutputType
from ..output_utils import validate_output_format


def test_validate_output_format():
    assert validate_output_format("json") == OutputType.JSON
    with pytest.raises(cappa.Exit):
        validate_output_format("invalid")
    assert validate_output_format(None) is None
    assert validate_output_format("YAML") == OutputType.YAML
    with pytest.raises(cappa.Exit):
        validate_output_format("INVALID")
