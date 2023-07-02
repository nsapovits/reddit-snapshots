import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from PIL import Image

subreddits = ["apple",
              "cars",
              "costco",
              "electricvehicles",
              "maryland",
              "sysadmin"]

# Build a yyyymmdd date for screenshots
today = datetime.now()
date = "-" + today.strftime("%Y%m%d")

# Set Firefox options to run in headless mode (without opening a visible browser window)
options = Options()
options.add_argument('-headless')

# Create a Firefox WebDriver instance
driver = webdriver.Firefox(options=options)

# Install uB0 extension
cwd = os.getcwd()
print(cwd)
driver.install_addon(cwd + r"/uBlock0@raymondhill.net.xpi", temporary=True)

# Sleep to make sure uB0 has loaded
time.sleep(3)

# click to hide signup banner
driver.get("https://old.reddit.com/r/all/top/")
element = driver.find_element(By.XPATH, "/html/body/div[4]/section/a[2]")
element.click()
driver.save_full_page_screenshot(r"output/all" + date + ".png")
image = Image.open(r"output/all" + date + ".png")
image.convert("RGB").save(r"output/all" + date + ".jpg", "JPEG")
os.remove(r"output/all" + date + ".png")

# Iterate through subreddits of interest
for subreddit in subreddits:
    driver.get("https://old.reddit.com/r/" + subreddit + "/top/")
    driver.save_full_page_screenshot(r"output/" + subreddit + date + ".png")
    image = Image.open(r"output/" + subreddit + date + ".png")
    image.convert("RGB").save(r"output/" + subreddit + date + ".jpg", "JPEG")
    os.remove(r"output/" + subreddit + date + ".png")

# Clean up and quit the WebDriver
driver.quit()
