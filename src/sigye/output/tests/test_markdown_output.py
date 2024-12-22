from ...models import TimeEntry
from ..markdown_output import MarkdownOutput


def test_markdown_entry():
    entry = TimeEntry(
        id="1234567890",
        start_time="2021-01-01T00:00:00",
        end_time="2021-01-01T01:00:00",
        project="test",
        comment="test",
        tags=["test"],
    )
    output = MarkdownOutput()
    output.single_entry_output(entry)

    # TODO: Check the output


def test_markdown_multiple_entries():
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
    output = MarkdownOutput()
    output.multiple_entries_output(entries)
    # TODO: Check the output


def test_markdown_export():
    output = MarkdownOutput()
    output.export_output(2, "test.md")
    # TODO: Check the output


def test_markdown_no_entry():
    output = MarkdownOutput()
    output.single_entry_output(None)
    # TODO: Check the output
