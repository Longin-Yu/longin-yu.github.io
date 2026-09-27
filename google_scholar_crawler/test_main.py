"""Regression tests for Scholar parsing and preservation of cached counts."""
import subprocess
import tempfile
import unittest
from pathlib import Path
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
            subprocess.CompletedProcess([], 0, first.encode()),
            subprocess.CompletedProcess([], 0, PROFILE.replace(":one", ":three").replace(":two", ":four").encode()),
        ]
        with patch.object(crawler.subprocess, "run", side_effect=responses) as request:
            result = crawler.fetch_stats("DnYC9yoAAAAJ")
        self.assertEqual(len(result["publications"]), 4)
        self.assertIn("cstart=100", request.call_args.args[0][-1])
        repeated = subprocess.CompletedProcess([], 0, first.encode())
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


if __name__ == "__main__":
    unittest.main()
