# sigye (시계)

A simple, command-line time tracking program.

## Overview

sigye (시계 Korean for clock) is a CLI program to help you track your time. With sigye, there are basic operations:
* start (start tracking time towards a project)
* stop (stop tracking time)
* status (get the current status)
* edit (edit a time entry record using the current default EDITOR)
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

To override this value for a environment, you can set the environment variable `SIGYE_DATA_FILENAME` to whatever value you'd like and that will become the default.

> [!IMPORTANT]  
> Make sure the directory exists before overriding.

### Start tracking
```shell
sigye start <project-name> "<optional comment>" --tag "optional_tag"
```

### Check status
```shell
sigye status
```

### Stop tracking
```shell
sigye stop
```

### List Entries
#### List All Entries
```shell
sigye list
```
#### List Filtered Entries

All entries from a named time frame (options: `today`, `week` and `month`):
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

### Edit Entries
To edit an entry, use the full or partial ID (just has to be enough digits for it to be unique among your time entry file or data). By default, sigye shows the first 4 digits from an entry ID.
```shell
sigye edit ID
```

### Localization Support (experimental Korean output)
To get *output* in Korean:
`export SIGYE_LOCALE=ko_KR`

The `sigye list` and `sigye status` commands will output some information in Korean.

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
  * YAML
  * TOML
* Language Localization (in-progress)
* SQLite storage
* TOML storage