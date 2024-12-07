from typing import Any

import click

from .output import OutputType


def validate_output_format(ctx: click.Context, param: Any, value: str | None) -> OutputType | None:
    """Validation callback for the output format option."""
    if value is not None:
        try:
            return OutputType(value.lower())
        except ValueError as e:
            raise click.BadParameter(f"Invalid output format: {value}") from e
    return None
