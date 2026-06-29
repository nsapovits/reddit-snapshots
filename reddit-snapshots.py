# -*- coding: utf-8 -*-

import os
import html
from playwright.sync_api import sync_playwright

# ------------- Flags -------------
use_local_source = False
use_print_as_debug = False

# ------------- Static -------------
posts = 0
reddit = "https://old.reddit.com/r/"

# ------------- I/O prep -------------
os.makedirs("output", exist_ok=True)
os.makedirs("output/local", exist_ok=True)

# Read "subreddits.txt" for targets
with open("subreddits.txt", "r", encoding="utf-8") as f:
    subreddits = [line.strip() for line in f if line.strip()]


def scrape_subreddit(page, subreddit):
    """Load subreddit hot page and return list of post dicts. Skips ads."""
    local_path = os.path.join("output", "local", f"{subreddit.lower()}.html")

    if use_local_source:
        if not os.path.exists(local_path):
            print(f"could not find source for {subreddit.lower()}")
            return []
        with open(local_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        page.set_content(content)
    else:
        url = reddit + subreddit.lower() + "/hot/"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # Save local copy for debugging
        with open(local_path, "w", encoding="utf-8") as fh:
            fh.write(page.content())

    reddit_domains = {
        f"self.{subreddit.lower()}",
        "i.redd.it", "v.redd.it", "old.reddit.com", "reddit.com", "www.reddit.com",
    }

    posts_data = page.evaluate("""(reddit_domains) => {
        const things = document.querySelectorAll('div.thing');
        const results = [];
        for (const thing of things) {
            // Skip promoted/ads
            if (thing.dataset.promoted === 'true') continue;

            const titleEl = thing.querySelector('a.title');
            const scoreEl = thing.querySelector('div.score.unvoted');
            const commentsEl = thing.querySelector('a.comments');
            const domainEl = thing.querySelector('span.domain');

            if (!titleEl || !scoreEl || !commentsEl || !domainEl) continue;

            const title = titleEl.textContent.trim();
            let link = titleEl.href;
            const scoreText = scoreEl.textContent.trim();
            const commentsText = commentsEl.textContent.split(' ')[0].replace('comment', '0').trim();
            const c_link = commentsEl.href;
            const domain = domainEl.textContent.replace('(','').replace(')','').trim();

            if (reddit_domains.includes(domain.toLowerCase())) {
                link = c_link;
            }

            results.push({ title, link, score: scoreText, comments: commentsText, c_link, domain });
        }
        return results;
    }""", list(reddit_domains))

    return posts_data


def build_rows(posts_data):
    """Convert scraped post dicts to HTML rows, skipping low-score posts."""
    global posts
    rows = []
    count = 0

    for d in posts_data:
        if count >= 25:
            break

        score = d.get("score", "0").strip()

        # Skip bullet/hidden scores and low scores
        try:
            if int(score) <= 1:
                continue
        except ValueError:
            pass  # keep non-numeric scores like "•"

        if score == "•":
            score = "-"

        title = d.get("title", "").strip()
        domain = d.get("domain", "").strip()
        comments = d.get("comments", "0")
        link = d.get("link", "")
        c_link = d.get("c_link", "")

        if use_print_as_debug:
            print(f'"{title}","{domain}","{score}","{comments}","{c_link}","{link}"')

        safe_title = html.escape(title)
        safe_domain = html.escape(domain)
        safe_link = html.escape(link, quote=True)
        safe_c_link = html.escape(c_link, quote=True)

        rows.append(
            '\t\t\t\t<tr>\n'
            f'\t\t\t\t\t<td class="title"><a target="_blank" href="{safe_link}">{safe_title}</a></td>\n'
            f'\t\t\t\t\t<td class="domain">{safe_domain}</td>\n'
            f'\t\t\t\t\t<td class="score">{score}</td>\n'
            f'\t\t\t\t\t<td class="comments"><a target="_blank" href="{safe_c_link}">{comments}</a></td>\n'
            '\t\t\t\t</tr>\n'
        )
        posts += 1
        count += 1

    return rows


# ------------- Main -------------
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        java_script_enabled=True,
    )

    # Block ad/tracker domains at the network level
    ad_domains = [
        "doubleclick.net", "googlesyndication.com", "adservice.google.com",
        "amazon-adsystem.com", "moatads.com", "adnxs.com", "outbrain.com",
        "taboola.com", "scorecardresearch.com", "quantserve.com",
        "redditads.com", "redditmedia.com",
    ]
    def block_ads(route):
        if any(d in route.request.url for d in ad_domains):
            route.abort()
        else:
            route.continue_()
    context.route("**/*", block_ads)

    page = context.new_page()

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
                f'<a target="_blank" href="{reddit}{subreddit}/hot/">{html.escape(subreddit)}</a></th>\n'
                "\t\t\t</tr>\n"
            )

            posts_data = scrape_subreddit(page, subreddit)
            rows = build_rows(posts_data)
            for row in rows:
                outf.write(row)

        outf.write(
            "\t\t</table>\n"
            "\t</body>\n"
            "</html>\n"
        )

    browser.close()

print(f"processed {posts} posts")
