from datetime import datetime, timedelta
import functools

import click

from .models import EntryListFilter
from .output.text_output import list_output, single_entry_output
from .services import TimeTrackingService
from .repositories.time_entry_repo import TimeEntryRepository
from .repositories.time_entry_repo_yaml import TimeEntryRepositoryYaml


def _get_repo_from_filename(filename: str) -> TimeEntryRepository:
    # TODO: add logic here to swap to sqlite or something else based on the filename
    return TimeEntryRepositoryYaml(filename)


def config_params(func):
    @click.option("--filename", "-f", default="time_entries.yaml")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    print("hello from main CLI")


@cli.command()
@click.argument("project", required=True, type=str)
@click.option("--tag", multiple=True)
@click.argument("comment", required=False, type=str)
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
@click.argument("time_period", required=False, default="")
@click.option("--start_date")
@click.option("--end_date")
@click.option("--tag", multiple=True)
@click.option("--project", multiple=True)
@click.option("--format")
@config_params
def list(time_period, start_date, end_date, tag, project, format, filename):
    """display list of time entries for a time period"""
    tts = TimeTrackingService(_get_repo_from_filename(filename))
    filter = EntryListFilter()
    if time_period:
        now = datetime.now()
        if time_period == "today":
            filter.start_date = now.date()
        elif time_period == "week":
            filter.start_date = now.date() - timedelta(
                days=now.date().weekday()
            )  # Monday
        elif time_period == "month":
            filter.start_date = now.date() - timedelta(
                days=(now.date().day - 1)
            )  # 1st of current month
        time_list = tts.list_entries(filter=filter)
    else:
        time_list = tts.list_entries()
    list_output(time_list)
