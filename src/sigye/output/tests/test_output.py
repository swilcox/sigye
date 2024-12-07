from .. import create_output_formatter
from ..json_output import JsonOutput
from ..output import OutputFormatter
from ..rich_text_output import RichTextOutput
from ..text_output import RawTextOutput


def test_output():
    """Test the output module"""
    output = OutputFormatter()
    assert output

    output = create_output_formatter("rich", force=True)
    assert isinstance(output, RichTextOutput)

    output = create_output_formatter("text", force=True)
    assert isinstance(output, RawTextOutput)

    output = create_output_formatter("json", force=True)
    assert isinstance(output, JsonOutput)
