from datetime import datetime
import pytest
from freezegun import freeze_time
from ..datetime_utils import parse_time


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
