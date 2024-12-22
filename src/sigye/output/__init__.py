import sys

from .csv_output import CsvOutput
from .json_output import JsonOutput
from .markdown_output import MarkdownOutput
from .output import OutputFormatter, OutputType
from .output_utils import validate_output_format
from .rich_text_output import RichTextOutput
from .text_output import RawTextOutput
from .yaml_output import YamlOutput

__all__ = [
    CsvOutput,
    JsonOutput,
    OutputFormatter,
    OutputType,
    RawTextOutput,
    RichTextOutput,
    YamlOutput,
    validate_output_format,
    "create_output_formatter",
]


def create_output_formatter(output_format: OutputType | None, force: bool = False) -> OutputFormatter:
    """Function to create an output formatter based on the output format."""
    if not force:
        if sys.stdout.isatty() and output_format is None or output_format in (OutputType.EMPTY, OutputType.RICH):
            output_format = OutputType.RICH
        elif not sys.stdout.isatty() and output_format is None or output_format in (OutputType.EMPTY, OutputType.JSON):
            output_format = OutputType.JSON
        else:
            output_format = OutputType.TEXT
    match output_format:
        case OutputType.TEXT:
            return RawTextOutput()
        case OutputType.JSON:
            return JsonOutput()
        case OutputType.RICH:
            return RichTextOutput()
        case OutputType.YAML:
            return YamlOutput()
        case OutputType.MARKDOWN:
            return MarkdownOutput()
        case OutputType.CSV:
            return CsvOutput()
    raise ValueError(f"Unsupported output format: {output_format}")
