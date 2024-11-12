from datetime import datetime
import functools
import tempfile
import os
import subprocess
import humanize.i18n
import yaml

import click
import humanize

from .config.settings import Settings
from .models import EntryListFilter, TimeEntry
from .output.text_output import list_output, single_entry_output
from .services import TimeTrackingService
from .repositories.time_entry_repo import TimeEntryRepository
from .repositories.time_entry_repo_yaml import TimeEntryRepositoryYaml
from .utils.translation import init_translations


DEFAULT_SETTINGS = Settings()
if DEFAULT_SETTINGS.locale not in ["en", "en_US", "en_GB"]:
    _ = humanize.i18n.activate(DEFAULT_SETTINGS.locale)
    _ = init_translations(lang=DEFAULT_SETTINGS.locale)


def _get_repo_from_filename(filename: str) -> TimeEntryRepository:
    # TODO: add logic here to swap to sqlite or something else based on the filename
    return TimeEntryRepositoryYaml(filename)


def config_params(func):
    @click.option(
        "--filename", "-f", default=DEFAULT_SETTINGS.data_filename, show_default=True
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def _get_editor_command():
    return os.environ.get("EDITOR", "vim")


def _format_entry_for_edit(entry: TimeEntry) -> str:
    """Format a time entry as YAML for editing"""
    # Convert to dict and format as YAML
    entry_dict = entry.model_dump(mode="json")
    return yaml.dump(entry_dict)


def _parse_edited_entry(content: str) -> TimeEntry:
    """Parse edited YAML content back into a TimeEntry"""
    try:
        data = yaml.safe_load(content)
        return TimeEntry(**data)
    except Exception as e:
        raise click.ClickException(f"Invalid entry format: {str(e)}")


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx): ...


@cli.command()
@click.argument("project", required=True, type=str)
@click.option("--tag", multiple=True)
@click.argument("comment", required=False, type=str, default="")
@config_params
def start(project, tag, comment, filename):
    """start tracking work on a project"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))
    time_entry = tts.start_tracking(project, comment=comment, tags=tag)
    single_entry_output(time_entry)


@cli.command()
@config_params
def stop(filename):
    """stop tracking work on a project"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))
    time_entry = tts.stop_tracking()
    if time_entry:
        single_entry_output(time_entry)
    else:
        print("No active time entry to stop.")


@cli.command()
@config_params
def status(filename):
    """displays currently tracked (if active)"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))
    time_entry = tts.get_active_entry()
    if time_entry:
        single_entry_output(time_entry)
    else:
        print("No active time entry.")


@cli.command()
@click.argument("id", required=True, type=str)
@config_params
def edit(id, filename):
    """edit a time entry using the system editor"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))

    # Get the entry to edit
    try:
        if entries := tts.list_entries(EntryListFilter(id=id)):
            if len(entries) > 1:
                raise IndexError
            entry = entries[0]
        else:
            raise KeyError
    except KeyError:
        raise click.ClickException(f"No entry found with id {id}")
    except IndexError:
        raise click.ClickException(f"Multiple records found starting with id {id}")

    # Create temp file with entry content
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as tmp:
        tmp.write(_format_entry_for_edit(entry))
        tmp.flush()
        tmp_path = tmp.name

    try:
        # Open editor
        editor = _get_editor_command()
        subprocess.run([editor, tmp_path], check=True)

        # Read and parse edited content
        with open(tmp_path, "r") as f:
            edited_content = f.read()
            updated_entry = _parse_edited_entry(edited_content)

        # Save the updated entry
        tts.update_entry(updated_entry)
        single_entry_output(updated_entry)

    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@cli.command()
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
@config_params
def list(time_period, start_date, end_date, tag, project, format, filename):
    """display list of time entries for a time period"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))

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
