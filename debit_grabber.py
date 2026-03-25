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

    # filtering for the correct dates
    # if after the 15th of each month we will check spending from the 15th until the current day
    # if before the 15th of the month we will check spending from the 15th of the previous month

    # download the csv file

    input("Press ENTER to quit\\n")
    page.close()

# move the csv file to the correct file location
