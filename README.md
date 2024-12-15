# sigye (시계)

A simple, command-line time tracking program.

## Overview

sigye (시계 Korean for clock) is a CLI program to help you track your time. With sigye, there are basic operations:
* start (start tracking time towards a project)
* stop (stop tracking time)
* status (get the current status)
* edit (edit a time entry record using the current default `EDITOR` value or `nano` if you don't have `EDITOR` set in your shell)
* list (list entries)
  * can filter entries by time range ("today", "week", "month") or fixed start and end dates.
  * can filter entries by project name(s) or a project starts with.
  * can filter entries by tags name(s).

The default storage of time entries is a YAML file (near future will be sqlite support). Using YAML makes manual editing of the entire file possible using any editor.

## Installation

### Via `uv`
```shell
uv tool install sigye
```

### Via `pipx`
```shell
pipx install sigye
```

## Usage

### Default Storage of Entries
By default, entries are stored in a YAML file at: `$HOME/.sigye/time_entries.yml`

To override this value, you can add `--filename <date_filename>` on every command to override adhoc.

To override this value for an environment, you can set the environment variable `SIGYE_DATA_FILENAME` to whatever value you'd like and that will become the default.

Or better yet, set the `data_filename` in the config.yaml file.

> [!IMPORTANT]  
> Make sure the directory exists before overriding.

### Start tracking
```shell
sigye start <project-name> "<optional comment>" --tag "optional_tag" --start_time "HH:MM"
```

The start command begins tracking time for a project. You can:
- Add an optional comment in quotes to describe what you're working on
- Add one or more tags using the --tag option
- Specify a custom start time using --start_time (or -s) in 24-hour format (HH:MM or HH:MM:SS) or AM/PM format
- Only one time entry can be tracked at a time
- Starting a new entry automatically stops the currently running one

### Stop tracking
```shell
sigye stop ["optional comment"] --stop_time "HH:MM"
```

The stop command ends time tracking for the current entry. You can:
- Add an optional comment in quotes to describe what was completed
- Specify a custom stop time using --stop_time (or -s) in 24-hour format (HH:MM or HH:MM:SS) or AM/PM format
- Use stop without a comment to simply end tracking
- If no stop time is specified, the current time is used

### Check status
```shell
sigye status
```

### List Entries
#### List All Entries
```shell
sigye list
```
#### List Filtered Entries

All entries from a named time frame (options: `today`, `yesterday`, `week` and `month`):
```shell
sigye list TIMEFRAME
```

All entries for a certain project (or list of projects)
```shell
sigye list --project abc-1234 --project abc-1233
```

Entries that "start with" a project name (note: you can use `+` or `.` or `*`):
```
sigye list --project abc+
```

All entries with any tag matching a tag or multiple tags:
```
sigye list --tag mytag
```

#### List Entries in a Different format

The output format can be set/overridden with the `--output_format` or `-o` option.

Valid options are:
* `rich` -- colorized text with ascii/unicode characters for nicer display. This is the default output if the `sigye` command is not being redirected somewhere besides `stdout`.
* `text` -- an extremely plain output mostly used for testing.
* `json` -- output in JSON format. This is the default if no option is provided and `stdout` is redirected.
* `yaml` -- output in YAML format, suitable for exporting entries to a new file.

Example:

```
sigye -o yaml list --project abc.
```

The above would list all entries that have a project that starts with "abc" in yaml format.

### Edit Entries
To edit an entry, use the full or partial ID (just has to be enough digits for it to be unique among your time entry file or data). By default, sigye shows the first 4 digits from an entry ID.
```shell
sigye edit ID
```

## Configuration

sigye can be configured using a YAML configuration file located at `~/.sigye/config.yaml`. Here's an example configuration file with available options:

```yaml
# Override the default locale (en_US)
# locale: ko_KR
# data_filename: /full/path/to/a/file.yaml
# Auto-tagging rules
# Each rule consists of:
#   - pattern: regular expression pattern to match against project name
#   - match_type: how to match the pattern (regex)
#   - tags: list of tags to apply when pattern matches
auto_tag_rules:
  - pattern: "^abc"  # Matches projects starting with "abc"
    match_type: "regex"
    tags: ["learning"]
  
  - pattern: "^PROJ-\\d+"  # Matches PROJ- followed by numbers
    match_type: "regex"
    tags: ["work", "billable"]
  
  - pattern: ".*-urgent$"  # Projects ending with "-urgent"
    match_type: "regex"
    tags: ["urgent", "high-priority"]
  
  - pattern: "(feature|bugfix)/"  # Projects containing feature/ or bugfix/
    match_type: "regex"
    tags: ["development"]
```

The auto-tagging rules automatically apply tags to your time entries based on the project name. This helps maintain consistent tagging across similar projects without having to manually specify tags each time.

### Localization Support (experimental Korean output)
To get *output* in Korean:
`export SIGYE_LOCALE=ko_KR`

The `sigye list` and `sigye status` commands will now output some information in Korean.

> [!NOTE]
> This work is ongoing and subject to change.

## Development

### Install requirements

This project uses `uv` for dependency management.

### Running tests

```shell
uv run pytest
```

## Future Changes

* Configuration file support
  * YAML (mostly complete now)
  * TOML
* Language Localization (in-progress)
* SQLite storage
* TOML storage
