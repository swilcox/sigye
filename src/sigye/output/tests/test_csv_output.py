from ...models import TimeEntry
from .. import CsvOutput


def test_csv_output_single_entry():
    entry = TimeEntry(
        id="1234567890",
        start_time="2021-01-01T00:00:00",
        end_time="2021-01-01T01:00:00",
        project="test",
        comment="test",
        tags=["test"],
    )
    output = CsvOutput()
    output.single_entry_output(entry)


def test_csv_output_multiple_entries():
    entries = [
        TimeEntry(
            id="1234567890",
            start_time="2021-01-01T00:00:00",
            end_time="2021-01-01T01:00:00",
            project="test",
            comment="test",
            tags=["test"],
        ),
        TimeEntry(
            id="1234567890",
            start_time="2021-01-01T00:00:00",
            end_time="2021-01-01T01:00:00",
            project="test",
            comment="test",
            tags=["test"],
        ),
    ]
    output = CsvOutput()
    output.multiple_entries_output(entries)


def test_csv_output_export():
    output = CsvOutput()
    output.export_output(2, "test.csv")


def test_csv_output_no_entry():
    output = CsvOutput()
    output.single_entry_output(None)
