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

def main():
    # loading up the page using the URL for the page
    login_url = "https://www.americanexpress.com/en-us/account/login"

    with sync_playwright() as p:
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

        page.goto(login_url)

        # login to account
        page.wait_for_selector("#eliloUserID", timeout=10000)
        # page.type("#eliloUserID", username, delay=150)
        page.locator("#eliloUserID").press_sequentially(username, delay=random.uniform(55, 160))
        time.sleep(random.uniform(1, 3))
        # page.type("#eliloPassword", password, delay=145)
        page.locator("#eliloPassword").press_sequentially(password, delay=random.uniform(55, 160))
        time.sleep(random.uniform(1, 3))
        page.click("#loginSubmit")

        # getting to the correct page to download the csvs
        page.wait_for_selector("#hamburgerMenuOpener", timeout=15000)
        page.get_by_test_id("simple_switcher_combobox").click()
        # clicking the element from the drop down that designates the gold card `*=` designates that only part of that word needs to be in the label
        gold_element = page.locator('div[aria-label*="Gold Card"]')
        gold_element.click()
        # working within the gold card
        page.wait_for_selector("#hamburgerMenuOpener", timeout=20000)
        time.sleep(random.uniform(2.5, 5))
        page.get_by_role("link", name="View All Recent Transactions").click()
        # opening the calendar
        page.get_by_test_id("myca-feed-DateRangePicker-Header").click()
        page.get_by_test_id("dateRangePicker.customDateBadge").click()
        page.get_by_label("Open calendar").click()
        # logic to pick custom dates for the csv
        if day_num < 15:
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

            print(f"Saved to {saved_path}")
            
        else:
            print("Getting around to it")
        
        # moving the first gold file to its correct location and renaming it
        gold_name = month_name + str(current_date.year) + "GoldExpenses.csv"
        shutil.move("/Users/nickbourgeois/Downloads/activity.csv", "/Users/nickbourgeois/Documents/finance/expense-docs/Amex Gold/2026")
        os.rename("/Users/nickbourgeois/Documents/finance/expense-docs/Amex Gold/2026/activity.csv", f"/Users/nickbourgeois/Documents/finance/expense-docs/Amex Gold/2026/{gold_name}")

        input("Press ENTER to quit\\n")
        page.close()

if __name__ == "__main__":
    main()