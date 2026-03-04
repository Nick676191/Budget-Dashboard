# # testing that the selenium google driver works
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from dotenv import load_dotenv
# import os

# load_dotenv()

# username = os.getenv("USERNAME")
# password = os.getenv("PASSWORD")

# driver = webdriver.Chrome()

# driver.get("https://www.americanexpress.com/en-us/account/login")

# # logging into the form, making sure to wait until everything loads before proceeding
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='eliloUserID']"))).send_keys(username)
# # find password input box and put it in
# driver.find_element(By.XPATH, "//input[@name='eliloPassword']").send_keys(password)
# # click the log in button
# driver.find_element(By.ID, "loginSubmit").submit()

# # code to keep the page open until I close it
# input("Press ENTER to exit\\n")
# driver.quit()

""""Everything above is done in selenium, does not allow me to log into the website. So I will need something a little more lightweight. Let's try playwright"""
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
import os
import datetime
from pprint import pprint
from playwright.sync_api import sync_playwright
from datetime import timedelta
import re

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
        context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        page.goto(login_url)

        # login to account
        page.wait_for_selector("#eliloUserID", timeout=10000)
        page.type("#eliloUserID", username, delay=150)
        page.type("#eliloPassword", password, delay=145)
        page.click("#loginSubmit")

        # getting to the correct page to download the csvs
        page.wait_for_selector("#hamburgerMenuOpener", timeout=15000)
        page.get_by_test_id("simple_switcher_combobox").click()
        # clicking the element from the drop down that designates the gold card `*=` designates that only part of that word needs to be in the label
        gold_element = page.locator('div[aria-label*="Gold Card"]')
        gold_element.click()
        # working within the gold card
        page.wait_for_selector("#hamburgerMenuOpener", timeout=20000)
        page.get_by_role("link", name="View All Recent Transactions").click()
        page.wait_for_timeout(5000)
        page.get_by_test_id("myca-feed-DateRangePicker-Header").click()
        page.get_by_test_id("dateRangePicker.customDateBadge").click()
        page.get_by_label("Open calendar").click()
        # logic to pick custom dates for the csv
        if day_num < 15:
            page.get_by_label("Previous month").click()
            prev_month_date_string = prev_month + " " + "15," + " " + str(current_date.year)
            # page.locator(f"button[aria-label*={prev_month_date_string}]").click()
            page.get_by_role("button", name=re.compile(prev_month_date_string, re.IGNORECASE)).click()
            page.get_by_label("Next month").click()
            current_date_string = month_name + " " + str(day_num) + "," + " " + str(current_date.year)
            # page.locator(f"button[aria-label*={current_date_string}]").click()
            page.get_by_role("button", re.compile(current_date_string, re.IGNORECASE)).click()
            page.get_by_label("Done").click()
            page.get_by_label("Download").click()

        input("Press ENTER to quit\\n")
        page.close()

if __name__ == "__main__":
    main()