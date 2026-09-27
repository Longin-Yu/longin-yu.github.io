"""Fetch public Google Scholar counts for the Acad Homepage stats branch.

No login, API key or paid proxy is needed. Invalid/blocked responses fail before
writing any files, so the last successful snapshot remains available.
"""
import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


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
        # curl uses the machine's http_proxy / https_proxy configuration.
        response = subprocess.run(
            ["curl", "--fail", "--silent", "--show-error", "--location",
             "--max-time", "30", url],
            check=True, capture_output=True, timeout=35,
        )
        page = parse_page(response.stdout, scholar_id, first_page=start == 0)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scholar-id", default=os.environ.get("GOOGLE_SCHOLAR_ID"))
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--snapshot", type=Path, help="Also refresh the Jekyll build-time snapshot.")
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "_config.yml").read_text(encoding="utf-8"))
    scholar_id = args.scholar_id or config["google_scholar_id"]
    stats = fetch_stats(scholar_id)
    write_json(args.output / "gs_data.json", stats)
    write_json(args.output / "gs_data_shieldsio.json", {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(stats["citedby"]),
    })
    if args.snapshot:
        write_json(args.snapshot, stats)
    print(f"Updated {stats['name']}: {stats['citedby']} citations; "
          f"{len(stats['publications'])} publications; {stats['updated']}")


if __name__ == "__main__":
    main()
