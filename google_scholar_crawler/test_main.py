"""Regression tests for Scholar parsing and preservation of cached counts."""
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

import main as crawler

PROFILE = """
<div id="gsc_prf_in">Hao Yu</div>
<table id="gsc_rsb_st">
<tr><th>All</th><th>Recent</th></tr>
<tr><td>Citations</td><td class="gsc_rsb_std">5,594</td><td>5578</td></tr>
<tr><td>h-index</td><td class="gsc_rsb_std">13</td><td>13</td></tr>
<tr><td>i10-index</td><td class="gsc_rsb_std">14</td><td>14</td></tr>
</table>
<table>
<tr class="gsc_a_tr"><td><a class="gsc_a_at" href="/citations?citation_for_view=DnYC9yoAAAAJ:one">Paper One</a></td><td><a class="gsc_a_ac">2,575*</a></td></tr>
<tr class="gsc_a_tr"><td><a class="gsc_a_at" href="/citations?citation_for_view=DnYC9yoAAAAJ:two">Paper Two</a></td><td><a class="gsc_a_ac"></a></td></tr>
</table>
<button id="gsc_bpf_more" disabled>Show more</button>
"""


class ScholarTests(unittest.TestCase):
    def test_realistic_counts_including_merged_and_uncited_papers(self):
        result = crawler.parse_page(PROFILE, "DnYC9yoAAAAJ")
        self.assertEqual(result["citedby"], 5594)
        self.assertEqual(result["publications"]["DnYC9yoAAAAJ:one"]["num_citations"], 2575)
        self.assertEqual(result["publications"]["DnYC9yoAAAAJ:two"]["num_citations"], 0)
        self.assertFalse(result["has_more"])

    def test_blocked_html_is_not_interpreted_as_zero(self):
        with self.assertRaises(ValueError):
            crawler.parse_page("<html>Sorry, verify you are human.</html>", "DnYC9yoAAAAJ")

    def test_other_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            crawler.parse_page(PROFILE.replace("DnYC9yoAAAAJ:one", "someoneelse:one"), "DnYC9yoAAAAJ")

    def test_pagination_follows_more_and_detects_repeated_pages(self):
        first = PROFILE.replace(' disabled', '')
        responses = [
            subprocess.CompletedProcess([], 0, first.encode() + b"\n200"),
            subprocess.CompletedProcess([], 0, PROFILE.replace(":one", ":three").replace(":two", ":four").encode() + b"\n200"),
        ]
        with patch.object(crawler.subprocess, "run", side_effect=responses) as request:
            result = crawler.fetch_stats("DnYC9yoAAAAJ")
        self.assertEqual(len(result["publications"]), 4)
        self.assertIn("cstart=100", request.call_args.args[0][-1])
        repeated = subprocess.CompletedProcess([], 0, first.encode() + b"\n200")
        with patch.object(crawler.subprocess, "run", return_value=repeated):
            with self.assertRaisesRegex(ValueError, "repeated"):
                crawler.fetch_stats("DnYC9yoAAAAJ")

    def test_failed_fetch_preserves_existing_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "scholar.json"
            snapshot.write_text('{"citedby":5594}')
            output = Path(directory) / "results"
            with patch("sys.argv", ["main.py", "--snapshot", str(snapshot), "--output", str(output)]):
                with patch.object(crawler, "fetch_stats", side_effect=ValueError("Blocked")):
                    with self.assertRaises(ValueError):
                        crawler.main()
            self.assertEqual(snapshot.read_text(), '{"citedby":5594}')
            self.assertFalse(output.exists())

    def test_blocked_refresh_preserves_all_cached_files_and_reports_skipped(self):
        for status in (403, 429):
            for second_page in (False, True):
                with self.subTest(status=status, second_page=second_page), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    output = root / "results"
                    output.mkdir()
                    snapshot = root / "scholar.json"
                    cached = [snapshot, output / "gs_data.json", output / "gs_data_shieldsio.json"]
                    for path in cached:
                        path.write_text('{"citedby":5594,"updated":"2026-09-27T12:14:57Z"}')
                    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in cached}
                    responses = []
                    if second_page:
                        responses.append(subprocess.CompletedProcess([], 0, PROFILE.replace(' disabled', '').encode() + b"\n200"))
                    responses.append(subprocess.CompletedProcess([], 22, f"\n{status}".encode(), f"curl: (22) HTTP {status}".encode()))
                    env = {"GITHUB_ACTIONS": "true", "GITHUB_OUTPUT": str(root / "outputs"), "GITHUB_STEP_SUMMARY": str(root / "summary")}
                    argv = ["main.py", "--skip-blocked", "--snapshot", str(snapshot), "--output", str(output)]
                    warnings = io.StringIO()
                    with patch("sys.argv", argv), patch.dict(os.environ, env), redirect_stdout(warnings):
                        with patch.object(crawler.subprocess, "run", side_effect=responses):
                            crawler.main()
                    for path in cached:
                        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before[path])
                    self.assertEqual((root / "outputs").read_text(), "updated=false\n")
                    self.assertIn(f"HTTP {status}", (root / "summary").read_text())
                    self.assertIn("::warning::Citation refresh skipped", warnings.getvalue())

    def test_skip_blocked_does_not_hide_unexpected_errors(self):
        responses = [
            (subprocess.CompletedProcess([], 22, b"\n404", b"Not found"), crawler.ScholarHTTPError, "HTTP 404"),
            (subprocess.CompletedProcess([], 22, b"\n500", b"Server error"), crawler.ScholarHTTPError, "HTTP 500"),
            (subprocess.CompletedProcess([], 28, b"\n000", b"Operation timed out"), RuntimeError, "curl exit 28.*timed out"),
            (subprocess.CompletedProcess([], 0, b"<html>verify you are human</html>\n200"), ValueError, "public profile"),
        ]
        for response, error, message in responses:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "results"
                with patch("sys.argv", ["main.py", "--skip-blocked", "--output", str(output)]):
                    with patch.object(crawler.subprocess, "run", return_value=response):
                        with self.assertRaisesRegex(error, message):
                            crawler.main()
                self.assertFalse(output.exists())

    def test_blocked_response_fails_without_explicit_skip_option(self):
        response = subprocess.CompletedProcess([], 22, b"\n403", b"curl: (22) The requested URL returned error: 403")
        with patch("sys.argv", ["main.py"]), patch.object(crawler.subprocess, "run", return_value=response):
            with self.assertRaisesRegex(crawler.ScholarHTTPError, "HTTP 403.*curl:.*403"):
                crawler.main()

    def test_successful_refresh_writes_counts_and_enables_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "results"
            snapshot = root / "scholar.json"
            env = {"GITHUB_OUTPUT": str(root / "outputs"), "GITHUB_STEP_SUMMARY": str(root / "summary")}
            response = subprocess.CompletedProcess([], 0, PROFILE.encode() + b"\n200")
            argv = ["main.py", "--skip-blocked", "--snapshot", str(snapshot), "--output", str(output)]
            with patch("sys.argv", argv), patch.dict(os.environ, env), redirect_stdout(io.StringIO()):
                with patch.object(crawler.subprocess, "run", return_value=response):
                    crawler.main()
            stats = json.loads((output / "gs_data.json").read_text())
            self.assertEqual(stats["citedby"], 5594)
            self.assertEqual(stats["scholar_id"], "DnYC9yoAAAAJ")
            self.assertEqual(json.loads(snapshot.read_text()), stats)
            self.assertEqual(json.loads((output / "gs_data_shieldsio.json").read_text())["message"], "5594")
            self.assertEqual((root / "outputs").read_text(), "updated=true\n")
            self.assertIn("Updated Hao Yu: 5594 citations", (root / "summary").read_text())


if __name__ == "__main__":
    unittest.main()
