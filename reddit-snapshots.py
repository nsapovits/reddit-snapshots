# -*- coding: utf-8 -*-

# TODO:
# push style.css into output directory
# email integration for run logs?
# dating html files and having a way to browse past files
# maybe relabel image, video, self posts links in some way
# maybe redirect image links to raw image, what about videos?

# import os
# import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# Flags
use_local_source = False
use_headless_mode = True
use_print_as_debug = False

# Static Variables
posts = 0
reddit = 'https://old.reddit.com/r/'

# Read "subreddits.txt" for targets
with open('subreddits.txt', 'r') as file:
    subreddits_raw = file.readlines()
subreddits = [subreddit.strip() for subreddit in subreddits_raw]

# Start setting up for Selenium if we are doing full scraping
if not use_local_source:
    # Set Firefox options to run in headless mode (without opening a visible browser window)
    options = Options()

    # Check use_headless_mode flag to set headless arg if desired
    if use_headless_mode:
        print('using headless mode')
        options.add_argument('-headless')

    # Create a Firefox WebDriver instance
    driver = webdriver.Firefox(options=options)

# Start writing the final HTML file
file = open(r'output/index.html', 'w+', encoding='utf-8')

file.write('<!DOCTYPE html>\n'
           '<html lang="en">\n'
           '\t<head>\n'
           '\t\t<title>Reddit</title>\n'
           '\t\t<link rel="stylesheet" type="text/css" href="style.css">\n'
           '\t\t<meta charset="UTF-8">\n'
           '\t\t<meta name="referrer" content="no-referrer">\n'
           '\t</head>\n'
           '\t<body>\n'
           '\t\t<table>\n')

# Iterate through subreddits of interest
for subreddit in subreddits:

    # Identify Reddit-specific link domains so they can be rewritten later
    reddit_domains = ['self.' + subreddit.lower(),
                      'i.redd.it',
                      'v.redd.it',
                      'old.reddit.com',
                      'reddit.com']

    # Write HTML table header row per subreddit
    file.write('\t\t\t<tr>\n'
               '\t\t\t\t<th class="title" colspan="4">'
               '<a target="_blank" href="' + reddit + subreddit + '/top/">' + subreddit + '</a></th>\n'
               '\t\t\t</tr>\n')

    # Determine which source to use and start loading it
    if use_local_source:
        print('using local source at /output/local/' + subreddit.lower() + '.html')
        try:
            html_source = open(r'output/local/' + subreddit.lower() + '.html', 'r', encoding='utf-8')
        except OSError:
            print('could not find source for ' + subreddit.lower())
            continue
    else:
        print('using web source')
        # noinspection PyUnboundLocalVariable
        driver.get(reddit + subreddit.lower() + "/top/")
        html_source = driver.page_source

    soup = BeautifulSoup(html_source, 'html.parser')

    # Save the source HTML for re-runs when debugging
    if not use_local_source:
        source = soup.prettify()
        with open(r'output/local/' + subreddit.lower() + '.html', '+w', encoding='utf-8') as export:
            export.write(source)

    # Find all post elements
    post_elements = soup.find_all('div', class_='thing')

    # Process each post element
    for post in post_elements:
        # Skip promoted posts
        if post.get('data-promoted') == 'true':
            continue

        # Extract post details
        title = post.find('a', class_='title').text
        link = post.find('a', class_='title')['href']
        score = post.find('div', class_='score unvoted').text.strip()
        comments = post.find('a', class_='comments').text.split()[0]
        c_link = post.find('a', class_='comments')['href']
        domain = post.find('span', class_='domain').text.strip()

        # Run some basic text manipulations
        title = title.strip()
        domain = domain.replace('(', '').replace(')', '').strip()
        score = score.strip()
        comments = comments.replace(' comments', '').replace(' comment', '').replace('comment', '0').strip()

        # Print posts to console when debugging
        if use_print_as_debug:
            print('"' + title + '","'
                      + domain + '","'
                      + score + '","'
                      + comments + '","'
                      + c_link + '","'
                      + link + '"')

        # Skip posts with a low score
        try:
            if int(score) <= 1:
                continue
        except ValueError:
            pass

        # Replace bullet characters for 'prettier' output
        if score == "•":
            score = "-"

        # If the post is to a Reddit domain, the URL is relative, so instead just use the comment link
        if domain.lower() in reddit_domains:
            link = c_link

        # Write the posts to the final HTML file
        file.write('\t\t\t\t<tr>\n'
                   '\t\t\t\t\t<td class="title"><a target="_blank" href="' + link + '">' + title + '</a></td>\n'
                   '\t\t\t\t\t<td class="domain">' + domain + '</td>\n'
                   '\t\t\t\t\t<td class="score">' + score + '</td>\n'
                   '\t\t\t\t\t<td class="comments"><a target="_blank" href="' + c_link + '">' + comments + '</a></td>\n'
                   '\t\t\t\t</tr>\n')

        # Simple counter for debugging
        posts += 1

# Quit Firefox if we started it
if not use_local_source:
    driver.quit()

# Write the closing HTML for the final output
file.write('\t\t</table>\n'
           '\t</body>\n'
           '</html>\n')

# Close the final output file
file.close()

# Print the simple counter to see how many posts were processed
print('processed ' + str(posts) + ' posts')
