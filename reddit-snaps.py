# -*- coding: utf-8 -*-

# TODO: push style.css into output directory

# import os
# import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

use_local_source = True
use_headless_mode = True
use_print_as_debug = True

subreddits = ['News',
              'WorldNews',
              'Maryland',
              'Apple',
              'AMD',
              'Intel',
              'NVidia',
              'SysAdmin',
              'Cars',
              'ElectricVehicles',
              'Cordcutters',
              'Costco',
              'Lego',
              'TMobile',
              'WOW',
              'XBox',
              'XBoxGamePass',
              'XBoxSeriesX'
              ]

if not use_local_source:
    # Set Firefox options to run in headless mode (without opening a visible browser window)
    options = Options()

    # Check use_headless_mode flag to set headless arg if desired
    if use_headless_mode:
        print('using headless mode')
        options.add_argument('-headless')

    # Create a Firefox WebDriver instance
    driver = webdriver.Firefox(options=options)

file = open(r'output/output.html', 'w+', encoding='utf-8')

file.write('<!DOCTYPE html>\n'
           '<html lang="en">\n'
           '\t<head>\n'
           '\t\t<title>Reddit</title>\n'
           '\t\t<link rel="stylesheet" type="text/css" href="../style.css">\n'
           '\t</head>\n'
           '\t<body>\n'
           '\t\t<table>\n')

# Iterate through subreddits of interest
for subreddit in subreddits:
    file.write('\t\t\t<tr>\n'
               '\t\t\t\t<th class="title" colspan="4">'
               '<a href="https://old.reddit.com/r/' + subreddit + '/top/">' + subreddit + '</a></th>\n'
               '\t\t\t</tr>\n')

    if use_local_source:
        print('using local source')
        html_source = open(r'output/' + subreddit + '.html', 'r', encoding='utf-8')
    else:
        print('using web source')
        # noinspection PyUnboundLocalVariable
        driver.get("https://old.reddit.com/r/" + subreddit + "/top/")
        html_source = driver.page_source

    soup = BeautifulSoup(html_source, 'html.parser')

    if not use_local_source:
        source = soup.prettify()
        with open(r'output/' + subreddit + '.html', '+w', encoding='utf-8') as export:
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
        domain = post.find('span', class_='domain').text.strip()

        title = title.strip()
        domain = domain.replace('(', '').replace(')', '').strip()
        score = score.strip()
        comments = comments.replace(' comments', '').replace(' comment', '').strip()

        # TODO: fix links to reddit's own sites
        # Example: "/r/XboxSeriesX/comments/14pt1v0/buying_witcher_3_on_xbox_nextgen_updated_included/"

        if use_print_as_debug:
            print('"' + title + '","' + domain + '","' + score + '","' + comments + '","' + link + '"')

        try:
            if int(score) <= 1:
                print('found low-scoring post - skipping...')
                continue
        except ValueError:
            print('casting score to int failed - continuing...')

        if score == "•":
            score = "-"

        file.write('\t\t\t\t<tr>\n'
                   '\t\t\t\t\t<td class="title"><a href="' + link + '">' + title + '</a></td>\n'
                   '\t\t\t\t\t<td class="domain">' + domain + '</td>\n'
                   '\t\t\t\t\t<td class="score">' + score + '</td>\n'
                   '\t\t\t\t\t<td class="comments">' + comments + '</td>\n'
                   '\t\t\t\t</tr>\n')

if not use_local_source:
    driver.quit()

file.write('\t\t</table>\n'
           '\t</body>\n'
           '</html>\n')

file.close()
