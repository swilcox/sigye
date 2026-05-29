from datetime import datetime

import pytest
from freezegun import freeze_time

from ..datetime_utils import adjust_stop_time, format_delta, parse_time


@freeze_time("2021-01-01")
def test_parse_time():
    # Test 24-hour format
    assert parse_time("12:00") == datetime(2021, 1, 1, 12, 0).astimezone()
    assert parse_time("23:59") == datetime(2021, 1, 1, 23, 59).astimezone()
    assert parse_time("00:00") == datetime(2021, 1, 1, 0, 0).astimezone()
    assert parse_time("01:02:03") == datetime(2021, 1, 1, 1, 2, 3).astimezone()

    # Test 12-hour format
    assert parse_time("12:00 PM") == datetime(2021, 1, 1, 12, 0).astimezone()
    assert parse_time("11:59 PM") == datetime(2021, 1, 1, 23, 59).astimezone()
    assert parse_time("12:00 AM") == datetime(2021, 1, 1, 0, 0).astimezone()
    assert parse_time("01:02:03 AM") == datetime(2021, 1, 1, 1, 2, 3).astimezone()
    assert parse_time("01:02:03 PM") == datetime(2021, 1, 1, 13, 2, 3).astimezone()

    # Test 12-hour format without leading zero
    assert parse_time("1:02:03 AM") == datetime(2021, 1, 1, 1, 2, 3).astimezone()
    assert parse_time("1:02:03 PM") == datetime(2021, 1, 1, 13, 2, 3).astimezone()

    # Test 12-hour format with meridiem in lowercase
    assert parse_time("12:00 pm") == datetime(2021, 1, 1, 12, 0).astimezone()
    assert parse_time("11:59 pm") == datetime(2021, 1, 1, 23, 59).astimezone()
    assert parse_time("12:00 am") == datetime(2021, 1, 1, 0, 0).astimezone()

    # Test invalid formats
    with pytest.raises(ValueError):
        parse_time("24:00")
    with pytest.raises(ValueError):
        parse_time("12:60")
    with pytest.raises(ValueError):
        parse_time("12:00:60")
    with pytest.raises(ValueError):
        parse_time("13:00 AM")
    with pytest.raises(ValueError):
        parse_time("13:00 PM")
    with pytest.raises(ValueError):
        parse_time("13:00:00 AM")
    with pytest.raises(ValueError):
        parse_time("13:00:00 PM")


def test_adjust_stop_time_prior_day():
    # Active entry started yesterday morning; a bare "17:00" parsed as today
    # should be pulled back to the entry's start date.
    start = datetime(2021, 1, 1, 9, 0).astimezone()
    today_stop = datetime(2021, 1, 2, 17, 0).astimezone()
    assert adjust_stop_time(start, today_stop) == datetime(2021, 1, 1, 17, 0).astimezone()


def test_adjust_stop_time_multiple_days_prior():
    # The start date is used even when the entry is several days stale.
    start = datetime(2021, 1, 1, 9, 0).astimezone()
    today_stop = datetime(2021, 1, 4, 17, 0).astimezone()
    assert adjust_stop_time(start, today_stop) == datetime(2021, 1, 1, 17, 0).astimezone()


def test_adjust_stop_time_same_day_unchanged():
    # When the entry started today, the stop time is left untouched.
    start = datetime(2021, 1, 2, 9, 0).astimezone()
    stop = datetime(2021, 1, 2, 17, 0).astimezone()
    assert adjust_stop_time(start, stop) == stop


def test_adjust_stop_time_before_start_falls_back():
    # If the stop time-of-day is before the start time-of-day, pulling it back to
    # the start date would be invalid, so the original (today) value is kept.
    start = datetime(2021, 1, 1, 18, 0).astimezone()
    today_stop = datetime(2021, 1, 2, 17, 0).astimezone()
    assert adjust_stop_time(start, today_stop) == today_stop


def test_format_timedelta():
    assert format_delta(datetime(2021, 1, 1, 12, 0) - datetime(2021, 1, 1, 11, 0)) == "1 hour"
    assert format_delta(datetime(2021, 1, 1, 12, 0) - datetime(2021, 1, 1, 11, 30)) == "0.5 hours"
    assert format_delta(datetime(2021, 1, 1, 12, 0) - datetime(2021, 1, 1, 11, 45)) == "0.2 hours"
