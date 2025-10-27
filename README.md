# DORA Metrics Calculator

This script calculates key DORA (DevOps Research and Assessment) metrics: Deployment Frequency, Change Failure Rate, and Mean Time to Recover. It processes release data from a CSV file provided via standard input.

## Usage

The script expects CSV data piped to its standard input. The CSV must contain the following columns: `app name`, `version`, and `publication date`.

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
