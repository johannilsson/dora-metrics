import unittest
from datetime import datetime
from unittest.mock import patch, mock_open
from io import StringIO
import sys

from dora.__main__ import (
    parse_version,
    parse_publication_date,
    format_timedelta_human,
    print_dora_metrics,
    print_markdown_list,
    main,
)

class TestDoraFunctions(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("1.2"), (1, 2, 0))
        self.assertEqual(parse_version("1"), None)
        self.assertEqual(parse_version("a.b.c"), None)
        self.assertEqual(parse_version("1.2.3-alpha"), (1, 2, 3))

    def test_parse_publication_date(self):
        self.assertEqual(
            parse_publication_date("June 1, 2024"), datetime(2024, 6, 1)
        )
        self.assertEqual(
            parse_publication_date("2024-06-01"), datetime(2024, 6, 1)
        )
        self.assertEqual(
            parse_publication_date("20240601"), datetime(2024, 6, 1)
        )
        self.assertEqual(parse_publication_date("Invalid date"), None)

    def test_format_timedelta_human(self):
        self.assertEqual(format_timedelta_human(86400), "1 day")
        self.assertEqual(format_timedelta_human(90000), "1 day, 1 hour")
        self.assertEqual(format_timedelta_human(3660), "1 hour, 1 minute")
        self.assertEqual(format_timedelta_human(60), "1 minute")
        self.assertEqual(format_timedelta_human(30), "Less than a minute")
        self.assertEqual(format_timedelta_human(0), "Less than a minute")
        self.assertEqual(format_timedelta_human(-100), "N/A")
        self.assertEqual(
            format_timedelta_human(176400), "2 days, 1 hour"
        )

class TestDoraMain(unittest.TestCase):
    def setUp(self):
        self.csv_data = (
            "app name,version,publication date\n"
            "AppA,v1.0.0,2024-01-01\n"
            "AppA,v1.0.1,2024-01-05\n"
            "AppA,v1.1.0,2024-01-15\n"
            "AppB,v2.0.0,2024-02-01\n"
            "AppB,v2.0.1,2024-02-02\n"
        )

    @patch("sys.stdin", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_dora_metrics(self, mock_stdout, mock_stdin):
        mock_stdin.write(self.csv_data)
        mock_stdin.seek(0)
        
        with patch('sys.stdin', mock_stdin):
            main()

        output = mock_stdout.getvalue()
        self.assertIn("### Metrics for App: AppA", output)
        self.assertIn("### Metrics for App: AppB", output)
        self.assertIn("-> Change Failure Rate:", output)
        self.assertIn("-> Mean Time to Recover (MTTR):", output)

    @patch("sys.stdin", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_print_markdown_list(self, mock_stdout, mock_stdin):
        mock_stdin.write(self.csv_data)
        mock_stdin.seek(0)
        
        with patch('sys.stdin', mock_stdin):
            with patch('sys.argv', ['', '--markdown-list']):
                main()

        output = mock_stdout.getvalue()
        self.assertIn("### AppA", output)
        self.assertIn("- v1.0.0 on 2024-01-01", output)
        self.assertIn("### AppB", output)
        self.assertIn("- v2.0.0 on 2024-02-01", output)

    @patch("sys.stderr", new_callable=StringIO)
    def test_main_no_stdin(self, mock_stderr):
        with patch('sys.stdin.isatty', return_value=True):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
        
        output = mock_stderr.getvalue()
        self.assertIn("Error: No data piped to stdin.", output)

class TestDoraMetricsCalculation(unittest.TestCase):
    def run_main_with_data(self, csv_data):
        with patch('sys.stdin', StringIO(csv_data)), \
             patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            main()
            return mock_stdout.getvalue()

    def test_release_frequency(self):
        csv_data = (
            "app name,version,publication date\n"
            "AppA,v1.0.0,2024-01-01\n"
            "AppA,v1.1.0,2024-01-11\n"
        )
        output = self.run_main_with_data(csv_data)
        self.assertIn("Average time between releases: 10.00 days", output)

    def test_change_failure_rate(self):
        csv_data = (
            "app name,version,publication date\n"
            "AppA,v1.0.0,2024-01-01\n"
            "AppA,v1.0.1,2024-01-02\n" # Failure 1
            "AppA,v1.1.0,2024-01-10\n"
            "AppA,v1.2.0,2024-01-20\n"
            "AppA,v1.2.1,2024-01-21\n" # Failure 2
        )
        output = self.run_main_with_data(csv_data)
        # 2 failures out of 5 releases = 40%
        self.assertIn("40.00% (2 changes required a hotfix out of 5 total releases)", output)

    def test_mean_time_to_recover(self):
        csv_data = (
            "app name,version,publication date\n"
            "AppA,v1.0.0,2024-01-01\n"
            "AppA,v1.0.1,2024-01-03\n" # 2 days to recover
            "AppA,v1.1.0,2024-01-10\n"
            "AppA,v1.2.0,2024-01-20\n"
            "AppA,v1.2.1,2024-01-24\n" # 4 days to recover
        )
        output = self.run_main_with_data(csv_data)
        # Average of 2 and 4 days is 3 days
        self.assertIn("Average: 3 days", output)

if __name__ == "__main__":
    unittest.main()
