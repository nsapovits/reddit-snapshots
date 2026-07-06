# -*- coding: utf-8 -*-

import os
import html
import json
import subprocess

# ------------- Flags -------------
use_local_source = False
use_print_as_debug = False

# ------------- Static -------------
posts = 0
reddit = "https://old.reddit.com/r/"

SSH_HOST = os.environ.get("SSH_HOST", "")
SSH_USER = os.environ.get("SSH_USER", "")
SSH_TARGET = f"{SSH_USER}@{SSH_HOST}"

REMOTE_TMP_DIR = "/tmp/reddit-snapshots"

REMOTE_SCRIPT = r'''#!/bin/bash
set -u
mkdir -p /tmp/reddit-snapshots
rm -f /tmp/reddit-snapshots/*.json

for sub in "$@"; do
  osascript <<APPLESCRIPT > "/tmp/reddit-snapshots/${sub}.json"
tell application "Safari"
    activate
    open location "https://old.reddit.com/r/${sub}/top.json?limit=25&t=day"
    delay 3
    set pageSource to source of front document
    close front document
end tell
return pageSource
APPLESCRIPT
  sleep 2
done
'''

# ------------- I/O prep -------------
os.makedirs("output", exist_ok=True)
os.makedirs("output/local", exist_ok=True)

# Read "subreddits.txt" for targets
with open("subreddits.txt", "r", encoding="utf-8") as f:
    subreddits = [line.strip() for line in f if line.strip()]


def fetch_all_subreddits(subs):
    """Runs one SSH session that fetches all subreddits into /tmp/reddit-snapshots
    on the Mac via Safari/osascript, scp's the JSON files back to output/local,
    then always attempts remote cleanup."""
    try:
        subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=accept-new", SSH_TARGET, "bash", "-s", "--"] + subs,
            input=REMOTE_SCRIPT,
            text=True,
            check=True,
            timeout=600,
        )

        subprocess.run(
            ["scp", "-o", "StrictHostKeyChecking=accept-new",
             f"{SSH_TARGET}:{REMOTE_TMP_DIR}/*.json", "output/local/"],
            check=True,
            timeout=120,
        )
    finally:
        subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=accept-new", SSH_TARGET, "rm", "-rf", REMOTE_TMP_DIR],
            check=False,
            timeout=60,
        )


def load_subreddit_json(subreddit):
    """Load the previously-fetched JSON for a subreddit from output/local."""
    local_path = os.path.join("output", "local", f"{subreddit}.json")

    if not os.path.exists(local_path):
        print(f"could not find source for {subreddit}")
        return None

    with open(local_path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            print(f"invalid JSON for {subreddit}")
            return None


def build_rows(listing, subreddit):
    """Convert a top.json listing into HTML rows, skipping low-score/stickied posts."""
    global posts
    rows = []
    count = 0

    if not listing or "data" not in listing:
        return rows

    children = listing["data"].get("children", [])

    reddit_domains = {
        f"self.{subreddit.lower()}",
        "i.redd.it", "v.redd.it", "old.reddit.com", "reddit.com", "www.reddit.com",
    }

    for child in children:
        if count >= 25:
            break

        if child.get("kind") != "t3":
            continue

        d = child.get("data", {})

        if d.get("stickied") or d.get("promoted"):
            continue

        score = d.get("score", 0)
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 0

        if score <= 1:
            continue

        title = (d.get("title") or "").strip()
        domain = (d.get("domain") or "").strip()
        num_comments = d.get("num_comments") or 0
        permalink = "https://old.reddit.com" + (d.get("permalink") or "")
        url_raw = d.get("url_overridden_by_dest") or d.get("url") or permalink

        link = permalink if domain.lower() in reddit_domains else url_raw

        if use_print_as_debug:
            print(f'"{title}","{domain}","{score}","{num_comments}","{permalink}","{link}"')

        safe_title = html.escape(title)
        safe_domain = html.escape(domain)
        safe_link = html.escape(link, quote=True)
        safe_permalink = html.escape(permalink, quote=True)

        rows.append(
            '\t\t\t\t<tr>\n'
            f'\t\t\t\t\t<td class="title"><a target="_blank" href="{safe_link}">{safe_title}</a></td>\n'
            f'\t\t\t\t\t<td class="domain">{safe_domain}</td>\n'
            f'\t\t\t\t\t<td class="score">{score}</td>\n'
            f'\t\t\t\t\t<td class="comments"><a target="_blank" href="{safe_permalink}">{num_comments}</a></td>\n'
            '\t\t\t\t</tr>\n'
        )
        posts += 1
        count += 1

    return rows


# ------------- Main -------------
if not use_local_source:
    fetch_all_subreddits(subreddits)

with open("output/index.html", "w", encoding="utf-8") as outf:
    outf.write(
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "\t<head>\n"
        "\t\t<title>Reddit</title>\n"
        '\t\t<link rel="stylesheet" type="text/css" href="style.css">\n'
        '\t\t<meta charset="UTF-8">\n'
        '\t\t<meta name="referrer" content="no-referrer">\n'
        "\t</head>\n"
        "\t<body>\n"
        "\t\t<table>\n"
    )

    for subreddit in subreddits:
        print(("using local source at output/local/" if use_local_source else "using web source for ") + subreddit.lower())

        outf.write(
            "\t\t\t<tr>\n"
            f'\t\t\t\t<th class="title" colspan="4">'
            f'<a target="_blank" href="{reddit}{subreddit}/top/?t=day">{html.escape(subreddit)}</a></th>\n'
            "\t\t\t</tr>\n"
        )

        listing = load_subreddit_json(subreddit)
        rows = build_rows(listing, subreddit)
        for row in rows:
            outf.write(row)

    outf.write(
        "\t\t</table>\n"
        "\t</body>\n"
        "</html>\n"
    )

print(f"processed {posts} posts")
