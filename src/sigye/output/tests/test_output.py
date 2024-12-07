from ..json_output import JsonOutput
from ..output import OutputFormatter
from ..rich_text_output import RichTextOutput
from ..text_output import RawTextOutput


def test_output():
    """Test the output module"""
    output = OutputFormatter()
    assert output

    output = OutputFormatter.create("rich", force=True)
    assert isinstance(output, RichTextOutput)

    output = OutputFormatter.create("text", force=True)
    assert isinstance(output, RawTextOutput)

    output = OutputFormatter.create("json", force=True)
    assert isinstance(output, JsonOutput)
