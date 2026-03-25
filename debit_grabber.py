from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
import datetime
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
from datetime import timedelta
import re
import random
import time
import shutil
import pandas as pd
from grab_csvs import page_setup

# getting the username and password for the account
load_dotenv()

username = os.getenv("D_USER")
password = os.getenv("D_PASS")

# finding the current month of the year
current_date = datetime.datetime.now()
month_name = current_date.strftime("%B")
day_num = current_date.day
# finding the previous month as well
first_day_month = current_date.replace(day=1)
last_day_prev_month = first_day_month - timedelta(days=1)
prev_month = last_day_prev_month.strftime("%B")

url = "https://www.aacu.com/"

with sync_playwright() as p:
    page = page_setup(p)
    page.goto(url)

    # login
    page.locator('button[value="LOG IN"]').click()
    page.locator("#user_id").press_sequentially(username, delay=random.uniform(55, 160))
    time.sleep(random.uniform(1, 3))
    page.locator("#password").press_sequentially(password, delay=random.uniform(55, 160))
    time.sleep(random.uniform(1, 3))
    page.locator("#BankingLoginSubmit").click()

    # clicking into the checking account
    page.wait_for_selector("#ember7", timeout=20000)
    # first issue to debug
    page.locator('q2-icon[test-id="ae-account-tile-category-icon"]').click()
    time.sleep(random.uniform(2, 4))

    # filtering for the correct dates
    # if after the 15th of each month we will check spending from the 15th until the current day
    # if before the 15th of the month we will check spending from the 15th of the previous month
    page.get_by_test_id("q2BtnInnerButton").click()
    page.locator("#input-guid-1017").click()
    page.locator('q2-option[value="custom"]').click()
    page.locator("#input-guid-1020").click()

    if day_num <= 15:
        page.get_by_label("Previous month").click()
        page.locator('td[data-day="15"]').click()
        page.locator("#input-guid-1021").click()
        day_num_str = str(day_num)
        page.locator(f'td[data-day="{day_num_str}"]').click()
        page.get_by_test_id("btnApplyFilter").click()
    else:
        page.locator('td[data-day="15"]').click()
        page.locator("#input-guid-1021").click()
        day_num_str = str(day_num)
        page.locator(f'td[data-day="{day_num_str}"]').click()
        page.get_by_test_id("btnApplyFilter").click()

    # download the csv file
    page.get_by_test_id("q2BtnInnerButton").click()
    with page.expect_download() as download_info:
        page.click('q2-dropdown-item[id="CSV"]')
    
    download = download_info.value
    saved_path = os.path.expanduser("~/Downloads/" + download.suggested_filename)
    download.save_as(saved_path)

    input("Press ENTER to quit\\n")
    page.close()

# move the csv file to the correct file location
