"""Fetch public Google Scholar counts for the Acad Homepage stats branch.

No login, API key or paid proxy is needed. Unavailable or invalid responses never
overwrite the last successful snapshot. CI may explicitly skip HTTP 403/429.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


class ScholarHTTPError(RuntimeError):
    def __init__(self, status, detail=""):
        self.status = status
        super().__init__(f"Google Scholar returned HTTP {status}. {detail}".strip())


def fetch_page(url):
    # Keep the HTTP status separate from the body, including when --fail exits 22.
    # curl uses the machine's http_proxy / https_proxy configuration.
    response = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location",
         "--max-time", "30", "--write-out", "\n%{http_code}", url],
        check=False, capture_output=True, timeout=35,
    )
    body, _, status_text = response.stdout.rpartition(b"\n")
    status = int(status_text) if re.fullmatch(rb"\d{3}", status_text) else 0
    detail = (response.stderr or b"").decode("utf-8", errors="replace").strip()
    if response.returncode:
        if response.returncode == 22 and status >= 400:
            raise ScholarHTTPError(status, detail)
        raise RuntimeError(f"Scholar request failed (curl exit {response.returncode}): {detail}")
    if status != 200:
        raise ScholarHTTPError(status, detail)
    return body


def parse_count(text, *, empty_is_zero=False):
    value = text.strip().replace(",", "").rstrip("*").strip()
    if not value and empty_is_zero:
        return 0
    if not re.fullmatch(r"\d+", value):
        raise ValueError(f"Invalid Scholar citation count: {text!r}")
    return int(value)


def parse_page(html, scholar_id, *, first_page=True):
    soup = BeautifulSoup(html, "html.parser")
    result = {"publications": {}}
    if first_page:
        name = soup.select_one("#gsc_prf_in")
        rows = soup.select("#gsc_rsb_st tr")
        if name is None or len(rows) < 4:
            raise ValueError("Scholar did not return a public profile and citation table.")
        result["name"] = name.get_text(" ", strip=True)
        for key, row in zip(("citedby", "hindex", "i10index"), rows[1:4]):
            cell = row.select_one(".gsc_rsb_std")
            if cell is None:
                raise ValueError("Incomplete Scholar citation table.")
            result[key] = parse_count(cell.get_text(" ", strip=True))

    for row in soup.select(".gsc_a_tr"):
        title = row.select_one(".gsc_a_at")
        citations = row.select_one(".gsc_a_ac")
        if title is None or citations is None:
            raise ValueError("Incomplete Scholar publication row.")
        query = parse_qs(urlsplit(title.get("href", "")).query)
        paper_id = query.get("citation_for_view", [""])[0]
        if not paper_id.startswith(scholar_id + ":"):
            raise ValueError("Publication belongs to a different Scholar profile.")
        result["publications"][paper_id] = {
            "author_pub_id": paper_id,
            "bib": {"title": title.get_text(" ", strip=True)},
            "num_citations": parse_count(citations.get_text(" ", strip=True), empty_is_zero=True),
        }
    if not result["publications"]:
        raise ValueError("Scholar returned no publications; refusing an empty replacement.")
    more = soup.select_one("#gsc_bpf_more")
    result["has_more"] = more is not None and not more.has_attr("disabled")
    return result


def fetch_stats(scholar_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", scholar_id):
        raise ValueError("Invalid Scholar ID.")
    stats = {
        "scholar_id": scholar_id,
        "source": f"https://scholar.google.com/citations?user={scholar_id}&hl=en",
        "publications": {},
    }
    for start in range(0, 2000, 100):
        params = {"user": scholar_id, "hl": "en", "pagesize": 100}
        if start:
            params["cstart"] = start
        url = "https://scholar.google.com/citations?" + urlencode(params)
        page = parse_page(fetch_page(url), scholar_id, first_page=start == 0)
        if start == 0:
            for key in ("name", "citedby", "hindex", "i10index"):
                stats[key] = page[key]
        previous_size = len(stats["publications"])
        stats["publications"].update(page["publications"])
        if not page["has_more"]:
            break
        if len(stats["publications"]) == previous_size:
            raise ValueError("Scholar pagination repeated; refusing incomplete results.")
    else:
        raise ValueError("Scholar pagination limit reached.")
    stats["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return stats


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def report_result(updated, message):
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"updated={str(updated).lower()}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as summary:
            summary.write(message + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scholar-id", default=os.environ.get("GOOGLE_SCHOLAR_ID"))
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--snapshot", type=Path, help="Also refresh the Jekyll build-time snapshot.")
    parser.add_argument("--skip-blocked", action="store_true",
                        help="Skip HTTP 403/429 with a warning and keep existing data unchanged.")
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    scholar_id = args.scholar_id or config["google_scholar_id"]
    try:
        stats = fetch_stats(scholar_id)
    except ScholarHTTPError as error:
        if not args.skip_blocked or error.status not in (403, 429):
            raise
        message = (f"Citation refresh skipped: Google Scholar returned HTTP {error.status}. "
                   "Existing citation counts and their update date remain unchanged. "
                   "The next scheduled run will try again.")
        in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        prefix = "::warning::" if in_actions else "Warning: "
        print(prefix + message, file=sys.stdout if in_actions else sys.stderr)
        report_result(False, message)
        return
    write_json(args.output / "gs_data.json", stats)
    write_json(args.output / "gs_data_shieldsio.json", {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(stats["citedby"]),
    })
    if args.snapshot:
        write_json(args.snapshot, stats)
    message = (f"Updated {stats['name']}: {stats['citedby']} citations; "
               f"{len(stats['publications'])} publications; {stats['updated']}")
    print(message)
    report_result(True, message)


if __name__ == "__main__":
    main()
