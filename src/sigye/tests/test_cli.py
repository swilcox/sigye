import io
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from unittest import mock

from ..cli import cli as cli_main
from ..cli import load_settings
from ..models import TimeEntry
from ..output.text_output import RawTextOutput


def mock_single_entry_output(entry: TimeEntry):
    print(f"{entry.id} {entry.start_time} {entry.end_time} {entry.project} {entry.comment}")


@dataclass
class CliResult:
    exit_code: int
    output: str


class CliRunner:
    """Minimal click-CliRunner-style helper around cappa.invoke."""

    @contextmanager
    def isolated_filesystem(self, temp_dir: Path):
        cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            yield
        finally:
            os.chdir(cwd)

    def invoke(self, argv: list[str]) -> CliResult:
        buf = io.StringIO()
        try:
            with redirect_stdout(buf), redirect_stderr(buf):
                cli_main(argv=list(argv))
            exit_code = 0
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 1
        return CliResult(exit_code, buf.getvalue())


def test_load_settings(tmp_path):
    """Test settings loading with default and custom config"""
    settings = load_settings()
    assert settings is not None

    config_file = tmp_path / "config.yaml"
    config_content = """
    locale: en_US
    data_filename: test.yaml
    """
    config_file.write_text(config_content)
    settings = load_settings(config_file)
    assert settings.locale == "en_US"
    assert settings.data_filename == Path("test.yaml")


def test_start_command(tmp_path):
    """Test the start command"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(["-f", "test.yaml", "start", "test-project"])
        assert result.exit_code == 0
        assert "test-project" in result.output

        result = runner.invoke(
            [
                "-f",
                "test.yaml",
                "start",
                "test-project",
                "test comment",
                "--tag",
                "tag1",
                "--tag",
                "tag2",
            ],
        )
        assert result.exit_code == 0
        assert "test-project" in result.output
        assert "test comment" in result.output
        assert "tag1" in result.output
        assert "tag2" in result.output

        result = runner.invoke(["-f", "test2.yaml", "start", "test-project", "--start_time", "09:00"])
        assert result.exit_code == 0
        assert "09:00" in result.output

        result = runner.invoke(["-f", "test3.yaml", "start", "test-project", "--start_time", "invalid"])
        assert result.exit_code != 0
        assert "Invalid time format" in result.output


def test_stop_command(tmp_path):
    """Test the stop command"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(["-f", "test.yaml", "start", "test-project"])

        result = runner.invoke(["-f", "test.yaml", "stop"])
        assert result.exit_code == 0
        assert "test-project" in result.output

        runner.invoke(["-f", "test2.yaml", "start", "test-project", "--start_time", "09:00"])
        result = runner.invoke(["-f", "test2.yaml", "stop", "--stop_time", "17:00"])
        assert result.exit_code == 0
        assert "17:00" in result.output

        runner.invoke(["-f", "test3.yaml", "start", "test-project", "--start_time", "09:00"])
        result = runner.invoke(["-f", "test3.yaml", "stop", "--stop_time", "invalid"])
        assert result.exit_code != 0
        assert "Invalid time format" in result.output


def test_status_command(tmp_path):
    """Test the status command"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(["-f", "test.yaml", "status"])
        assert result.exit_code == 0
        assert "No active time record" in result.output

        runner.invoke(["-f", "test.yaml", "start", "test-project", "test comment"])
        result = runner.invoke(["-f", "test.yaml", "status"])
        assert result.exit_code == 0
        assert "test-project" in result.output
        assert "test comment" in result.output


def test_list_command_and_aliases(tmp_path):
    """Test the list command and its aliases"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(["-f", "test.yaml", "start", "project1", "--tag", "tag1"])
        runner.invoke(["-f", "test.yaml", "stop"])
        runner.invoke(["-f", "test.yaml", "start", "project2", "--tag", "tag2"])
        runner.invoke(["-f", "test.yaml", "stop"])

        result = runner.invoke(["-f", "test.yaml", "list"])
        assert result.exit_code == 0
        assert "project1" in result.output
        assert "project2" in result.output

        result = runner.invoke(["-f", "test.yaml", "ls"])
        assert result.exit_code == 0
        assert "project1" in result.output
        assert "project2" in result.output

        result = runner.invoke(["-f", "test.yaml", "list", "today"])
        assert result.exit_code == 0
        assert "project1" in result.output
        assert "project2" in result.output

        result = runner.invoke(["-f", "test.yaml", "list", "--project", "project1"])
        assert result.exit_code == 0
        assert "project1" in result.output
        assert "project2" not in result.output

        result = runner.invoke(["-f", "test.yaml", "list", "--tag", "tag1"])
        assert result.exit_code == 0
        assert "project1" in result.output
        assert "project2" not in result.output


def test_edit_command(tmp_path):
    """Test the edit command"""
    runner = CliRunner()
    with (
        mock.patch("sigye.output.rich_text_output.RichTextOutput", side_effect=RawTextOutput),
        runner.isolated_filesystem(temp_dir=tmp_path),
    ):
        result = runner.invoke(["-f", "test.yaml", "start", "test-project"])
        runner.invoke(["-f", "test.yaml", "stop"])

        entry_id = result.output.split()[0]
        assert entry_id is not None

        result = runner.invoke(["-f", "test.yaml", "edit", "invalid-id"])
        assert result.exit_code != 0
        assert "No entry found" in result.output


def test_delete_command_and_aliases(tmp_path):
    """Test the delete command and its aliases"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(["-f", "test.yaml", "-o", "text", "start", "test-project"])
        runner.invoke(["-f", "test.yaml", "-o", "text", "stop"])
        entry_id = result.output.split()[0]

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "delete", entry_id])
        assert result.exit_code == 0
        assert "test-project" in result.output

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "start", "test-project"])
        runner.invoke(["-f", "test.yaml", "stop"])
        entry_id = result.output.split()[0]

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "rm", entry_id])
        assert result.exit_code == 0
        assert "test-project" in result.output

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "start", "test-project"])
        runner.invoke(["-f", "test.yaml", "stop"])
        entry_id = result.output.split()[0]

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "del", entry_id])
        assert result.exit_code == 0
        assert "test-project" in result.output

        result = runner.invoke(["-f", "test.yaml", "-o", "text", "delete", "invalid-id"])
        assert result.exit_code != 0
        assert "No entry found" in result.output


def test_config_file_option(tmp_path):
    """Test using custom config file"""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        config_file = tmp_path / "custom_config.yaml"
        config_content = """
        locale: en_US
        data_filename: custom_test.yaml
        """
        config_file.write_text(config_content)

        result = runner.invoke(["-c", str(config_file), "start", "test-project"])
        assert result.exit_code == 0
        assert "test-project" in result.output
