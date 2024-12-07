from dataclasses import dataclass
from pathlib import Path

import click
from click_aliases import ClickAliasedGroup
from click_datetime import Datetime

from .config.settings import DEFAULT_CONFIG_PATH, Settings
from .models import EntryListFilter
from .output import OutputFormatter, OutputType, create_output_formatter, validate_output_format
from .services import EditorServiceError, TimeTrackingService
from .utils.datetime_utils import validate_time
from .utils.translation import set_locale


def load_settings(config_file: Path | None = None) -> Settings:
    """Load settings from config file, falling back to defaults if needed"""
    settings = Settings.load_from_file(config_file) if config_file else Settings.load_from_file()
    set_locale(settings.locale)
    return settings


@dataclass
class ContextObject:
    tts: TimeTrackingService
    output: OutputFormatter


pass_context_object = click.make_pass_decorator(ContextObject, ensure=True)


@click.group(cls=ClickAliasedGroup)
@click.version_option()
@click.option(
    "--config-file",
    "-c",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_PATH,
    help="Path to config file",
    show_default=True,
)
@click.option(
    "--filename",
    "-f",
    type=click.Path(path_type=Path),
    help="Path to data file",
)
@click.option(
    "--output_format",
    "-o",
    type=click.Choice(OutputType.choices(), case_sensitive=False),
    help="Output format",
    callback=validate_output_format,
)
@click.pass_context
def cli(ctx, config_file, filename, output_format: OutputType | None):
    settings = load_settings(config_file)
    settings.data_filename = filename or settings.data_filename
    settings.output_format = output_format or settings.output_format
    ctx.obj = ContextObject(
        TimeTrackingService(settings),
        create_output_formatter(settings.output_format, force=(bool(output_format))),
    )


@cli.command("start")
@click.argument("project", required=True, type=str)
@click.argument("comment", required=False, type=str, default="")
@click.option("--tag", required=False, type=str, multiple=True)
@click.option(
    "--start_time",
    "-s",
    required=False,
    type=str,
    help="Start time expressed as HH:MM or HH:MM:SS in 24-hour format or AM/PM",
    default=None,
    callback=validate_time,
)
@pass_context_object
def start(context: ContextObject, project, comment, tag, start_time):
    """start tracking work on a project"""
    time_entry = context.tts.start_tracking(project, comment=comment, tags=set(tag), start_time=start_time)
    context.output.single_entry_output(time_entry)


@cli.command("stop")
@click.argument("comment", required=False, type=str, default="")
@click.option(
    "--stop_time",
    "-s",
    callback=validate_time,
    required=False,
    type=str,
    default=None,
    help="Stop/End time expressed as HH:MM or HH:MM:SS in 24-hour format or AM/PM",
)
@pass_context_object
def stop(context: ContextObject, comment, stop_time):
    """stop tracking work on a project"""
    if comment:
        time_entry = context.tts.get_active_entry()
        time_entry.comment = comment
        time_entry = context.tts.update_entry(time_entry)
    time_entry = context.tts.stop_tracking(stop_time=stop_time)
    context.output.single_entry_output(time_entry)


@cli.command("status")
@pass_context_object
def status(context: ContextObject):
    """displays currently tracked (if active)"""
    time_entry = context.tts.get_active_entry()
    context.output.single_entry_output(time_entry)


@cli.command("edit")
@click.argument("id", required=True, type=str)
@pass_context_object
def edit_entry(context: ContextObject, id):
    """edit a time entry using the system editor"""
    try:
        entry = context.tts.get_entry_by_partial_id(id)
    except KeyError as e:
        raise click.ClickException(f"No entry found with id {id}") from e
    except IndexError as e:
        raise click.ClickException(f"Multiple records found starting with id {id}") from e
    try:
        context.output.single_entry_output(context.tts.edit_entry(entry.id))
    except EditorServiceError as e:
        raise click.ClickException(f"Error editing entry: {str(e)}") from e


@cli.command("delete", aliases=["del", "rm"])
@click.argument("id", required=True, type=str)
@pass_context_object
def delete_entry(context: ContextObject, id):
    """delete a time entry"""
    try:
        entry = context.tts.get_entry_by_partial_id(id)  # Get the entry to delete
    except KeyError as e:
        raise click.ClickException(f"No entry found with id {id}") from e
    except IndexError as e:
        raise click.ClickException(f"Multiple records found starting with id {id}") from e
    entry = context.tts.delete_entry(entry.id)
    context.output.single_entry_output(entry)


@cli.command("list", aliases=["ls"])
@click.argument(
    "time_period",
    required=False,
    type=click.Choice(["today", "yesterday", "week", "month", "all", ""]),
    default="",
)
@click.option(
    "--start_date",
    type=Datetime(format="%Y-%m-%d"),
    help="Start date in format YYYY-MM-DD",
)
@click.option("--end_date", type=Datetime(format="%Y-%m-%d"), help="End date in format YYYY-MM-DD")
@click.option("--tag", multiple=True)
@click.option("--project", multiple=True)
@click.option("--format")
@pass_context_object
def list_entries(context: ContextObject, time_period, start_date, end_date, tag, project, format):
    """display list of time entries for a time period"""
    filter = EntryListFilter(
        time_period=time_period,
        start_date=start_date,
        end_date=end_date,
        tags=set(tag),
        projects=set(project),
        output_format=format,
    )
    time_list = context.tts.list_entries(filter=filter)
    context.output.multiple_entries_output(time_list)
