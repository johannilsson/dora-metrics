# AGENT Guidelines for DORA Metrics Calculator Project

This document provides guidelines for AI agents working with the `dora` project.

## Project Overview

The `dora` project is a Python script designed to calculate key DORA (DevOps Research and Assessment) metrics: Deployment Frequency, Change Failure Rate, and Mean Time to Recover. It processes release data provided in a CSV format via standard input.

## Key Features

*   **DORA Metrics Calculation:** Computes Deployment Frequency, Change Failure Rate, and Mean Time to Recover.
*   **CSV Input:** Expects CSV data with `app name`, `version`, and `publication date` columns.
*   **Flexible Date Parsing:** Supports various date formats for the `publication date` field.
*   **Output Modes:**
    *   Default: Detailed DORA metrics report.
    *   Markdown List: Simple markdown-formatted list of releases.

## How to Run

The script expects CSV data piped to its standard input.

### Default Mode (DORA Metrics)

```bash
cat data.csv | dora
```

### Markdown List Mode

```bash
cat data.csv | dora --markdown-list
```

## Development Environment

*   **Python Version:** 3.11
*   **Dependency Management:** `uv` is used for managing dependencies.

### Setup

To set up the development environment, install the project in editable mode with its development dependencies:

```bash
uv pip install -e ".[dev]"
```

### Linting and Formatting

The project uses `ruff` for linting and formatting.

*   **Check for linting issues:**
    ```bash
    uv run ruff check .
    ```
*   **Automatically fix issues and format code:**
    ```bash
    uv run ruff check . --fix
    uv run ruff format .
    ```

### Testing

Unit tests are written using `pytest`.

*   **Run tests:**
    ```bash
    uv run pytest
    ```

## Code Structure

*   `src/dora/__main__.py`: Contains the core logic for parsing, calculating metrics, and printing results.
    *   `parse_version(version_str)`: Extracts semantic version from a string.
    *   `parse_publication_date(date_str)`: Parses various date formats.
    *   `format_timedelta_human(total_seconds)`: Converts seconds to a human-readable duration.
    *   `calculate_dora_metrics(releases)`: Calculates the DORA metrics.
    *   `print_dora_metrics(apps_data)`: Prints the detailed DORA metrics report.
    *   `print_markdown_list(apps_data)`: Prints a markdown list of releases.
    *   `main()`: Entry point for the script, handles input and output modes.
*   `tests/test_main.py`: Contains unit and integration tests for the `dora` script.

## Definition of Failure (for DORA Metrics)

A "failed change" is defined as a release (e.g., `v1.2` or `v1.2.0`) that is immediately followed by a patch release for it (e.g., `v1.2.1`). The Mean Time to Recover (MTTR) is the duration between these two releases.

## General Guidelines for Agents

*   **Adhere to existing conventions:** Maintain the current code style, formatting, and architectural patterns.
*   **Test thoroughly:** When making changes, ensure existing tests pass and add new tests for new features or bug fixes.
*   **Use `uv` for commands:** Prefer `uv run` for executing project-specific commands (e.g., `uv run pytest`, `uv run ruff`).
*   **Provide clear explanations:** When proposing changes or explaining code, be concise and clear.
