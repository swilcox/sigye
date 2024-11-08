from datetime import datetime, timedelta

import pytest

from ..models import TimeEntry


def test_time_entry():
    now = datetime.now().astimezone()

    t1 = TimeEntry(
        start_time=now + timedelta(hours=-4), project="test-project", comment="hello"
    )
    t2 = TimeEntry(
        start_time=now + timedelta(hours=-2, minutes=-30),
        end_time=now,
        project="test-project-2",
        comment="test2",
        tags=["testtag2"],
    )

    assert t1.humanized_duration == "4 hours"
    assert t2.humanized_duration == "2.5 hours"  # our current precisiondelta config


def test_time_entry_stop():
    now = datetime.now().astimezone()

    t1 = TimeEntry(
        start_time=now + timedelta(hours=-4), project="test-project", comment="hello"
    )
    t1.stop()
    assert t1.humanized_duration == "4 hours"
    assert t1.end_time is not None
    # verify we can't re-stop an already stopped entry
    with pytest.raises(ValueError):
        t1.stop()


def test_get_naive_time():
    now = datetime.now().astimezone()
    naive_time = TimeEntry._get_naive_time(now)
    assert naive_time.tzinfo is None
    assert naive_time.hour == now.hour


def test_duration():
    now = datetime.now().astimezone()
    t2 = TimeEntry(
        start_time=now + timedelta(hours=-2),
        end_time=now,
        project="test-project-2",
        comment="test2",
        tags=["testtag2"],
    )
    assert t2.duration == t2.end_time - t2.start_time
