""""Tried first in selenium, does not allow me to log into the website. So I will need something a little more lightweight. Let's try playwright"""
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
import datetime
from pprint import pprint
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent
from datetime import timedelta
import re
import asyncio
import random
import time
import shutil
import pandas as pd

# getting the username and password for the account
load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# finding the current month of the year
current_date = datetime.datetime.now()
month_name = current_date.strftime("%B")
day_num = current_date.day
# finding the previous month as well
first_day_month = current_date.replace(day=1)
last_day_prev_month = first_day_month - timedelta(days=1)
prev_month = last_day_prev_month.strftime("%B")

# defining functions for main function
def page_setup(p):
    browser = p.chromium.launch(channel="chrome",
                                headless=False,
                                args=["--disable-blink-features=AutomationControlled"])
    ua = UserAgent()
    user_agent = ua.random
    context = browser.new_context(
    user_agent=user_agent,
    accept_downloads=True
    )
    page = context.new_page()

    return page

def login(page):
    page.wait_for_selector("#eliloUserID", timeout=10000)
    page.locator("#eliloUserID").press_sequentially(username, delay=random.uniform(55, 160))
    time.sleep(random.uniform(1, 3))
    page.locator("#eliloPassword").press_sequentially(password, delay=random.uniform(55, 160))
    time.sleep(random.uniform(1, 3))
    page.click("#loginSubmit")

    return page

def get_to_calendar(page, card_string):
    page.wait_for_selector("#hamburgerMenuOpener", timeout=15000)
    page.get_by_test_id("simple_switcher_combobox").click()
    # clicking the element from the drop down that designates the gold card `*=` designates that only part of that word needs to be in the label
    element = page.locator(f'div[aria-label*="{card_string}"]')
    element.click()
    # working within the gold card
    page.wait_for_selector("#hamburgerMenuOpener", timeout=20000)
    time.sleep(random.uniform(2.5, 5))
    if "Gold" in card_string:
        page.get_by_role("link", name="View All Recent Transactions").click()
    # opening the calendar
    page.get_by_test_id("myca-feed-DateRangePicker-Header").click()
    page.get_by_test_id("dateRangePicker.customDateBadge").click()
    page.get_by_label("Open calendar").click()

    return page

def pre_fifteen_download(page):
    page.get_by_label("Previous month").click()
    prev_month_date_string = prev_month + " " + "15," + " " + str(current_date.year)
    time.sleep(random.uniform(1, 3))
    page.get_by_role("button", name=re.compile(prev_month_date_string, re.IGNORECASE)).click()
    page.get_by_label("Next month").click()
    current_date_string = month_name + " " + str(day_num) + "," + " " + str(current_date.year)
    page.get_by_role("button", name=re.compile(current_date_string, re.IGNORECASE)).click()
    time.sleep(random.uniform(2, 4))
    page.get_by_label("Done").click()
    page.get_by_label("Download").click()
    time.sleep(random.uniform(1, 3))
    # clicking into the page that comes up to finalize the download
    page.click("label[for='myca-activity-download-body-selection-options-csv']")
    with page.expect_download() as download_information:
        page.click("span:text-is('Download')")

    download = download_information.value
    saved_path = os.path.expanduser("~/Downloads/" + download.suggested_filename)
    download.save_as(saved_path)

    return page

def shifter(card_string):
    name = str(current_date.day) + month_name + str(current_date.year) + f"{card_string}Expenses.csv"
    shutil.move("/Users/nickbourgeois/Downloads/activity.csv", f"/Users/nickbourgeois/Documents/finance/expense-docs/Amex {card_string}/2026")
    os.rename(f"/Users/nickbourgeois/Documents/finance/expense-docs/Amex {card_string}/2026/activity.csv", f"/Users/nickbourgeois/Documents/finance/expense-docs/Amex {card_string}/2026/{name}")
    df = pd.read_csv(f"/Users/nickbourgeois/Documents/finance/expense-docs/Amex {card_string}/2026/{name}")

    return df


def main():
    # loading up the page using the URL for the page
    login_url = "https://www.americanexpress.com/en-us/account/login"

    with sync_playwright() as p:
        page = page_setup(p)
        page.goto(login_url)

        # login to account
        page = login(page)

        # getting to the correct page to download the csvs
        page = get_to_calendar(page, "Gold Card")

        # logic to pick custom dates for the csv
        if day_num < 15:
            page = pre_fifteen_download(page)
        else:
            print("Getting around to it")
        
        # moving the first gold file to its correct location and renaming it
        gold_card_df = shifter("Gold")

        # getting the platinum card next
        page = get_to_calendar(page, "Platinum")

        if day_num < 15:
            page = pre_fifteen_download(page)
        else:
            print("Getting to it")
        
        # moving the first gold file to its correct location and renaming it
        plat_card_df = shifter("Platinum")

        input("Press ENTER to quit\\n")
        page.close()
    
    # concatenate the files together and export to my computer to be input into the dashboard
    concat_card_df = pd.concat([gold_card_df, plat_card_df])
    concat_name = str(current_date.day) + month_name + str(current_date.year) + "Expenses.csv"
    concat_card_df.to_csv(f"/Users/nickbourgeois/Documents/finance/expense-docs/Merged Cards/{concat_name}", index=False)

if __name__ == "__main__":
    main()