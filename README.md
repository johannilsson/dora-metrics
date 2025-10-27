# DORA Metrics Calculator

This script calculates key DORA (DevOps Research and Assessment) metrics: Deployment Frequency, Change Failure Rate, and Mean Time to Recover. It processes release data from a CSV file provided via standard input.

## Usage

The script expects CSV data piped to its standard input. The CSV must contain the following columns: `app name`, `version`, and `publication date`.

## Development

### Setup

To set up the development environment, install the project in editable mode with its development dependencies:

```bash
uv pip install -e ".[dev]"
```

### Linting and Formatting

This project uses `ruff` for linting and formatting.

To check for linting issues, run:

```bash
uv run ruff check .
```

To automatically fix issues and format the code, run:

```bash
uv run ruff check . --fix
uv run ruff format .
```

### Testing

To run the unit tests, use `pytest`:

```bash
uv run pytest
```

### Example CSV Input (`data.csv`):

```csv
app name,version,publication date
AppA,v1.0.0,2024-01-01
AppA,v1.0.1,2024-01-05
AppA,v1.1.0,2024-01-15
AppB,v2.0.0,2024-02-01
AppB,v2.0.1,2024-02-02
```

### Running the Script

#### Using `uvx`
You can run the script using `uvx`, which will execute the command in a temporary virtual environment. Remember to use `--from` to ensure `uvx` can find the `dora` package.

```bash
cat data.csv | uvx --from <path to package> dora
```

#### 1. Calculate DORA Metrics (Default Mode)

To calculate and display DORA metrics:

```bash
cat data.csv | dora
```

#### 2. Generate Markdown List of Releases

To output a simple markdown-formatted list of all releases per application:

```bash
cat data.csv | dora --markdown-list
```

### Output

```
######################################
### Metrics for App: AppA
######################################
Total Releases: 3

-> Release Frequency:
   Average time between releases: 7.00 days
   Releases included in calculation:
   - v1.0.0 on 2024-01-01
   - v1.0.1 on 2024-01-05
   - v1.1.0 on 2024-01-15

-> Change Failure Rate:
   33.33% (1 change required a hotfix out of 3 total releases)
   Changes that failed (and their subsequent fix):
   - Change v1.0.0 (2024-01-01) failed, fixed by v1.0.1 (2024-01-05)

-> Mean Time to Recover (MTTR):
   Average: 4 days
   Recovery periods included in calculation:
   - From v1.0.0 (2024-01-01) to v1.0.1 (2024-01-05): 4 days

######################################
### Metrics for App: AppB
######################################
Total Releases: 2

-> Release Frequency:
   Average time between releases: 1.00 days
   Releases included in calculation:
   - v2.0.0 on 2024-02-01
   - v2.0.1 on 2024-02-02

-> Change Failure Rate:
   50.00% (1 change required a hotfix out of 2 total releases)
   Changes that failed (and their subsequent fix):
   - Change v2.0.0 (2024-02-01) failed, fixed by v2.0.1 (2024-02-02)

-> Mean Time to Recover (MTTR):
   Average: 1 day
   Recovery periods included in calculation:
   - From v2.0.0 (2024-02-01) to v2.0.1 (2024-02-02): 1 day
```
