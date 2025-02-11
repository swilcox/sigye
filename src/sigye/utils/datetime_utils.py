import re
from datetime import datetime, time, timedelta

import click
import humanize


def parse_time(time_str: str) -> datetime:
    """Parse user-entered time string into datetime object for current date."""
    time_str = time_str.strip().upper()

    pattern = r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*((?:am|pm)?)"
    match = re.match(pattern, time_str, re.IGNORECASE)

    if not match:
        raise ValueError("Invalid time format. Use HH:MM or HH:MM:SS with optional AM/PM")

    hours, minutes, seconds, meridiem = match.groups()
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds) if seconds else 0

    if hours > 12 and meridiem:
        raise ValueError("Hours cannot exceed 12 in 12-hour format")

    meridiem = meridiem.upper() if meridiem else ""

    if meridiem == "PM" and hours < 12:
        hours += 12
    elif meridiem == "AM" and hours == 12:
        hours = 0

    if hours > 23:
        raise ValueError("Hours cannot exceed 23")
    if minutes > 59:
        raise ValueError("Minutes cannot exceed 59")
    if seconds > 59:
        raise ValueError("Seconds cannot exceed 59")

    today = datetime.now().date()
    return datetime.combine(today, time(hours, minutes, seconds)).astimezone()


def validate_time(ctx: click.Context, param: click.Parameter, value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return parse_time(value)
    except ValueError as ex:
        raise click.BadParameter(str(ex)) from ex


def format_delta(td: timedelta) -> str:
    return humanize.precisedelta(
        td,
        suppress=(
            "years",
            "months",
            "days",
        ),
        minimum_unit="hours",
        format="%0.1f",
    )
