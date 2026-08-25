#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

REPOS = {
    "https://github.com/ApodexAI/FrontierAgent": "ApodexAI/FrontierAgent",
    "https://github.com/ApodexAI/AgentHarness": "ApodexAI/AgentHarness",
    "https://github.com/Alibaba-NLP/DeepResearch/": "Alibaba-NLP/DeepResearch",
}


def format_stars(count):
    if count >= 1000:
        value = f"{count / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{value}k"
    return str(count)


def fetch_stars(repo):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "LiangcaiSu.github.io-star-updater",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload["stargazers_count"]


def update_link(html, url, label):
    anchor_pattern = re.compile(
        rf'(<a href="{re.escape(url)}">)(?P<body>.*?)(</a>)',
        re.DOTALL,
    )

    def replace_anchor(match):
        body = re.sub(
            r"GitHub\s*\([^)]*stars\)",
            f"GitHub ({label} stars)",
            match.group("body"),
        )
        return f"{match.group(1)}{body}{match.group(3)}"

    html, replacements = anchor_pattern.subn(replace_anchor, html, count=1)
    if replacements != 1:
        raise RuntimeError(f"Could not find GitHub link for {url}")
    return html


def main():
    html = INDEX.read_text(encoding="utf-8")
    for url, repo in REPOS.items():
        stars = fetch_stars(repo)
        html = update_link(html, url, format_stars(stars))

    INDEX.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, KeyError) as exc:
        print(f"Failed to update GitHub stars: {exc}", file=sys.stderr)
        sys.exit(1)
