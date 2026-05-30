import cappa

from .output import OutputType


def validate_output_format(value: str | None) -> OutputType | None:
    """Parser for the output format option."""
    if value is None or value == "":
        return None
    try:
        return OutputType(value.lower())
    except ValueError as e:
        raise cappa.Exit(f"Invalid output format: {value}", code=2) from e
