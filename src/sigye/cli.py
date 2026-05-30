from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import cappa

from .config.settings import DEFAULT_CONFIG_PATH, Settings
from .editors import EditorError
from .models import EntryListFilter
from .output import OutputFormatter, OutputType, create_output_formatter
from .output.output_utils import validate_output_format
from .services import TimeTrackingService
from .utils.datetime_utils import validate_time
from .utils.translation import set_locale


def load_settings(config_file: Path | None = None) -> Settings:
    """Load settings from config file, falling back to defaults if needed"""
    settings = Settings.load_from_file(config_file) if config_file else Settings.load_from_file()
    set_locale(settings.locale)
    return settings


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass
class ContextObject:
    tts: TimeTrackingService
    output: OutputFormatter


def build_context(sigye: "Sigye") -> ContextObject:
    settings = load_settings(sigye.config_file)
    settings.data_filename = sigye.filename or settings.data_filename
    settings.output_format = sigye.output_format or settings.output_format
    return ContextObject(
        TimeTrackingService(settings),
        create_output_formatter(settings.output_format, force=bool(sigye.output_format)),
    )


Context = Annotated[ContextObject, cappa.Dep(build_context)]


@cappa.command(name="start", help="start tracking work on a project")
@dataclass
class Start:
    project: str
    comment: str = ""
    tag: Annotated[list[str], cappa.Arg(long=True)] = field(default_factory=list)
    start_time: Annotated[
        datetime | None,
        cappa.Arg(
            short="-s",
            long="--start_time",
            parse=validate_time,
            parse_inference=False,
            help="Start time expressed as HH:MM or HH:MM:SS in 24-hour format or AM/PM",
        ),
    ] = None

    def __call__(self, context: Context) -> None:
        time_entry = context.tts.start_tracking(
            self.project, comment=self.comment, tags=set(self.tag), start_time=self.start_time
        )
        context.output.single_entry_output(time_entry)


@cappa.command(name="stop", help="stop tracking work on a project")
@dataclass
class Stop:
    comment: str = ""
    stop_time: Annotated[
        datetime | None,
        cappa.Arg(
            short="-s",
            long="--stop_time",
            parse=validate_time,
            parse_inference=False,
            help="Stop/End time expressed as HH:MM or HH:MM:SS in 24-hour format or AM/PM",
        ),
    ] = None

    def __call__(self, context: Context) -> None:
        try:
            if self.comment:
                time_entry = context.tts.get_active_entry()
                time_entry.comment = self.comment
                time_entry = context.tts.update_entry(time_entry)
            time_entry = context.tts.stop_tracking(stop_time=self.stop_time)
        except ValueError as e:
            raise cappa.Exit(str(e), code=1) from e
        context.output.single_entry_output(time_entry)


@cappa.command(name="status", help="displays currently tracked (if active)")
@dataclass
class Status:
    def __call__(self, context: Context) -> None:
        time_entry = context.tts.get_active_entry()
        context.output.single_entry_output(time_entry)


@cappa.command(name="edit", help="edit a time entry using the system editor")
@dataclass
class Edit:
    id: str

    def __call__(self, context: Context) -> None:
        try:
            entry = context.tts.get_entry_by_partial_id(self.id)
        except KeyError as e:
            raise cappa.Exit(f"No entry found with id {self.id}", code=1) from e
        except IndexError as e:
            raise cappa.Exit(f"Multiple records found starting with id {self.id}", code=1) from e
        try:
            context.output.single_entry_output(context.tts.edit_entry(entry.id))
        except EditorError as e:
            raise cappa.Exit(f"Error editing entry: {str(e)}", code=1) from e


@cappa.command(name="delete", aliases=["del", "rm"], help="delete a time entry")
@dataclass
class Delete:
    id: str

    def __call__(self, context: Context) -> None:
        try:
            entry = context.tts.get_entry_by_partial_id(self.id)
        except KeyError as e:
            raise cappa.Exit(f"No entry found with id {self.id}", code=1) from e
        except IndexError as e:
            raise cappa.Exit(f"Multiple records found starting with id {self.id}", code=1) from e
        entry = context.tts.delete_entry(entry.id)
        context.output.single_entry_output(entry)


@cappa.command(name="list", aliases=["ls"], help="display list of time entries for a time period")
@dataclass
class List:
    """display list of time entries for a time period

    Default behavior (no time_period): shows today's entries, plus any active entry from a previous date.
    Use 'all' to display all time entries.
    """

    time_period: Annotated[str, cappa.Arg(choices=["today", "yesterday", "week", "month", "all", ""])] = ""
    start_date: Annotated[
        date | None,
        cappa.Arg(
            long="--start_date",
            parse=_parse_date,
            parse_inference=False,
            help="Start date in format YYYY-MM-DD",
        ),
    ] = None
    end_date: Annotated[
        date | None,
        cappa.Arg(
            long="--end_date",
            parse=_parse_date,
            parse_inference=False,
            help="End date in format YYYY-MM-DD",
        ),
    ] = None
    tag: Annotated[list[str], cappa.Arg(long=True)] = field(default_factory=list)
    project: Annotated[list[str], cappa.Arg(long=True)] = field(default_factory=list)

    def __call__(self, context: Context) -> None:
        filter = EntryListFilter(
            time_period=self.time_period,
            start_date=self.start_date,
            end_date=self.end_date,
            tags=set(self.tag),
            projects=set(self.project),
        )
        time_list = context.tts.list_entries(filter=filter)
        context.output.multiple_entries_output(time_list)


@cappa.command(name="export", help="export time entries to a file")
@dataclass
class Export:
    export_filename: Path

    def __call__(self, context: Context) -> None:
        records_exported = context.tts.export_entries(self.export_filename)
        context.output.export_output(records_exported, self.export_filename)


@cappa.command(name="sigye")
@dataclass
class Sigye:
    """A simple command-line program for tracking time."""

    config_file: Annotated[
        Path,
        cappa.Arg(short="-c", long="--config-file", help="Path to config file"),
    ] = DEFAULT_CONFIG_PATH
    filename: Annotated[
        Path | None,
        cappa.Arg(short="-f", long="--filename", help="Path to data file"),
    ] = None
    output_format: Annotated[
        OutputType | None,
        cappa.Arg(
            short="-o",
            long="--output_format",
            parse=validate_output_format,
            parse_inference=False,
            help="Output format",
        ),
    ] = None
    cmd: cappa.Subcommands[Start | Stop | Status | Edit | Delete | List | Export] = None


def cli(argv: list[str] | None = None) -> None:
    cappa.invoke(Sigye, argv=argv)
