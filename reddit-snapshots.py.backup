# -*- coding: utf-8 -*-

import os
import json
import time
import html
import random
import requests

# ------------- Flags -------------
use_local_source = False
use_print_as_debug = False
strict_last_24h = True   # hot + strict 24h filter + local sort by score

# ------------- Static -------------
posts = 0
base = "https://www.reddit.com"
listing_path = "/r/{sub}/hot.json"
listing_params = {
    "limit": 100,     # pull more, then filter/sort locally
    "raw_json": 1     # unescaped unicode
}

# ------------- I/O prep -------------
os.makedirs("output", exist_ok=True)
os.makedirs("output/local", exist_ok=True)

# Read "subreddits.txt" for targets
with open(r"subreddits.txt", "r", encoding="utf-8") as f:
    subreddits = [line.strip() for line in f if line.strip()]

# ------------- HTTP session -------------
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:146.0) Gecko/20100101 Firefox/146.0"
})

def fetch_subreddit_hot_json(subreddit, retries=3, backoff_base=0.8):
    """
    Fetch hot posts as JSON listing. Returns parsed dict.
    If use_local_source is True, load from output/local/<subreddit>.json.
    """
    local_path = os.path.join("output", "local", f"{subreddit.lower()}.json")

    if use_local_source:
        if not os.path.exists(local_path):
            print(f"could not find source for {subreddit.lower()}")
            return None
        with open(local_path, "r", encoding="utf-8") as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                print(f"invalid JSON for {subreddit.lower()}")
                return None

    # Remote fetch
    url = base + listing_path.format(sub=subreddit.lower())
    params = listing_params.copy()

    for attempt in range(1, retries + 1):
        try:
            resp = SESSION.get(url, params=params, timeout=20)
            if resp.status_code >= 400:
                raise requests.HTTPError(f"HTTP {resp.status_code}")
            data = resp.json()
            # Save local copy for debugging
            with open(local_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            return data
        except Exception as e:
            if attempt == retries:
                print(f"[{subreddit}] failed after {retries} attempts: {e}")
                return None
            sleep_s = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.3)
            print(f"[{subreddit}] error: {e} — retrying in {sleep_s:.1f}s")
            time.sleep(sleep_s)

def extract_rows_from_listing(listing, subreddit):
    """
    Convert listing JSON to list of rows for HTML.
    Now: hot.json -> strict last 24h -> sort by score desc -> top 25 (or fewer).
    Applies your original transformations and skips.
    """
    global posts
    rows = []

    if not listing or "data" not in listing:
        return rows

    children = listing["data"].get("children", [])

    # Collect post data first, then filter/sort before rendering rows
    cutoff = int(time.time()) - 24 * 60 * 60
    post_dicts = []

    for child in children:
        if child.get("kind") != "t3":
            continue
        d = child.get("data", {})

        # Score normalization (keep your original handling)
        score = d.get("score") or 0
        if isinstance(score, str):
            try:
                score = int(score)
            except ValueError:
                score = 0

        # Skip if score <= 1 (your original behavior)
        if score <= 1:
            continue

        # Strict 24h filter by created_utc (primary daily definition now)
        created = d.get("created_utc") or 0
        try:
            created = int(created)
        except (TypeError, ValueError):
            created = 0

        if strict_last_24h and created < cutoff:
            continue

        d["_score_norm"] = score  # stash normalized score for sorting
        post_dicts.append(d)

    # Sort by score descending, then take up to 25
    post_dicts.sort(key=lambda x: x.get("_score_norm", 0), reverse=True)
    post_dicts = post_dicts[:25]

    # Render rows
    for d in post_dicts:
        score = d.get("_score_norm", 0)

        title = (d.get("title") or "").strip()
        domain = (d.get("domain") or "").strip()
        num_comments = d.get("num_comments") or 0
        permalink = d.get("permalink") or ""
        comments_link = base + permalink if permalink else ""

        # Prefer external destination; if Reddit-internal, use comments link
        link = d.get("url_overridden_by_dest") or d.get("url") or comments_link

        # Rewrite "www.reddit.com" to "old.reddit.com"
        if link and "www.reddit.com" in link:
            link = link.replace("www.reddit.com", "old.reddit.com")
        if comments_link and "www.reddit.com" in comments_link:
            comments_link = comments_link.replace("www.reddit.com", "old.reddit.com")

        reddit_domains = {
            f"self.{subreddit.lower()}",
            "i.redd.it", "v.redd.it", "old.reddit.com", "reddit.com", "www.reddit.com"
        }
        if domain.lower() in reddit_domains:
            link = comments_link

        # Replace bullet score like your old code (unlikely here, but keeping parity)
        score_str = "-" if (isinstance(score, str) and score.strip() == "•") else str(score)

        # Escape HTML-sensitive fields
        safe_title = html.escape(title)
        safe_domain = html.escape(domain)
        safe_link = html.escape(link, quote=True)
        safe_comments_link = html.escape(comments_link, quote=True)

        rows.append(
            '\t\t\t\t<tr>\n'
            f'\t\t\t\t\t<td class="title"><a target="_blank" href="{safe_link}">{safe_title}</a></td>\n'
            f'\t\t\t\t\t<td class="domain">{safe_domain}</td>\n'
            f'\t\t\t\t\t<td class="score">{score_str}</td>\n'
            f'\t\t\t\t\t<td class="comments"><a target="_blank" href="{safe_comments_link}">{num_comments}</a></td>\n'
            '\t\t\t\t</tr>\n'
        )
        posts += 1

    return rows

# ------------- Write HTML head -------------
with open(r"output/index.html", "w", encoding="utf-8") as outf:
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

    # ------------- Per-subreddit -------------
    for subreddit in subreddits:
        print(("using local source at output/local/" if use_local_source else "using web source for ") + subreddit.lower())

        # Header row with link to hot page (matches new fetch logic)
        outf.write(
            "\t\t\t<tr>\n"
            f'\t\t\t\t<th class="title" colspan="4"><a target="_blank" href="{base}/r/{subreddit}/hot/">{html.escape(subreddit)}</a></th>\n'
            "\t\t\t</tr>\n"
        )

        listing = fetch_subreddit_hot_json(subreddit)
        rows = extract_rows_from_listing(listing, subreddit)
        for row in rows:
            if use_print_as_debug:
                pass
            outf.write(row)

    # ------------- Close HTML -------------
    outf.write(
        "\t\t</table>\n"
        "\t</body>\n"
        "</html>\n"
    )

print(f"processed {posts} posts")
