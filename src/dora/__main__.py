#
# DORA Metrics Calculator
#
# Purpose:
# This script calculates key DORA metrics (Deployment Frequency, Change Failure Rate,
# and Mean Time to Recover) from a CSV file of release notes.
#
# It can also generate a simple markdown list of all releases per app using a
# command-line flag.
#
# --- MODES ---
#
# 1. Default Mode (DORA Metrics):
#    Calculates and prints a detailed report with DORA metrics.
#    Usage: cat your_data.csv | python this_script.py
#
# 2. Markdown List Mode:
#    Outputs a simple, markdown-formatted list of every version and its date.
#    Usage: cat your_data.csv | python this_script.py --markdown-list
#
# -----------------------------------------------------------------------------
#
# Definition of Failure (for DORA Metrics):
# A "failed change" is a release (e.g., v1.2 or v1.2.0) that is immediately
# followed by a patch release for it (e.g., v1.2.1). The time to recover (MTTR)
# is the duration between these two releases.
#
# Supported Date Formats in 'Publication date' field:
# - Month Day, Year (e.g., "June 1, 2024")
# - YYYY-MM-DD (e.g., "2024-06-01")
# - YYYYMMDD (e.g., "20240601")
#
import csv
import re
import sys
from datetime import datetime


def parse_version(version_str):
    """
    Extracts a semantic version (Major.Minor.Patch) from a string.
    Assumes versions like 'X.Y' are 'X.Y.0'.
    Returns a tuple of (major, minor, patch) integers or None if not found.
    """
    match = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', str(version_str))
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3)) if match.group(3) else 0
        return (major, minor, patch)
    return None

def parse_publication_date(date_str):
    """
    Finds and parses the first recognizable date from a string.
    Tries common formats like 'Month Day, Year', 'YYYY-MM-DD', and 'YYYYMMDD'.
    Returns a datetime object or None if parsing fails.
    """
    s_date_str = str(date_str)

    date_pattern_text = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4})'
    match = re.search(date_pattern_text, s_date_str, re.IGNORECASE)
    if match:
        date_part = match.group(1)
        for fmt in ('%B %d, %Y', '%b %d, %Y'):
            try:
                return datetime.strptime(date_part, fmt)
            except ValueError:
                continue

    date_pattern_iso = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern_iso, s_date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except ValueError:
            pass

    date_pattern_compact = r'\b(\d{8})\b'
    match = re.search(date_pattern_compact, s_date_str)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%d')
        except ValueError:
            pass

    return None

def format_timedelta_human(total_seconds):
    """
    Converts a duration in seconds to a human-readable string (e.g., "X days, Y hours").
    """
    if total_seconds < 0:
        return "N/A"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{int(days)} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")

    if not parts:
        return "Less than a minute"

    return ", ".join(parts)

def print_dora_metrics(apps_data):
    """
    Calculates and prints the detailed DORA metrics report for each app.
    """
    for app_name, releases in sorted(apps_data.items()):
        if not releases:
            continue

        # Data is pre-sorted, but we confirm it here.
        releases.sort(key=lambda r: r['date'])
        num_releases = len(releases)

        print("\n" + "#" * 38)
        print(f"### Metrics for App: {app_name}")
        print("#" * 38)
        print(f"Total Releases: {num_releases}\n")

        # --- Identify Failure and Recovery Events ---
        failure_events = []
        for i in range(num_releases - 1):
            current_release = releases[i]
            next_release = releases[i+1]
            v_curr = current_release['version']
            v_next = next_release['version']
            if v_next[0] == v_curr[0] and v_next[1] == v_curr[1] and v_next[2] > v_curr[2]:
                failure_events.append({
                    'failed_change': current_release,
                    'fix': next_release
                })

        # 1. Release Frequency
        print("-> Release Frequency:")
        if num_releases < 2:
            print("   Not enough data to calculate frequency.")
        else:
            total_duration = releases[-1]['date'] - releases[0]['date']
            avg_days_between_releases = total_duration.days / (num_releases - 1)
            print(f"   Average time between releases: {avg_days_between_releases:.2f} days")
            print("   Releases included in calculation:")
            for r in releases:
                version_str = '.'.join(map(str, r['version']))
                date_str = r['date'].strftime('%Y-%m-%d')
                print(f"   - v{version_str} on {date_str}")

        # 2. Change Failure Rate
        print("\n-> Change Failure Rate:")
        num_failed_changes = len(failure_events)
        if num_releases > 0:
            failure_rate = (num_failed_changes / num_releases) * 100
            details = (
                f"({num_failed_changes} change{'s' if num_failed_changes != 1 else ''} required a hotfix "
                f"out of {num_releases} total releases)"
            )
            print(f"   {failure_rate:.2f}% {details}")
            if failure_events:
                print("   Changes that failed (and their subsequent fix):")
                for event in failure_events:
                    fail_v = '.'.join(map(str, event['failed_change']['version']))
                    fail_d = event['failed_change']['date'].strftime('%Y-%m-%d')
                    fix_v = '.'.join(map(str, event['fix']['version']))
                    fix_d = event['fix']['date'].strftime('%Y-%m-%d')
                    print(f"   - Change v{fail_v} ({fail_d}) failed, fixed by v{fix_v} ({fix_d})")
        else:
            print("   No releases found.")

        # 3. Mean Time to Recover (MTTR)
        print("\n-> Mean Time to Recover (MTTR):")
        if not failure_events:
            print("   Not applicable (no failed changes recorded)")
        else:
            recovery_times_seconds = [
                (event['fix']['date'] - event['failed_change']['date']).total_seconds()
                for event in failure_events
            ]
            avg_recovery_seconds = sum(recovery_times_seconds) / len(recovery_times_seconds)
            print(f"   Average: {format_timedelta_human(avg_recovery_seconds)}")
            print("   Recovery periods included in calculation:")
            for event in failure_events:
                fail_v = '.'.join(map(str, event['failed_change']['version']))
                fail_d = event['failed_change']['date'].strftime('%Y-%m-%d')
                fix_v = '.'.join(map(str, event['fix']['version']))
                fix_d = event['fix']['date'].strftime('%Y-%m-%d')
                duration = event['fix']['date'] - event['failed_change']['date']
                duration_str = format_timedelta_human(duration.total_seconds())
                print(f"   - From v{fail_v} ({fail_d}) to v{fix_v} ({fix_d}): {duration_str}")

def print_markdown_list(apps_data):
    """
    Prints a simple markdown-formatted list of releases for each app.
    """
    for app_name, releases in sorted(apps_data.items()):
        if not releases:
            continue

        releases.sort(key=lambda r: r['date'])

        print(f"### {app_name}\n")
        for r in releases:
            version_str = '.'.join(map(str, r['version']))
            date_str = r['date'].strftime('%Y-%m-%d')
            print(f"- v{version_str} on {date_str}")
        print() # Add a newline for spacing

def main():
    """
    Main function to read CSV, process data, and print metrics based on mode.
    """
    if sys.stdin.isatty():
        sys.stderr.write("Error: No data piped to stdin. Please provide CSV data.\n")
        sys.stderr.write("Usage: cat your_data.csv | python this_script.py [--markdown-list]\n")
        sys.exit(1)

    markdown_mode = '--markdown-list' in sys.argv

    try:
        reader = csv.DictReader(sys.stdin)
        reader.fieldnames = [h.lower() for h in reader.fieldnames]

        apps_data = {}

        for row in reader:
            app_name = row.get('app name')
            version_str = row.get('version')
            date_str = row.get('publication date')

            if not all([app_name, version_str, date_str]):
                continue

            version = parse_version(version_str)
            pub_date = parse_publication_date(date_str)

            if not version or not pub_date:
                sys.stderr.write(
                    f"Warning: Skipping row with unparsable data. App: {app_name}, "
                    f"Version: '{version_str}', Date: '{date_str}'\n"
                )
                continue

            if app_name not in apps_data:
                apps_data[app_name] = []

            apps_data[app_name].append({
                'version': version,
                'date': pub_date,
            })

    except (OSError, csv.Error) as e:
        sys.stderr.write(f"Error reading or parsing CSV from stdin: {e}\n")
        sys.exit(1)

    # Execute the correct output mode
    if markdown_mode:
        print_markdown_list(apps_data)
    else:
        print_dora_metrics(apps_data)


if __name__ == "__main__":
    main()
