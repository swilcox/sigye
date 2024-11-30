from datetime import datetime
import humanize.i18n
from pathlib import Path

import click
import humanize

from .config.settings import Settings, DEFAULT_CONFIG_PATH
from .models import EntryListFilter
from .output.text_output import list_output, single_entry_output
from .services import TimeTrackingService, EditorServiceError
from .utils.translation import init_translations
from .utils.datetime_utils import parse_time


def load_settings(config_file: Path | None = None) -> Settings:
    """Load settings from config file, falling back to defaults if needed"""
    if config_file:
        settings = Settings.load_from_file(config_file)
    else:
        settings = Settings.load_from_file()
    if settings.locale not in ["en", "en_US", "en_GB"]:
        _ = humanize.i18n.activate(settings.locale)
        _ = init_translations(lang=settings.locale)
    return settings


pass_tts = click.make_pass_decorator(TimeTrackingService, ensure=True)


@click.group()
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
@click.pass_context
def cli(ctx, config_file, filename):
    settings = load_settings(config_file)
    settings.data_filename = filename or settings.data_filename
    ctx.obj = TimeTrackingService(settings)


@cli.command()
@click.argument("project", required=True, type=str)
@click.argument("comment", required=False, type=str, default="")
@click.option("--tag", required=False, type=str, multiple=True)
@click.option(
    "--start_time",
    "-s",
    required=False,
    type=str,
    help="Start time expressed as HH:MM or HH:MM:SS in 24-hour format or AM/PM",
)
@pass_tts
def start(tts, project, comment, tag, start_time):
    """start tracking work on a project"""
    if start_time:
        try:
            start_time_dt = parse_time(start_time)
        except ValueError as ex:
            raise click.ClickException(f"Invalid start time format: {ex}")
    else:
        start_time_dt = None
    time_entry = tts.start_tracking(
        project, comment=comment, tags=set(tag), start_time=start_time_dt
    )
    single_entry_output(time_entry)


@cli.command()
@click.argument("comment", required=False, type=str, default="")
@click.option("--stop_time", "-s", required=False, type=str)
@pass_tts
def stop(tts: TimeTrackingService, comment, stop_time):
    """stop tracking work on a project"""
    if stop_time:
        try:
            stop_time_dt = parse_time(stop_time)
        except ValueError as ex:
            raise click.ClickException(f"Invalid start time format: {ex}")
    else:
        stop_time_dt = None
    if comment:
        time_entry = tts.get_active_entry()
        time_entry.comment = comment
        time_entry = tts.update_entry(time_entry)
    time_entry = tts.stop_tracking(stop_time=stop_time_dt)
    single_entry_output(time_entry)


@cli.command()
@pass_tts
def status(tts):
    """displays currently tracked (if active)"""
    time_entry = tts.get_active_entry()
    single_entry_output(time_entry)


@cli.command("edit")
@click.argument("id", required=True, type=str)
@pass_tts
def edit_entry(tts, id):
    """edit a time entry using the system editor"""
    try:
        entry = tts.get_entry_by_partial_id(id)
    except KeyError:
        raise click.ClickException(f"No entry found with id {id}")
    except IndexError:
        raise click.ClickException(f"Multiple records found starting with id {id}")
    try:
        single_entry_output(tts.edit_entry(entry.id))
    except EditorServiceError as e:
        raise click.ClickException(f"Error editing entry: {str(e)}")


@cli.command("delete")
@click.argument("id", required=True, type=str)
@pass_tts
def delete_entry(tts, id):
    """delete a time entry"""
    try:
        entry = tts.get_entry_by_partial_id(id)  # Get the entry to delete
    except KeyError:
        raise click.ClickException(f"No entry found with id {id}")
    except IndexError:
        raise click.ClickException(f"Multiple records found starting with id {id}")
    entry = tts.delete_entry(entry.id)
    single_entry_output(entry)


@cli.command("list")
@click.argument(
    "time_period",
    required=False,
    type=click.Choice(["today", "week", "month", ""]),
    default="",
)
@click.option("--start_date")
@click.option("--end_date")
@click.option("--tag", multiple=True)
@click.option("--project", multiple=True)
@click.option("--format")
@pass_tts
def list_entries(tts, time_period, start_date, end_date, tag, project, format):
    """display list of time entries for a time period"""
    filter_params = {}
    if time_period:
        filter_params["time_period"] = time_period
    if start_date:
        filter_params["start_date"] = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        filter_params["end_date"] = datetime.strptime(end_date, "%Y-%m-%d").date()
    if tag:
        filter_params["tags"] = set(tag)
    if project:
        filter_params["projects"] = set(project)
    if format:
        filter_params["output_format"] = format

    filter = EntryListFilter(**filter_params)
    time_list = tts.list_entries(filter=filter)
    list_output(time_list)
