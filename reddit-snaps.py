# import os
# import time
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

subreddits = ['apple',
              'cars',
              'costco',
              'electricvehicles',
              'lego',
              'maryland',
              'sysadmin',
              'tmobile']


# # Set Firefox options to run in headless mode (without opening a visible browser window)
# options = Options()
# options.add_argument('-headless')
#
# # Create a Firefox WebDriver instance
# driver = webdriver.Firefox(options=options)
#
# # Install uB0 extension
# cwd = os.getcwd()
# driver.install_addon(cwd + r"/uBlock0@raymondhill.net.xpi", temporary=True)
#
# # Sleep to make sure uB0 has loaded
# time.sleep(3)

# driver.get("https://old.reddit.com/r/all/top/")
# html_source = driver.page_source
# # Clean up and quit the WebDriver
# driver.quit()

# DEBUG: read from saved html file to save time during dev
html_source = open(r'output/soup.html', 'r', encoding='utf-8')

soup = BeautifulSoup(html_source, 'html.parser')

# DEBUG: prettify html and write to disk if necessary for debugging
# source = soup.prettify()
# with open(r'output/soup.html', 'w', encoding='utf-8') as file:
#     file.write(source)

post_titles = soup.find_all('a', class_='title may-blank')
titles = [title.text for title in post_titles]

post_domains = soup.find_all('span', class_='domain')
domains = [domain.text for domain in post_domains]

post_scores = soup.find_all('div', class_='score unvoted')
scores = [score.text for score in post_scores]

post_comments = soup.find_all('a', class_='bylink comments may-blank')
comments = [comment.text for comment in post_comments]

file = open(r'output/output.html', 'w+', encoding='utf-8')

file.write('<!DOCTYPE html>\n'
           '<html lang="en">\n'
           '\t<head>\n'
           '\t\t<title>Test</title>\n'
           '\t\t<link rel="stylesheet" type="text/css" href="../style.css">\n'
           '\t</head>\n'
           '\t<body>\n'
           '\t\t<table>\n'
           '\t\t\t<tr>\n'
           '\t\t\t\t<th class="title" colspan="4">/r/all</th>\n'
           '\t\t\t</tr>\n')

for title, domain, score, comment in zip(titles, domains, scores, comments):
    file.write('\t\t\t\t<tr>\n'
               '\t\t\t\t\t<td class="title">' + title.strip() + '</td>\n'
               '\t\t\t\t\t<td class="domain">' + domain.replace('(', '').replace(')', '').strip() + '</td>\n'
               '\t\t\t\t\t<td class="score">' + score.strip() + '</td>\n'
               '\t\t\t\t\t<td class="comment">' + comment.replace(' comments', '').strip() + '</td>\n'
               '\t\t\t\t</tr>\n')

file.write('\t\t</table>\n'
           '\t</body>\n'
           '</html>\n')

# # Iterate through subreddits of interest
# for subreddit in subreddits:
#     driver.get("https://old.reddit.com/r/" + subreddit + "/top/")

file.close()